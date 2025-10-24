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
    
    # Accreditation navigation (read-only views)
    path('accreditation/department/<str:dept_id>/programs/', dashboard_views.accreditation_department_programs_view, name='accreditation_department_programs'),
    path('accreditation/department/<str:dept_id>/programs/<str:prog_id>/types/', dashboard_views.accreditation_program_types_view, name='accreditation_program_types'),
    path('accreditation/department/<str:dept_id>/programs/<str:prog_id>/types/<str:type_id>/areas/', dashboard_views.accreditation_type_areas_view, name='accreditation_type_areas'),
    path('accreditation/department/<str:dept_id>/programs/<str:prog_id>/types/<str:type_id>/areas/<str:area_id>/checklists/', dashboard_views.accreditation_area_checklists_view, name='accreditation_area_checklists'),
    
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
    
    # Programs management (within departments)
    path('settings/departments/<str:dept_id>/programs/', dashboard_views.department_programs_view, name='department_programs'),
    path('settings/departments/<str:dept_id>/programs/add/', dashboard_views.program_add_view, name='program_add'),
    path('settings/departments/<str:dept_id>/programs/edit/<str:prog_id>/', dashboard_views.program_edit_view, name='program_edit'),
    path('settings/departments/<str:dept_id>/programs/archive/<str:prog_id>/', dashboard_views.program_archive_view, name='program_archive'),
    path('settings/departments/<str:dept_id>/programs/toggle-active/<str:prog_id>/', dashboard_views.program_toggle_active_view, name='program_toggle_active'),
    path('settings/departments/<str:dept_id>/programs/delete/<str:prog_id>/', dashboard_views.program_delete_view, name='program_delete'),
    path('settings/departments/<str:dept_id>/programs/get/<str:prog_id>/', dashboard_views.program_get_view, name='program_get'),
    
    # Accreditation Types management (within programs)
    path('settings/departments/<str:dept_id>/programs/<str:prog_id>/types/', dashboard_views.program_types_view, name='program_types'),
    path('settings/departments/<str:dept_id>/programs/<str:prog_id>/types/add/', dashboard_views.accreditation_type_add_view, name='accreditation_type_add'),
    path('settings/departments/<str:dept_id>/programs/<str:prog_id>/types/edit/<str:type_id>/', dashboard_views.accreditation_type_edit_view, name='accreditation_type_edit'),
    path('settings/departments/<str:dept_id>/programs/<str:prog_id>/types/archive/<str:type_id>/', dashboard_views.accreditation_type_archive_view, name='accreditation_type_archive'),
    path('settings/departments/<str:dept_id>/programs/<str:prog_id>/types/toggle-active/<str:type_id>/', dashboard_views.accreditation_type_toggle_active_view, name='accreditation_type_toggle_active'),
    path('settings/departments/<str:dept_id>/programs/<str:prog_id>/types/delete/<str:type_id>/', dashboard_views.accreditation_type_delete_view, name='accreditation_type_delete'),
    path('settings/departments/<str:dept_id>/programs/<str:prog_id>/types/get/<str:type_id>/', dashboard_views.accreditation_type_get_view, name='accreditation_type_get'),
    
    # Areas management (within accreditation types)
    path('settings/departments/<str:dept_id>/programs/<str:prog_id>/types/<str:type_id>/areas/', dashboard_views.type_areas_view, name='type_areas'),
    path('settings/departments/<str:dept_id>/programs/<str:prog_id>/types/<str:type_id>/areas/add/', dashboard_views.area_add_view, name='area_add'),
    path('settings/departments/<str:dept_id>/programs/<str:prog_id>/types/<str:type_id>/areas/edit/<str:area_id>/', dashboard_views.area_edit_view, name='area_edit'),
    path('settings/departments/<str:dept_id>/programs/<str:prog_id>/types/<str:type_id>/areas/archive/<str:area_id>/', dashboard_views.area_archive_view, name='area_archive'),
    path('settings/departments/<str:dept_id>/programs/<str:prog_id>/types/<str:type_id>/areas/toggle-active/<str:area_id>/', dashboard_views.area_toggle_active_view, name='area_toggle_active'),
    path('settings/departments/<str:dept_id>/programs/<str:prog_id>/types/<str:type_id>/areas/delete/<str:area_id>/', dashboard_views.area_delete_view, name='area_delete'),
    path('settings/departments/<str:dept_id>/programs/<str:prog_id>/types/<str:type_id>/areas/get/<str:area_id>/', dashboard_views.area_get_view, name='area_get'),
    
    # Checklists management (within areas)
    path('settings/departments/<str:dept_id>/programs/<str:prog_id>/types/<str:type_id>/areas/<str:area_id>/checklists/', dashboard_views.area_checklists_view, name='area_checklists'),
    path('settings/departments/<str:dept_id>/programs/<str:prog_id>/types/<str:type_id>/areas/<str:area_id>/checklists/add/', dashboard_views.checklist_add_view, name='checklist_add'),
    path('settings/departments/<str:dept_id>/programs/<str:prog_id>/types/<str:type_id>/areas/<str:area_id>/checklists/edit/<str:checklist_id>/', dashboard_views.checklist_edit_view, name='checklist_edit'),
    path('settings/departments/<str:dept_id>/programs/<str:prog_id>/types/<str:type_id>/areas/<str:area_id>/checklists/archive/<str:checklist_id>/', dashboard_views.checklist_archive_view, name='checklist_archive'),
    path('settings/departments/<str:dept_id>/programs/<str:prog_id>/types/<str:type_id>/areas/<str:area_id>/checklists/toggle-active/<str:checklist_id>/', dashboard_views.checklist_toggle_active_view, name='checklist_toggle_active'),
    path('settings/departments/<str:dept_id>/programs/<str:prog_id>/types/<str:type_id>/areas/<str:area_id>/checklists/delete/<str:checklist_id>/', dashboard_views.checklist_delete_view, name='checklist_delete'),
    path('settings/departments/<str:dept_id>/programs/<str:prog_id>/types/<str:type_id>/areas/<str:area_id>/checklists/get/<str:checklist_id>/', dashboard_views.checklist_get_view, name='checklist_get'),
    
    # Document management (within checklists)
    path('accreditation/department/<str:dept_id>/programs/<str:prog_id>/types/<str:type_id>/areas/<str:area_id>/checklists/<str:checklist_id>/documents/', dashboard_views.checklist_documents_view, name='checklist_documents'),
    path('accreditation/department/<str:dept_id>/programs/<str:prog_id>/types/<str:type_id>/areas/<str:area_id>/checklists/<str:checklist_id>/documents/add/', dashboard_views.document_add_view, name='document_add'),
    path('accreditation/department/<str:dept_id>/programs/<str:prog_id>/types/<str:type_id>/areas/<str:area_id>/checklists/<str:checklist_id>/documents/<str:document_id>/view/', dashboard_views.document_view, name='document_view'),
    path('accreditation/department/<str:dept_id>/programs/<str:prog_id>/types/<str:type_id>/areas/<str:area_id>/checklists/<str:checklist_id>/documents/<str:document_id>/update-status/', dashboard_views.document_update_status_view, name='document_update_status'),
    path('accreditation/department/<str:dept_id>/programs/<str:prog_id>/types/<str:type_id>/areas/<str:area_id>/checklists/<str:checklist_id>/documents/<str:document_id>/delete/', dashboard_views.document_delete_view, name='document_delete'),
    
    path('settings/appearance/', dashboard_views.system_appearance_view, name='system_appearance'),
    path('change-password/', dashboard_views.change_password_view, name='change_password'),
    
    # Archive API endpoints
    path('archive/api/departments/', dashboard_views.archive_api_departments, name='archive_api_departments'),
    path('archive/api/programs/', dashboard_views.archive_api_programs, name='archive_api_programs'),
    path('archive/api/types/', dashboard_views.archive_api_types, name='archive_api_types'),
    path('archive/api/areas/', dashboard_views.archive_api_areas, name='archive_api_areas'),
    path('archive/api/checklists/', dashboard_views.archive_api_checklists, name='archive_api_checklists'),
    path('archive/api/<str:item_type>/<str:item_id>/unarchive/', dashboard_views.archive_api_unarchive, name='archive_api_unarchive'),
    path('archive/api/<str:item_type>/<str:item_id>/delete/', dashboard_views.archive_api_delete, name='archive_api_delete'),
    
    # API endpoints for document modal dropdowns
    path('api/departments/', dashboard_views.api_get_departments, name='api_get_departments'),
    path('api/departments/<str:dept_id>/programs/', dashboard_views.api_get_department_programs, name='api_get_department_programs'),
    path('api/programs/<str:prog_id>/types/', dashboard_views.api_get_program_types, name='api_get_program_types'),
    path('api/types/<str:type_id>/areas/', dashboard_views.api_get_type_areas, name='api_get_type_areas'),
    path('api/areas/<str:area_id>/checklists/', dashboard_views.api_get_area_checklists, name='api_get_area_checklists'),
    
    # Legacy URLs for backward compatibility
    path('qa-head/', dashboard_views.qa_head_dashboard, name='qa_head_dashboard'),
    path('qa-admin/', dashboard_views.qa_admin_dashboard, name='qa_admin_dashboard'),
    path('department/', dashboard_views.department_dashboard, name='department_dashboard'),
]