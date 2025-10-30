import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'accreditation.settings')
django.setup()

from accreditation.firebase_utils import get_all_documents, get_document

print("Testing uploader name retrieval...")
print("=" * 60)

# Get all documents
documents = get_all_documents('documents')
print(f"Total documents: {len(documents)}")

# Get active documents only
active_docs = [d for d in documents if d.get('is_active', False) and not d.get('is_archived', False)]
print(f"Active documents: {len(active_docs)}")

# Test uploader name retrieval for first 5 active documents
print("\nTesting uploader names for first 5 active documents:")
print("-" * 60)

for i, doc in enumerate(active_docs[:5], 1):
    doc_name = doc.get('name', 'Untitled')
    uploaded_by = doc.get('uploaded_by')
    
    print(f"\n{i}. Document: {doc_name}")
    print(f"   Uploaded by ID: {uploaded_by}")
    
    if uploaded_by:
        user_doc = get_document('users', uploaded_by)
        if user_doc:
            first_name = user_doc.get('first_name', '')
            last_name = user_doc.get('last_name', '')
            email = user_doc.get('email', '')
            full_name = f"{first_name} {last_name}".strip()
            
            print(f"   User found: {full_name if full_name else email}")
            print(f"   First name: {first_name}")
            print(f"   Last name: {last_name}")
            print(f"   Email: {email}")
        else:
            print(f"   User NOT found in database!")
    else:
        print(f"   No uploader ID set!")

print("\n" + "=" * 60)
print("Test complete!")
