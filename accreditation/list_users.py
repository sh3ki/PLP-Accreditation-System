import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'accreditation.settings')
django.setup()

from accreditation.firebase_utils import get_all_documents

print("Listing all users in the database...")
print("=" * 60)

users = get_all_documents('users')
print(f"Total users: {len(users)}\n")

for i, user in enumerate(users, 1):
    print(f"{i}. ID: {user.get('id', 'N/A')}")
    print(f"   Email: {user.get('email', 'N/A')}")
    print(f"   First Name: {user.get('first_name', 'N/A')}")
    print(f"   Last Name: {user.get('last_name', 'N/A')}")
    print(f"   Role: {user.get('role', 'N/A')}")
    print()

print("=" * 60)
