#!/usr/bin/env python
"""
Quick script to check Firestore data
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'accreditation.settings')
django.setup()

from accreditation.firebase_utils import get_all_documents

print("=" * 80)
print("CHECKING FIRESTORE DATA")
print("=" * 80)

# Check Programs
print("\n1. PROGRAMS:")
programs = get_all_documents('programs')
print(f"Total programs: {len(programs)}")
if programs:
    print("\nFirst 3 programs:")
    for i, prog in enumerate(programs[:3]):
        print(f"  Program {i+1}:")
        print(f"    ID: {prog.get('id', 'N/A')}")
        print(f"    Name: {prog.get('name', 'N/A')}")
        print(f"    Status: {prog.get('status', 'N/A')}")
        print(f"    Active field: {prog.get('active', 'N/A')}")
        print(f"    Archived: {prog.get('archived', 'N/A')}")
        print(f"    All keys: {list(prog.keys())}")

# Check Documents
print("\n2. DOCUMENTS:")
documents = get_all_documents('documents')
print(f"Total documents: {len(documents)}")

# Count by status
status_counts = {}
for doc in documents:
    status = doc.get('status', 'no_status')
    status_counts[status] = status_counts.get(status, 0) + 1

print(f"Document status breakdown:")
for status, count in sorted(status_counts.items()):
    print(f"  {status}: {count}")

if documents:
    print("\nFirst 3 documents:")
    for i, doc in enumerate(documents[:3]):
        print(f"  Document {i+1}:")
        print(f"    ID: {doc.get('id', 'N/A')}")
        print(f"    Title: {doc.get('title', 'N/A')}")
        print(f"    Status: {doc.get('status', 'N/A')}")
        print(f"    Uploaded at: {doc.get('uploaded_at', 'N/A')}")

# Check Departments
print("\n3. DEPARTMENTS:")
departments = get_all_documents('departments')
print(f"Total departments: {len(departments)}")
if departments:
    print("\nAll departments:")
    for i, dept in enumerate(departments):
        print(f"  Department {i+1}:")
        print(f"    All keys: {list(dept.keys())}")
        for key in dept.keys():
            print(f"    {key}: {dept.get(key)}")

# Check Checklists
print("\n4. CHECKLISTS:")
checklists = get_all_documents('checklists')
print(f"Total checklists: {len(checklists)}")
if checklists:
    print("\nFirst 3 checklists:")
    for i, checklist in enumerate(checklists[:3]):
        print(f"  Checklist {i+1}:")
        print(f"    All keys: {list(checklist.keys())}")
        for key in ['id', 'name', 'is_active', 'is_archived', 'area_id']:
            if key in checklist:
                print(f"    {key}: {checklist.get(key)}")

print("\n" + "=" * 80)
