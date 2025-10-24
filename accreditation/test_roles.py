"""
Quick test script to verify roles in database
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'accreditation.settings')
django.setup()

from accreditation.firebase_utils import get_all_documents

roles = get_all_documents('roles')
print(f'\n✅ Found {len(roles)} roles in database:\n')

for role in roles:
    print(f'  • {role.get("name")} ({role.get("code")})')
    print(f'    Description: {role.get("description")}')
    print()
