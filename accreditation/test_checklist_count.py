import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'accreditation.settings')
django.setup()

from accreditation.firebase_utils import get_all_documents

print("Testing Checklist Count...")
print("=" * 80)

# Get all checklists
all_checklists = get_all_documents('checklists')
print(f"Total checklists in database: {len(all_checklists)}")

# Filter active checklists
active_checklists = [c for c in all_checklists if c.get('is_active', False) and not c.get('is_archived', False)]
print(f"Active checklists (is_active=True, is_archived=False): {len(active_checklists)}")

# Show breakdown
print("\nBreakdown:")
print("-" * 80)
active_true = [c for c in all_checklists if c.get('is_active', False)]
print(f"Checklists with is_active=True: {len(active_true)}")

not_archived = [c for c in all_checklists if not c.get('is_archived', False)]
print(f"Checklists with is_archived=False: {len(not_archived)}")

print("\nSample checklists:")
print("-" * 80)
for i, checklist in enumerate(active_checklists[:5], 1):
    print(f"{i}. {checklist.get('name', 'Untitled')} - Active: {checklist.get('is_active')}, Archived: {checklist.get('is_archived')}")

print("\n" + "=" * 80)
print(f"RESULT: Total active checklists should be: {len(active_checklists)}")
