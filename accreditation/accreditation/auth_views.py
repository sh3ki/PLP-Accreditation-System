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
from accreditation.forms import LoginForm
from accreditation.firebase_auth import FirebaseUser, AnonymousUser
from accreditation.decorators import login_required, qa_head_required, qa_admin_required


@never_cache
@csrf_protect
def login_view(request):
    """Login view"""
    # Redirect if user is already authenticated
    if hasattr(request, 'user') and request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            if user:
                # Store user data in session
                request.session['user_id'] = user.id
                request.session['user_email'] = user.email
                request.session['user_role'] = user.role
                request.session['user_name'] = user.full_name
                request.session['is_password_changed'] = user.is_password_changed
                
                # Set session expiry based on remember_me
                if form.cleaned_data.get('remember_me'):
                    request.session.set_expiry(1209600)  # 2 weeks
                else:
                    request.session.set_expiry(86400)    # 1 day
                
                messages.success(request, f'Welcome back, {user.full_name}!')
                
                # Redirect to unified dashboard home
                return redirect('dashboard:home')
            else:
                messages.error(request, 'Authentication failed. Please try again.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LoginForm()
    
    context = {
        'form': form,
        'title': 'PLP Accreditation System - Login',
    }
    
    return render(request, 'auth/login.html', context)


@never_cache
def logout_view(request):
    """Logout view"""
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
    """QA Head dashboard"""
    user = get_user_from_session(request)
    
    context = {
        'user': user,
        'title': 'QA Head Dashboard',
        'role': 'QA Head',
    }
    
    return render(request, 'dashboards/qa_head_dashboard.html', context)


@qa_admin_required
def qa_admin_dashboard(request):
    """QA Admin dashboard"""
    user = get_user_from_session(request)
    
    context = {
        'user': user,
        'title': 'QA Admin Dashboard',
        'role': 'QA Admin',
    }
    
    return render(request, 'dashboards/qa_admin_dashboard.html', context)


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