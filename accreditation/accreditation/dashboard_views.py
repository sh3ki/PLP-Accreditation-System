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
from accreditation.cloudinary_utils import upload_image_to_cloudinary, delete_image_from_cloudinary
from accreditation.document_validator import validate_document_header
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
    """Accreditation page - displays all active items"""
    user = get_user_from_session(request)
    
    # Fetch all active departments
    try:
        departments = get_all_documents('departments')
        
        # Filter only active and non-archived departments
        departments = [
            dept for dept in departments 
            if dept.get('is_active', True) and not dept.get('is_archived', False)
        ]
        
        for dept in departments:
            # Set default values if not present
            if 'logo_url' not in dept:
                dept['logo_url'] = ''
        
        # Sort by name
        departments.sort(key=lambda x: x.get('name', ''))
        
    except Exception as e:
        print(f"Error fetching departments: {str(e)}")
        departments = []
    
    # Fetch all active programs
    try:
        programs = get_all_documents('programs')
        
        # Filter only active and non-archived programs
        programs = [
            prog for prog in programs 
            if prog.get('is_active', True) and not prog.get('is_archived', False)
        ]
        
        # Sort by code
        programs.sort(key=lambda x: x.get('code', ''))
        
    except Exception as e:
        print(f"Error fetching programs: {str(e)}")
        programs = []
    
    # Fetch all active accreditation types
    try:
        types = get_all_documents('accreditation_types')
        
        # Filter only active and non-archived types
        types = [
            t for t in types 
            if t.get('is_active', True) and not t.get('is_archived', False)
        ]
        
        # Sort by type name
        types.sort(key=lambda x: x.get('type', ''))
        
    except Exception as e:
        print(f"Error fetching types: {str(e)}")
        types = []
    
    # Fetch all active areas
    try:
        areas = get_all_documents('areas')
        
        # Filter only active and non-archived areas
        areas = [
            mod for mod in areas 
            if mod.get('is_active', True) and not mod.get('is_archived', False)
        ]
        
        # Sort by name
        areas.sort(key=lambda x: x.get('name', ''))
        
    except Exception as e:
        print(f"Error fetching areas: {str(e)}")
        areas = []
    
    # NOTE: Checklists are NOT fetched here to avoid quota issues
    # They are loaded dynamically when user navigates to a specific area
    
    context = {
        'active_page': 'accreditation',
        'user': user,
        'departments': departments,
        'programs': programs,
        'types': types,
        'areas': areas,
    }
    return render(request, 'dashboard/accreditation.html', context)


@login_required
def accreditation_department_programs_view(request, dept_id):
    """Accreditation Programs page - read-only view of programs under a department"""
    user = get_user_from_session(request)
    
    # Get department info
    try:
        department = get_document('departments', dept_id)
        if not department:
            messages.error(request, 'Department not found.')
            return redirect('dashboard:accreditation')
    except Exception as e:
        print(f"Error fetching department: {str(e)}")
        messages.error(request, 'Error fetching department.')
        return redirect('dashboard:accreditation')
    
    # Get all active programs for this department
    try:
        all_programs = get_all_documents('programs')
        programs = [
            prog for prog in all_programs 
            if prog.get('department_id') == dept_id 
            and prog.get('is_active', True) 
            and not prog.get('is_archived', False)
        ]
        programs.sort(key=lambda x: x.get('code', ''))
    except Exception as e:
        print(f"Error fetching programs: {str(e)}")
        programs = []
    
    context = {
        'active_page': 'accreditation',
        'user': user,
        'department': department,
        'programs': programs,
        'dept_id': dept_id,
    }
    return render(request, 'dashboard/accreditation_programs.html', context)


@login_required
def accreditation_program_types_view(request, dept_id, prog_id):
    """Accreditation Types page - read-only view of types under a program"""
    user = get_user_from_session(request)
    
    # Get department and program info
    try:
        department = get_document('departments', dept_id)
        program = get_document('programs', prog_id)
        if not department or not program:
            messages.error(request, 'Department or Program not found.')
            return redirect('dashboard:accreditation')
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        messages.error(request, 'Error fetching data.')
        return redirect('dashboard:accreditation')
    
    # Get all active types for this program
    try:
        all_types = get_all_documents('accreditation_types')
        types = [
            t for t in all_types 
            if t.get('program_id') == prog_id 
            and t.get('is_active', True) 
            and not t.get('is_archived', False)
        ]
        types.sort(key=lambda x: x.get('type', ''))
    except Exception as e:
        print(f"Error fetching types: {str(e)}")
        types = []
    
    context = {
        'active_page': 'accreditation',
        'user': user,
        'department': department,
        'program': program,
        'types': types,
        'dept_id': dept_id,
        'prog_id': prog_id,
    }
    return render(request, 'dashboard/accreditation_types.html', context)


@login_required
def accreditation_type_areas_view(request, dept_id, prog_id, type_id):
    """Accreditation Areas page - read-only view of areas under a type"""
    user = get_user_from_session(request)
    
    # Get breadcrumb info
    try:
        department = get_document('departments', dept_id)
        program = get_document('programs', prog_id)
        accreditation_type = get_document('accreditation_types', type_id)
        if not department or not program or not accreditation_type:
            messages.error(request, 'Data not found.')
            return redirect('dashboard:accreditation')
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        messages.error(request, 'Error fetching data.')
        return redirect('dashboard:accreditation')
    
    # Get all active areas for this type
    try:
        all_areas = get_all_documents('areas')
        areas = [
            mod for mod in all_areas 
            if (mod.get('type_id') == type_id or mod.get('accreditation_type_id') == type_id)
            and mod.get('is_active', True) 
            and not mod.get('is_archived', False)
        ]
        areas.sort(key=lambda x: x.get('name', ''))
    except Exception as e:
        print(f"Error fetching areas: {str(e)}")
        areas = []
    
    context = {
        'active_page': 'accreditation',
        'user': user,
        'department': department,
        'program': program,
        'accreditation_type': accreditation_type,
        'areas': areas,
        'dept_id': dept_id,
        'prog_id': prog_id,
        'type_id': type_id,
    }
    return render(request, 'dashboard/accreditation_areas.html', context)


@login_required
def accreditation_area_checklists_view(request, dept_id, prog_id, type_id, area_id):
    """Accreditation Checklists page - read-only view of checklists under a area"""
    user = get_user_from_session(request)
    
    # Get breadcrumb info
    try:
        department = get_document('departments', dept_id)
        program = get_document('programs', prog_id)
        accreditation_type = get_document('accreditation_types', type_id)
        area = get_document('areas', area_id)
        if not department or not program or not accreditation_type or not area:
            messages.error(request, 'Data not found.')
            return redirect('dashboard:accreditation')
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        messages.error(request, 'Error fetching data.')
        return redirect('dashboard:accreditation')
    
    # Get all active checklists for this area
    try:
        all_checklists = get_all_documents('checklists')
        checklists = [
            checklist for checklist in all_checklists 
            if checklist.get('area_id') == area_id 
            and checklist.get('is_active', True) 
            and not checklist.get('is_archived', False)
        ]
        checklists.sort(key=lambda x: x.get('name', ''))
    except Exception as e:
        print(f"Error fetching checklists: {str(e)}")
        checklists = []
    
    context = {
        'active_page': 'accreditation',
        'user': user,
        'department': department,
        'program': program,
        'accreditation_type': accreditation_type,
        'area': area,
        'checklists': checklists,
        'dept_id': dept_id,
        'prog_id': prog_id,
        'type_id': type_id,
        'area_id': area_id,
    }
    return render(request, 'dashboard/accreditation_checklists.html', context)


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
                if search_query in u.get('first_name', '').lower()
                or search_query in u.get('middle_name', '').lower()
                or search_query in u.get('last_name', '').lower()
                or search_query in u.get('email', '').lower()
            ]
        
        # Get departments and roles for filters
        departments = get_all_documents('departments')
        roles = get_all_documents('roles')
        
        # Create department mapping (code -> name)
        dept_mapping = {dept.get('code'): dept.get('name') for dept in departments if dept.get('code')}
        
        # Add department names and construct full names for users
        for user_item in filtered_users:
            # Construct full name from first, middle, and last name
            first_name = user_item.get('first_name', '')
            middle_name = user_item.get('middle_name', '')
            last_name = user_item.get('last_name', '')
            
            # Build full name
            if middle_name:
                user_item['name'] = f"{first_name} {middle_name} {last_name}"
            else:
                user_item['name'] = f"{first_name} {last_name}"
            
            # Add department name
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
                'profile_picture': 'https://res.cloudinary.com/dygrh6ztt/image/upload/v1761284240/default-profile-account-unknown-icon-black-silhouette-free-vector_jdlpve.jpg',  # Default profile picture
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
        
        create_document('departments', dept_data, code)
        
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
                # Delete old logo from Cloudinary if it exists and is from our account
                if current_logo_url and 'dygrh6ztt' in current_logo_url:
                    from accreditation.cloudinary_utils import delete_image_from_cloudinary
                    delete_image_from_cloudinary(current_logo_url)
                
                # Upload new logo
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
        logo_url = dept.get('logo_url', '')
        
        # Delete logo from Cloudinary if it exists and is from our account
        if logo_url and 'dygrh6ztt' in logo_url:
            from accreditation.cloudinary_utils import delete_image_from_cloudinary
            try:
                delete_image_from_cloudinary(logo_url)
            except Exception as e:
                print(f"Warning: Could not delete logo from Cloudinary: {str(e)}")
                # Continue with deletion even if logo deletion fails
        
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


# ============================================
# PROGRAMS MANAGEMENT VIEWS
# ============================================

@login_required
def department_programs_view(request, dept_id):
    """View programs for a specific department"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        messages.error(request, 'Access denied. Only QA Head and QA Admin can access Programs.')
        return render(request, 'dashboard_base.html', {
            'active_page': 'dashboard',
            'user': user,
        })
    
    # Get department details
    try:
        department = get_document('departments', dept_id)
        if not department:
            messages.error(request, 'Department not found.')
            return redirect('dashboard:accreditation_settings')
        
        # Fetch programs for this department
        all_programs = get_all_documents('programs')
        programs = [p for p in all_programs if p.get('department_id') == dept_id]
        
        # Set default values if not present
        for prog in programs:
            if 'is_archived' not in prog:
                prog['is_archived'] = False
            if 'is_active' not in prog:
                prog['is_active'] = True
        
        # Sort by code
        programs.sort(key=lambda x: x.get('code', ''))
        
    except Exception as e:
        print(f"Error fetching programs: {str(e)}")
        programs = []
        department = {'name': 'Unknown Department', 'code': dept_id}
    
    context = {
        'active_page': 'accreditation_settings',
        'user': user,
        'department': department,
        'programs': programs,
    }
    return render(request, 'dashboard/department_programs.html', context)


@login_required
@require_http_methods(["POST"])
def program_add_view(request, dept_id):
    """Add a new program to a department"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        return JsonResponse({
            'success': False,
            'message': 'Access denied.'
        }, status=403)
    
    try:
        # Verify department exists
        department = get_document('departments', dept_id)
        if not department:
            return JsonResponse({
                'success': False,
                'message': 'Department not found'
            }, status=404)
        
        code = request.POST.get('code', '').strip().upper()
        name = request.POST.get('name', '').strip()
        
        # Validation
        errors = {}
        if not code:
            errors['code'] = ['Program code is required']
        if not name:
            errors['name'] = ['Program name is required']
        
        if errors:
            return JsonResponse({
                'success': False,
                'message': 'Validation failed',
                'errors': errors
            })
        
        # Check if code already exists
        existing_prog = get_document('programs', code)
        if existing_prog:
            return JsonResponse({
                'success': False,
                'message': 'Program code already exists',
                'errors': {'code': ['This program code is already in use']}
            })
        
        # Create program
        prog_data = {
            'code': code,
            'name': name,
            'department_id': dept_id,
            'is_archived': False,
            'is_active': True
        }
        
        create_document('programs', prog_data, code)
        
        return JsonResponse({
            'success': True,
            'message': f'Program "{name}" created successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error creating program: {str(e)}'
        }, status=500)


@login_required
def program_get_view(request, dept_id, prog_id):
    """Get program details"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        return JsonResponse({
            'success': False,
            'message': 'Access denied.'
        }, status=403)
    
    try:
        prog = get_document('programs', prog_id)
        
        if not prog:
            return JsonResponse({
                'success': False,
                'message': 'Program not found'
            }, status=404)
        
        return JsonResponse({
            'success': True,
            'program': prog
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error retrieving program: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def program_edit_view(request, dept_id, prog_id):
    """Edit program"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        return JsonResponse({
            'success': False,
            'message': 'Access denied.'
        }, status=403)
    
    try:
        # Check if program exists
        prog = get_document('programs', prog_id)
        if not prog:
            return JsonResponse({
                'success': False,
                'message': 'Program not found'
            }, status=404)
        
        name = request.POST.get('name', '').strip()
        
        # Validation
        errors = {}
        if not name:
            errors['name'] = ['Program name is required']
        
        if errors:
            return JsonResponse({
                'success': False,
                'message': 'Validation failed',
                'errors': errors
            })
        
        # Update program (code cannot be changed)
        update_data = {
            'name': name
        }
        
        update_document('programs', prog_id, update_data)
        
        return JsonResponse({
            'success': True,
            'message': f'Program "{name}" updated successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating program: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def program_archive_view(request, dept_id, prog_id):
    """Archive/Unarchive program"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        return JsonResponse({
            'success': False,
            'message': 'Access denied.'
        }, status=403)
    
    try:
        # Check if program exists
        prog = get_document('programs', prog_id)
        if not prog:
            return JsonResponse({
                'success': False,
                'message': 'Program not found'
            }, status=404)
        
        # Get is_archived from request body
        data = json.loads(request.body)
        is_archived = data.get('is_archived', False)
        
        # Update program
        update_document('programs', prog_id, {'is_archived': is_archived})
        
        action = 'archived' if is_archived else 'unarchived'
        return JsonResponse({
            'success': True,
            'message': f'Program "{prog.get("name")}" {action} successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error archiving program: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def program_delete_view(request, dept_id, prog_id):
    """Delete program"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        return JsonResponse({
            'success': False,
            'message': 'Access denied.'
        }, status=403)
    
    try:
        # Check if program exists
        prog = get_document('programs', prog_id)
        if not prog:
            return JsonResponse({
                'success': False,
                'message': 'Program not found'
            }, status=404)
        
        prog_name = prog.get('name')
        
        # Delete program
        delete_document('programs', prog_id)
        
        return JsonResponse({
            'success': True,
            'message': f'Program "{prog_name}" deleted successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error deleting program: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def program_toggle_active_view(request, dept_id, prog_id):
    """Toggle program active status"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        return JsonResponse({
            'success': False,
            'message': 'Access denied.'
        }, status=403)
    
    try:
        # Check if program exists
        prog = get_document('programs', prog_id)
        if not prog:
            return JsonResponse({
                'success': False,
                'message': 'Program not found'
            }, status=404)
        
        # Get is_active from request body
        data = json.loads(request.body)
        is_active = data.get('is_active', False)
        
        # Update program
        update_document('programs', prog_id, {'is_active': is_active})
        
        action = 'activated' if is_active else 'deactivated'
        return JsonResponse({
            'success': True,
            'message': f'Program "{prog.get("name")}" {action} successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating program status: {str(e)}'
        }, status=500)


# =============================================
# ACCREDITATION TYPES MANAGEMENT VIEWS
# =============================================

@login_required
def program_types_view(request, dept_id, prog_id):
    """View accreditation types for a specific program"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        messages.error(request, 'Access denied. Only QA Head and QA Admin can access Accreditation Types.')
        return render(request, 'dashboard_base.html', {
            'active_page': 'dashboard',
            'user': user,
        })
    
    # Get department and program details
    try:
        department = get_document('departments', dept_id)
        if not department:
            messages.error(request, 'Department not found.')
            return redirect('dashboard:accreditation_settings')
        
        program = get_document('programs', prog_id)
        if not program:
            messages.error(request, 'Program not found.')
            return redirect('dashboard:department_programs', dept_id=dept_id)
        
        # Fetch accreditation types for this program
        all_types = get_all_documents('accreditation_types')
        types = [t for t in all_types if t.get('program_id') == prog_id]
        
        # Set default values if not present
        for type_item in types:
            if 'is_archived' not in type_item:
                type_item['is_archived'] = False
            if 'is_active' not in type_item:
                type_item['is_active'] = True
            if 'logo_url' not in type_item:
                type_item['logo_url'] = ''
        
        # Sort by name
        types.sort(key=lambda x: x.get('name', ''))
        
    except Exception as e:
        print(f"Error fetching accreditation types: {str(e)}")
        types = []
        program = {'name': 'Unknown Program', 'code': prog_id}
        department = {'name': 'Unknown Department', 'code': dept_id}
    
    context = {
        'active_page': 'accreditation_settings',
        'user': user,
        'department': department,
        'program': program,
        'types': types,
    }
    return render(request, 'dashboard/program_types.html', context)


@login_required
@require_http_methods(["POST"])
def accreditation_type_add_view(request, dept_id, prog_id):
    """Add a new accreditation type to a program"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        return JsonResponse({
            'success': False,
            'message': 'Access denied.'
        }, status=403)
    
    try:
        # Verify program exists
        program = get_document('programs', prog_id)
        if not program:
            return JsonResponse({
                'success': False,
                'message': 'Program not found'
            }, status=404)
        
        name = request.POST.get('name', '').strip()
        logo_file = request.FILES.get('logo')
        
        # Validation
        errors = {}
        if not name:
            errors['name'] = ['Type name is required']
        
        if errors:
            return JsonResponse({
                'success': False,
                'message': 'Validation failed',
                'errors': errors
            })
        
        # Generate unique ID for the type
        import uuid
        type_id = str(uuid.uuid4())
        
        # Upload logo if provided
        logo_url = ''
        if logo_file:
            try:
                logo_url = upload_image_to_cloudinary(logo_file, 'departments')
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Error uploading logo: {str(e)}'
                }, status=500)
        
        # Create accreditation type
        type_data = {
            'id': type_id,
            'name': name,
            'program_id': prog_id,
            'logo_url': logo_url,
            'is_archived': False,
            'is_active': True
        }
        
        create_document('accreditation_types', type_data, type_id)
        
        return JsonResponse({
            'success': True,
            'message': f'Accreditation type "{name}" created successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error creating accreditation type: {str(e)}'
        }, status=500)


@login_required
def accreditation_type_get_view(request, dept_id, prog_id, type_id):
    """Get accreditation type details"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        return JsonResponse({
            'success': False,
            'message': 'Access denied.'
        }, status=403)
    
    try:
        type_item = get_document('accreditation_types', type_id)
        if not type_item:
            return JsonResponse({
                'success': False,
                'message': 'Accreditation type not found'
            }, status=404)
        
        return JsonResponse({
            'success': True,
            'type': type_item
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error retrieving accreditation type: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def accreditation_type_edit_view(request, dept_id, prog_id, type_id):
    """Edit an existing accreditation type"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        return JsonResponse({
            'success': False,
            'message': 'Access denied.'
        }, status=403)
    
    try:
        # Check if type exists
        type_item = get_document('accreditation_types', type_id)
        if not type_item:
            return JsonResponse({
                'success': False,
                'message': 'Accreditation type not found'
            }, status=404)
        
        name = request.POST.get('name', '').strip()
        logo_file = request.FILES.get('logo')
        
        # Validation
        errors = {}
        if not name:
            errors['name'] = ['Type name is required']
        
        if errors:
            return JsonResponse({
                'success': False,
                'message': 'Validation failed',
                'errors': errors
            })
        
        # Prepare update data
        update_data = {
            'name': name
        }
        
        # Upload new logo if provided and delete old logo
        if logo_file:
            try:
                # Delete old logo if exists
                old_logo_url = type_item.get('logo_url')
                if old_logo_url:
                    delete_image_from_cloudinary(old_logo_url)
                
                logo_url = upload_image_to_cloudinary(logo_file, 'departments')
                update_data['logo_url'] = logo_url
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Error uploading logo: {str(e)}'
                }, status=500)
        
        # Update type
        update_document('accreditation_types', type_id, update_data)
        
        return JsonResponse({
            'success': True,
            'message': f'Accreditation type "{name}" updated successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating accreditation type: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def accreditation_type_archive_view(request, dept_id, prog_id, type_id):
    """Archive accreditation type"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        return JsonResponse({
            'success': False,
            'message': 'Access denied.'
        }, status=403)
    
    try:
        # Check if type exists
        type_item = get_document('accreditation_types', type_id)
        if not type_item:
            return JsonResponse({
                'success': False,
                'message': 'Accreditation type not found'
            }, status=404)
        
        # Get is_archived from request body
        data = json.loads(request.body)
        is_archived = data.get('is_archived', False)
        
        # Update type
        update_document('accreditation_types', type_id, {'is_archived': is_archived})
        
        action = 'archived' if is_archived else 'unarchived'
        return JsonResponse({
            'success': True,
            'message': f'Accreditation type "{type_item.get("name")}" {action} successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error archiving accreditation type: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def accreditation_type_delete_view(request, dept_id, prog_id, type_id):
    """Delete accreditation type"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        return JsonResponse({
            'success': False,
            'message': 'Access denied.'
        }, status=403)
    
    try:
        # Check if type exists
        type_item = get_document('accreditation_types', type_id)
        if not type_item:
            return JsonResponse({
                'success': False,
                'message': 'Accreditation type not found'
            }, status=404)
        
        type_name = type_item.get('name')
        
        # Delete logo from Cloudinary if exists
        logo_url = type_item.get('logo_url')
        if logo_url:
            try:
                delete_image_from_cloudinary(logo_url)
            except Exception as e:
                print(f"Error deleting logo from Cloudinary: {str(e)}")
        
        # Delete type
        delete_document('accreditation_types', type_id)
        
        return JsonResponse({
            'success': True,
            'message': f'Accreditation type "{type_name}" deleted successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error deleting accreditation type: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def accreditation_type_toggle_active_view(request, dept_id, prog_id, type_id):
    """Toggle accreditation type active status"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        return JsonResponse({
            'success': False,
            'message': 'Access denied.'
        }, status=403)
    
    try:
        # Check if type exists
        type_item = get_document('accreditation_types', type_id)
        if not type_item:
            return JsonResponse({
                'success': False,
                'message': 'Accreditation type not found'
            }, status=404)
        
        # Get is_active from request body
        data = json.loads(request.body)
        is_active = data.get('is_active', False)
        
        # Update type
        update_document('accreditation_types', type_id, {'is_active': is_active})
        
        action = 'activated' if is_active else 'deactivated'
        return JsonResponse({
            'success': True,
            'message': f'Accreditation type "{type_item.get("name")}" {action} successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating accreditation type status: {str(e)}'
        }, status=500)


# =============================================
# AREAS MANAGEMENT VIEWS
# =============================================

@login_required
def type_areas_view(request, dept_id, prog_id, type_id):
    """View areas for a specific accreditation type"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        messages.error(request, 'Access denied. Only QA Head and QA Admin can access Areas.')
        return render(request, 'dashboard_base.html', {
            'active_page': 'dashboard',
            'user': user,
        })
    
    # Get department, program, and type details
    try:
        department = get_document('departments', dept_id)
        if not department:
            messages.error(request, 'Department not found.')
            return redirect('dashboard:accreditation_settings')
        
        program = get_document('programs', prog_id)
        if not program:
            messages.error(request, 'Program not found.')
            return redirect('dashboard:department_programs', dept_id=dept_id)
        
        accreditation_type = get_document('accreditation_types', type_id)
        if not accreditation_type:
            messages.error(request, 'Accreditation type not found.')
            return redirect('dashboard:program_types', dept_id=dept_id, prog_id=prog_id)
        
        # Fetch areas for this type
        all_areas = get_all_documents('areas')
        areas = [m for m in all_areas if m.get('accreditation_type_id') == type_id]
        
        # Set default values if not present
        for area in areas:
            if 'is_archived' not in area:
                area['is_archived'] = False
            if 'is_active' not in area:
                area['is_active'] = True
        
        # Sort by name
        areas.sort(key=lambda x: x.get('name', ''))
        
    except Exception as e:
        print(f"Error fetching areas: {str(e)}")
        areas = []
        accreditation_type = {'name': 'Unknown Type', 'id': type_id}
        program = {'name': 'Unknown Program', 'code': prog_id}
        department = {'name': 'Unknown Department', 'code': dept_id}
    
    context = {
        'active_page': 'accreditation_settings',
        'user': user,
        'department': department,
        'program': program,
        'accreditation_type': accreditation_type,
        'areas': areas,
    }
    return render(request, 'dashboard/type_areas.html', context)


@login_required
@require_http_methods(["POST"])
def area_add_view(request, dept_id, prog_id, type_id):
    """Add a new area to an accreditation type"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        return JsonResponse({
            'success': False,
            'message': 'Access denied.'
        }, status=403)
    
    try:
        # Verify type exists
        accreditation_type = get_document('accreditation_types', type_id)
        if not accreditation_type:
            return JsonResponse({
                'success': False,
                'message': 'Accreditation type not found'
            }, status=404)
        
        name = request.POST.get('name', '').strip()
        
        # Validation
        errors = {}
        if not name:
            errors['name'] = ['Area name is required']
        
        if errors:
            return JsonResponse({
                'success': False,
                'message': 'Validation failed',
                'errors': errors
            })
        
        # Generate unique ID for the area
        import uuid
        area_id = str(uuid.uuid4())
        
        # Create area
        module_data = {
            'id': area_id,
            'name': name,
            'accreditation_type_id': type_id,
            'is_archived': False,
            'is_active': True
        }
        
        create_document('areas', module_data, area_id)
        
        return JsonResponse({
            'success': True,
            'message': f'Area "{name}" created successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error creating area: {str(e)}'
        }, status=500)


@login_required
def area_get_view(request, dept_id, prog_id, type_id, area_id):
    """Get area details"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        return JsonResponse({
            'success': False,
            'message': 'Access denied.'
        }, status=403)
    
    try:
        area = get_document('areas', area_id)
        if not area:
            return JsonResponse({
                'success': False,
                'message': 'Area not found'
            }, status=404)
        
        return JsonResponse({
            'success': True,
            'area': area
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error retrieving area: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def area_edit_view(request, dept_id, prog_id, type_id, area_id):
    """Edit an existing area"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        return JsonResponse({
            'success': False,
            'message': 'Access denied.'
        }, status=403)
    
    try:
        # Check if area exists
        area = get_document('areas', area_id)
        if not area:
            return JsonResponse({
                'success': False,
                'message': 'Area not found'
            }, status=404)
        
        name = request.POST.get('name', '').strip()
        
        # Validation
        errors = {}
        if not name:
            errors['name'] = ['Area name is required']
        
        if errors:
            return JsonResponse({
                'success': False,
                'message': 'Validation failed',
                'errors': errors
            })
        
        # Update area
        update_document('areas', area_id, {'name': name})
        
        return JsonResponse({
            'success': True,
            'message': f'Area "{name}" updated successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating area: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def area_archive_view(request, dept_id, prog_id, type_id, area_id):
    """Archive area"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        return JsonResponse({
            'success': False,
            'message': 'Access denied.'
        }, status=403)
    
    try:
        # Check if area exists
        area = get_document('areas', area_id)
        if not area:
            return JsonResponse({
                'success': False,
                'message': 'Area not found'
            }, status=404)
        
        # Get is_archived from request body
        data = json.loads(request.body)
        is_archived = data.get('is_archived', False)
        
        # Update area
        update_document('areas', area_id, {'is_archived': is_archived})
        
        action = 'archived' if is_archived else 'unarchived'
        return JsonResponse({
            'success': True,
            'message': f'Area "{area.get("name")}" {action} successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error archiving area: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def area_delete_view(request, dept_id, prog_id, type_id, area_id):
    """Delete area"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        return JsonResponse({
            'success': False,
            'message': 'Access denied.'
        }, status=403)
    
    try:
        # Check if area exists
        area = get_document('areas', area_id)
        if not area:
            return JsonResponse({
                'success': False,
                'message': 'Area not found'
            }, status=404)
        
        module_name = area.get('name')
        
        # Delete area
        delete_document('areas', area_id)
        
        return JsonResponse({
            'success': True,
            'message': f'Area "{module_name}" deleted successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error deleting area: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def area_toggle_active_view(request, dept_id, prog_id, type_id, area_id):
    """Toggle area active status"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        return JsonResponse({
            'success': False,
            'message': 'Access denied.'
        }, status=403)
    
    try:
        # Check if area exists
        area = get_document('areas', area_id)
        if not area:
            return JsonResponse({
                'success': False,
                'message': 'Area not found'
            }, status=404)
        
        # Get is_active from request body
        data = json.loads(request.body)
        is_active = data.get('is_active', False)
        
        # Update area
        update_document('areas', area_id, {'is_active': is_active})
        
        action = 'activated' if is_active else 'deactivated'
        return JsonResponse({
            'success': True,
            'message': f'Area "{area.get("name")}" {action} successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating area status: {str(e)}'
        }, status=500)


# =============================================
# CHECKLISTS MANAGEMENT VIEWS
# =============================================

@login_required
def area_checklists_view(request, dept_id, prog_id, type_id, area_id):
    """View checklists for a specific area"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        messages.error(request, 'Access denied. Only QA Head and QA Admin can access Checklists.')
        return render(request, 'dashboard_base.html', {
            'active_page': 'dashboard',
            'user': user,
        })
    
    # Get department, program, type, and area details
    try:
        department = get_document('departments', dept_id)
        if not department:
            messages.error(request, 'Department not found.')
            return redirect('dashboard:accreditation_settings')
        
        program = get_document('programs', prog_id)
        if not program:
            messages.error(request, 'Program not found.')
            return redirect('dashboard:department_programs', dept_id=dept_id)
        
        accreditation_type = get_document('accreditation_types', type_id)
        if not accreditation_type:
            messages.error(request, 'Accreditation type not found.')
            return redirect('dashboard:program_types', dept_id=dept_id, prog_id=prog_id)
        
        area = get_document('areas', area_id)
        if not area:
            messages.error(request, 'Area not found.')
            return redirect('dashboard:type_areas', dept_id=dept_id, prog_id=prog_id, type_id=type_id)
        
        # Fetch checklists for this area
        all_checklists = get_all_documents('checklists')
        checklists = [c for c in all_checklists if c.get('area_id') == area_id]
        
        # Set default values if not present
        for checklist in checklists:
            if 'is_archived' not in checklist:
                checklist['is_archived'] = False
            if 'is_active' not in checklist:
                checklist['is_active'] = True
        
        # Sort by checklist number (extract number from "Checklist X")
        def get_checklist_number(checklist):
            name = checklist.get('name', '')
            try:
                # Extract number from "Checklist X" format
                if 'Checklist' in name:
                    return int(name.replace('Checklist', '').strip())
                return 0
            except:
                return 0
        
        checklists.sort(key=get_checklist_number)
        
    except Exception as e:
        print(f"Error fetching checklists: {str(e)}")
        checklists = []
        area = {'name': 'Unknown Area', 'id': area_id}
        accreditation_type = {'name': 'Unknown Type', 'id': type_id}
        program = {'name': 'Unknown Program', 'code': prog_id}
        department = {'name': 'Unknown Department', 'code': dept_id}
    
    context = {
        'active_page': 'accreditation_settings',
        'user': user,
        'department': department,
        'program': program,
        'accreditation_type': accreditation_type,
        'area': area,
        'checklists': checklists,
    }
    return render(request, 'dashboard/area_checklists.html', context)


@login_required
@require_http_methods(["POST"])
def checklist_add_view(request, dept_id, prog_id, type_id, area_id):
    """Add a new checklist to a area"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        return JsonResponse({
            'success': False,
            'message': 'Access denied.'
        }, status=403)
    
    try:
        # Verify area exists
        area = get_document('areas', area_id)
        if not area:
            return JsonResponse({
                'success': False,
                'message': 'Area not found'
            }, status=404)
        
        name = request.POST.get('name', '').strip()
        
        # Validation
        errors = {}
        if not name:
            errors['name'] = ['Checklist name is required']
        
        if errors:
            return JsonResponse({
                'success': False,
                'message': 'Validation failed',
                'errors': errors
            })
        
        # Generate unique ID for the checklist
        import uuid
        checklist_id = str(uuid.uuid4())
        
        # Create checklist
        checklist_data = {
            'id': checklist_id,
            'name': name,
            'area_id': area_id,
            'is_archived': False,
            'is_active': True
        }
        
        create_document('checklists', checklist_data, checklist_id)
        
        return JsonResponse({
            'success': True,
            'message': f'Checklist "{name}" created successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error creating checklist: {str(e)}'
        }, status=500)


@login_required
def checklist_get_view(request, dept_id, prog_id, type_id, area_id, checklist_id):
    """Get checklist details"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        return JsonResponse({
            'success': False,
            'message': 'Access denied.'
        }, status=403)
    
    try:
        checklist = get_document('checklists', checklist_id)
        if not checklist:
            return JsonResponse({
                'success': False,
                'message': 'Checklist not found'
            }, status=404)
        
        return JsonResponse({
            'success': True,
            'checklist': checklist
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error retrieving checklist: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def checklist_edit_view(request, dept_id, prog_id, type_id, area_id, checklist_id):
    """Edit an existing checklist"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        return JsonResponse({
            'success': False,
            'message': 'Access denied.'
        }, status=403)
    
    try:
        # Check if checklist exists
        checklist = get_document('checklists', checklist_id)
        if not checklist:
            return JsonResponse({
                'success': False,
                'message': 'Checklist not found'
            }, status=404)
        
        name = request.POST.get('name', '').strip()
        
        # Validation
        errors = {}
        if not name:
            errors['name'] = ['Checklist name is required']
        
        if errors:
            return JsonResponse({
                'success': False,
                'message': 'Validation failed',
                'errors': errors
            })
        
        # Update checklist
        update_document('checklists', checklist_id, {'name': name})
        
        return JsonResponse({
            'success': True,
            'message': f'Checklist "{name}" updated successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating checklist: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def checklist_archive_view(request, dept_id, prog_id, type_id, area_id, checklist_id):
    """Archive checklist"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        return JsonResponse({
            'success': False,
            'message': 'Access denied.'
        }, status=403)
    
    try:
        # Check if checklist exists
        checklist = get_document('checklists', checklist_id)
        if not checklist:
            return JsonResponse({
                'success': False,
                'message': 'Checklist not found'
            }, status=404)
        
        # Get is_archived from request body
        data = json.loads(request.body)
        is_archived = data.get('is_archived', False)
        
        # Update checklist
        update_document('checklists', checklist_id, {'is_archived': is_archived})
        
        action = 'archived' if is_archived else 'unarchived'
        return JsonResponse({
            'success': True,
            'message': f'Checklist "{checklist.get("name")}" {action} successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error archiving checklist: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def checklist_delete_view(request, dept_id, prog_id, type_id, area_id, checklist_id):
    """Delete checklist"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        return JsonResponse({
            'success': False,
            'message': 'Access denied.'
        }, status=403)
    
    try:
        # Check if checklist exists
        checklist = get_document('checklists', checklist_id)
        if not checklist:
            return JsonResponse({
                'success': False,
                'message': 'Checklist not found'
            }, status=404)
        
        checklist_name = checklist.get('name')
        
        # Delete checklist
        delete_document('checklists', checklist_id)
        
        return JsonResponse({
            'success': True,
            'message': f'Checklist "{checklist_name}" deleted successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error deleting checklist: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def checklist_toggle_active_view(request, dept_id, prog_id, type_id, area_id, checklist_id):
    """Toggle checklist active status"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        return JsonResponse({
            'success': False,
            'message': 'Access denied.'
        }, status=403)
    
    try:
        # Check if checklist exists
        checklist = get_document('checklists', checklist_id)
        if not checklist:
            return JsonResponse({
                'success': False,
                'message': 'Checklist not found'
            }, status=404)
        
        # Get is_active from request body
        data = json.loads(request.body)
        is_active = data.get('is_active', False)
        
        # Update checklist
        update_document('checklists', checklist_id, {'is_active': is_active})
        
        action = 'activated' if is_active else 'deactivated'
        return JsonResponse({
            'success': True,
            'message': f'Checklist "{checklist.get("name")}" {action} successfully'
        })
        
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating checklist status: {str(e)}'
        }, status=500)


# ============================================
# ARCHIVE API VIEWS
# ============================================

@login_required
def archive_api_departments(request):
    """Get archived departments"""
    user = get_user_from_session(request)
    
    try:
        # Get all archived departments
        archived_depts = query_documents('departments', 'is_archived', '==', True)
        
        return JsonResponse({
            'success': True,
            'items': archived_depts
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error retrieving archived departments: {str(e)}'
        }, status=500)


@login_required
def archive_api_programs(request):
    """Get archived programs"""
    user = get_user_from_session(request)
    
    try:
        # Get all archived programs
        archived_programs = query_documents('programs', 'is_archived', '==', True)
        
        # Fetch department info for each program
        for program in archived_programs:
            if program.get('department_id'):
                dept = get_document('departments', program['department_id'])
                if dept:
                    program['department_code'] = dept.get('code', 'N/A')
                    program['department_name'] = dept.get('name', 'Unknown Department')
                    program['department_logo'] = dept.get('logo_url', '')
        
        return JsonResponse({
            'success': True,
            'items': archived_programs
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error retrieving archived programs: {str(e)}'
        }, status=500)


@login_required
def archive_api_types(request):
    """Get archived accreditation types"""
    user = get_user_from_session(request)
    
    try:
        # Get all archived types
        archived_types = query_documents('accreditation_types', 'is_archived', '==', True)
        
        # Fetch department and program info for each type
        for type_item in archived_types:
            if type_item.get('program_id'):
                program = get_document('programs', type_item['program_id'])
                if program:
                    type_item['program_code'] = program.get('code', 'N/A')
                    type_item['program_name'] = program.get('name', 'Unknown Program')
                    
                    # Get department info
                    if program.get('department_id'):
                        dept = get_document('departments', program['department_id'])
                        if dept:
                            type_item['department_code'] = dept.get('code', 'N/A')
                            type_item['department_name'] = dept.get('name', 'Unknown Department')
        
        return JsonResponse({
            'success': True,
            'items': archived_types
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error retrieving archived types: {str(e)}'
        }, status=500)


@login_required
def archive_api_areas(request):
    """Get archived areas"""
    user = get_user_from_session(request)
    
    try:
        # Get all archived areas
        archived_areas = query_documents('areas', 'is_archived', '==', True)
        
        # Fetch type, program, and department info for each area
        for area in archived_areas:
            # Initialize with defaults
            area['department_code'] = 'N/A'
            area['program_code'] = 'N/A'
            area['type_name'] = 'Unknown Type'
            
            type_id = area.get('type_id') or area.get('accreditation_type_id')
            if type_id:
                type_item = get_document('accreditation_types', type_id)
                if type_item:
                    area['type_name'] = type_item.get('name', 'Unknown Type')
                    
                    # Get program info
                    program_id = type_item.get('program_id')
                    if program_id:
                        program = get_document('programs', program_id)
                        if program:
                            area['program_code'] = program.get('code', 'N/A')
                            area['program_name'] = program.get('name', 'Unknown Program')
                            
                            # Get department info
                            dept_id = program.get('department_id')
                            if dept_id:
                                dept = get_document('departments', dept_id)
                                if dept:
                                    area['department_code'] = dept.get('code', 'N/A')
                                    area['department_name'] = dept.get('name', 'Unknown Department')
        
        return JsonResponse({
            'success': True,
            'items': archived_areas
        })
        
    except Exception as e:
        import traceback
        print(f"Error in archive_api_areas: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'message': f'Error retrieving archived areas: {str(e)}'
        }, status=500)


@login_required
def archive_api_checklists(request):
    """Get archived checklists"""
    user = get_user_from_session(request)
    
    try:
        # Get all archived checklists
        archived_checklists = query_documents('checklists', 'is_archived', '==', True)
        
        # Fetch area, type, program, and department info for each checklist
        for checklist in archived_checklists:
            # Initialize with defaults
            checklist['department_code'] = 'N/A'
            checklist['program_code'] = 'N/A'
            checklist['type_name'] = 'Unknown Type'
            checklist['module_name'] = 'Unknown Area'
            
            area_id = checklist.get('area_id')
            if area_id:
                area = get_document('areas', area_id)
                if area:
                    checklist['module_name'] = area.get('name', 'Unknown Area')
                    
                    # Get type info
                    type_id = area.get('type_id') or area.get('accreditation_type_id')
                    if type_id:
                        type_item = get_document('accreditation_types', type_id)
                        if type_item:
                            checklist['type_name'] = type_item.get('name', 'Unknown Type')
                            
                            # Get program info
                            program_id = type_item.get('program_id')
                            if program_id:
                                program = get_document('programs', program_id)
                                if program:
                                    checklist['program_code'] = program.get('code', 'N/A')
                                    checklist['program_name'] = program.get('name', 'Unknown Program')
                                    
                                    # Get department info
                                    dept_id = program.get('department_id')
                                    if dept_id:
                                        dept = get_document('departments', dept_id)
                                        if dept:
                                            checklist['department_code'] = dept.get('code', 'N/A')
                                            checklist['department_name'] = dept.get('name', 'Unknown Department')
        
        return JsonResponse({
            'success': True,
            'items': archived_checklists
        })
        
    except Exception as e:
        import traceback
        print(f"Error in archive_api_checklists: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'message': f'Error retrieving archived checklists: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def archive_api_unarchive(request, item_type, item_id):
    """Unarchive any item"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        return JsonResponse({
            'success': False,
            'message': 'Access denied.'
        }, status=403)
    
    try:
        # Map item type to collection name
        collection_map = {
            'departments': 'departments',
            'programs': 'programs',
            'types': 'accreditation_types',
            'areas': 'areas',
            'checklists': 'checklists'
        }
        
        collection = collection_map.get(item_type)
        if not collection:
            return JsonResponse({
                'success': False,
                'message': 'Invalid item type'
            }, status=400)
        
        # Get the item
        item = get_document(collection, item_id)
        if not item:
            return JsonResponse({
                'success': False,
                'message': 'Item not found'
            }, status=404)
        
        # Unarchive the item
        update_document(collection, item_id, {'is_archived': False})
        
        item_name = item.get('name') or item.get('code', 'Item')
        
        return JsonResponse({
            'success': True,
            'message': f'"{item_name}" unarchived successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error unarchiving item: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def archive_api_delete(request, item_type, item_id):
    """Permanently delete archived item"""
    user = get_user_from_session(request)
    
    # Check if user is QA Head or QA Admin
    if user.get('role') not in ['qa_head', 'qa_admin']:
        return JsonResponse({
            'success': False,
            'message': 'Access denied.'
        }, status=403)
    
    try:
        # Map item type to collection name
        collection_map = {
            'departments': 'departments',
            'programs': 'programs',
            'types': 'accreditation_types',
            'areas': 'areas',
            'checklists': 'checklists'
        }
        
        collection = collection_map.get(item_type)
        if not collection:
            return JsonResponse({
                'success': False,
                'message': 'Invalid item type'
            }, status=400)
        
        # Get the item
        item = get_document(collection, item_id)
        if not item:
            return JsonResponse({
                'success': False,
                'message': 'Item not found'
            }, status=404)
        
        item_name = item.get('name') or item.get('code', 'Item')
        
        # Delete image if it's a department or type
        if item_type in ['departments', 'types']:
            logo_url = item.get('logo_url')
            if logo_url:
                try:
                    delete_image_from_cloudinary(logo_url)
                except Exception as e:
                    print(f"Error deleting image from Cloudinary: {str(e)}")
        
        # Delete the item
        delete_document(collection, item_id)
        
        
        return JsonResponse({
            'success': True,
            'message': f'"{item_name}" permanently deleted'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error deleting item: {str(e)}'
        }, status=500)


# ============================================
# DOCUMENT MANAGEMENT VIEWS
# ============================================

@login_required
def checklist_documents_view(request, dept_id, prog_id, type_id, area_id, checklist_id):
    """View documents for a specific checklist"""
    user = get_user_from_session(request)
    
    try:
        # Get breadcrumb data
        department = get_document('departments', dept_id)
        program = get_document('programs', prog_id)
        accreditation_type = get_document('accreditation_types', type_id)
        area = get_document('areas', area_id)
        checklist = get_document('checklists', checklist_id)
        
        if not all([department, program, accreditation_type, area, checklist]):
            messages.error(request, 'Data not found.')
            return redirect('dashboard:accreditation')
        
        # Get documents for this checklist
        all_documents = get_all_documents('documents')
        documents = [
            doc for doc in all_documents 
            if doc.get('checklist_id') == checklist_id 
            and not doc.get('is_archived', False)
        ]
        
        # Separate required and additional documents
        required_document = next((doc for doc in documents if doc.get('is_required', False)), None)
        additional_documents = [doc for doc in documents if not doc.get('is_required', False)]
        
        # Sort additional documents by creation date
        additional_documents.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
    except Exception as e:
        print(f"Error fetching documents: {str(e)}")
        messages.error(request, 'Error fetching documents.')
        return redirect('dashboard:accreditation')
    
    context = {
        'active_page': 'accreditation',
        'user': user,
        'department': department,
        'program': program,
        'accreditation_type': accreditation_type,
        'area': area,
        'checklist': checklist,
        'required_document': required_document,
        'additional_documents': additional_documents,
        'dept_id': dept_id,
        'prog_id': prog_id,
        'type_id': type_id,
        'area_id': area_id,
        'checklist_id': checklist_id,
    }
    return render(request, 'dashboard/checklist_documents.html', context)


@login_required
@require_http_methods(["POST"])
def document_add_view(request, dept_id, prog_id, type_id, area_id, checklist_id):
    """Add documents to a checklist"""
    from accreditation.cloudinary_utils import upload_document_to_cloudinary
    import uuid
    
    user = get_user_from_session(request)
    
    try:
        # Get IDs from dropdown selections (they override URL parameters)
        selected_dept_id = request.POST.get('department_id', dept_id)
        selected_prog_id = request.POST.get('program_id', prog_id)
        selected_type_id = request.POST.get('accreditation_type_id', type_id)
        selected_area_id = request.POST.get('area_id', area_id)
        selected_checklist_id = request.POST.get('checklist_id', checklist_id)
        
        # Handle multiple required documents
        required_files = request.FILES.getlist('required_documents[]')
        required_names = request.POST.getlist('required_document_names[]')
        
        if not required_files or len(required_files) == 0:
            return JsonResponse({
                'success': False,
                'message': 'At least one required document is required'
            }, status=400)
        
        if len(required_names) != len(required_files):
            return JsonResponse({
                'success': False,
                'message': 'Document names and files count mismatch'
            }, status=400)
        
        # Validate and upload required documents
        allowed_formats = ['doc', 'docx']
        uploaded_count = 0
        
        for idx, required_file in enumerate(required_files):
            required_doc_name = required_names[idx].strip() if idx < len(required_names) else ''
            
            if not required_doc_name:
                return JsonResponse({
                    'success': False,
                    'message': f'Document name is required for file: {required_file.name}'
                }, status=400)
            
            if not required_file.name:
                continue
            
            # Validate required document format
            file_ext = required_file.name.split('.')[-1].lower()
            
            if file_ext not in allowed_formats:
                return JsonResponse({
                    'success': False,
                    'message': f'Invalid file format for {required_file.name}. Allowed formats: {", ".join(allowed_formats)}'
                }, status=400)
            
            # ============================================
            # VALIDATE DOCUMENT HEADER AGAINST TEMPLATE
            # ============================================
            if file_ext in ['doc', 'docx']:
                is_valid, error_message = validate_document_header(required_file)
                if not is_valid:
                    return JsonResponse({
                        'success': False,
                        'message': f'Header validation failed for {required_file.name}: {error_message}'
                    }, status=400)
                
                # Reset file pointer after validation
                required_file.seek(0)
            
            # Upload required document
            file_url = upload_document_to_cloudinary(
                required_file, 
                folder=f'documents/{selected_dept_id}/{selected_prog_id}/{selected_type_id}/{selected_area_id}/{selected_checklist_id}'
            )
            
            if not file_url:
                return JsonResponse({
                    'success': False,
                    'message': f'Failed to upload document: {required_file.name}'
                }, status=500)
            
            # Create required document record
            from datetime import datetime
            required_doc_data = {
                'department_id': selected_dept_id,
                'program_id': selected_prog_id,
                'accreditation_type_id': selected_type_id,
                'area_id': selected_area_id,
                'checklist_id': selected_checklist_id,
                'name': required_doc_name,
                'file_url': file_url,
                'format': file_ext,
                'uploaded_by': user.get('email', 'Unknown'),
                'uploaded_at': datetime.now().isoformat(),
                'is_required': True,
                'status': 'submitted',
                'comment': '',  # Comment will be added by disapprover later
                'is_active': True,
                'is_archived': False,
            }
            
            doc_id = str(uuid.uuid4())
            create_document('documents', required_doc_data, doc_id)
            uploaded_count += 1
        
        # Handle additional documents with individual names
        additional_files = request.FILES.getlist('additional_documents[]')
        additional_names = request.POST.getlist('additional_document_names[]')
        additional_allowed_formats = ['doc', 'docx', 'pdf', 'ppt', 'pptx', 'xls', 'xlsx', 
                                     'jpg', 'jpeg', 'png', 'gif']
        
        for idx, additional_file in enumerate(additional_files):
            if not additional_file.name:
                continue
            
            add_file_ext = additional_file.name.split('.')[-1].lower()
            
            if add_file_ext not in additional_allowed_formats:
                continue
            
            # Get the name for this additional document
            add_doc_name = additional_names[idx].strip() if idx < len(additional_names) and additional_names[idx].strip() else additional_file.name
            
            # Upload additional document
            add_file_url = upload_document_to_cloudinary(
                additional_file,
                folder=f'documents/{selected_dept_id}/{selected_prog_id}/{selected_type_id}/{selected_area_id}/{selected_checklist_id}/additional'
            )
            
            if add_file_url:
                # Create additional document record
                additional_doc_data = {
                    'department_id': selected_dept_id,
                    'program_id': selected_prog_id,
                    'accreditation_type_id': selected_type_id,
                    'area_id': selected_area_id,
                    'checklist_id': selected_checklist_id,
                    'name': add_doc_name,
                    'file_url': add_file_url,
                    'format': add_file_ext,
                    'uploaded_by': user.get('email', 'Unknown'),
                    'uploaded_at': datetime.now().isoformat(),
                    'is_required': False,
                    'status': 'submitted',
                    'comment': '',  # Comment will be added by disapprover later
                    'is_active': True,
                    'is_archived': False,
                }
                
                add_doc_id = str(uuid.uuid4())
                create_document('documents', additional_doc_data, add_doc_id)
        
        total_docs = uploaded_count + len([f for f in additional_files if f.name])
        return JsonResponse({
            'success': True,
            'message': f'{total_docs} document(s) uploaded successfully'
        })
        
    except Exception as e:
        print(f"Error adding documents: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error uploading documents: {str(e)}'
        }, status=500)


@login_required
def document_view(request, dept_id, prog_id, type_id, area_id, checklist_id, document_id):
    """Get document details for viewing"""
    try:
        document = get_document('documents', document_id)
        
        if not document:
            return JsonResponse({
                'success': False,
                'message': 'Document not found'
            }, status=404)
        
        return JsonResponse({
            'success': True,
            'document': document
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching document: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def document_update_status_view(request, dept_id, prog_id, type_id, area_id, checklist_id, document_id):
    """Update document status (approve/disapprove)"""
    user = get_user_from_session(request)
    
    # Only QA Head and QA Admin can update status
    if user.get('role') not in ['qa_head', 'qa_admin']:
        return JsonResponse({
            'success': False,
            'message': 'Unauthorized'
        }, status=403)
    
    try:
        import json as json_module
        data = json_module.loads(request.body)
        status = data.get('status')
        comment = data.get('comment', '').strip()
        
        if status not in ['approved', 'disapproved']:
            return JsonResponse({
                'success': False,
                'message': 'Invalid status'
            }, status=400)
        
        # Validate comment for disapproval
        if status == 'disapproved' and not comment:
            return JsonResponse({
                'success': False,
                'message': 'Comment is required for disapproval'
            }, status=400)
        
        document = get_document('documents', document_id)
        
        if not document:
            return JsonResponse({
                'success': False,
                'message': 'Document not found'
            }, status=404)
        
        # Update document status
        update_data = {
            'status': status,
            'approved_by': user.get('email', 'Unknown')
        }
        
        # Add comment if provided
        if comment:
            update_data['comment'] = comment
        
        update_document('documents', document_id, update_data)
        
        return JsonResponse({
            'success': True,
            'message': f'Document {status} successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating status: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def document_delete_view(request, dept_id, prog_id, type_id, area_id, checklist_id, document_id):
    """Delete a document"""
    from accreditation.cloudinary_utils import delete_document_from_cloudinary
    
    try:
        document = get_document('documents', document_id)
        
        if not document:
            return JsonResponse({
                'success': False,
                'message': 'Document not found'
            }, status=404)
        
        # Delete file from Cloudinary
        file_url = document.get('file_url', '')
        if file_url:
            delete_document_from_cloudinary(file_url)
        
        # Delete document record
        delete_document('documents', document_id)
        
        return JsonResponse({
            'success': True,
            'message': 'Document deleted successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error deleting document: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def document_proxy_view(request, dept_id, prog_id, type_id, area_id, checklist_id, document_id):
    """Proxy view to serve documents from Cloudinary"""
    import requests
    from django.http import HttpResponse, StreamingHttpResponse
    import cloudinary
    import cloudinary.api
    import cloudinary.uploader
    import os
    
    try:
        # Get document details
        document = get_document('documents', document_id)
        
        if not document:
            return HttpResponse('Document not found', status=404)
        
        file_url = document.get('file_url')
        if not file_url:
            return HttpResponse('Document file URL not found', status=404)
        
        # Configure Cloudinary
        api_key = os.environ.get('CLOUDINARY_API_KEY', '')
        api_secret = os.environ.get('CLOUDINARY_API_SECRET', '')
        
        cloudinary.config(
            cloud_name='dygrh6ztt',
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )
        
        from accreditation.cloudinary_utils import extract_public_id_from_url
        public_id = extract_public_id_from_url(file_url)
        
        if not public_id:
            return HttpResponse('Invalid Cloudinary URL', status=400)
        
        # Use Cloudinary Admin API to get the file directly
        try:
            # Use Cloudinary's API to generate a temporary download URL
            import hashlib
            import time
            
            timestamp = int(time.time())
            
            # Create signature for authenticated access
            to_sign = f"public_id={public_id}&timestamp={timestamp}{api_secret}"
            signature = hashlib.sha1(to_sign.encode('utf-8')).hexdigest()
            
            # Build authenticated download URL
            auth_url = f"https://api.cloudinary.com/v1_1/dygrh6ztt/raw/download?public_id={public_id}&timestamp={timestamp}&signature={signature}&api_key={api_key}"
            
            print(f"Trying authenticated download URL...")
            response = requests.get(auth_url, stream=True, timeout=30)
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                # Success! Stream the file
                format_lower = (document.get('format') or '').lower()
                
                content_type_map = {
                    'pdf': 'application/pdf',
                    'doc': 'application/msword',
                    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'xls': 'application/vnd.ms-excel',
                    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    'ppt': 'application/vnd.ms-powerpoint',
                    'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                }
                
                content_type = content_type_map.get(format_lower, 'application/pdf')
                
                django_response = StreamingHttpResponse(
                    response.iter_content(chunk_size=8192),
                    content_type=content_type
                )
                django_response['Content-Disposition'] = f'inline; filename="{document.get("name", "document.pdf")}"'
                django_response['Cache-Control'] = 'no-cache'
                
                return django_response
            
        except Exception as e:
            print(f"Authenticated download failed: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # If everything fails, return error message
        return HttpResponse(
            '<html><body style="font-family: Arial; padding: 40px; text-align: center;">'
            '<h2>Unable to load PDF</h2>'
            '<p>Please check your Cloudinary settings or contact support.</p>'
            '</body></html>',
            content_type='text/html'
        )
        
    except Exception as e:
        print(f"Error in proxy view: {str(e)}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f'Error: {str(e)}', status=500)
        return HttpResponse(f'Error loading document: {str(e)}', status=500)


# API endpoints for document modal dropdowns
@login_required
@require_http_methods(["GET"])
def api_get_departments(request):
    """Get all departments for modal dropdown"""
    try:
        departments = get_all_documents('departments')
        active_departments = [
            {'id': dept['id'], 'name': dept.get('name', 'Unknown')}
            for dept in departments 
            if dept.get('is_active', True) and not dept.get('is_archived', False)
        ]
        return JsonResponse({'departments': active_departments})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def api_get_department_programs(request, dept_id):
    """Get programs for a specific department"""
    try:
        # Query by department_id
        programs = query_documents('programs', 'department_id', '==', dept_id)
        
        # Filter for active and non-archived
        filtered_programs = [
            prog for prog in programs
            if prog.get('is_active', True) and not prog.get('is_archived', False)
        ]
        
        program_list = [
            {
                'id': prog['id'], 
                'name': prog.get('name', 'Unknown'),
                'code': prog.get('code', '')
            }
            for prog in filtered_programs
        ]
        return JsonResponse({'programs': program_list})
    except Exception as e:
        print(f"Error in api_get_department_programs: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e), 'programs': []}, status=500)


@login_required
@require_http_methods(["GET"])
def api_get_program_types(request, prog_id):
    """Get accreditation types for a specific program"""
    try:
        # Query by program_id
        types = query_documents('accreditation_types', 'program_id', '==', prog_id)
        
        # Filter for active and non-archived
        filtered_types = [
            t for t in types
            if t.get('is_active', True) and not t.get('is_archived', False)
        ]
        
        type_list = [
            {'id': t['id'], 'name': t.get('name', 'Unknown')}
            for t in filtered_types
        ]
        return JsonResponse({'types': type_list})
    except Exception as e:
        print(f"Error in api_get_program_types: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e), 'types': []}, status=500)


@login_required
@require_http_methods(["GET"])
def api_get_type_areas(request, type_id):
    """Get areas for a specific accreditation type"""
    try:
        # Query by accreditation_type_id
        areas = query_documents('areas', 'accreditation_type_id', '==', type_id)
        
        # Filter for active and non-archived
        filtered_areas = [
            area for area in areas
            if area.get('is_active', True) and not area.get('is_archived', False)
        ]
        
        area_list = [
            {'id': area['id'], 'name': area.get('name', 'Unknown')}
            for area in filtered_areas
        ]
        return JsonResponse({'areas': area_list})
    except Exception as e:
        print(f"Error in api_get_type_areas: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e), 'areas': []}, status=500)


@login_required
@require_http_methods(["GET"])
def api_get_area_checklists(request, area_id):
    """Get checklists for a specific area"""
    try:
        # Query by area_id
        checklists = query_documents('checklists', 'area_id', '==', area_id)
        
        # Filter for active and non-archived
        filtered_checklists = [
            cl for cl in checklists
            if cl.get('is_active', True) and not cl.get('is_archived', False)
        ]
        
        checklist_list = [
            {'id': cl['id'], 'name': cl.get('name', 'Unknown')}
            for cl in filtered_checklists
        ]
        return JsonResponse({'checklists': checklist_list})
    except Exception as e:
        print(f"Error in api_get_area_checklists: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e), 'checklists': []}, status=500)


@login_required
@require_http_methods(["GET"])
def download_template_view(request):
    """Download the official document template"""
    import os
    from django.http import FileResponse, Http404
    from django.conf import settings
    
    try:
        # Path to the template file
        template_path = os.path.join(settings.BASE_DIR, 'Template.docx')
        
        if not os.path.exists(template_path):
            raise Http404("Template file not found")
        
        # Open and return the file
        response = FileResponse(
            open(template_path, 'rb'),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = 'attachment; filename="Template.docx"'
        
        return response
        
    except Exception as e:
        print(f"Error downloading template: {str(e)}")
        raise Http404("Error downloading template file")
