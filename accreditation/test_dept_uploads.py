import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'accreditation.settings')
django.setup()

from accreditation.firebase_utils import get_all_documents, get_document

print("Testing Department Uploads Data...")
print("=" * 80)

# Get active documents
all_documents = get_all_documents('documents')
active_documents = [d for d in all_documents if d.get('is_active', False) and not d.get('is_archived', False)]

print(f"Total active documents: {len(active_documents)}")

# Get department names for each document
dept_uploads = {}
for doc in active_documents:
    dept_id = doc.get('department_id')
    if dept_id:
        dept = get_document('departments', dept_id)
        if dept:
            dept_name = dept.get('name', 'Unknown')
            dept_uploads[dept_name] = dept_uploads.get(dept_name, 0) + 1

print("\nDocuments by Department:")
print("-" * 80)
for dept_name, count in dept_uploads.items():
    print(f"  {dept_name}: {count} documents")

print("\n" + "=" * 80)
print(f"Labels: {list(dept_uploads.keys())}")
print(f"Values: {list(dept_uploads.values())}")
