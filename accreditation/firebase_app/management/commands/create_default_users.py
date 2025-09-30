"""
Django management command to create default users

Usage: python manage.py create_default_users
"""

from django.core.management.base import BaseCommand
from accreditation.firebase_auth import create_default_users


class Command(BaseCommand):
    help = 'Create default users for the PLP Accreditation System'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating default users...'))
        
        try:
            create_default_users()
            
            self.stdout.write('\n' + self.style.SUCCESS('Default users created successfully! 🎉'))
            self.stdout.write('\n' + self.style.WARNING('Default Login Credentials:'))
            self.stdout.write('=' * 50)
            
            self.stdout.write(self.style.SUCCESS('\n🔑 QA Head:'))
            self.stdout.write('   Email: qahead@plp.edu')
            self.stdout.write('   Password: qahead123')
            
            self.stdout.write(self.style.SUCCESS('\n🔑 QA Admin:'))
            self.stdout.write('   Email: qaadmin@plp.edu')
            self.stdout.write('   Password: qaadmin123')
            
            self.stdout.write(self.style.SUCCESS('\n🔑 Department User:'))
            self.stdout.write('   Email: deptuser@plp.edu')
            self.stdout.write('   Password: deptuser123')
            
            self.stdout.write('\n' + '=' * 50)
            self.stdout.write(self.style.WARNING('⚠️  Change these passwords after first login!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating default users: {e}'))