import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'accreditation.settings')
django.setup()

from accreditation.firebase_utils import get_all_documents, update_document

# Logo URL
logo_url = "https://res.cloudinary.com/dlu2bqrda/image/upload/v1760107585/compsci_tcgeee.png"

# Get all departments
departments = get_all_documents('departments')

# Find College of Computer Studies
ccs_dept = None
for dept in departments:
    if 'Computer' in dept.get('name', '') or 'CCS' in dept.get('code', ''):
        ccs_dept = dept
        break

if ccs_dept:
    dept_id = ccs_dept.get('code')
    dept_name = ccs_dept.get('name')
    
    # Update the logo URL
    update_document('departments', dept_id, {'logo_url': logo_url})
    
    print(f'✅ Successfully updated logo for "{dept_name}" (ID: {dept_id})')
    print(f'Logo URL: {logo_url}')
else:
    print('⚠️  College of Computer Studies department not found')
    print('Available departments:')
    for dept in departments:
        print(f'  - {dept.get("name")} ({dept.get("code")})')
