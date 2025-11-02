"""
URL patterns for authentication views
"""

from django.urls import path
from accreditation import auth_views

app_name = 'auth'

urlpatterns = [
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('verify-otp/', auth_views.verify_otp_view, name='verify_otp'),
    path('verify-otp/submit/', auth_views.verify_otp_submit, name='verify_otp_submit'),
    path('verify-otp/resend/', auth_views.resend_otp_view, name='resend_otp'),
    path('check-auth/', auth_views.check_auth_status, name='check_auth'),
    
    # Forgot Password Flow
    path('forgot-password/', auth_views.forgot_password_view, name='forgot_password'),
    path('forgot-password/send-otp/', auth_views.forgot_password_send_otp, name='forgot_password_send_otp'),
    path('forgot-password/verify-otp/', auth_views.forgot_password_verify_otp, name='forgot_password_verify_otp'),
    path('forgot-password/resend-otp/', auth_views.forgot_password_resend_otp, name='forgot_password_resend_otp'),
    path('forgot-password/reset/', auth_views.reset_password_view, name='reset_password'),
    path('forgot-password/reset-submit/', auth_views.reset_password_submit, name='reset_password_submit'),
]