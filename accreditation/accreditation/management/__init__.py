"""
Django management command to test Firebase Firestore connection

Usage: python manage.py test_firebase
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Test Firebase Firestore connection and basic operations'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing Firebase Firestore connection...'))
        
        # Check if service account file exists
        service_account_path = settings.FIREBASE_SERVICE_ACCOUNT_PATH
        if not os.path.exists(service_account_path):
            self.stdout.write(
                self.style.ERROR(
                    f'Firebase service account file not found at: {service_account_path}\n'
                    'Please download your service account key from Firebase Console:\n'
                    '1. Go to https://console.firebase.google.com/\n'
                    '2. Select your "accreditation" project\n'
                    '3. Go to Project Settings > Service Accounts\n'
                    '4. Click "Generate new private key"\n'
                    '5. Save the file as "firebase-service-account.json" in your project root'
                )
            )
            return
        
        try:
            # Import Firebase utilities
            from accreditation.firebase_utils import firestore_helper
            
            # Test connection
            if not firestore_helper.is_connected():
                self.stdout.write(self.style.ERROR('Failed to connect to Firestore'))
                return
            
            self.stdout.write(self.style.SUCCESS('✓ Successfully connected to Firestore'))
            
            # Test basic operations
            self.stdout.write('Testing basic CRUD operations...')
            
            # Test CREATE
            test_data = {
                'name': 'Test Document',
                'description': 'This is a test document for Firebase connection',
                'status': 'active',
                'test_field': 'test_value'
            }
            
            doc_id = firestore_helper.create_document('test_collection', test_data)
            self.stdout.write(self.style.SUCCESS(f'✓ Created test document with ID: {doc_id}'))
            
            # Test READ
            retrieved_doc = firestore_helper.get_document('test_collection', doc_id)
            if retrieved_doc:
                self.stdout.write(self.style.SUCCESS('✓ Successfully retrieved test document'))
                self.stdout.write(f'   Document data: {retrieved_doc}')
            else:
                self.stdout.write(self.style.ERROR('✗ Failed to retrieve test document'))
            
            # Test UPDATE
            update_data = {
                'status': 'updated',
                'test_update': 'updated_value'
            }
            
            success = firestore_helper.update_document('test_collection', doc_id, update_data)
            if success:
                self.stdout.write(self.style.SUCCESS('✓ Successfully updated test document'))
                
                # Verify update
                updated_doc = firestore_helper.get_document('test_collection', doc_id)
                if updated_doc and updated_doc.get('status') == 'updated':
                    self.stdout.write(self.style.SUCCESS('✓ Update verified'))
                else:
                    self.stdout.write(self.style.ERROR('✗ Update verification failed'))
            else:
                self.stdout.write(self.style.ERROR('✗ Failed to update test document'))
            
            # Test QUERY
            query_results = firestore_helper.query_documents('test_collection', 'status', '==', 'updated')
            if query_results:
                self.stdout.write(self.style.SUCCESS(f'✓ Query successful, found {len(query_results)} document(s)'))
            else:
                self.stdout.write(self.style.ERROR('✗ Query failed or returned no results'))
            
            # Test DELETE
            success = firestore_helper.delete_document('test_collection', doc_id)
            if success:
                self.stdout.write(self.style.SUCCESS('✓ Successfully deleted test document'))
                
                # Verify deletion
                deleted_doc = firestore_helper.get_document('test_collection', doc_id)
                if deleted_doc is None:
                    self.stdout.write(self.style.SUCCESS('✓ Deletion verified'))
                else:
                    self.stdout.write(self.style.ERROR('✗ Deletion verification failed'))
            else:
                self.stdout.write(self.style.ERROR('✗ Failed to delete test document'))
            
            # Display project info
            self.stdout.write('\n' + self.style.SUCCESS('Firebase Project Information:'))
            self.stdout.write(f'Project ID: {settings.FIREBASE_CONFIG["project_id"]}')
            self.stdout.write(f'Project Number: {settings.FIREBASE_CONFIG["project_number"]}')
            
            self.stdout.write('\n' + self.style.SUCCESS('All tests completed successfully! 🎉'))
            self.stdout.write('Your Django project is now connected to Firebase Firestore.')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during testing: {e}'))
            self.stdout.write(
                self.style.WARNING(
                    'Make sure you have:\n'
                    '1. Downloaded the service account key from Firebase Console\n'
                    '2. Saved it as "firebase-service-account.json" in your project root\n'
                    '3. Enabled Firestore in your Firebase project'
                )
            )