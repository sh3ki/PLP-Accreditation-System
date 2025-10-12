import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'accreditation.settings')
django.setup()

from accreditation.firebase_utils import get_all_documents, update_document

# Get all departments
departments = get_all_documents('departments')

print('Updating all departments to include is_active field...\n')

for dept in departments:
    dept_id = dept.get('code')
    dept_name = dept.get('name')
    
    # Check if is_active already exists
    if 'is_active' not in dept:
        # Set is_active to True by default
        update_document('departments', dept_id, {'is_active': True})
        print(f'✅ Updated "{dept_name}" (ID: {dept_id}) - Added is_active: True')
    else:
        print(f'⏭️  Skipped "{dept_name}" (ID: {dept_id}) - is_active already exists')

print('\n✅ All departments updated successfully!')
