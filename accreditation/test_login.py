import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'accreditation.settings')
django.setup()

from accreditation.firebase_auth import FirebaseUser
import hashlib

# Test QA Head user
print("="*60)
print("Testing QA Head Login")
print("="*60)

user = FirebaseUser.get_by_email('qahead@plpasig.edu.ph')
print(f"User found: {user is not None}")

if user:
    print(f"Email: {user.email}")
    print(f"Name: {user.full_name}")
    print(f"Role: {user.role}")
    print(f"Is active: {user.is_active}")
    print(f"Has password hash: {bool(user.password_hash)}")
    
    if user.password_hash:
        print(f"\nPassword hash format: {user.password_hash[:50]}...")
        
        # Test password
        test_password = 'qahead123'
        try:
            salt, stored_hash = user.password_hash.split('$')
            computed_hash = hashlib.pbkdf2_hmac('sha256',
                                               test_password.encode('utf-8'),
                                               salt.encode('utf-8'),
                                               100000).hex()
            
            print(f"\nPassword verification:")
            print(f"  Salt length: {len(salt)}")
            print(f"  Stored hash: {stored_hash[:20]}...")
            print(f"  Computed hash: {computed_hash[:20]}...")
            print(f"  Matches: {computed_hash == stored_hash}")
            
            # Test using the check_password method
            print(f"\nUsing check_password method: {user.check_password(test_password)}")
            
            # Test authentication
            auth_user = FirebaseUser.authenticate('qahead@plpasig.edu.ph', 'qahead123')
            print(f"Authentication result: {auth_user is not None}")
            
        except Exception as e:
            print(f"Error during password check: {e}")
else:
    print("User not found in Firebase!")
