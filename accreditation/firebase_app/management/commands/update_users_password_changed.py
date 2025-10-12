from django.core.management.base import BaseCommand
from accreditation.firebase_utils import get_all_documents, update_document


class Command(BaseCommand):
    help = 'Update existing users to add is_password_changed field'

    def handle(self, *args, **kwargs):
        try:
            # Get all users
            users = get_all_documents('users')
            
            if not users:
                self.stdout.write(self.style.WARNING('No users found in database.'))
                return
            
            updated_count = 0
            for user_data in users:
                # Get user ID from the document
                user_id = user_data.get('id')
                if not user_id:
                    continue
                
                # Check if is_password_changed field already exists
                if 'is_password_changed' not in user_data:
                    # Add the field, default to True for existing users
                    # (they've already been using the system)
                    update_document('users', user_id, {
                        'is_password_changed': True
                    })
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Updated user: {user_data.get("name", user_data.get("email", user_id))}')
                    )
            
            if updated_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'\nSuccessfully updated {updated_count} user(s) with is_password_changed field.')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('All users already have the is_password_changed field.')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error updating users: {str(e)}')
            )
