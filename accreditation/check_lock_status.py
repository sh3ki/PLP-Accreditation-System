import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'accreditation.settings')
django.setup()

from accreditation.firebase_utils import get_document, update_document
from accreditation.firebase_auth import FirebaseUser

# Get the qahead user
user = FirebaseUser.get_by_email('qahead@plpasig.edu.ph')

if user:
    print(f"User found: {user.email}")
    
    # Get user document from Firestore
    from accreditation.firebase_utils import get_document
    user_doc = get_document('users', user.id)
    
    if user_doc:
        print(f"Failed login attempts: {user_doc.get('failed_login_attempts', 0)}")
        print(f"Locked until: {user_doc.get('locked_until')}")
        print(f"Is active: {user_doc.get('is_active', True)}")
        
        # Reset the lock
        print("\nResetting lock and failed attempts...")
        update_document('users', user.id, {
            'failed_login_attempts': 0,
            'locked_until': None
        })
        print("Done! Account unlocked.")
else:
    print("User not found")
