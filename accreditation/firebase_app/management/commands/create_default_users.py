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
            self.stdout.write('=' * 60)
            
            self.stdout.write(self.style.SUCCESS('\n🔑 QA Head:'))
            self.stdout.write('   Email: qahead@plpasig.edu.ph')
            self.stdout.write('   Password: qahead123')
            self.stdout.write('   Department: CCS')
            
            self.stdout.write(self.style.SUCCESS('\n🔑 QA Admin:'))
            self.stdout.write('   Email: qaadmin@plpasig.edu.ph')
            self.stdout.write('   Password: qaadmin123')
            self.stdout.write('   Department: CCS')
            
            self.stdout.write(self.style.SUCCESS('\n🔑 Department User (CCS):'))
            self.stdout.write('   Email: ccsuser@plpasig.edu.ph')
            self.stdout.write('   Password: ccsuser123')
            self.stdout.write('   Department: CCS')
            
            self.stdout.write(self.style.SUCCESS('\n🔑 Department User (CED):'))
            self.stdout.write('   Email: ceduser@plpasig.edu.ph')
            self.stdout.write('   Password: ceduser123')
            self.stdout.write('   Department: CED')
            
            self.stdout.write(self.style.SUCCESS('\n🔑 Department User (CAS):'))
            self.stdout.write('   Email: casuser@plpasig.edu.ph')
            self.stdout.write('   Password: casuser123')
            self.stdout.write('   Department: CAS')
            
            self.stdout.write('\n' + '=' * 60)
            self.stdout.write(self.style.WARNING('⚠️  Change these passwords after first login!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating default users: {e}'))