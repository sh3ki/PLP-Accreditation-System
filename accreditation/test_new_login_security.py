"""
TEST SCRIPT: Login Security with New Logic

This demonstrates the new login security system:

CYCLE 1: First 3 Failed Attempts
- Attempt 1 (fail): Warning - "2 attempts remaining"
- Attempt 2 (fail): Warning - "1 attempt remaining"  
- Attempt 3 (fail): LOCKED for 3 minutes
  * Can't click Login button
  * Can't click Forgot Password
  * Timer shows countdown: "LOCKED - 2:59"
  * Lock persists across page refreshes/browser close

AFTER 3 MINUTES: Lock expires automatically
- failed_login_attempts reset to 0
- User can try again

CYCLE 2: Next 3 Failed Attempts (after first lock)
- Attempt 4 (fail): Warning - "2 attempts remaining"
- Attempt 5 (fail): Warning - "1 attempt remaining"
- Attempt 6 (fail): PERMANENT DEACTIVATION
  * Account is_active = False
  * Deactivation modal appears
  * Must contact admin to reactivate

KEY FEATURES:
✅ Lock is persistent (survives page refresh, back button, browser close)
✅ Lock is tied to EMAIL address in Firestore
✅ Uses Asia/Manila timezone for all datetime operations
✅ Disables ALL form elements during lock (inputs + forgot password link)
✅ Only 2 cycles: First lock (3 min temp) → Second lock (permanent deactivation)
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'accreditation.settings')
django.setup()

from accreditation.firebase_auth import FirebaseUser
from accreditation.firebase_utils import get_document, update_document

print("=" * 70)
print("LOGIN SECURITY TEST - New Logic")
print("=" * 70)

# Test email
test_email = "qahead@plpasig.edu.ph"

# Get user
user = FirebaseUser.get_by_email(test_email)
if not user:
    print(f"❌ User {test_email} not found")
    exit()

print(f"\n✅ Testing with user: {test_email}")

# Get current state
user_doc = get_document('users', user.id)
print(f"\n📊 Current State:")
print(f"   - Failed attempts: {user_doc.get('failed_login_attempts', 0)}")
print(f"   - Locked until: {user_doc.get('locked_until')}")
print(f"   - Has been locked once: {user_doc.get('has_been_locked_once', False)}")
print(f"   - Is active: {user_doc.get('is_active', True)}")

# Reset for clean test
print(f"\n🔄 Resetting account for clean test...")
update_document('users', user.id, {
    'failed_login_attempts': 0,
    'locked_until': None,
    'has_been_locked_once': False,
    'is_active': True
})
print("✅ Account reset complete")

print("\n" + "=" * 70)
print("CYCLE 1: First 3 Failed Attempts")
print("=" * 70)

# Simulate 3 failed attempts
for i in range(1, 4):
    print(f"\n🔴 Attempt {i} - Wrong password")
    result = FirebaseUser.authenticate(test_email, "wrongpassword")
    print(f"   Result: {result.get('message')}")
    if result.get('error') == 'account_locked':
        print(f"   🔒 LOCKED! Until: {result.get('locked_until')}")
        print(f"   ⏱️ Remaining: {result.get('remaining_seconds')} seconds")
        break

user_doc = get_document('users', user.id)
print(f"\n📊 After CYCLE 1:")
print(f"   - Failed attempts: {user_doc.get('failed_login_attempts', 0)}")
print(f"   - Has been locked once: {user_doc.get('has_been_locked_once', False)}")

print("\n💡 Lock expires after 3 minutes. Let's simulate that...")
print("   (Manually clearing lock for testing purposes)")
update_document('users', user.id, {
    'locked_until': None,
    'failed_login_attempts': 0  # Reset on lock expiry
})

print("\n" + "=" * 70)
print("CYCLE 2: Next 3 Failed Attempts (After First Lock)")
print("=" * 70)

# Simulate 3 more failed attempts
for i in range(4, 7):
    print(f"\n🔴 Attempt {i} - Wrong password")
    result = FirebaseUser.authenticate(test_email, "wrongpassword")
    print(f"   Result: {result.get('message')}")
    if result.get('error') == 'account_deactivated':
        print(f"   🚫 PERMANENTLY DEACTIVATED!")
        break

user_doc = get_document('users', user.id)
print(f"\n📊 Final State:")
print(f"   - Failed attempts: {user_doc.get('failed_login_attempts', 0)}")
print(f"   - Has been locked once: {user_doc.get('has_been_locked_once', False)}")
print(f"   - Is active: {user_doc.get('is_active', True)}")
print(f"   - Deactivation reason: {user_doc.get('deactivation_reason', 'N/A')}")

# Restore account
print("\n🔄 Restoring account for normal use...")
update_document('users', user.id, {
    'failed_login_attempts': 0,
    'locked_until': None,
    'has_been_locked_once': False,
    'is_active': True,
    'deactivation_reason': None,
    'deactivated_at': None
})
print("✅ Account restored")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
