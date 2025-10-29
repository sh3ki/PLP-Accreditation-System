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
]