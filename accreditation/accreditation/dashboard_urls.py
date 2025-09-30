"""
URL patterns for dashboard views
"""

from django.urls import path
from accreditation import auth_views

app_name = 'dashboard'

urlpatterns = [
    path('', auth_views.dashboard_view, name='dashboard'),
    path('qa-head/', auth_views.qa_head_dashboard, name='qa_head_dashboard'),
    path('qa-admin/', auth_views.qa_admin_dashboard, name='qa_admin_dashboard'),
    path('department/', auth_views.department_dashboard, name='department_dashboard'),
]