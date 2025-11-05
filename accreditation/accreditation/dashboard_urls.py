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
    
    # My Accreditation (user's personal accreditation view)
    path('my-accreditation/', dashboard_views.my_accreditation_view, name='my_accreditation'),
    path('my-accreditation/department/<str:dept_id>/programs/', dashboard_views.my_accreditation_department_programs_view, name='my_accreditation_department_programs'),
    path('my-accreditation/department/<str:dept_id>/programs/<str:prog_id>/types/', dashboard_views.my_accreditation_program_types_view, name='my_accreditation_program_types'),
    path('my-accreditation/department/<str:dept_id>/programs/<str:prog_id>/types/<str:type_id>/areas/', dashboard_views.my_accreditation_type_areas_view, name='my_accreditation_type_areas'),
    path('my-accreditation/department/<str:dept_id>/programs/<str:prog_id>/types/<str:type_id>/areas/<str:area_id>/checklists/', dashboard_views.my_accreditation_area_checklists_view, name='my_accreditation_area_checklists'),
    path('my-accreditation/department/<str:dept_id>/programs/<str:prog_id>/types/<str:type_id>/areas/<str:area_id>/checklists/<str:checklist_id>/documents/', dashboard_views.my_accreditation_checklist_documents_view, name='my_accreditation_checklist_documents'),
    path('my-accreditation/department/<str:dept_id>/programs/<str:prog_id>/types/<str:type_id>/areas/<str:area_id>/checklists/<str:checklist_id>/documents/<str:document_id>/view/', dashboard_views.my_accreditation_view_document, name='my_accreditation_view_document'),
    path('my-accreditation/department/<str:dept_id>/programs/<str:prog_id>/types/<str:type_id>/areas/<str:area_id>/checklists/<str:checklist_id>/documents/<str:document_id>/download/', dashboard_views.my_accreditation_download_document, name='my_accreditation_download_document'),
    
    path('performance/', dashboard_views.performance_view, name='performance'),
    path('reports/', dashboard_views.reports_view, name='reports'),
    path('reports/generate/', dashboard_views.generate_report, name='generate_report'),
    path('reports/delete/<str:report_id>/', dashboard_views.delete_report, name='delete_report'),
    path('results/', dashboard_views.results_view, name='results'),
    path('results/toggle-certificate/<str:area_id>/', dashboard_views.toggle_certificate_view, name='toggle_certificate'),
    path('audit/', dashboard_views.audit_trail_view, name='audit'),
    path('archive/', dashboard_views.archive_view, name='archive'),
    
    # Profile Settings and sub-settings
    path('profile-settings/', dashboard_views.settings_view, name='settings'),
    path('profile-settings/upload-image/', dashboard_views.upload_profile_image_view, name='upload_profile_image'),
    path('profile-settings/remove-image/', dashboard_views.remove_profile_image_view, name='remove_profile_image'),
    path('profile-settings/update-info/', dashboard_views.update_personal_info_view, name='update_personal_info'),
    path('profile-settings/change-password/', dashboard_views.change_password_view, name='change_password'),
    path('settings/user-management/', dashboard_views.user_management_view, name='user_management'),
    path('settings/user-management/add/', dashboard_views.user_add_view, name='user_add'),
    path('settings/user-management/edit/<str:user_id>/', dashboard_views.user_edit_view, name='user_edit'),
    path('settings/user-management/delete/<str:user_id>/', dashboard_views.user_delete_view, name='user_delete'),
    path('settings/user-management/toggle-status/<str:user_id>/', dashboard_views.user_toggle_status_view, name='user_toggle_status'),
    path('settings/user-management/get/<str:user_id>/', dashboard_views.user_get_view, name='user_get'),
    path('settings/accreditation/', dashboard_views.accreditation_settings_view, name='accreditation_settings'),
    path('settings/set-deadline/', dashboard_views.set_deadline_view, name='set_deadline'),
    path('settings/get-deadline/', dashboard_views.get_deadline_view, name='get_deadline'),
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
    path('accreditation/department/<str:dept_id>/programs/<str:prog_id>/types/<str:type_id>/areas/<str:area_id>/checklists/<str:checklist_id>/documents/<str:document_id>/proxy/', dashboard_views.document_proxy_view, name='document_proxy'),
    path('accreditation/department/<str:dept_id>/programs/<str:prog_id>/types/<str:type_id>/areas/<str:area_id>/checklists/<str:checklist_id>/documents/<str:document_id>/update-status/', dashboard_views.document_update_status_view, name='document_update_status'),
    path('accreditation/department/<str:dept_id>/programs/<str:prog_id>/types/<str:type_id>/areas/<str:area_id>/checklists/<str:checklist_id>/documents/<str:document_id>/delete/', dashboard_views.document_delete_view, name='document_delete'),
    path('accreditation/department/<str:dept_id>/programs/<str:prog_id>/types/<str:type_id>/areas/<str:area_id>/checklists/<str:checklist_id>/documents/<str:document_id>/download/', dashboard_views.accreditation_download_document, name='accreditation_download_document'),
    
    # System Appearance
    path('settings/appearance/', dashboard_views.system_appearance_view, name='system_appearance'),
    path('settings/appearance/get/', dashboard_views.get_appearance_settings, name='get_appearance_settings'),
    path('settings/appearance/save-color/', dashboard_views.save_theme_color, name='save_theme_color'),
    path('settings/appearance/upload-logo/', dashboard_views.upload_logo, name='upload_logo'),
    path('settings/appearance/remove-logo/', dashboard_views.remove_logo, name='remove_logo'),
    path('settings/appearance/save-title/', dashboard_views.save_system_title, name='save_system_title'),
    path('settings/appearance/upload-background/', dashboard_views.upload_background, name='upload_background'),
    path('settings/appearance/remove-background/', dashboard_views.remove_background, name='remove_background'),
    
    path('change-password/', dashboard_views.change_password_view, name='change_password'),
    
    # Simple archive endpoints for accreditation navigation
    path('settings/departments/<str:dept_code>/archive/', dashboard_views.archive_department_simple, name='archive_department_simple'),
    path('settings/programs/<str:prog_code>/archive/', dashboard_views.archive_program_simple, name='archive_program_simple'),
    path('settings/types/<str:type_id>/archive/', dashboard_views.archive_type_simple, name='archive_type_simple'),
    path('settings/areas/<str:area_id>/archive/', dashboard_views.archive_area_simple, name='archive_area_simple'),
    path('settings/checklists/<str:checklist_id>/archive/', dashboard_views.archive_checklist_simple, name='archive_checklist_simple'),
    
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
    
    # Download template
    path('download-template/', dashboard_views.download_template_view, name='download_template'),
    
    # Calendar event management
    path('calendar/events/', dashboard_views.get_calendar_events, name='get_calendar_events'),
    path('calendar/events/create/', dashboard_views.create_calendar_event, name='create_calendar_event'),
    path('calendar/events/<str:event_id>/update/', dashboard_views.update_calendar_event, name='update_calendar_event'),
    path('calendar/events/<str:event_id>/delete/', dashboard_views.delete_calendar_event, name='delete_calendar_event'),
    path('calendar/events/<str:event_id>/archive/', dashboard_views.archive_calendar_event, name='archive_calendar_event'),
    
    # Contact Us (Department Users only)
    path('contact-us/', dashboard_views.contact_us_view, name='contact_us'),
    path('contact-us/submit/', dashboard_views.contact_us_submit, name='contact_us_submit'),
    
    # Notifications
    path('notifications/list/', dashboard_views.notifications_list_view, name='notifications_list'),
    path('notifications/<str:notification_id>/mark-read/', dashboard_views.notification_mark_read_view, name='notification_mark_read'),
    path('notifications/mark-all-read/', dashboard_views.notifications_mark_all_read_view, name='notifications_mark_all_read'),
    
    # Department User Pages
    path('dept-home/', dashboard_views.dept_home, name='dept_home'),
    path('about/', dashboard_views.about, name='about'),
    path('location/', dashboard_views.location, name='location'),
    path('mission-vision/', dashboard_views.mission_vision, name='mission_vision'),
    
    # Legacy URLs for backward compatibility
    path('qa-head/', dashboard_views.qa_head_dashboard, name='qa_head_dashboard'),
    path('qa-admin/', dashboard_views.qa_admin_dashboard, name='qa_admin_dashboard'),
    path('department/', dashboard_views.department_dashboard, name='department_dashboard'),
]