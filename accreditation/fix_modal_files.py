"""
Fix modal implementation in accreditation_types.html, accreditation_areas.html, and accreditation_checklists.html
by removing malformed modals and replacing with correct implementation.
"""

import os
import re

# Define the base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates', 'dashboard')

# Modal HTML template
MODAL_HTML = '''<!-- Add Document Modal -->
<div id="documentModal" class="modal">
    <div class="modal-content">
        <div class="modal-header">
            <h3>Add Documents</h3>
            <button class="modal-close" onclick="closeDocumentModal()">&times;</button>
        </div>
        <form id="documentForm" enctype="multipart/form-data">
            <div class="modal-body">
                <input type="hidden" name="csrfmiddlewaretoken" value="{{{{ csrf_token }}}}">
                
                <div class="form-group">
                    <label for="modalDepartment">Department <span style="color: red;">*</span></label>
                    <select id="modalDepartment" name="department_id" required onchange="loadModalPrograms()">
                        <option value="">Select Department</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="modalProgram">Program <span style="color: red;">*</span></label>
                    <select id="modalProgram" name="program_id" required onchange="loadModalTypes()">
                        <option value="">Select Program</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="modalType">Accreditation Type <span style="color: red;">*</span></label>
                    <select id="modalType" name="accreditation_type_id" required onchange="loadModalAreas()">
                        <option value="">Select Type</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="modalArea">Area <span style="color: red;">*</span></label>
                    <select id="modalArea" name="area_id" required onchange="loadModalChecklists()">
                        <option value="">Select Area</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="modalChecklist">Checklist <span style="color: red;">*</span></label>
                    <select id="modalChecklist" name="checklist_id" required>
                        <option value="">Select Checklist</option>
                    </select>
                </div>
                
                <hr style="margin: 20px 0; border: none; border-top: 1px solid #e0e0e0;">
                
                <div class="form-group">
                    <label for="requiredDocumentName">Required Document Name <span style="color: red;">*</span></label>
                    <input type="text" id="requiredDocumentName" name="required_document_name" required placeholder="Enter required document name">
                </div>
                
                <div class="form-group">
                    <label for="requiredDocument">Required Document File <span style="color: red;">*</span></label>
                    <input type="file" id="requiredDocument" name="required_document" accept=".doc,.docx" required>
                    <div class="file-format-note">Accepted formats: .doc, .docx</div>
                </div>
                
                <div class="form-group">
                    <label>Additional Documents (Optional)</label>
                    <div class="additional-documents">
                        <div id="additionalDocumentsContainer">
                            <div class="additional-document-item">
                                <input type="text" name="additional_document_names[]" placeholder="Document name" style="margin-bottom: 5px;">
                                <input type="file" name="additional_documents[]" accept=".doc,.docx,.pdf,.ppt,.pptx,.xls,.xlsx,.jpg,.jpeg,.png,.gif">
                            </div>
                        </div>
                        <button type="button" class="btn-add-additional" onclick="addAdditionalDocumentField()">
                            <i class="fas fa-plus"></i> Add More
                        </button>
                    </div>
                    <div class="file-format-note">Accepted formats: .doc, .docx, .pdf, .ppt, .pptx, .xls, .xlsx, images</div>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn-cancel" onclick="closeDocumentModal()">Cancel</button>
                <button type="button" class="btn-submit" onclick="uploadDocuments()">Upload</button>
            </div>
        </form>
    </div>
</div>

<script>
{context_vars}

function getCookie(name) {{
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {{
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {{
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {{
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }}
        }}
    }}
    return cookieValue;
}}

function openAddDocumentModal() {{
    document.getElementById('documentModal').classList.add('show');
    document.getElementById('documentForm').reset();
    loadModalDepartments();
}}

function closeDocumentModal() {{
    document.getElementById('documentModal').classList.remove('show');
}}

function loadModalDepartments() {{
    fetch('/dashboard/api/departments/')
        .then(response => response.json())
        .then(data => {{
            const select = document.getElementById('modalDepartment');
            select.innerHTML = '<option value="">Select Department</option>';
            data.departments.forEach(dept => {{
                const option = document.createElement('option');
                option.value = dept.id;
                option.textContent = dept.name;
                select.appendChild(option);
            }});
            if (departmentId) {{
                select.value = departmentId;
                loadModalPrograms();
            }}
        }});
}}

function loadModalPrograms() {{
    const deptId = document.getElementById('modalDepartment').value;
    const select = document.getElementById('modalProgram');
    if (!deptId) {{
        select.innerHTML = '<option value="">Select Program</option>';
        document.getElementById('modalType').innerHTML = '<option value="">Select Type</option>';
        document.getElementById('modalArea').innerHTML = '<option value="">Select Area</option>';
        document.getElementById('modalChecklist').innerHTML = '<option value="">Select Checklist</option>';
        return;
    }}
    fetch(`/dashboard/api/departments/${{deptId}}/programs/`)
        .then(response => response.json())
        .then(data => {{
            select.innerHTML = '<option value="">Select Program</option>';
            data.programs.forEach(prog => {{
                const option = document.createElement('option');
                option.value = prog.id;
                option.textContent = prog.code ? `${{prog.code}} - ${{prog.name}}` : prog.name;
                select.appendChild(option);
            }});
            if (programId) {{
                select.value = programId;
                loadModalTypes();
            }}
        }});
}}

function loadModalTypes() {{
    const progId = document.getElementById('modalProgram').value;
    const select = document.getElementById('modalType');
    if (!progId) {{
        select.innerHTML = '<option value="">Select Type</option>';
        document.getElementById('modalArea').innerHTML = '<option value="">Select Area</option>';
        document.getElementById('modalChecklist').innerHTML = '<option value="">Select Checklist</option>';
        return;
    }}
    fetch(`/dashboard/api/programs/${{progId}}/types/`)
        .then(response => response.json())
        .then(data => {{
            select.innerHTML = '<option value="">Select Type</option>';
            data.types.forEach(type => {{
                const option = document.createElement('option');
                option.value = type.id;
                option.textContent = type.name;
                select.appendChild(option);
            }});
            if (typeId) {{
                select.value = typeId;
                loadModalAreas();
            }}
        }});
}}

function loadModalAreas() {{
    const tId = document.getElementById('modalType').value;
    const select = document.getElementById('modalArea');
    if (!tId) {{
        select.innerHTML = '<option value="">Select Area</option>';
        document.getElementById('modalChecklist').innerHTML = '<option value="">Select Checklist</option>';
        return;
    }}
    fetch(`/dashboard/api/types/${{tId}}/areas/`)
        .then(response => response.json())
        .then(data => {{
            select.innerHTML = '<option value="">Select Area</option>';
            data.areas.forEach(area => {{
                const option = document.createElement('option');
                option.value = area.id;
                option.textContent = area.name;
                select.appendChild(option);
            }});
            if (areaId) {{
                select.value = areaId;
                loadModalChecklists();
            }}
        }});
}}

function loadModalChecklists() {{
    const aId = document.getElementById('modalArea').value;
    const select = document.getElementById('modalChecklist');
    if (!aId) {{
        select.innerHTML = '<option value="">Select Checklist</option>';
        return;
    }}
    fetch(`/dashboard/api/areas/${{aId}}/checklists/`)
        .then(response => response.json())
        .then(data => {{
            select.innerHTML = '<option value="">Select Checklist</option>';
            data.checklists.forEach(checklist => {{
                const option = document.createElement('option');
                option.value = checklist.id;
                option.textContent = checklist.name;
                select.appendChild(option);
            }});
            if (checklistId) {{
                select.value = checklistId;
            }}
        }});
}}

function addAdditionalDocumentField() {{
    const container = document.getElementById('additionalDocumentsContainer');
    const newField = document.createElement('div');
    newField.className = 'additional-document-item';
    newField.innerHTML = `
        <input type="text" name="additional_document_names[]" placeholder="Document name" style="margin-bottom: 5px;">
        <input type="file" name="additional_documents[]" accept=".doc,.docx,.pdf,.ppt,.pptx,.xls,.xlsx,.jpg,.jpeg,.png,.gif">
        <button type="button" class="btn-remove-additional" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    container.appendChild(newField);
}}

function uploadDocuments() {{
    const form = document.getElementById('documentForm');
    const formData = new FormData(form);
    const deptId = document.getElementById('modalDepartment').value;
    const progId = document.getElementById('modalProgram').value;
    const tId = document.getElementById('modalType').value;
    const aId = document.getElementById('modalArea').value;
    const clId = document.getElementById('modalChecklist').value;
    
    if (!deptId || !progId || !tId || !aId || !clId) {{
        Toast.error('Please select all navigation fields');
        return;
    }}
    
    const submitBtn = document.querySelector('.btn-submit');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Uploading...';
    submitBtn.disabled = true;
    const csrftoken = getCookie('csrftoken');
    
    fetch(`/dashboard/accreditation/department/${{deptId}}/programs/${{progId}}/types/${{tId}}/areas/${{aId}}/checklists/${{clId}}/documents/add/`, {{
        method: 'POST',
        body: formData,
        headers: {{ 'X-CSRFToken': csrftoken }}
    }})
    .then(response => response.json())
    .then(data => {{
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
        if (data.success) {{
            Toast.success(data.message);
            closeDocumentModal();
        }} else {{
            Toast.error(data.message || 'Failed to upload documents');
        }}
    }})
    .catch(error => {{
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
        Toast.error('An error occurred while uploading');
        console.error('Error:', error);
    }});
}}
</script>'''

# File configurations with their context variables
FILES_TO_FIX = {
    'accreditation_types.html': {
        'context_vars': """const departmentId = '{{ dept_id }}';
const programId = '{{ prog_id }}';
const typeId = '';
const areaId = '';
const checklistId = '';"""
    },
    'accreditation_areas.html': {
        'context_vars': """const departmentId = '{{ dept_id }}';
const programId = '{{ prog_id }}';
const typeId = '{{ type_id }}';
const areaId = '';
const checklistId = '';"""
    },
    'accreditation_checklists.html': {
        'context_vars': """const departmentId = '{{ dept_id }}';
const programId = '{{ prog_id }}';
const typeId = '{{ type_id }}';
const areaId = '{{ area_id }}';
const checklistId = '';"""
    }
}


def fix_file(filename, context_vars):
    """Fix a single template file by removing all modals and adding the correct one."""
    filepath = os.path.join(TEMPLATES_DIR, filename)
    
    print(f"\nFixing {filename}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove all occurrences of the modal (from <!-- Add Document Modal --> to </script>)
    # This regex finds modal blocks that start with the comment and end with </script>
    pattern = r'<!-- Add Document Modal -->.*?</script>\s*'
    content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    # Find the last {% endblock %} and insert the modal before it
    endblock_pattern = r'({% endblock %})\s*$'
    modal_with_context = MODAL_HTML.format(context_vars=context_vars)
    replacement = f'\n{modal_with_context}\n\n\\1'
    
    content = re.sub(endblock_pattern, replacement, content)
    
    # Write back to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Fixed {filename}")


def main():
    print("Starting modal fix script...\n")
    
    for filename, config in FILES_TO_FIX.items():
        try:
            fix_file(filename, config['context_vars'])
        except Exception as e:
            print(f"✗ Error fixing {filename}: {str(e)}")
    
    print("\n✓ All files fixed successfully!")


if __name__ == '__main__':
    main()
