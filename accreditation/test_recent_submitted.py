import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'accreditation.settings')
django.setup()

from accreditation.firebase_utils import get_all_documents

def safe_get_datetime(doc, field_name):
    """Helper to safely get datetime from document"""
    try:
        value = doc.get(field_name)
        if isinstance(value, datetime):
            return value
        elif isinstance(value, str):
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        else:
            return datetime.min
    except:
        return datetime.min

print("Testing Recent Submitted Document URL...")
print("=" * 80)

# Get active documents
all_documents = get_all_documents('documents')
active_documents = [d for d in all_documents if d.get('is_active', False) and not d.get('is_archived', False)]

# Sort by uploaded_at descending
active_documents.sort(key=lambda x: safe_get_datetime(x, 'uploaded_at'), reverse=True)

# Filter submitted documents
submitted_docs = [d for d in active_documents if d.get('status') == 'submitted']

print(f"Total active documents: {len(active_documents)}")
print(f"Submitted documents: {len(submitted_docs)}")

if submitted_docs:
    most_recent = submitted_docs[0]
    print("\nMost Recent Submitted Document:")
    print("-" * 80)
    print(f"Name: {most_recent.get('name', 'Untitled')}")
    print(f"Status: {most_recent.get('status')}")
    print(f"Uploaded at: {most_recent.get('uploaded_at')}")
    print(f"Department ID: {most_recent.get('department_id')}")
    print(f"Program ID: {most_recent.get('program_id')}")
    print(f"Type ID: {most_recent.get('accreditation_type_id')}")
    print(f"Area ID: {most_recent.get('area_id')}")
    print(f"Checklist ID: {most_recent.get('checklist_id')}")
    
    dept_id = most_recent.get('department_id')
    prog_id = most_recent.get('program_id')
    type_id = most_recent.get('accreditation_type_id')
    area_id = most_recent.get('area_id')
    checklist_id = most_recent.get('checklist_id')
    
    if dept_id and prog_id and type_id and area_id and checklist_id:
        url = f"/dashboard/accreditation/department/{dept_id}/programs/{prog_id}/types/{type_id}/areas/{area_id}/checklists/{checklist_id}/documents/"
        print(f"\nGenerated URL:")
        print(url)
    else:
        print("\nMissing IDs - cannot generate URL")
else:
    print("\nNo submitted documents found!")
    print("Review Documents will link to: #")

print("\n" + "=" * 80)
