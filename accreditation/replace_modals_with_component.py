"""
Replace all inline modals with the reusable modal component.
This script will:
1. Remove all modal HTML and JavaScript from each page
2. Replace with {% include 'components/document_upload_modal.html' %} and context variables
"""

import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates', 'dashboard')

# File configurations with their context variables
FILES_TO_UPDATE = {
    'accreditation.html': {
        'dept_id': '',
        'prog_id': '',
        'type_id': '',
        'area_id': '',
        'checklist_id': ''
    },
    'accreditation_programs.html': {
        'dept_id': '{{ dept_id }}',
        'prog_id': '',
        'type_id': '',
        'area_id': '',
        'checklist_id': ''
    },
    'accreditation_types.html': {
        'dept_id': '{{ dept_id }}',
        'prog_id': '{{ prog_id }}',
        'type_id': '',
        'area_id': '',
        'checklist_id': ''
    },
    'accreditation_areas.html': {
        'dept_id': '{{ dept_id }}',
        'prog_id': '{{ prog_id }}',
        'type_id': '{{ type_id }}',
        'area_id': '',
        'checklist_id': ''
    },
    'accreditation_checklists.html': {
        'dept_id': '{{ dept_id }}',
        'prog_id': '{{ prog_id }}',
        'type_id': '{{ type_id }}',
        'area_id': '{{ area_id }}',
        'checklist_id': ''
    }
}


def update_file(filename, context):
    """Replace inline modal with include statement."""
    filepath = os.path.join(TEMPLATES_DIR, filename)
    
    print(f"\nUpdating {filename}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove the entire modal section (from <!-- Add Document Modal --> to the script closing tag before {% endblock %})
    # Pattern matches: <!-- Add Document Modal --> ... </script> before {% endblock %}
    pattern = r'<!-- Add Document Modal -->.*?</script>\s*(?={% endblock %})'
    
    # Create the replacement with context setting and include
    replacement = f'''<script>
// Set modal context for preselection
var MODAL_CONTEXT = {{
    departmentId: '{context["dept_id"]}',
    programId: '{context["prog_id"]}',
    typeId: '{context["type_id"]}',
    areaId: '{context["area_id"]}',
    checklistId: '{context["checklist_id"]}'
}};
</script>

{{% include 'components/document_upload_modal.html' %}}

'''
    
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Write back to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Updated {filename}")


def main():
    print("Starting modal replacement script...\n")
    print("=" * 60)
    
    for filename, context in FILES_TO_UPDATE.items():
        try:
            update_file(filename, context)
        except Exception as e:
            print(f"✗ Error updating {filename}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✓ All files updated successfully!")
    print("\nNow all pages use the reusable modal component:")
    print("  templates/components/document_upload_modal.html")


if __name__ == '__main__':
    main()
