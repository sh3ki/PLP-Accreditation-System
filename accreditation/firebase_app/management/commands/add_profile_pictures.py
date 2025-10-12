from django.core.management.base import BaseCommand
from accreditation.firebase_utils import get_all_documents, update_document


class Command(BaseCommand):
    help = 'Add profile_picture field to existing users'

    def handle(self, *args, **kwargs):
        try:
            # Get all users
            users = get_all_documents('users')
            
            if not users:
                self.stdout.write(self.style.WARNING('No users found in database.'))
                return
            
            self.stdout.write(self.style.SUCCESS('\n=== Adding Profile Pictures ===\n'))
            
            default_profile = 'https://res.cloudinary.com/dlu2bqrda/image/upload/v1760105137/default-profile-account-unknown-icon-black-silhouette-free-vector_jdlpve.jpg'
            updated_count = 0
            already_has = 0
            
            for user_data in users:
                user_id = user_data.get('id')
                email = user_data.get('email', 'N/A')
                
                if 'profile_picture' not in user_data or not user_data.get('profile_picture'):
                    # Add default profile picture
                    update_document('users', user_id, {
                        'profile_picture': default_profile
                    })
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Added profile picture: {email}')
                    )
                else:
                    already_has += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Already has profile picture: {email}')
                    )
            
            self.stdout.write(self.style.SUCCESS(f'\n=== Summary ==='))
            self.stdout.write(f'Added profile pictures: {updated_count}')
            self.stdout.write(f'Already had profile pictures: {already_has}')
            self.stdout.write(self.style.SUCCESS('\n=== Complete ===\n'))
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error updating users: {str(e)}')
            )
            import traceback
            traceback.print_exc()
