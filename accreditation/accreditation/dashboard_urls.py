"""
URL patterns for dashboard views
Unified dashboard with multiple sections
"""

from django.urls import path
from accreditation import dashboard_views

app_name = 'dashboard'

urlpatterns = [
    # Main dashboard sections
    path('', dashboard_views.dashboard_home, name='home'),
    path('calendar/', dashboard_views.calendar_view, name='calendar'),
    path('accreditation/', dashboard_views.accreditation_view, name='accreditation'),
    path('performance/', dashboard_views.performance_view, name='performance'),
    path('reports/', dashboard_views.reports_view, name='reports'),
    path('results/', dashboard_views.results_view, name='results'),
    path('audit/', dashboard_views.audit_view, name='audit'),
    path('archive/', dashboard_views.archive_view, name='archive'),
    
    # Settings and sub-settings
    path('settings/', dashboard_views.settings_view, name='settings'),
    path('settings/user-management/', dashboard_views.user_management_view, name='user_management'),
    path('settings/user-management/add/', dashboard_views.user_add_view, name='user_add'),
    path('settings/user-management/edit/<str:user_id>/', dashboard_views.user_edit_view, name='user_edit'),
    path('settings/user-management/delete/<str:user_id>/', dashboard_views.user_delete_view, name='user_delete'),
    path('settings/user-management/toggle-status/<str:user_id>/', dashboard_views.user_toggle_status_view, name='user_toggle_status'),
    path('settings/user-management/get/<str:user_id>/', dashboard_views.user_get_view, name='user_get'),
    path('settings/accreditation/', dashboard_views.accreditation_settings_view, name='accreditation_settings'),
    path('settings/departments/add/', dashboard_views.department_add_view, name='department_add'),
    path('settings/departments/edit/<str:dept_id>/', dashboard_views.department_edit_view, name='department_edit'),
    path('settings/departments/archive/<str:dept_id>/', dashboard_views.department_archive_view, name='department_archive'),
    path('settings/departments/toggle-active/<str:dept_id>/', dashboard_views.department_toggle_active_view, name='department_toggle_active'),
    path('settings/departments/delete/<str:dept_id>/', dashboard_views.department_delete_view, name='department_delete'),
    path('settings/departments/get/<str:dept_id>/', dashboard_views.department_get_view, name='department_get'),
    path('settings/appearance/', dashboard_views.system_appearance_view, name='system_appearance'),
    path('settings/departments/', dashboard_views.department_settings_view, name='department_settings'),
    path('change-password/', dashboard_views.change_password_view, name='change_password'),
    
    # Legacy URLs for backward compatibility
    path('qa-head/', dashboard_views.qa_head_dashboard, name='qa_head_dashboard'),
    path('qa-admin/', dashboard_views.qa_admin_dashboard, name='qa_admin_dashboard'),
    path('department/', dashboard_views.department_dashboard, name='department_dashboard'),
]