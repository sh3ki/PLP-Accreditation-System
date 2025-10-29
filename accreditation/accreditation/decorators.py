"""
Role-based access control decorators and utilities
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from accreditation.firebase_auth import UserRole, AnonymousUser


def login_required(view_func):
    """Decorator to require login"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = getattr(request, 'user', AnonymousUser())
        if not user.is_authenticated:
            messages.warning(request, 'Please log in to access this page.')
            return redirect('auth:login')
        return view_func(request, *args, **kwargs)
    return wrapper


def role_required(*allowed_roles):
    """Decorator to require specific roles"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = getattr(request, 'user', AnonymousUser())
            
            if not user.is_authenticated:
                messages.warning(request, 'Please log in to access this page.')
                return redirect('auth:login')
            
            if user.role not in allowed_roles:
                messages.error(request, 'Access denied. You do not have permission to access this page.')
                return redirect('dashboard:dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def qa_head_required(view_func):
    """Decorator to require QA Head role"""
    return role_required(UserRole.QA_HEAD)(view_func)


def qa_admin_required(view_func):
    """Decorator to require QA Admin role"""
    return role_required(UserRole.QA_ADMIN)(view_func)


def qa_staff_required(view_func):
    """Decorator to require QA Head or QA Admin role"""
    return role_required(UserRole.QA_HEAD, UserRole.QA_ADMIN)(view_func)


def department_user_required(view_func):
    """Decorator to require Department User role"""
    return role_required(UserRole.DEPARTMENT_USER)(view_func)


class RoleBasedAccessMixin:
    """Mixin for class-based views to add role-based access control"""
    
    allowed_roles = None
    login_required = True
    
    def dispatch(self, request, *args, **kwargs):
        user = getattr(request, 'user', AnonymousUser())
        
        if self.login_required and not user.is_authenticated:
            messages.warning(request, 'Please log in to access this page.')
            return redirect('auth:login')
        
        if self.allowed_roles and user.role not in self.allowed_roles:
            messages.error(request, 'Access denied. You do not have permission to access this page.')
            return redirect('dashboard:dashboard')
        
        return super().dispatch(request, *args, **kwargs)


class QAHeadMixin(RoleBasedAccessMixin):
    """Mixin for QA Head only views"""
    allowed_roles = [UserRole.QA_HEAD]


class QAAdminMixin(RoleBasedAccessMixin):
    """Mixin for QA Admin only views"""
    allowed_roles = [UserRole.QA_ADMIN]


class QAStaffMixin(RoleBasedAccessMixin):
    """Mixin for QA Head and QA Admin views"""
    allowed_roles = [UserRole.QA_HEAD, UserRole.QA_ADMIN]


class DepartmentUserMixin(RoleBasedAccessMixin):
    """Mixin for Department User only views"""
    allowed_roles = [UserRole.DEPARTMENT_USER]