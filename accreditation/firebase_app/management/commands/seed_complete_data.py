"""
Django management command to seed complete Firebase data structure

Usage: python manage.py seed_complete_data

This will create:
- 3 users (QA Head, QA Admin, Department User)
- 2 departments (CCS, CED)
- 2 programs per department (4 total)
- 2 accreditation types per program (COPC & ALCUCOA) (8 total)
- 2 areas per type (Area A, Area B) (16 total)
- 2 checklists per area (32 total)
"""

from django.core.management.base import BaseCommand
from accreditation.firebase_utils import firestore_helper, create_document
import uuid
import hashlib
import secrets
from datetime import datetime


class Command(BaseCommand):
    help = 'Seed complete data structure into Firebase'
    
    def hash_password(self, raw_password):
        """Generate password hash using pbkdf2_hmac"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', 
                                          raw_password.encode('utf-8'),
                                          salt.encode('utf-8'),
                                          100000)
        return f"{salt}${password_hash.hex()}"
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🌱 Starting comprehensive data seeding...'))
        
        try:
            # Step 0: Delete all existing data
            self.stdout.write('\n' + self.style.WARNING('Step 0: Deleting all existing data...'))
            self.delete_all_data()
            
            # Step 1: Create Roles
            self.stdout.write('\n' + self.style.WARNING('Step 1: Creating Roles...'))
            roles = self.create_roles()
            
            # Step 2: Create Users
            self.stdout.write('\n' + self.style.WARNING('Step 2: Creating Users...'))
            users_created = self.create_users()
            
            # Step 3: Create Departments
            self.stdout.write('\n' + self.style.WARNING('Step 3: Creating Departments...'))
            departments = self.create_departments()
            
            # Step 4: Create Programs
            self.stdout.write('\n' + self.style.WARNING('Step 4: Creating Programs...'))
            programs = self.create_programs(departments)
            
            # Step 5: Create Accreditation Types
            self.stdout.write('\n' + self.style.WARNING('Step 5: Creating Accreditation Types...'))
            types = self.create_accreditation_types(programs)
            
            # Step 6: Create Areas
            self.stdout.write('\n' + self.style.WARNING('Step 6: Creating Areas...'))
            areas = self.create_areas(types)
            
            # Step 7: Create Checklists
            self.stdout.write('\n' + self.style.WARNING('Step 7: Creating Checklists...'))
            checklists = self.create_checklists(areas)
            
            # Summary
            self.stdout.write('\n' + '=' * 80)
            self.stdout.write(self.style.SUCCESS('✅ Data seeding completed successfully! 🎉'))
            self.stdout.write('=' * 80)
            self.stdout.write(f'\n📊 Summary:')
            self.stdout.write(f'   • Roles: {len(roles)}')
            self.stdout.write(f'   • Users: {len(users_created)}')
            self.stdout.write(f'   • Departments: {len(departments)}')
            self.stdout.write(f'   • Programs: {len(programs)}')
            self.stdout.write(f'   • Accreditation Types: {len(types)}')
            self.stdout.write(f'   • Areas: {len(areas)}')
            self.stdout.write(f'   • Checklists: {len(checklists)}')
            
            # Display login credentials
            self.stdout.write('\n' + '=' * 80)
            self.stdout.write(self.style.WARNING('🔑 Login Credentials:'))
            self.stdout.write('=' * 80)
            
            for user_info in users_created:
                self.stdout.write(f'\n{user_info["icon"]} {user_info["role"]}:')
                self.stdout.write(f'   Email: {user_info["email"]}')
                self.stdout.write(f'   Password: {user_info["password"]}')
                if user_info.get("department"):
                    self.stdout.write(f'   Department: {user_info["department"]}')
            
            self.stdout.write('\n' + '=' * 80)
            self.stdout.write(self.style.WARNING('⚠️  Change these passwords after first login!'))
            self.stdout.write('=' * 80 + '\n')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Error: {str(e)}'))
            raise
    
    def delete_all_data(self):
        """Delete all existing data from collections"""
        collections = ['roles', 'users', 'departments', 'programs', 'accreditation_types', 'areas', 'checklists']
        
        for collection_name in collections:
            try:
                collection = firestore_helper.db.collection(collection_name)
                docs = collection.stream()
                deleted_count = 0
                
                for doc in docs:
                    doc.reference.delete()
                    deleted_count += 1
                
                self.stdout.write(f'   ✓ Deleted {deleted_count} documents from {collection_name}')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'   ⚠ Error deleting {collection_name}: {str(e)}'))
    
    def create_roles(self):
        """Create roles for the system"""
        roles_collection = firestore_helper.db.collection('roles')
        
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
        
        roles_created = []
        for role_data in roles_data:
            role_id = str(uuid.uuid4())
            role_data['id'] = role_id
            roles_collection.document(role_id).set(role_data)
            roles_created.append(role_data)
            self.stdout.write(f'   ✓ Created role: {role_data["name"]} ({role_data["code"]})')
        
        return roles_created
    
    def create_users(self):
        """Create 3 users for each role"""
        users_collection = firestore_helper.db.collection('users')
        users_created = []
        
        # QA Head user (1)
        user_id = str(uuid.uuid4())
        user_doc = {
            'uid': user_id,
            'id': user_id,
            'first_name': 'QA',
            'last_name': 'Head',
            'email': 'qahead@plpasig.edu.ph',
            'role': 'qa_head',
            'department': None,
            'password_hash': self.hash_password('qahead123'),
            'is_active': True,
            'is_password_changed': False,
            'password_changed': False,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        users_collection.document(user_id).set(user_doc)
        users_created.append({
            'icon': '👑',
            'role': 'QA Head',
            'email': 'qahead@plpasig.edu.ph',
            'password': 'qahead123',
            'department': None
        })
        self.stdout.write(f'   ✓ Created QA Head: qahead@plpasig.edu.ph')
        
        # QA Admin user (1)
        user_id = str(uuid.uuid4())
        user_doc = {
            'uid': user_id,
            'id': user_id,
            'first_name': 'QA',
            'last_name': 'Admin',
            'email': 'qaadmin@plpasig.edu.ph',
            'role': 'qa_admin',
            'department': None,
            'password_hash': self.hash_password('qaadmin123'),
            'is_active': True,
            'is_password_changed': False,
            'password_changed': False,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        users_collection.document(user_id).set(user_doc)
        users_created.append({
            'icon': '🔧',
            'role': 'QA Admin',
            'email': 'qaadmin@plpasig.edu.ph',
            'password': 'qaadmin123',
            'department': None
        })
        self.stdout.write(f'   ✓ Created QA Admin: qaadmin@plpasig.edu.ph')
        
        # Department User (1)
        user_id = str(uuid.uuid4())
        user_doc = {
            'uid': user_id,
            'id': user_id,
            'first_name': 'CCS',
            'last_name': 'User',
            'email': 'user1@plpasig.edu.ph',
            'role': 'department_user',
            'department': 'CCS',
            'password_hash': self.hash_password('user123'),
            'is_active': True,
            'is_password_changed': False,
            'password_changed': False,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        users_collection.document(user_id).set(user_doc)
        users_created.append({
            'icon': '👤',
            'role': 'Department User (CCS)',
            'email': 'user1@plpasig.edu.ph',
            'password': 'user123',
            'department': 'CCS'
        })
        self.stdout.write(f'   ✓ Created Department User: user1@plpasig.edu.ph (CCS)')
        
        return users_created
    
    def create_departments(self):
        """Create 2 departments"""
        departments_collection = firestore_helper.db.collection('departments')
        
        # Use a default placeholder image from Cloudinary for departments without logos
        default_dept_logo = 'https://res.cloudinary.com/dygrh6ztt/image/upload/v1761284240/default-profile-account-unknown-icon-black-silhouette-free-vector_jdlpve.jpg'
        
        departments_data = [
            {
                'code': 'CCS',
                'name': 'College of Computer Studies',
                'logo_url': 'https://res.cloudinary.com/dygrh6ztt/image/upload/v1761284240/compsci_tcgeee.png',
                'is_active': True,
                'is_archived': False,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            },
            {
                'code': 'CED',
                'name': 'College of Education',
                'logo_url': default_dept_logo,
                'is_active': True,
                'is_archived': False,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
        ]
        
        for dept in departments_data:
            departments_collection.document(dept['code']).set(dept)
            self.stdout.write(f'   ✓ Created department: {dept["name"]} ({dept["code"]})')
        
        return departments_data
    
    def create_programs(self, departments):
        """Create 2 programs per department"""
        programs_collection = firestore_helper.db.collection('programs')
        all_programs = []
        
        programs_per_dept = {
            'CCS': [
                {'code': 'BSCS', 'name': 'Bachelor of Science in Computer Science'},
                {'code': 'BSIT', 'name': 'Bachelor of Science in Information Technology'}
            ],
            'CED': [
                {'code': 'BEED', 'name': 'Bachelor of Elementary Education'},
                {'code': 'BSED', 'name': 'Bachelor of Secondary Education'}
            ]
        }
        
        for dept in departments:
            dept_code = dept['code']
            programs = programs_per_dept[dept_code]
            
            for prog in programs:
                # Use program code as document ID (not UUID)
                program_code = prog['code']
                program_doc = {
                    'code': program_code,
                    'name': prog['name'],
                    'department_id': dept_code,
                    'is_active': True,
                    'is_archived': False,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                
                programs_collection.document(program_code).set(program_doc)
                all_programs.append(program_doc)
                self.stdout.write(f'   ✓ Created program: {prog["name"]} ({prog["code"]}) in {dept_code}')
        
        return all_programs
    
    def create_accreditation_types(self, programs):
        """Create 2 accreditation types per program"""
        types_collection = firestore_helper.db.collection('accreditation_types')
        all_types = []
        
        type_templates = [
            {
                'name': 'Certificate of Program Compliance',
                'short_name': 'COPC',
                'logo_url': 'https://via.placeholder.com/100/FF9800/FFFFFF?text=COPC'
            },
            {
                'name': 'Association of Local Colleges and University Commission on Accreditation',
                'short_name': 'ALCUCOA',
                'logo_url': 'https://via.placeholder.com/100/9C27B0/FFFFFF?text=ALCUCOA'
            }
        ]
        
        for program in programs:
            for type_template in type_templates:
                type_id = str(uuid.uuid4())
                type_doc = {
                    'id': type_id,
                    'name': type_template['name'],
                    'short_name': type_template['short_name'],
                    'logo_url': type_template['logo_url'],
                    'program_id': program['code'],  # Use program code as reference
                    'department_id': program['department_id'],
                    'is_active': True,
                    'is_archived': False,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                
                types_collection.document(type_id).set(type_doc)
                all_types.append(type_doc)
                self.stdout.write(f'   ✓ Created type: {type_template["short_name"]} for {program["code"]}')
        
        return all_types
    
    def create_areas(self, types):
        """Create 2 areas for each type"""
        areas_collection = firestore_helper.db.collection('areas')
        all_areas = []
        
        area_names = ['Area 1', 'Area 2']
        
        for acc_type in types:
            for area_name in area_names:
                area_id = str(uuid.uuid4())
                area_doc = {
                    'id': area_id,
                    'name': area_name,
                    'accreditation_type_id': acc_type['id'],
                    'program_id': acc_type['program_id'],
                    'department_id': acc_type['department_id'],
                    'is_active': True,
                    'is_archived': False,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                
                areas_collection.document(area_id).set(area_doc)
                all_areas.append(area_doc)
        
        self.stdout.write(f'   ✓ Created {len(all_areas)} areas (2 per type)')
        return all_areas
    
    def create_checklists(self, areas):
        """Create 2 checklists per area"""
        checklists_collection = firestore_helper.db.collection('checklists')
        all_checklists = []
        
        for area in areas:
            for i in range(1, 3):  # Create Checklist 1 to Checklist 2
                checklist_id = str(uuid.uuid4())
                checklist_doc = {
                    'id': checklist_id,
                    'name': f'Checklist {i}',
                    'area_id': area['id'],
                    'accreditation_type_id': area['accreditation_type_id'],
                    'program_id': area['program_id'],
                    'department_id': area['department_id'],
                    'order': i,
                    'is_active': True,
                    'is_archived': False,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                
                checklists_collection.document(checklist_id).set(checklist_doc)
                all_checklists.append(checklist_doc)
        
        self.stdout.write(f'   ✓ Created {len(all_checklists)} checklists (2 per area)')
        return all_checklists
