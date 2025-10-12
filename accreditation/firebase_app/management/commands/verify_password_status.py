from django.core.management.base import BaseCommand
from accreditation.firebase_utils import get_all_documents


class Command(BaseCommand):
    help = 'Verify is_password_changed field for all users'

    def handle(self, *args, **kwargs):
        try:
            # Get all users
            users = get_all_documents('users')
            
            if not users:
                self.stdout.write(self.style.WARNING('No users found in database.'))
                return
            
            self.stdout.write(self.style.SUCCESS('\n=== User Password Status ===\n'))
            
            for user_data in users:
                user_id = user_data.get('id')
                email = user_data.get('email', 'N/A')
                name = user_data.get('name', 'N/A')
                is_password_changed = user_data.get('is_password_changed', 'NOT SET')
                
                # Color code based on status
                if is_password_changed is True:
                    status_msg = self.style.SUCCESS(f'✓ TRUE')
                elif is_password_changed is False:
                    status_msg = self.style.ERROR(f'✗ FALSE')
                else:
                    status_msg = self.style.WARNING(f'⚠ NOT SET')
                
                self.stdout.write(
                    f'{name:30} | {email:30} | is_password_changed: {status_msg}'
                )
            
            self.stdout.write(self.style.SUCCESS('\n=== End of Report ===\n'))
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error retrieving users: {str(e)}')
            )
