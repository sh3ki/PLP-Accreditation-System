"""
Django management command to initialize departments and roles in Firebase

Usage: python manage.py init_departments_roles
"""

from django.core.management.base import BaseCommand
from accreditation.firebase_utils import create_document, get_all_documents
from datetime import datetime


class Command(BaseCommand):
    help = 'Initialize departments and roles in Firebase Firestore'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Initializing departments and roles...'))
        
        try:
            # Initialize Departments
            self.stdout.write('\n📚 Creating departments...')
            departments = [
                {
                    'code': 'QA',
                    'name': 'Quality Assurance',
                    'description': 'Quality Assurance Office',
                    'is_active': True,
                },
                {
                    'code': 'CBA',
                    'name': 'College of Business and Accountancy',
                    'description': 'Business, Accounting, and Management programs',
                    'is_active': True,
                },
                {
                    'code': 'CIHM',
                    'name': 'College of International Hospitality Management',
                    'description': 'International Hospitality and Hotel Management',
                    'is_active': True,
                },
                {
                    'code': 'COE',
                    'name': 'College of Education',
                    'description': 'Education and Teaching programs',
                    'is_active': True,
                },
                {
                    'code': 'CAS',
                    'name': 'College of Arts and Sciences',
                    'description': 'Liberal Arts, Sciences, and Humanities',
                    'is_active': True,
                },
                {
                    'code': 'CCS',
                    'name': 'College of Computer Studies',
                    'description': 'Computer Science and Information Technology',
                    'is_active': True,
                },
                {
                    'code': 'CENG',
                    'name': 'College of Engineering',
                    'description': 'Engineering and Technology programs',
                    'is_active': True,
                },
                {
                    'code': 'CON',
                    'name': 'College of Nursing',
                    'description': 'Nursing and Healthcare programs',
                    'is_active': True,
                },
            ]
            
            # Check if departments already exist
            existing_depts = get_all_documents('departments')
            if existing_depts:
                self.stdout.write(self.style.WARNING(f'   Found {len(existing_depts)} existing departments'))
                user_input = input('   Do you want to recreate them? (yes/no): ')
                if user_input.lower() != 'yes':
                    self.stdout.write(self.style.WARNING('   Skipping departments creation'))
                else:
                    for dept in departments:
                        doc_id = create_document('departments', dept, dept['code'])
                        self.stdout.write(self.style.SUCCESS(f'   ✓ Created: {dept["name"]} ({dept["code"]})'))
            else:
                for dept in departments:
                    doc_id = create_document('departments', dept, dept['code'])
                    self.stdout.write(self.style.SUCCESS(f'   ✓ Created: {dept["name"]} ({dept["code"]})'))
            
            # Initialize Roles
            self.stdout.write('\n👥 Creating roles...')
            roles = [
                {
                    'code': 'qa_head',
                    'name': 'Super Admin',
                    'description': 'Full system access - QA Head',
                    'permissions': [
                        'user_management',
                        'accreditation_settings',
                        'system_appearance',
                        'view_all_departments',
                        'edit_all_departments',
                        'view_reports',
                        'view_audit_trail',
                        'manage_calendar',
                        'manage_performance',
                        'manage_results',
                        'manage_archive',
                    ],
                    'is_active': True,
                },
                {
                    'code': 'qa_admin',
                    'name': 'Admin',
                    'description': 'Administrative access - QA Admin',
                    'permissions': [
                        'accreditation_settings',
                        'system_appearance',
                        'view_all_departments',
                        'edit_all_departments',
                        'view_reports',
                        'view_audit_trail',
                        'manage_calendar',
                        'manage_performance',
                        'manage_results',
                        'manage_archive',
                    ],
                    'is_active': True,
                },
                {
                    'code': 'department_user',
                    'name': 'User',
                    'description': 'Department level access',
                    'permissions': [
                        'view_own_department',
                        'edit_own_department',
                        'view_calendar',
                        'view_performance',
                        'submit_documents',
                    ],
                    'is_active': True,
                },
            ]
            
            # Check if roles already exist
            existing_roles = get_all_documents('roles')
            if existing_roles:
                self.stdout.write(self.style.WARNING(f'   Found {len(existing_roles)} existing roles'))
                user_input = input('   Do you want to recreate them? (yes/no): ')
                if user_input.lower() != 'yes':
                    self.stdout.write(self.style.WARNING('   Skipping roles creation'))
                else:
                    for role in roles:
                        doc_id = create_document('roles', role, role['code'])
                        self.stdout.write(self.style.SUCCESS(f'   ✓ Created: {role["name"]} ({role["code"]})'))
            else:
                for role in roles:
                    doc_id = create_document('roles', role, role['code'])
                    self.stdout.write(self.style.SUCCESS(f'   ✓ Created: {role["name"]} ({role["code"]})'))
            
            self.stdout.write('\n' + '=' * 60)
            self.stdout.write(self.style.SUCCESS('✅ Departments and roles initialized successfully!'))
            self.stdout.write('=' * 60)
            
            # Display summary
            all_depts = get_all_documents('departments')
            all_roles = get_all_documents('roles')
            
            self.stdout.write(f'\n📊 Summary:')
            self.stdout.write(f'   Departments: {len(all_depts)}')
            self.stdout.write(f'   Roles: {len(all_roles)}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Error initializing departments and roles: {e}'))
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc()))
