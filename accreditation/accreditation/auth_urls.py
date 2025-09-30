"""
URL patterns for authentication views
"""

from django.urls import path
from accreditation import auth_views

app_name = 'auth'

urlpatterns = [
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('check-auth/', auth_views.check_auth_status, name='check_auth'),
]