#!/usr/bin/env python3
"""
Script to add the document upload modal to all navigation pages
"""

import os
import re

# Define the pages and their context IDs
PAGES = [
    {
        'file': 'templates/dashboard/accreditation_programs.html',
        'dept_id': "dept_id",
        'prog_id': "",
        'type_id': "",
        'area_id': "",
        'checklist_id': ""
    },
    {
        'file': 'templates/dashboard/accreditation_types.html',
        'dept_id': "dept_id",
        'prog_id': "prog_id",
        'type_id': "",
        'area_id': "",
        'checklist_id': ""
    },
    {
        'file': 'templates/dashboard/accreditation_areas.html',
        'dept_id': "dept_id",
        'prog_id': "prog_id",
        'type_id': "type_id",
        'area_id': "",
        'checklist_id': ""
    },
    {
        'file': 'templates/dashboard/accreditation_checklists.html',
        'dept_id': "dept_id",
        'prog_id': "prog_id",
        'type_id': "type_id",
        'area_id': "area_id",
        'checklist_id': ""
    },
]

# CSS styles to add
MODAL_STYLES = """
    .btn-action-header {
        background: var(--plp-green);
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 4px;
        font-weight: 500;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 8px;
        transition: background 0.3s;
        font-size: 14px;
    }
    
    .btn-action-header:hover {
        background: var(--plp-dark-green);
    }
    
    /* Modal Styles */
    .modal {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        z-index: 9999;
        animation: fadeIn 0.3s;
    }
    
    .modal.show {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
    .modal-content {
        background: white;
        border-radius: 8px;
        width: 90%;
        max-width: 600px;
        max-height: 90vh;
        overflow-y: auto;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px;
        border-bottom: 1px solid #eee;
    }
    
    .modal-header h3 {
        margin: 0;
        color: #333;
    }
    
    .modal-close {
        background: none;
        border: none;
        font-size: 24px;
        cursor: pointer;
        color: #999;
        padding: 0;
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .modal-close:hover {
        color: #333;
    }
    
    .modal-body {
        padding: 20px;
    }
    
    .modal-footer {
        padding: 20px;
        border-top: 1px solid #eee;
        display: flex;
        justify-content: flex-end;
        gap: 10px;
    }
    
    .form-group {
        margin-bottom: 20px;
    }
    
    .form-group label {
        display: block;
        margin-bottom: 8px;
        font-weight: 500;
        color: #333;
    }
    
    .form-group input[type="text"],
    .form-group input[type="file"],
    .form-group select {
        width: 100%;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 14px;
    }
    
    .form-group select {
        cursor: pointer;
    }
    
    .form-group input:focus,
    .form-group select:focus {
        outline: none;
        border-color: var(--plp-green);
    }
    
    .file-format-note {
        font-size: 12px;
        color: #666;
        margin-top: 5px;
    }
    
    .additional-document-item {
        margin-bottom: 15px;
        padding: 15px;
        border: 1px solid #eee;
        border-radius: 4px;
        position: relative;
    }
    
    .btn-remove-additional {
        position: absolute;
        top: 10px;
        right: 10px;
        background: #dc3545;
        color: white;
        border: none;
        border-radius: 50%;
        width: 25px;
        height: 25px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .btn-add-additional {
        background: var(--plp-green);
        color: white;
        padding: 8px 16px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
        margin-top: 10px;
    }
    
    .btn-cancel {
        background: #6c757d;
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
    }
    
    .btn-submit {
        background: var(--plp-green);
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
    }
"""

# Button HTML
ADD_BUTTON = """        <button class="btn-action-header" onclick="openAddDocumentModal()">
            <i class="fas fa-plus"></i>
            Add Document
        </button>"""

def add_modal_to_page(page_info):
    """Add the document modal to a page"""
    file_path = page_info['file']
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if modal already added
    if 'id="documentModal"' in content:
        print(f"✓ Modal already exists in {file_path}")
        return True
    
    # 1. Add styles before </style>
    if MODAL_STYLES not in content:
        content = content.replace('</style>', MODAL_STYLES + '\n</style>')
    
    # 2. Add button to action-buttons-group
    if ADD_BUTTON not in content:
        # Find the action-buttons-group and add button
        pattern = r'(<div class="action-buttons-group">.*?</div>\s+</div>)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            old_div = match.group(1)
            new_div = old_div.replace('</div>\n    </div>', ADD_BUTTON + '\n        </div>\n    </div>')
            content = content.replace(old_div, new_div)
    
    # 3. Add modal HTML and JavaScript before {% endblock %}
    modal_html = f"""

<!-- Add Document Modal -->
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
                    <div class="file-format-note">Accepted formats: .doc, .docx, .pdf, .ppt, .pptx, .xls, .xlsx, .jpg, .jpeg, .png, .gif</div>
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
const departmentId = '{page_info['dept_id']}' ? '{{{{ {page_info['dept_id']} }}}}' : '';
const programId = '{page_info['prog_id']}' ? '{{{{ {page_info['prog_id']} }}}}' : '';
const typeId = '{page_info['type_id']}' ? '{{{{ {page_info['type_id']} }}}}' : '';
const areaId = '{page_info['area_id']}' ? '{{{{ {page_info['area_id']} }}}}' : '';
const checklistId = '{page_info['checklist_id']}' ? '{{{{ {page_info['checklist_id']} }}}}' : '';

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
</script>

{{% endblock %}}
"""
    
    # Add before {% endblock %}
    content = content.replace('{% endblock %}', modal_html)
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Successfully added modal to {file_path}")
    return True

def main():
    print("🚀 Adding document upload modal to navigation pages...\n")
    
    for page in PAGES:
        add_modal_to_page(page)
    
    print("\n✨ All done!")

if __name__ == '__main__':
    main()
