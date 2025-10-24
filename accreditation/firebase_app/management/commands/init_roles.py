"""
Django management command to initialize roles in Firestore
"""
from django.core.management.base import BaseCommand
from accreditation.firebase_utils import create_document, get_all_documents, delete_document
from datetime import datetime


class Command(BaseCommand):
    help = 'Initialize roles collection in Firestore'

    def handle(self, *args, **options):
        self.stdout.write('=' * 60)
        self.stdout.write(self.style.WARNING('Initializing Roles Collection'))
        self.stdout.write('=' * 60)
        
        # Define the roles
        roles_data = [
            {
                'code': 'qa_head',
                'name': 'QA Head',
                'description': 'QA Head with full system access',
                'permissions': [
                    'manage_users',
                    'manage_departments',
                    'manage_programs',
                    'manage_accreditation',
                    'view_reports',
                    'manage_settings',
                    'view_audit_trail',
                    'manage_archive'
                ],
                'is_active': True,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            },
            {
                'code': 'qa_admin',
                'name': 'QA Admin',
                'description': 'QA Admin with administrative access',
                'permissions': [
                    'manage_accreditation',
                    'view_reports',
                    'manage_programs',
                    'view_audit_trail'
                ],
                'is_active': True,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            },
            {
                'code': 'department_user',
                'name': 'Department User',
                'description': 'Department user with limited access',
                'permissions': [
                    'view_department_programs',
                    'submit_accreditation',
                    'view_reports'
                ],
                'is_active': True,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
        ]
        
        try:
            # Check if roles already exist
            existing_roles = get_all_documents('roles')
            
            if existing_roles:
                self.stdout.write(self.style.WARNING(f'\n⚠️  Found {len(existing_roles)} existing roles'))
                
                # Ask user if they want to delete existing roles
                confirm = input('Do you want to delete existing roles and recreate them? (yes/no): ')
                
                if confirm.lower() in ['yes', 'y']:
                    self.stdout.write('\nDeleting existing roles...')
                    for role in existing_roles:
                        if role.get('id'):
                            delete_document('roles', role['id'])
                    self.stdout.write(self.style.SUCCESS('✓ Deleted existing roles'))
                else:
                    self.stdout.write(self.style.WARNING('\nSkipping role creation. Existing roles retained.'))
                    return
            
            # Create roles
            self.stdout.write('\nCreating roles...')
            created_count = 0
            
            for role_data in roles_data:
                role_id = create_document('roles', role_data)
                created_count += 1
                self.stdout.write(f'  ✓ Created role: {role_data["name"]} ({role_data["code"]})')
            
            self.stdout.write('\n' + '=' * 60)
            self.stdout.write(self.style.SUCCESS(f'✅ Successfully created {created_count} roles!'))
            self.stdout.write('=' * 60)
            
            # Display created roles
            self.stdout.write('\n📋 Created Roles:')
            self.stdout.write('-' * 60)
            for role in roles_data:
                self.stdout.write(f"\n  • {role['name']} ({role['code']})")
                self.stdout.write(f"    Description: {role['description']}")
                self.stdout.write(f"    Permissions: {', '.join(role['permissions'])}")
            
            self.stdout.write('\n' + '=' * 60)
            self.stdout.write(self.style.SUCCESS('✨ Roles initialization completed!'))
            self.stdout.write('=' * 60)
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Error: {str(e)}'))
            raise e
