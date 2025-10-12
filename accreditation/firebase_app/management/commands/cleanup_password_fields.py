from django.core.management.base import BaseCommand
from accreditation.firebase_utils import get_all_documents, get_document, update_document
from accreditation.dashboard_views import hash_password
from google.cloud import firestore


class Command(BaseCommand):
    help = 'Clean up old password field and ensure password_hash is used'

    def handle(self, *args, **kwargs):
        try:
            # Get all users
            users = get_all_documents('users')
            
            if not users:
                self.stdout.write(self.style.WARNING('No users found in database.'))
                return
            
            self.stdout.write(self.style.SUCCESS('\n=== Password Field Cleanup ===\n'))
            
            migrated_count = 0
            cleaned_count = 0
            already_correct = 0
            
            # Initialize Firestore client for field deletion
            from accreditation.firebase_utils import firestore_helper
            from google.cloud.firestore import DELETE_FIELD
            
            for user_data in users:
                user_id = user_data.get('id')
                email = user_data.get('email', 'N/A')
                has_password = 'password' in user_data
                has_password_hash = 'password_hash' in user_data
                
                if has_password and not has_password_hash:
                    # Migrate: hash the plain password and create password_hash
                    plain_password = user_data['password']
                    hashed = hash_password(plain_password)
                    
                    # Update with password_hash
                    update_document('users', user_id, {
                        'password_hash': hashed
                    })
                    
                    # Remove the old password field
                    user_ref = firestore_helper.db.collection('users').document(user_id)
                    user_ref.update({
                        'password': DELETE_FIELD
                    })
                    
                    migrated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Migrated: {email} (hashed password and removed old field)')
                    )
                    
                elif has_password and has_password_hash:
                    # Has both: remove the old password field
                    user_ref = firestore_helper.db.collection('users').document(user_id)
                    user_ref.update({
                        'password': DELETE_FIELD
                    })
                    
                    cleaned_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'⚠ Cleaned: {email} (removed duplicate password field)')
                    )
                    
                elif has_password_hash and not has_password:
                    # Already correct
                    already_correct += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ OK: {email} (already using password_hash)')
                    )
                    
                else:
                    # No password at all
                    self.stdout.write(
                        self.style.ERROR(f'✗ ERROR: {email} (no password or password_hash found!)')
                    )
            
            self.stdout.write(self.style.SUCCESS('\n=== Summary ==='))
            self.stdout.write(f'Migrated (password → password_hash): {migrated_count}')
            self.stdout.write(f'Cleaned (removed duplicate): {cleaned_count}')
            self.stdout.write(f'Already correct: {already_correct}')
            self.stdout.write(self.style.SUCCESS('\n=== Cleanup Complete ===\n'))
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during cleanup: {str(e)}')
            )
            import traceback
            traceback.print_exc()
