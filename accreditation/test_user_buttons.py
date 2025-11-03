"""
Test script to debug user management button errors
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'accreditation.settings')
django.setup()

from accreditation.firebase_utils import get_document
from accreditation.dashboard_views import safe_get_document

# Test user ID from the error logs
user_id = 'd0594386-e371-47de-94d0-dface5e8e8d4'

print(f"Testing with user ID: {user_id}\n")

# Test 1: Direct get_document call
print("Test 1: get_document('users', user_id)")
try:
    result = get_document('users', user_id)
    print(f"  Result type: {type(result)}")
    print(f"  Result: {result}\n")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}\n")

# Test 2: safe_get_document call
print("Test 2: safe_get_document('users', user_id)")
try:
    result = safe_get_document('users', user_id)
    print(f"  Result type: {type(result)}")
    print(f"  Result: {result}\n")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}\n")

# Test 3: Try to use .get() on the result
print("Test 3: safe_get_document('users', user_id).get('email')")
try:
    result = safe_get_document('users', user_id)
    email = result.get('email')
    print(f"  Email: {email}\n")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}\n")

print("All tests completed!")
