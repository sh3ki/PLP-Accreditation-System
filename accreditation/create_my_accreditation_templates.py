"""
Script to generate remaining My Accreditation template files
Run this script from the accreditation directory:
python create_my_accreditation_templates.py
"""

import os
import re

# Base directory for templates
TEMPLATES_DIR = "templates/dashboard"

# Mapping of source templates to target templates
TEMPLATE_MAPPINGS = {
    "accreditation_types.html": "my_accreditation_types.html",
    "accreditation_areas.html": "my_accreditation_areas.html",
    "accreditation_checklists.html": "my_accreditation_checklists.html",
    "checklist_documents.html": "my_accreditation_checklist_documents.html",
}

def transform_template(content, template_type):
    """Transform accreditation template to my_accreditation template"""
    
    # Change active_page
    content = content.replace("active_page == 'accreditation'", "active_page == 'my_accreditation'")
    
    # Update breadcrumb URLs
    content = content.replace("{% url 'dashboard:accreditation'", "{% url 'dashboard:my_accreditation'")
    content = content.replace("{% url 'dashboard:accreditation_department_programs'", "{% url 'dashboard:my_accreditation_department_programs'")
    content = content.replace("{% url 'dashboard:accreditation_program_types'", "{% url 'dashboard:my_accreditation_program_types'")
    content = content.replace("{% url 'dashboard:accreditation_type_areas'", "{% url 'dashboard:my_accreditation_type_areas'")
    content = content.replace("{% url 'dashboard:accreditation_area_checklists'", "{% url 'dashboard:my_accreditation_area_checklists'")
    content = content.replace("{% url 'dashboard:my_accreditation_checklist_documents'", "{% url 'dashboard:my_accreditation_checklist_documents'")
    
    # Update navigation JavaScript URLs
    content = content.replace("/dashboard/accreditation/", "/dashboard/my-accreditation/")
    
    # Remove archive buttons
    content = re.sub(
        r'<button[^>]*class="[^"]*btn-archive[^"]*"[^>]*>.*?</button>',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Wrap Add Document button in conditional
    content = re.sub(
        r'(<button[^>]*class="[^"]*btn-action-header[^"]*"[^>]*onclick="openAddDocumentModal\(\)"[^>]*>.*?</button>)',
        r'{% if is_user_department %}\n        \1\n        {% endif %}',
        content,
        flags=re.DOTALL
    )
    
    # Update modal context to lock department
    if 'var MODAL_CONTEXT = {' in content:
        # Find and replace the MODAL_CONTEXT block
        content = re.sub(
            r"var MODAL_CONTEXT = \{[^}]+\};",
            """var MODAL_CONTEXT = {
    departmentId: '{{ user_department_id|default:"" }}',
    programId: '{{ prog_id|default:"" }}',
    typeId: '{{ type_id|default:"" }}',
    areaId: '{{ area_id|default:"" }}',
    checklistId: '{{ checklist_id|default:"" }}',
    isDepartmentLocked: true  // Department is preset and locked
};""",
            content,
            flags=re.DOTALL
        )
    
    # For documents template, remove approve/disapprove buttons
    if template_type == "checklist_documents.html":
        # Remove approve button
        content = re.sub(
            r'<button[^>]*class="[^"]*btn-approve[^"]*"[^>]*>.*?</button>',
            '',
            content,
            flags=re.DOTALL
        )
        # Remove disapprove button  
        content = re.sub(
            r'<button[^>]*class="[^"]*btn-disapprove[^"]*"[^>]*>.*?</button>',
            '',
            content,
            flags=re.DOTALL
        )
    
    return content


def main():
    """Main function to generate all templates"""
    for source_file, target_file in TEMPLATE_MAPPINGS.items():
        source_path = os.path.join(TEMPLATES_DIR, source_file)
        target_path = os.path.join(TEMPLATES_DIR, target_file)
        
        print(f"Processing {source_file} -> {target_file}...")
        
        if not os.path.exists(source_path):
            print(f"  WARNING: Source file not found: {source_path}")
            continue
            
        # Read source template
        with open(source_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Transform content
        transformed_content = transform_template(content, source_file)
        
        # Write target template
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(transformed_content)
        
        print(f"  ✓ Created {target_file}")
    
    print("\n✅ All templates created successfully!")
    print("\n📋 Created files:")
    for target_file in TEMPLATE_MAPPINGS.values():
        print(f"  - {target_file}")


if __name__ == "__main__":
    main()
