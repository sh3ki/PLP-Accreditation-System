"""
Authentication Views for PLP Accreditation System
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods
import json
from firebase_admin import firestore
from accreditation.forms import LoginForm
from accreditation.firebase_auth import FirebaseUser, AnonymousUser
from accreditation.decorators import login_required, qa_head_required, qa_admin_required
from accreditation.audit_utils import log_audit, get_client_ip
from accreditation.otp_utils import generate_otp, send_otp_email, store_otp, verify_otp, resend_otp
from accreditation.dashboard_views import get_qa_admin_dashboard_data


@never_cache
@csrf_protect
def login_view(request):
    """Login view with security features"""
    # Redirect if user is already authenticated
    if hasattr(request, 'user') and request.user.is_authenticated:
        # Redirect based on user role
        if request.user.role == 'department_user':
            return redirect('dashboard:dept_home')
        else:
            return redirect('dashboard:home')
    
    locked_until = None
    remaining_seconds = None
    is_deactivated = False
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_result = form.get_auth_result()
            
            if user and auth_result.get('success'):
                # Store additional user fields for profile
                from accreditation.firebase_utils import get_document
                user_doc = get_document('users', user.id, request=request)
                
                # Ensure user_doc is a dict, not a list
                if isinstance(user_doc, list) and len(user_doc) > 0:
                    user_doc = user_doc[0]
                elif not isinstance(user_doc, dict):
                    user_doc = {}
                
                # Check if this is first login (password not changed)
                if not user.is_password_changed:
                    # MANDATORY OTP VERIFICATION FOR FIRST LOGIN
                    # Generate and send OTP
                    otp = generate_otp(6)
                    
                    if send_otp_email(user.email, user.full_name, otp):
                        if store_otp(user.id, otp):
                            # Store minimal session data for OTP verification
                            request.session['pending_otp_user_id'] = user.id
                            request.session['pending_otp_email'] = user.email
                            request.session['pending_otp_name'] = user.full_name
                            request.session['pending_otp_role'] = user.role
                            request.session['requires_otp'] = True
                            request.session['requires_password_change'] = True
                            
                            messages.success(request, f'OTP sent to {user.email}. Please check your email.')
                            return redirect('auth:verify_otp')
                        else:
                            messages.error(request, 'Failed to generate OTP. Please try again.')
                    else:
                        messages.error(request, 'Failed to send OTP email. Please contact administrator.')
                else:
                    # Normal login for users who have changed password
                    request.session['user_id'] = user.id
                    request.session['user_email'] = user.email
                    request.session['user_role'] = user.role
                    request.session['user_name'] = user.full_name
                    request.session['is_password_changed'] = user.is_password_changed
                    
                    if user_doc:
                        request.session['user'] = {
                            'id': user.id,
                            'email': user.email,
                            'role': user.role,
                            'name': user.full_name,
                            'first_name': user_doc.get('first_name', ''),
                            'middle_name': user_doc.get('middle_name', ''),
                            'last_name': user_doc.get('last_name', ''),
                            'profile_image_url': user_doc.get('profile_image_url', ''),
                            'department': user_doc.get('department', ''),
                            'department_id': user_doc.get('department', ''),
                        }
                    
                    # Set session expiry based on remember_me
                    if form.cleaned_data.get('remember_me'):
                        request.session.set_expiry(1209600)  # 2 weeks
                    else:
                        request.session.set_expiry(86400)    # 1 day
                    
                    messages.success(request, f'Welcome back, {user.full_name}!')
                    
                    # Log audit event for successful login
                    try:
                        ip = get_client_ip(request)
                        user_name = user_doc.get('name') or f"{user_doc.get('first_name', '')} {user_doc.get('last_name', '')}".strip()
                        log_audit(user_doc, action_type='login', resource_type='session', resource_id=None, details=f"Logged in successfully as {user_name}", status='success', ip=ip)
                    except Exception:
                        pass
                    
                    # Redirect based on user role
                    if user.role == 'department_user':
                        return redirect('dashboard:dept_home')
                    else:
                        return redirect('dashboard:home')
        else:
            # Form has errors - check if it's a lockout or deactivation
            if hasattr(form, 'locked_until'):
                locked_until = form.locked_until
                remaining_seconds = form.remaining_seconds
            if hasattr(form, 'is_deactivated'):
                is_deactivated = form.is_deactivated
    else:
        form = LoginForm()
    
    context = {
        'form': form,
        'title': 'PLP Accreditation System - Login',
        'locked_until': locked_until,
        'remaining_seconds': remaining_seconds,
        'is_deactivated': is_deactivated,
    }
    
    return render(request, 'auth/login.html', context)


@never_cache
def logout_view(request):
    """Logout view"""
    # Log audit event before clearing session
    try:
        user_id = request.session.get('user_id')
        user_email = request.session.get('user_email')
        if user_id and user_email:
            user = {'id': user_id, 'email': user_email, 'name': request.session.get('user_name')}
            ip = get_client_ip(request)
            user_name = user.get('name') or 'User'
            log_audit(user, action_type='logout', resource_type='session', resource_id=None, details=f"Logged out successfully - {user_name}", status='success', ip=ip)
    except Exception:
        pass
    
    # Clear session data
    request.session.flush()
    messages.info(request, 'You have been logged out successfully.')
    return redirect('auth:login')


@login_required
def dashboard_view(request):
    """Main dashboard view - redirects based on user role"""
    user = get_user_from_session(request)
    
    if user.is_qa_head:
        return redirect('dashboard:qa_head_dashboard')
    elif user.is_qa_admin:
        return redirect('dashboard:qa_admin_dashboard')
    else:
        return redirect('dashboard:department_dashboard')


@qa_head_required
def qa_head_dashboard(request):
    """QA Dashboard (shared with QA Admin)"""
    user = get_user_from_session(request)
    
    # Get dashboard data
    dashboard_data = get_qa_admin_dashboard_data(user)
    
    context = {
        'user': user,
        'title': 'QA Dashboard',
        'role': 'QA Head',
    }
    
    # Merge dashboard data into context
    context.update(dashboard_data)
    
    return render(request, 'dashboards/qa_dashboard.html', context)


@qa_admin_required
def qa_admin_dashboard(request):
    """QA Dashboard (shared with QA Head)"""
    user = get_user_from_session(request)
    
    # Get dashboard data
    dashboard_data = get_qa_admin_dashboard_data(user)
    
    context = {
        'user': user,
        'title': 'QA Dashboard',
        'role': 'QA Admin',
    }
    
    # Merge dashboard data into context
    context.update(dashboard_data)
    
    return render(request, 'dashboards/qa_dashboard.html', context)


@login_required
def department_dashboard(request):
    """Department User dashboard"""
    user = get_user_from_session(request)
    
    context = {
        'user': user,
        'title': 'Department Dashboard',
        'role': 'Department User',
    }
    
    return render(request, 'dashboards/department_dashboard.html', context)


def get_user_from_session(request):
    """Get user object from session data"""
    user_id = request.session.get('user_id')
    if user_id:
        user = FirebaseUser.get_by_id(user_id)
        if user and user.is_active:
            return user
    
    # Return anonymous user if no valid session
    return AnonymousUser()


@never_cache
def verify_otp_view(request):
    """OTP Verification View - MANDATORY for first login"""
    # Check if OTP verification is required
    if not request.session.get('requires_otp'):
        return redirect('auth:login')
    
    user_email = request.session.get('pending_otp_email')
    user_name = request.session.get('pending_otp_name')
    
    context = {
        'user_email': user_email,
        'user_name': user_name,
        'title': 'OTP Verification - PLP Accreditation System'
    }
    
    return render(request, 'auth/verify_otp.html', context)


@require_http_methods(["POST"])
def verify_otp_submit(request):
    """Handle OTP verification submission"""
    # Check if OTP verification is required
    if not request.session.get('requires_otp'):
        return JsonResponse({'success': False, 'message': 'Invalid session'}, status=400)
    
    try:
        data = json.loads(request.body)
        entered_otp = data.get('otp', '').strip()
        
        if not entered_otp:
            return JsonResponse({'success': False, 'message': 'Please enter OTP'})
        
        user_id = request.session.get('pending_otp_user_id')
        
        # Verify OTP
        result = verify_otp(user_id, entered_otp)
        
        if result['success']:
            # OTP verified successfully
            # Get user document
            from accreditation.firebase_utils import get_document
            user_doc = get_document('users', user_id, request=request)
            
            # Complete login session
            request.session['user_id'] = user_id
            request.session['user_email'] = request.session.get('pending_otp_email')
            request.session['user_role'] = request.session.get('pending_otp_role')
            request.session['user_name'] = request.session.get('pending_otp_name')
            request.session['is_password_changed'] = False  # Still need to change password
            request.session['otp_verified'] = True  # Mark OTP as verified
            
            if user_doc:
                request.session['user'] = {
                    'id': user_id,
                    'email': user_doc.get('email'),
                    'role': user_doc.get('role'),
                    'name': user_doc.get('name') or f"{user_doc.get('first_name', '')} {user_doc.get('last_name', '')}".strip(),
                    'first_name': user_doc.get('first_name', ''),
                    'middle_name': user_doc.get('middle_name', ''),
                    'last_name': user_doc.get('last_name', ''),
                    'profile_image_url': user_doc.get('profile_image_url', ''),
                    'department': user_doc.get('department', ''),
                    'department_id': user_doc.get('department', ''),
                }
            
            # Clear pending OTP session data
            request.session.pop('pending_otp_user_id', None)
            request.session.pop('pending_otp_email', None)
            request.session.pop('pending_otp_name', None)
            request.session.pop('pending_otp_role', None)
            request.session.pop('requires_otp', None)
            
            # Log successful OTP verification
            try:
                ip = get_client_ip(request)
                log_audit(user_doc, action_type='otp_verification', resource_type='session', resource_id=None, details=f"OTP verified successfully for first login", status='success', ip=ip)
            except Exception:
                pass
            
            # Redirect based on user role
            user_role = request.session.get('user_role')
            if user_role == 'department_user':
                redirect_url = '/dashboard/dept-home/'
            else:
                redirect_url = '/dashboard/'
            
            return JsonResponse({
                'success': True, 
                'message': 'OTP verified successfully',
                'redirect': redirect_url
            })
        else:
            return JsonResponse(result)
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid request format'})
    except Exception as e:
        print(f"Error in OTP verification: {e}")
        return JsonResponse({'success': False, 'message': 'Verification error. Please try again.'})


@require_http_methods(["POST"])
def resend_otp_view(request):
    """Resend OTP to user's email"""
    # Check if OTP verification is required
    if not request.session.get('requires_otp'):
        return JsonResponse({'success': False, 'message': 'Invalid session'}, status=400)
    
    user_id = request.session.get('pending_otp_user_id')
    user_email = request.session.get('pending_otp_email')
    user_name = request.session.get('pending_otp_name')
    
    if not all([user_id, user_email, user_name]):
        return JsonResponse({'success': False, 'message': 'Session expired. Please login again.'})
    
    result = resend_otp(user_id, user_email, user_name)
    return JsonResponse(result)


# AJAX views for API integration
def check_auth_status(request):
    """Check authentication status via AJAX"""
    user = get_user_from_session(request)
    
    return JsonResponse({
        'authenticated': user.is_authenticated,
        'user_id': user.id if user.is_authenticated else None,
        'email': user.email if user.is_authenticated else None,
        'role': user.role if user.is_authenticated else None,
        'full_name': user.full_name if user.is_authenticated else None,
    })


# Middleware to add user to request
class FirebaseAuthMiddleware:
    """Middleware to add Firebase user to request"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Add user to request
        request.user = get_user_from_session(request)
        
        response = self.get_response(request)
        return response


# ================== FORGOT PASSWORD FLOW ==================

@never_cache
def forgot_password_view(request):
    """Display forgot password form"""
    return render(request, 'auth/forgot_password.html', {
        'title': 'Forgot Password'
    })


@require_http_methods(["POST"])
def forgot_password_send_otp(request):
    """Send OTP for password reset"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        
        if not email:
            return JsonResponse({'success': False, 'message': 'Email is required'})
        
        # Check if user exists in Firestore
        from accreditation.firebase_utils import query_documents
        users = query_documents('users', [('email', '==', email)])
        
        if not users:
            return JsonResponse({'success': False, 'message': 'No account found with this email address'})
        
        user = users[0]
        user_id = user.get('id')
        user_name = user.get('name') or f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
        
        # Generate and send OTP
        otp = generate_otp(6)
        
        if send_otp_email(email, user_name, otp, purpose='password_reset'):
            if store_otp(user_id, otp, purpose='password_reset'):
                # Store session data for verification
                request.session['forgot_password_user_id'] = user_id
                request.session['forgot_password_email'] = email
                request.session['forgot_password_name'] = user_name
                request.session['forgot_password_otp_sent'] = True
                
                return JsonResponse({
                    'success': True,
                    'message': 'Verification code sent to your email',
                    'redirect': '/auth/forgot-password/verify-otp/'
                })
            else:
                return JsonResponse({'success': False, 'message': 'Failed to generate OTP. Please try again.'})
        else:
            return JsonResponse({'success': False, 'message': 'Failed to send email. Please try again.'})
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid request format'})
    except Exception as e:
        print(f"Error in forgot password OTP: {e}")
        return JsonResponse({'success': False, 'message': 'An error occurred. Please try again.'})


@never_cache
def forgot_password_verify_otp(request):
    """Display OTP verification page for password reset"""
    if not request.session.get('forgot_password_otp_sent'):
        return redirect('auth:forgot_password')
    
    return render(request, 'auth/forgot_password_verify_otp.html', {
        'title': 'Verify OTP',
        'user_email': request.session.get('forgot_password_email', '')
    })


@require_http_methods(["POST"])
def forgot_password_verify_otp(request):
    """Verify OTP for password reset"""
    try:
        data = json.loads(request.body)
        otp = data.get('otp', '').strip()
        
        if not otp:
            return JsonResponse({'success': False, 'message': 'OTP is required'})
        
        if not request.session.get('forgot_password_otp_sent'):
            return JsonResponse({'success': False, 'message': 'Invalid session. Please start over.'})
        
        user_id = request.session.get('forgot_password_user_id')
        
        if not user_id:
            return JsonResponse({'success': False, 'message': 'Session expired. Please start over.'})
        
        # Verify OTP
        result = verify_otp(user_id, otp, purpose='password_reset')
        
        if result.get('success'):
            # Mark OTP as verified
            request.session['forgot_password_otp_verified'] = True
            
            return JsonResponse({
                'success': True,
                'message': 'OTP verified successfully',
                'redirect': '/auth/forgot-password/reset/'
            })
        else:
            return JsonResponse(result)
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid request format'})
    except Exception as e:
        print(f"Error verifying OTP: {e}")
        return JsonResponse({'success': False, 'message': 'Verification error. Please try again.'})


@require_http_methods(["POST"])
def forgot_password_resend_otp(request):
    """Resend OTP for password reset"""
    if not request.session.get('forgot_password_otp_sent'):
        return JsonResponse({'success': False, 'message': 'Invalid session'}, status=400)
    
    user_id = request.session.get('forgot_password_user_id')
    user_email = request.session.get('forgot_password_email')
    user_name = request.session.get('forgot_password_name')
    
    if not all([user_id, user_email, user_name]):
        return JsonResponse({'success': False, 'message': 'Session expired. Please start over.'})
    
    result = resend_otp(user_id, user_email, user_name, purpose='password_reset')
    return JsonResponse(result)


@never_cache
def reset_password_view(request):
    """Display reset password form"""
    if not request.session.get('forgot_password_otp_verified'):
        return redirect('auth:forgot_password')
    
    return render(request, 'auth/reset_password.html', {
        'title': 'Reset Password'
    })


@require_http_methods(["POST"])
def reset_password_submit(request):
    """Submit new password"""
    try:
        data = json.loads(request.body)
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')
        
        if not all([new_password, confirm_password]):
            return JsonResponse({'success': False, 'message': 'All fields are required'})
        
        if new_password != confirm_password:
            return JsonResponse({'success': False, 'message': 'Passwords do not match'})
        
        # Validate password strength
        if len(new_password) < 8:
            return JsonResponse({'success': False, 'message': 'Password must be at least 8 characters'})
        
        if not any(c.isupper() for c in new_password):
            return JsonResponse({'success': False, 'message': 'Password must contain at least one uppercase letter'})
        
        if not any(c.islower() for c in new_password):
            return JsonResponse({'success': False, 'message': 'Password must contain at least one lowercase letter'})
        
        if not any(c.isdigit() for c in new_password):
            return JsonResponse({'success': False, 'message': 'Password must contain at least one number'})
        
        if not request.session.get('forgot_password_otp_verified'):
            return JsonResponse({'success': False, 'message': 'Invalid session. Please start over.'})
        
        user_id = request.session.get('forgot_password_user_id')
        
        if not user_id:
            return JsonResponse({'success': False, 'message': 'Session expired. Please start over.'})
        
        # Update password in Firestore
        from accreditation.firebase_utils import update_document
        from django.contrib.auth.hashers import make_password
        
        hashed_password = make_password(new_password)
        
        update_data = {
            'password': hashed_password,
            'is_password_changed': True,
            'updated_at': firestore.SERVER_TIMESTAMP
        }
        
        if update_document('users', user_id, update_data):
            # Clear forgot password session data
            request.session.pop('forgot_password_user_id', None)
            request.session.pop('forgot_password_email', None)
            request.session.pop('forgot_password_name', None)
            request.session.pop('forgot_password_otp_sent', None)
            request.session.pop('forgot_password_otp_verified', None)
            
            # Log audit event
            try:
                from accreditation.firebase_utils import get_document
                user_doc = get_document('users', user_id)
                if user_doc:
                    ip = get_client_ip(request)
                    log_audit(user_doc, action_type='password_reset', resource_type='user', 
                             resource_id=user_id, details='Password reset successfully via forgot password flow', 
                             status='success', ip=ip)
            except Exception:
                pass
            
            return JsonResponse({
                'success': True,
                'message': 'Password reset successfully. You can now login with your new password.',
                'redirect': '/auth/login/'
            })
        else:
            return JsonResponse({'success': False, 'message': 'Failed to update password. Please try again.'})
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid request format'})
    except Exception as e:
        print(f"Error resetting password: {e}")
        return JsonResponse({'success': False, 'message': 'An error occurred. Please try again.'})
