"""
Update department logos to use valid Cloudinary URLs
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'accreditation.settings')
django.setup()

from accreditation.firebase_utils import get_all_documents, update_document

print("\n🔄 Updating Department Logos...\n")
print("=" * 80)

# Default logo for departments without a logo
default_logo = 'https://res.cloudinary.com/dygrh6ztt/image/upload/v1761284240/default-profile-account-unknown-icon-black-silhouette-free-vector_jdlpve.jpg'

# Get all departments
departments = get_all_documents('departments')

print(f"Found {len(departments)} departments\n")

updated_count = 0
for dept in departments:
    dept_code = dept.get('code')
    dept_name = dept.get('name')
    current_logo = dept.get('logo_url', '')
    
    # Check if logo URL needs updating (contains via.placeholder or drvtezcke or dlu2bqrda)
    needs_update = False
    new_logo = current_logo
    
    if 'via.placeholder' in current_logo:
        needs_update = True
        new_logo = default_logo
        print(f"  ⚠️  {dept_name} ({dept_code}): Using placeholder - will update")
    elif 'drvtezcke' in current_logo or 'dlu2bqrda' in current_logo:
        needs_update = True
        # Keep CCS logo if it's the compsci one, otherwise use default
        if 'compsci' in current_logo:
            new_logo = 'https://res.cloudinary.com/dygrh6ztt/image/upload/v1761284240/compsci_tcgeee.png'
        else:
            new_logo = default_logo
        print(f"  ⚠️  {dept_name} ({dept_code}): Using old Cloudinary - will update")
    elif 'dygrh6ztt' in current_logo:
        print(f"  ✅ {dept_name} ({dept_code}): Already using new Cloudinary")
    else:
        print(f"  ⚠️  {dept_name} ({dept_code}): Unknown logo source - will use default")
        needs_update = True
        new_logo = default_logo
    
    if needs_update:
        update_document('departments', dept_code, {'logo_url': new_logo})
        updated_count += 1
        print(f"     → Updated to: {new_logo}")

print("\n" + "=" * 80)
print(f"✅ Updated {updated_count} department(s)")
print("=" * 80)
