"""
Dashboard views for PLP Accreditation System
Unified dashboard with role-based access control
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from accreditation.decorators import login_required
from accreditation.firebase_utils import (
    get_all_documents, 
    get_document, 
    create_document, 
    update_document, 
    delete_document,
    query_documents
)
from accreditation.forms import UserManagementForm
from accreditation.firebase_auth import FirebaseUser
from accreditation.password_generator import generate_strong_password
from accreditation.cloudinary_utils import upload_image_to_cloudinary
import json
import hashlib
import hashlib
import secrets


def hash_password(raw_password):
    """Hash a password using PBKDF2"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac('sha256', 
                                      raw_password.encode('utf-8'),
                                      salt.encode('utf-8'),
                                      100000)
    return f"{salt}${password_hash.hex()}"


def get_user_from_session(request):
    """Build user object from session data"""
    return {
        'id': request.session.get('user_id'),
        'email': request.session.get('user_email'),
        'role': request.session.get('user_role'),
        'name': request.session.get('user_name'),
    }


@login_required
def dashboard_home(request):
    """
    Main dashboard home page
    Shows stats cards and charts
    """
    context = {
        'active_page': 'dashboard',
        'user': get_user_from_session(request),
    }
    return render(request, 'dashboard_base.html', context)


@login_required
def calendar_view(request):
    """Calendar page"""
    context = {
        'active_page': 'calendar',
        'user': get_user_from_session(request),
    }
    return render(request, 'dashboard/calendar.html', context)


@login_required
def accreditation_view(request):
    """Accreditation page"""
    context = {
        'active_page': 'accreditation',
        'user': get_user_from_session(request),
    }
    return render(request, 'dashboard/accreditation.html', context)


@login_required
def performance_view(request):
    """Performance Management page"""
    context = {
        'active_page': 'performance',
        'user': get_user_from_session(request),
    }
    return render(request, 'dashboard/performance.html', context)


@login_required
def reports_view(request):
    """Reports page"""
    context = {
        'active_page': 'reports',
        'user': get_user_from_session(request),
    }
    return render(request, 'dashboard/reports.html', context)


@login_required
def results_view(request):
    """Results and Incentives page"""
    context = {
        'active_page': 'results',
        'user': get_user_from_session(request),
    }
    return render(request, 'dashboard/results.html', context)


@login_required
def audit_view(request):
    """Audit Trail page"""
    context = {
        'active_page': 'audit',
        'user': get_user_from_session(request),
    }
    return render(request, 'dashboard/audit.html', context)


@login_required
def archive_view(request):
    """Archive page"""
    context = {
        'active_page': 'archive',
        'user': get_user_from_session(request),
    }
    return render(request, 'dashboard/archive.html', context)


@login_required
def settings_view(request):
    """
    Settings page - Shows available settings based on user role
    """
    user = get_user_from_session(request)
    
    context = {
        'active_page': 'settings',
        'user': user,
    }
    return render(request, 'dashboard/settings.html', context)


@login_required
def user_management_view(request):
    """User Management page (QA Head only) - List all users"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head
    if user.get('role') != 'qa_head':
        messages.error(request, 'Access denied. Only QA Head can access User Management.')
        return redirect('dashboard:home')
    
    # Get filter parameters
    department_filter = request.GET.get('department', '')
    role_filter = request.GET.get('role', '')
    search_query = request.GET.get('search', '')
    
    # Get all users
    try:
        all_users = get_all_documents('users')
        
        # Apply filters
        filtered_users = all_users
        
        if department_filter:
            filtered_users = [u for u in filtered_users if u.get('department') == department_filter]
        
        if role_filter:
            filtered_users = [u for u in filtered_users if u.get('role') == role_filter]
        
        if search_query:
            search_query = search_query.lower()
            filtered_users = [
                u for u in filtered_users 
                if search_query in u.get('name', '').lower() 
                or search_query in u.get('email', '').lower()
            ]
        
        # Get departments and roles for filters
        departments = get_all_documents('departments')
        roles = get_all_documents('roles')
        
        # Create department mapping (code -> name)
        dept_mapping = {dept.get('code'): dept.get('name') for dept in departments if dept.get('code')}
        
        # Add department names to users
        for user_item in filtered_users:
            dept_code = user_item.get('department', '')
            user_item['department_name'] = dept_mapping.get(dept_code, dept_code if dept_code else '—')
        
    except Exception as e:
        messages.error(request, f'Error loading users: {str(e)}')
        filtered_users = []
        departments = []
        roles = []
    
    context = {
        'active_page': 'user_management',
        'user': user,
        'users': filtered_users,
        'departments': departments,
        'roles': roles,
        'department_filter': department_filter,
        'role_filter': role_filter,
        'search_query': search_query,
    }
    return render(request, 'dashboard/user_management.html', context)


@login_required
@require_http_methods(["POST"])
def user_add_view(request):
    """Add a new user (QA Head only)"""
    user = get_user_from_session(request)
    
    if user.get('role') != 'qa_head':
        return JsonResponse({'success': False, 'message': 'Access denied.'}, status=403)
    
    try:
        form = UserManagementForm(request.POST)
        
        if form.is_valid():
            # Get form data
            first_name = form.cleaned_data['first_name']
            middle_name = form.cleaned_data.get('middle_name', '')
            last_name = form.cleaned_data['last_name']
            email_prefix = form.cleaned_data['email_prefix']
            department = form.cleaned_data['department']
            role = form.cleaned_data['role']
            status = form.cleaned_data['status']
            
            # Build full name
            if middle_name:
                full_name = f"{first_name} {middle_name} {last_name}"
            else:
                full_name = f"{first_name} {last_name}"
            
            # Build full email
            email = f"{email_prefix}@plpasig.edu.ph"
            
            # Auto-generate strong password
            generated_password = generate_strong_password()
            
            # Check if user already exists
            existing_users = query_documents('users', 'email', '==', email)
            if existing_users:
                return JsonResponse({
                    'success': False, 
                    'message': 'A user with this email already exists.'
                }, status=400)
            
            # Create user document in Firestore
            user_data = {
                'first_name': first_name,
                'middle_name': middle_name,
                'last_name': last_name,
                'name': full_name,
                'email': email,
                'email_prefix': email_prefix,
                'department': department,
                'role': role,
                'is_active': (status == 'active'),
                'password_hash': hash_password(generated_password),  # Hash the password
                'is_password_changed': False,  # User must change password on first login
                'profile_picture': 'https://res.cloudinary.com/dlu2bqrda/image/upload/v1760105137/default-profile-account-unknown-icon-black-silhouette-free-vector_jdlpve.jpg',  # Default profile picture
            }
            
            user_id = create_document('users', user_data)
            
            return JsonResponse({
                'success': True, 
                'message': 'User created successfully!',
                'password': generated_password  # Return password for admin to give to new user
            })
        else:
            errors = dict(form.errors.items())
            return JsonResponse({
                'success': False, 
                'message': 'Please correct the errors below.',
                'errors': errors
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'Error creating user: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def user_edit_view(request, user_id):
    """Edit an existing user (QA Head only)"""
    user = get_user_from_session(request)
    
    if user.get('role') != 'qa_head':
        return JsonResponse({'success': False, 'message': 'Access denied.'}, status=403)
    
    try:
        # Get the user to edit
        user_to_edit = get_document('users', user_id)
        if not user_to_edit:
            return JsonResponse({
                'success': False, 
                'message': 'User not found.'
            }, status=404)
        
        form = UserManagementForm(request.POST, is_edit=True)
        
        if form.is_valid():
            # Get form data
            first_name = form.cleaned_data['first_name']
            middle_name = form.cleaned_data.get('middle_name', '')
            last_name = form.cleaned_data['last_name']
            email_prefix = form.cleaned_data['email_prefix']
            department = form.cleaned_data['department']
            role = form.cleaned_data['role']
            status = form.cleaned_data['status']
            
            # Build full name
            if middle_name:
                full_name = f"{first_name} {middle_name} {last_name}"
            else:
                full_name = f"{first_name} {last_name}"
            
            # Build full email
            email = f"{email_prefix}@plpasig.edu.ph"
            
            # Update user data
            update_data = {
                'first_name': first_name,
                'middle_name': middle_name,
                'last_name': last_name,
                'name': full_name,
                'email': email,
                'email_prefix': email_prefix,
                'department': department,
                'role': role,
                'is_active': (status == 'active'),
            }
            
            update_document('users', user_id, update_data)
            
            return JsonResponse({
                'success': True, 
                'message': 'User updated successfully!'
            })
        else:
            errors = dict(form.errors.items())
            return JsonResponse({
                'success': False, 
                'message': 'Please correct the errors below.',
                'errors': errors
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'Error updating user: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def user_delete_view(request, user_id):
    """Delete a user (QA Head only)"""
    user = get_user_from_session(request)
    
    if user.get('role') != 'qa_head':
        return JsonResponse({'success': False, 'message': 'Access denied.'}, status=403)
    
    try:
        # Get the user to delete
        user_to_delete = get_document('users', user_id)
        if not user_to_delete:
            return JsonResponse({
                'success': False, 
                'message': 'User not found.'
            }, status=404)
        
        # Prevent deleting self
        if user_to_delete.get('email') == user.get('email'):
            return JsonResponse({
                'success': False, 
                'message': 'You cannot delete your own account.'
            }, status=400)
        
        # Delete the user
        delete_document('users', user_id)
        
        return JsonResponse({
            'success': True, 
            'message': 'User deleted successfully!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'Error deleting user: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def user_toggle_status_view(request, user_id):
    """Toggle user active status (QA Head only)"""
    user = get_user_from_session(request)
    
    if user.get('role') != 'qa_head':
        return JsonResponse({'success': False, 'message': 'Access denied.'}, status=403)
    
    try:
        data = json.loads(request.body)
        is_active = data.get('is_active', True)
        
        # Get the user to update
        user_to_update = get_document('users', user_id)
        if not user_to_update:
            return JsonResponse({
                'success': False, 
                'message': 'User not found.'
            }, status=404)
        
        # Prevent deactivating self
        if user_to_update.get('email') == user.get('email') and not is_active:
            return JsonResponse({
                'success': False, 
                'message': 'You cannot deactivate your own account.'
            }, status=400)
        
        # Update the user status
        update_document('users', user_id, {'is_active': is_active})
        
        action = 'activated' if is_active else 'deactivated'
        return JsonResponse({
            'success': True, 
            'message': f'User {action} successfully!'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid request data.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'Error updating user status: {str(e)}'
        }, status=500)


@login_required
def user_get_view(request, user_id):
    """Get user details (QA Head only)"""
    user = get_user_from_session(request)
    
    if user.get('role') != 'qa_head':
        return JsonResponse({'success': False, 'message': 'Access denied.'}, status=403)
    
    try:
        user_data = get_document('users', user_id)
        if not user_data:
            return JsonResponse({
                'success': False, 
                'message': 'User not found.'
            }, status=404)
        
        # Remove password from response
        user_data.pop('password', None)
        
        return JsonResponse({
            'success': True,
            'user': user_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'Error retrieving user: {str(e)}'
        }, status=500)


@login_required
def accreditation_settings_view(request):
    """Accreditation Settings page (QA Head and QA Admin)"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        messages.error(request, 'Access denied. Only QA Head and QA Admin can access Accreditation Settings.')
        return render(request, 'dashboard_base.html', {
            'active_page': 'dashboard',
            'user': user,
        })
    
    # Fetch all departments
    try:
        departments = get_all_documents('departments')
        
        for dept in departments:
            # Set default values if not present
            if 'is_archived' not in dept:
                dept['is_archived'] = False
            if 'logo_url' not in dept:
                dept['logo_url'] = ''  # Use blank as default
        
        # Sort by name
        departments.sort(key=lambda x: x.get('name', ''))
        
    except Exception as e:
        print(f"Error fetching departments: {str(e)}")
        departments = []
    
    context = {
        'active_page': 'accreditation_settings',
        'user': user,
        'departments': departments,
    }
    return render(request, 'dashboard/accreditation_settings.html', context)


@login_required
def system_appearance_view(request):
    """System Appearance page (QA Head and QA Admin)"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        messages.error(request, 'Access denied. Only QA Head and QA Admin can access System Appearance.')
        return render(request, 'dashboard_base.html', {
            'active_page': 'dashboard',
            'user': user,
        })
    
    context = {
        'active_page': 'system_appearance',
        'user': user,
    }
    return render(request, 'dashboard/system_appearance.html', context)


@login_required
def department_settings_view(request):
    """Department Settings page (QA Head and QA Admin)"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        messages.error(request, 'Access denied. Only QA Head and QA Admin can access Department Settings.')
        return redirect('dashboard:home')
    
    # Get all departments
    try:
        departments = get_all_documents('departments')
    except Exception as e:
        messages.error(request, f'Error loading departments: {str(e)}')
        departments = []
    
    context = {
        'active_page': 'department_settings',
        'user': user,
        'departments': departments,
    }
    return render(request, 'dashboard/department_settings.html', context)


@login_required
@require_http_methods(["POST"])
def change_password_view(request):
    """Handle password change for first-time login"""
    user = get_user_from_session(request)
    
    try:
        data = json.loads(request.body)
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        
        # Validate passwords
        if not new_password or not confirm_password:
            return JsonResponse({
                'success': False,
                'message': 'Both password fields are required.'
            }, status=400)
        
        if new_password != confirm_password:
            return JsonResponse({
                'success': False,
                'message': 'Passwords do not match.'
            }, status=400)
        
        if len(new_password) < 6:
            return JsonResponse({
                'success': False,
                'message': 'Password must be at least 6 characters long.'
            }, status=400)
        
        # Get user from database
        user_id = user.get('id')
        users = query_documents('users', 'email', '==', user.get('email'))
        
        if not users:
            return JsonResponse({
                'success': False,
                'message': 'User not found.'
            }, status=404)
        
        user_doc = users[0]
        user_doc_id = user_doc.get('id')
        
        # Update password and mark as changed
        update_data = {
            'password_hash': hash_password(new_password),  # Hash the new password
            'is_password_changed': True
        }
        
        update_document('users', user_doc_id, update_data)
        
        # Update session
        request.session['is_password_changed'] = True
        
        return JsonResponse({
            'success': True,
            'message': 'Password changed successfully!'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid request data.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error changing password: {str(e)}'
        }, status=500)


@login_required
def toast_demo_view(request):
    """Toast notification demo page"""
    context = {
        'active_page': 'toast_demo',
        'user': get_user_from_session(request),
    }
    return render(request, 'dashboard/toast_demo.html', context)


# Legacy views for backward compatibility - redirect to unified dashboard
@login_required
def qa_head_dashboard(request):
    """Redirect to unified dashboard"""
    return dashboard_home(request)


@login_required
def qa_admin_dashboard(request):
    """Redirect to unified dashboard"""
    return dashboard_home(request)


@login_required
def department_dashboard(request):
    """Redirect to unified dashboard"""
    return dashboard_home(request)


@login_required
def dashboard_view(request):
    """Redirect to unified dashboard"""
    return dashboard_home(request)


# Department CRUD Views
@login_required
@require_http_methods(["POST"])
def department_add_view(request):
    """Add a new department"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        return JsonResponse({
            'success': False,
            'message': 'Access denied.'
        }, status=403)
    
    try:
        name = request.POST.get('name', '').strip()
        logo_file = request.FILES.get('logo')
        
        # Validation
        errors = {}
        if not name:
            errors['name'] = ['Department name is required']
        if not logo_file:
            errors['logo'] = ['Department logo is required']
        
        if errors:
            return JsonResponse({
                'success': False,
                'message': 'Validation failed',
                'errors': errors
            })
        
        # Upload logo to Cloudinary
        logo_url = ''
        if logo_file:
            try:
                logo_url = upload_image_to_cloudinary(logo_file, folder='departments')
                if not logo_url:
                    return JsonResponse({
                        'success': False,
                        'message': 'Error uploading logo. Please check Cloudinary configuration.',
                        'errors': {'logo': ['Upload failed. Check console for details.']}
                    })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Error uploading logo: {str(e)}',
                    'errors': {'logo': [f'Upload failed: {str(e)}']}
                })
        
        # Generate department code (e.g., "CCS", "CBA")
        code = ''.join([word[0].upper() for word in name.split()[:3]])
        
        # Check if code already exists
        existing_dept = get_document('departments', code)
        if existing_dept:
            # Try adding a number suffix
            counter = 1
            while get_document('departments', f"{code}{counter}"):
                counter += 1
            code = f"{code}{counter}"
        
        # Create department
        dept_data = {
            'name': name,
            'code': code,
            'logo_url': logo_url,
            'is_archived': False,
            'is_active': True
        }
        
        create_document('departments', code, dept_data)
        
        return JsonResponse({
            'success': True,
            'message': f'Department "{name}" created successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error creating department: {str(e)}'
        }, status=500)


@login_required
def department_get_view(request, dept_id):
    """Get department details"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        return JsonResponse({
            'success': False,
            'message': 'Access denied.'
        }, status=403)
    
    try:
        dept = get_document('departments', dept_id)
        
        if not dept:
            return JsonResponse({
                'success': False,
                'message': 'Department not found'
            }, status=404)
        
        return JsonResponse({
            'success': True,
            'department': dept
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error retrieving department: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def department_edit_view(request, dept_id):
    """Edit department"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        return JsonResponse({
            'success': False,
            'message': 'Access denied.'
        }, status=403)
    
    try:
        # Check if department exists
        dept = get_document('departments', dept_id)
        if not dept:
            return JsonResponse({
                'success': False,
                'message': 'Department not found'
            }, status=404)
        
        name = request.POST.get('name', '').strip()
        logo_file = request.FILES.get('logo')
        current_logo_url = request.POST.get('current_logo_url', '').strip()
        
        # Validation
        errors = {}
        if not name:
            errors['name'] = ['Department name is required']
        
        if errors:
            return JsonResponse({
                'success': False,
                'message': 'Validation failed',
                'errors': errors
            })
        
        # Upload new logo if provided, otherwise keep existing
        logo_url = current_logo_url
        if logo_file:
            try:
                logo_url = upload_image_to_cloudinary(logo_file, folder='departments')
                if not logo_url:
                    return JsonResponse({
                        'success': False,
                        'message': 'Error uploading logo. Please check Cloudinary configuration.',
                        'errors': {'logo': ['Upload failed. Check console for details.']}
                    })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Error uploading logo: {str(e)}',
                    'errors': {'logo': [f'Upload failed: {str(e)}']}
                })
        
        # Update department
        update_data = {
            'name': name,
            'logo_url': logo_url
        }
        
        update_document('departments', dept_id, update_data)
        
        return JsonResponse({
            'success': True,
            'message': f'Department "{name}" updated successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating department: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def department_archive_view(request, dept_id):
    """Archive/Unarchive department"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        return JsonResponse({
            'success': False,
            'message': 'Access denied.'
        }, status=403)
    
    try:
        # Check if department exists
        dept = get_document('departments', dept_id)
        if not dept:
            return JsonResponse({
                'success': False,
                'message': 'Department not found'
            }, status=404)
        
        # Get is_archived from request body
        data = json.loads(request.body)
        is_archived = data.get('is_archived', False)
        
        # Update department
        update_document('departments', dept_id, {'is_archived': is_archived})
        
        action = 'archived' if is_archived else 'unarchived'
        return JsonResponse({
            'success': True,
            'message': f'Department "{dept.get("name")}" {action} successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error archiving department: {str(e)}'
        }, status=500)


def department_delete_view(request, dept_id):
    """Delete department"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        return JsonResponse({
            'success': False,
            'message': 'Access denied.'
        }, status=403)
    
    try:
        # Check if department exists
        dept = get_document('departments', dept_id)
        if not dept:
            return JsonResponse({
                'success': False,
                'message': 'Department not found'
            }, status=404)
        
        dept_name = dept.get('name')
        
        # Delete department
        delete_document('departments', dept_id)
        
        return JsonResponse({
            'success': True,
            'message': f'Department "{dept_name}" deleted successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error deleting department: {str(e)}'
        }, status=500)


def department_toggle_active_view(request, dept_id):
    """Toggle department active status"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        return JsonResponse({
            'success': False,
            'message': 'Access denied.'
        }, status=403)
    
    try:
        # Check if department exists
        dept = get_document('departments', dept_id)
        if not dept:
            return JsonResponse({
                'success': False,
                'message': 'Department not found'
            }, status=404)
        
        # Get is_active from request body
        data = json.loads(request.body)
        is_active = data.get('is_active', False)
        
        # Update department
        update_document('departments', dept_id, {'is_active': is_active})
        
        action = 'activated' if is_active else 'deactivated'
        return JsonResponse({
            'success': True,
            'message': f'Department "{dept.get("name")}" {action} successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating department status: {str(e)}'
        }, status=500)
