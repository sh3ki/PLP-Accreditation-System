import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'accreditation.settings')
django.setup()

from accreditation.firebase_utils import get_all_documents

# Fetch audit logs
logs = get_all_documents('audit_trail')
print(f"\n=== AUDIT TRAIL DATABASE CHECK ===")
print(f"Total logs found: {len(logs)}")

if logs:
    print(f"\n=== FIRST 3 LOGS ===")
    for i, log in enumerate(logs[:3], 1):
        print(f"\nLog {i}:")
        print(f"  Action Type: {log.get('action_type')}")
        print(f"  User Email: {log.get('user_email')}")
        print(f"  User Name: {log.get('user_name')}")
        print(f"  Status: {log.get('status')}")
        print(f"  Details: {log.get('details')}")
        print(f"  Timestamp: {log.get('timestamp')}")
else:
    print("\nNo logs found in database!")
    print("Try logging in/out or performing an action to create logs.")
