"""
Comprehensive CRUD Operations Test Script
Tests all action buttons for Programs, Accreditation Types, Areas, and Checklists
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'accreditation.settings')
django.setup()

from django.test import Client
import json

# Test client
client = Client()

# Test data IDs
DEPT_ID = 'CCS'
TEST_PROG_CODE = 'TEST001'
TEST_TYPE_ID = None
TEST_AREA_ID = None
TEST_CHECKLIST_ID = None

def print_step(step_num, description):
    """Print test step header"""
    print(f"\n{'='*80}")
    print(f"STEP {step_num}: {description}")
    print(f"{'='*80}")

def print_result(success, message):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {message}")

"""
Comprehensive CRUD Operations Test Script
Tests all action buttons for Programs, Accreditation Types, Areas, and Checklists
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'accreditation.settings')
django.setup()

from django.test import Client
from accreditation.firebase_utils import query_documents
import json

# Test client (with allowed host)
client = Client(SERVER_NAME='127.0.0.1:8000')

# Test data IDs
DEPT_ID = 'CCS'
TEST_PROG_CODE = 'TEST001'
TEST_TYPE_ID = None
TEST_AREA_ID = None
TEST_CHECKLIST_ID = None

def print_step(step_num, description):
    """Print test step header"""
    print(f"\n{'='*80}")
    print(f"STEP {step_num}: {description}")
    print(f"{'='*80}")

def print_result(success, message):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {message}")

def login():
    """Login to get session"""
    print_step(0, "LOGIN")
    
    # Use the test client to login
    # We'll manually set the session since we're testing CRUD operations, not auth
    # We need to create a FirebaseUser-like object
    from accreditation.firebase_auth import FirebaseUser
    
    # Create a test user
    test_user = FirebaseUser(
        uid='qahead@plp.edu.ph',
        email='qahead@plp.edu.ph',
        role='qa_head',
        is_active=True
    )
    
    # Set session data
    session = client.session
    session['user_id'] = 'qahead@plp.edu.ph'
    session['user_email'] = 'qahead@plp.edu.ph'
    session['user_role'] = 'qa_head'
    session['user_name'] = 'QA Head'
    session['is_authenticated'] = True
    session.save()
    
    print_result(True, "Session configured for QA Head")
    return True

# ============================================
# PROGRAM CRUD TESTS
# ============================================

def test_program_add():
    """Test adding a program"""
    global TEST_PROG_CODE
    print_step(1, "ADD PROGRAM")
    
    response = client.post(
        f"/dashboard/settings/departments/{DEPT_ID}/programs/add/",
        data={
            'code': TEST_PROG_CODE,
            'name': 'Test Program for CRUD Operations'
        }
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, result.get('message', 'Unknown error'))
    return success

def test_program_get():
    """Test getting program details"""
    print_step(2, "GET PROGRAM DETAILS")
    
    response = client.get(
        f"/dashboard/settings/departments/{DEPT_ID}/programs/get/{TEST_PROG_CODE}/"
    )
    
    result = response.json()
    success = result.get('success', False)
    if success:
        prog = result.get('program', {})
        print_result(success, f"Retrieved program: {prog.get('name')}")
    else:
        print_result(success, result.get('message', 'Unknown error'))
    return success

def test_program_edit():
    """Test editing a program"""
    print_step(3, "EDIT PROGRAM")
    
    response = client.post(
        f"/dashboard/settings/departments/{DEPT_ID}/programs/edit/{TEST_PROG_CODE}/",
        data={
            'name': 'Test Program for CRUD Operations (EDITED)'
        }
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, result.get('message', 'Unknown error'))
    return success

def test_program_toggle_active():
    """Test activating/deactivating a program"""
    print_step(4, "TOGGLE PROGRAM ACTIVE STATUS")
    
    # Deactivate
    response = client.post(
        f"/dashboard/settings/departments/{DEPT_ID}/programs/toggle-active/{TEST_PROG_CODE}/",
        data=json.dumps({'is_active': False}),
        content_type='application/json'
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, f"Deactivate: {result.get('message', 'Unknown error')}")
    
    # Reactivate
    response = client.post(
        f"/dashboard/settings/departments/{DEPT_ID}/programs/toggle-active/{TEST_PROG_CODE}/",
        data=json.dumps({'is_active': True}),
        content_type='application/json'
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, f"Reactivate: {result.get('message', 'Unknown error')}")
    return success

def test_program_archive():
    """Test archiving/unarchiving a program"""
    print_step(5, "TOGGLE PROGRAM ARCHIVE STATUS")
    
    # Archive
    response = client.post(
        f"/dashboard/settings/departments/{DEPT_ID}/programs/archive/{TEST_PROG_CODE}/",
        data=json.dumps({'is_archived': True}),
        content_type='application/json'
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, f"Archive: {result.get('message', 'Unknown error')}")
    
    # Unarchive
    response = client.post(
        f"/dashboard/settings/departments/{DEPT_ID}/programs/archive/{TEST_PROG_CODE}/",
        data=json.dumps({'is_archived': False}),
        content_type='application/json'
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, f"Unarchive: {result.get('message', 'Unknown error')}")
    return success

# ============================================
# ACCREDITATION TYPE CRUD TESTS
# ============================================

def test_type_add():
    """Test adding an accreditation type"""
    global TEST_TYPE_ID
    print_step(6, "ADD ACCREDITATION TYPE")
    
    response = client.post(
        f"/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/add/",
        data={
            'name': 'Test Accreditation Type'
        }
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, result.get('message', 'Unknown error'))
    
    # Get the type ID
    if success:
        types = query_documents('accreditation_types', [('program_id', '==', TEST_PROG_CODE)])
        for t in types:
            if t.get('name') == 'Test Accreditation Type':
                TEST_TYPE_ID = t.get('id')
                print(f"   Type ID: {TEST_TYPE_ID}")
                break
    
    return success

def test_type_get():
    """Test getting type details"""
    print_step(7, "GET ACCREDITATION TYPE DETAILS")
    
    response = client.get(
        f"/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/get/{TEST_TYPE_ID}/"
    )
    
    result = response.json()
    success = result.get('success', False)
    if success:
        type_data = result.get('type', {})
        print_result(success, f"Retrieved type: {type_data.get('name')}")
    else:
        print_result(success, result.get('message', 'Unknown error'))
    return success

def test_type_edit():
    """Test editing a type"""
    print_step(8, "EDIT ACCREDITATION TYPE")
    
    response = client.post(
        f"/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/edit/{TEST_TYPE_ID}/",
        data={
            'name': 'Test Accreditation Type (EDITED)'
        }
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, result.get('message', 'Unknown error'))
    return success

def test_type_toggle_active():
    """Test activating/deactivating a type"""
    print_step(9, "TOGGLE TYPE ACTIVE STATUS")
    
    # Deactivate
    response = client.post(
        f"/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/toggle-active/{TEST_TYPE_ID}/",
        data=json.dumps({'is_active': False}),
        content_type='application/json'
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, f"Deactivate: {result.get('message', 'Unknown error')}")
    
    # Reactivate
    response = client.post(
        f"/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/toggle-active/{TEST_TYPE_ID}/",
        data=json.dumps({'is_active': True}),
        content_type='application/json'
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, f"Reactivate: {result.get('message', 'Unknown error')}")
    return success

def test_type_archive():
    """Test archiving/unarchiving a type"""
    print_step(10, "TOGGLE TYPE ARCHIVE STATUS")
    
    # Archive
    response = client.post(
        f"/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/archive/{TEST_TYPE_ID}/",
        data=json.dumps({'is_archived': True}),
        content_type='application/json'
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, f"Archive: {result.get('message', 'Unknown error')}")
    
    # Unarchive
    response = client.post(
        f"/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/archive/{TEST_TYPE_ID}/",
        data=json.dumps({'is_archived': False}),
        content_type='application/json'
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, f"Unarchive: {result.get('message', 'Unknown error')}")
    return success

# ============================================
# AREA CRUD TESTS
# ============================================

def test_module_add():
    """Test adding a area"""
    global TEST_AREA_ID
    print_step(11, "ADD AREA")
    
    response = client.post(
        f"/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/add/",
        data={
            'code': 'TESTMOD001',
            'name': 'Test Area'
        }
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, result.get('message', 'Unknown error'))
    
    if success:
        TEST_AREA_ID = 'TESTMOD001'
        print(f"   Area ID: {TEST_AREA_ID}")
    
    return success

def test_module_get():
    """Test getting area details"""
    print_step(12, "GET AREA DETAILS")
    
    response = client.get(
        f"/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/get/{TEST_AREA_ID}/"
    )
    
    result = response.json()
    success = result.get('success', False)
    if success:
        area = result.get('area', {})
        print_result(success, f"Retrieved area: {area.get('name')}")
    else:
        print_result(success, result.get('message', 'Unknown error'))
    return success

def test_module_edit():
    """Test editing a area"""
    print_step(13, "EDIT AREA")
    
    response = client.post(
        f"/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/edit/{TEST_AREA_ID}/",
        data={
            'name': 'Test Area (EDITED)'
        }
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, result.get('message', 'Unknown error'))
    return success

def test_module_toggle_active():
    """Test activating/deactivating a area"""
    print_step(14, "TOGGLE AREA ACTIVE STATUS")
    
    # Deactivate
    response = client.post(
        f"/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/toggle-active/{TEST_AREA_ID}/",
        data=json.dumps({'is_active': False}),
        content_type='application/json'
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, f"Deactivate: {result.get('message', 'Unknown error')}")
    
    # Reactivate
    response = client.post(
        f"/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/toggle-active/{TEST_AREA_ID}/",
        data=json.dumps({'is_active': True}),
        content_type='application/json'
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, f"Reactivate: {result.get('message', 'Unknown error')}")
    return success

def test_module_archive():
    """Test archiving/unarchiving a area"""
    print_step(15, "TOGGLE AREA ARCHIVE STATUS")
    
    # Archive
    response = client.post(
        f"/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/archive/{TEST_AREA_ID}/",
        data=json.dumps({'is_archived': True}),
        content_type='application/json'
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, f"Archive: {result.get('message', 'Unknown error')}")
    
    # Unarchive
    response = client.post(
        f"/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/archive/{TEST_AREA_ID}/",
        data=json.dumps({'is_archived': False}),
        content_type='application/json'
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, f"Unarchive: {result.get('message', 'Unknown error')}")
    return success

# ============================================
# CHECKLIST CRUD TESTS
# ============================================

def test_checklist_add():
    """Test adding a checklist"""
    global TEST_CHECKLIST_ID
    print_step(16, "ADD CHECKLIST")
    
    response = client.post(
        f"/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/{TEST_AREA_ID}/checklists/add/",
        data={
            'code': 'TESTCHK001',
            'name': 'Test Checklist'
        }
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, result.get('message', 'Unknown error'))
    
    if success:
        TEST_CHECKLIST_ID = 'TESTCHK001'
        print(f"   Checklist ID: {TEST_CHECKLIST_ID}")
    
    return success

def test_checklist_get():
    """Test getting checklist details"""
    print_step(17, "GET CHECKLIST DETAILS")
    
    response = client.get(
        f"/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/{TEST_AREA_ID}/checklists/get/{TEST_CHECKLIST_ID}/"
    )
    
    result = response.json()
    success = result.get('success', False)
    if success:
        checklist = result.get('checklist', {})
        print_result(success, f"Retrieved checklist: {checklist.get('name')}")
    else:
        print_result(success, result.get('message', 'Unknown error'))
    return success

def test_checklist_edit():
    """Test editing a checklist"""
    print_step(18, "EDIT CHECKLIST")
    
    response = client.post(
        f"/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/{TEST_AREA_ID}/checklists/edit/{TEST_CHECKLIST_ID}/",
        data={
            'name': 'Test Checklist (EDITED)'
        }
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, result.get('message', 'Unknown error'))
    return success

def test_checklist_toggle_active():
    """Test activating/deactivating a checklist"""
    print_step(19, "TOGGLE CHECKLIST ACTIVE STATUS")
    
    # Deactivate
    response = client.post(
        f"/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/{TEST_AREA_ID}/checklists/toggle-active/{TEST_CHECKLIST_ID}/",
        data=json.dumps({'is_active': False}),
        content_type='application/json'
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, f"Deactivate: {result.get('message', 'Unknown error')}")
    
    # Reactivate
    response = client.post(
        f"/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/{TEST_AREA_ID}/checklists/toggle-active/{TEST_CHECKLIST_ID}/",
        data=json.dumps({'is_active': True}),
        content_type='application/json'
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, f"Reactivate: {result.get('message', 'Unknown error')}")
    return success

def test_checklist_archive():
    """Test archiving/unarchiving a checklist"""
    print_step(20, "TOGGLE CHECKLIST ARCHIVE STATUS")
    
    # Archive
    response = client.post(
        f"/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/{TEST_AREA_ID}/checklists/archive/{TEST_CHECKLIST_ID}/",
        data=json.dumps({'is_archived': True}),
        content_type='application/json'
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, f"Archive: {result.get('message', 'Unknown error')}")
    
    # Unarchive
    response = client.post(
        f"/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/{TEST_AREA_ID}/checklists/archive/{TEST_CHECKLIST_ID}/",
        data=json.dumps({'is_archived': False}),
        content_type='application/json'
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, f"Unarchive: {result.get('message', 'Unknown error')}")
    return success

# ============================================
# CLEANUP - DELETE ALL TEST DATA
# ============================================

def test_checklist_delete():
    """Test deleting checklist"""
    print_step(21, "DELETE CHECKLIST")
    
    response = client.post(
        f"/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/{TEST_AREA_ID}/checklists/delete/{TEST_CHECKLIST_ID}/"
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, result.get('message', 'Unknown error'))
    return success

def test_module_delete():
    """Test deleting area"""
    print_step(22, "DELETE AREA")
    
    response = client.post(
        f"/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/delete/{TEST_AREA_ID}/"
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, result.get('message', 'Unknown error'))
    return success

def test_type_delete():
    """Test deleting type"""
    print_step(23, "DELETE ACCREDITATION TYPE")
    
    response = client.post(
        f"/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/delete/{TEST_TYPE_ID}/"
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, result.get('message', 'Unknown error'))
    return success

def test_program_delete():
    """Test deleting program"""
    print_step(24, "DELETE PROGRAM")
    
    response = client.post(
        f"/dashboard/settings/departments/{DEPT_ID}/programs/delete/{TEST_PROG_CODE}/"
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, result.get('message', 'Unknown error'))
    return success

# ============================================
# MAIN TEST RUNNER
# ============================================

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("COMPREHENSIVE CRUD OPERATIONS TEST")
    print("Testing Programs, Types, Areas, and Checklists")
    print("="*80)
    
    # Login
    if not login():
        print("\n❌ LOGIN FAILED - Cannot continue with tests")
        return
    
    # Program tests
    test_program_add()
    test_program_get()
    test_program_edit()
    test_program_toggle_active()
    test_program_archive()
    
    # Type tests
    test_type_add()
    test_type_get()
    test_type_edit()
    test_type_toggle_active()
    test_type_archive()
    
    # Area tests
    test_module_add()
    test_module_get()
    test_module_edit()
    test_module_toggle_active()
    test_module_archive()
    
    # Checklist tests
    test_checklist_add()
    test_checklist_get()
    test_checklist_edit()
    test_checklist_toggle_active()
    test_checklist_archive()
    
    # Cleanup - delete in reverse order
    test_checklist_delete()
    test_module_delete()
    test_type_delete()
    test_program_delete()
    
    print("\n" + "="*80)
    print("✅ ALL TESTS COMPLETED!")
    print("="*80 + "\n")

if __name__ == '__main__':
    main()


def test_program_add():
    """Test adding a program"""
    global TEST_PROG_CODE
    print_step(1, "ADD PROGRAM")
    
    csrf_token = session.cookies.get('csrftoken')
    
    response = session.post(
        f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/add/",
        data={
            'code': TEST_PROG_CODE,
            'name': 'Test Program for CRUD Operations',
            'csrfmiddlewaretoken': csrf_token
        },
        headers={'Referer': f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/"}
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, result.get('message', 'Unknown error'))
    return success

def test_program_get():
    """Test getting program details"""
    print_step(2, "GET PROGRAM DETAILS")
    
    response = session.get(
        f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/get/{TEST_PROG_CODE}/"
    )
    
    result = response.json()
    success = result.get('success', False)
    if success:
        prog = result.get('program', {})
        print_result(success, f"Retrieved program: {prog.get('name')}")
    else:
        print_result(success, result.get('message', 'Unknown error'))
    return success

def test_program_edit():
    """Test editing a program"""
    print_step(3, "EDIT PROGRAM")
    
    csrf_token = session.cookies.get('csrftoken')
    
    response = session.post(
        f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/edit/{TEST_PROG_CODE}/",
        data={
            'name': 'Test Program for CRUD Operations (EDITED)',
            'csrfmiddlewaretoken': csrf_token
        },
        headers={'Referer': f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/"}
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, result.get('message', 'Unknown error'))
    return success

def test_program_toggle_active():
    """Test activating/deactivating a program"""
    print_step(4, "TOGGLE PROGRAM ACTIVE STATUS")
    
    csrf_token = session.cookies.get('csrftoken')
    
    # Deactivate
    response = session.post(
        f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/toggle-active/{TEST_PROG_CODE}/",
        json={'is_active': False},
        headers={
            'Referer': f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/",
            'X-CSRFToken': csrf_token
        }
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, f"Deactivate: {result.get('message', 'Unknown error')}")
    
    # Reactivate
    response = session.post(
        f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/toggle-active/{TEST_PROG_CODE}/",
        json={'is_active': True},
        headers={
            'Referer': f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/",
            'X-CSRFToken': csrf_token
        }
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, f"Reactivate: {result.get('message', 'Unknown error')}")
    return success

def test_program_archive():
    """Test archiving/unarchiving a program"""
    print_step(5, "TOGGLE PROGRAM ARCHIVE STATUS")
    
    csrf_token = session.cookies.get('csrftoken')
    
    # Archive
    response = session.post(
        f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/archive/{TEST_PROG_CODE}/",
        json={'is_archived': True},
        headers={
            'Referer': f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/",
            'X-CSRFToken': csrf_token
        }
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, f"Archive: {result.get('message', 'Unknown error')}")
    
    # Unarchive
    response = session.post(
        f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/archive/{TEST_PROG_CODE}/",
        json={'is_archived': False},
        headers={
            'Referer': f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/",
            'X-CSRFToken': csrf_token
        }
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, f"Unarchive: {result.get('message', 'Unknown error')}")
    return success

# ============================================
# ACCREDITATION TYPE CRUD TESTS
# ============================================

def test_type_add():
    """Test adding an accreditation type"""
    global TEST_TYPE_ID
    print_step(6, "ADD ACCREDITATION TYPE")
    
    csrf_token = session.cookies.get('csrftoken')
    
    response = session.post(
        f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/add/",
        data={
            'name': 'Test Accreditation Type',
            'csrfmiddlewaretoken': csrf_token
        },
        headers={'Referer': f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/"}
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, result.get('message', 'Unknown error'))
    
    # Get the type ID by fetching all types (we'll use the firebase_utils)
    if success:
        from accreditation.firebase_utils import query_documents
        types = query_documents('accreditation_types', [('program_id', '==', TEST_PROG_CODE)])
        for t in types:
            if t.get('name') == 'Test Accreditation Type':
                TEST_TYPE_ID = t.get('id')
                print(f"   Type ID: {TEST_TYPE_ID}")
                break
    
    return success

def test_type_get():
    """Test getting type details"""
    print_step(7, "GET ACCREDITATION TYPE DETAILS")
    
    response = session.get(
        f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/get/{TEST_TYPE_ID}/"
    )
    
    result = response.json()
    success = result.get('success', False)
    if success:
        type_data = result.get('type', {})
        print_result(success, f"Retrieved type: {type_data.get('name')}")
    else:
        print_result(success, result.get('message', 'Unknown error'))
    return success

def test_type_edit():
    """Test editing a type"""
    print_step(8, "EDIT ACCREDITATION TYPE")
    
    csrf_token = session.cookies.get('csrftoken')
    
    response = session.post(
        f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/edit/{TEST_TYPE_ID}/",
        data={
            'name': 'Test Accreditation Type (EDITED)',
            'csrfmiddlewaretoken': csrf_token
        },
        headers={'Referer': f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/"}
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, result.get('message', 'Unknown error'))
    return success

def test_type_toggle_active():
    """Test activating/deactivating a type"""
    print_step(9, "TOGGLE TYPE ACTIVE STATUS")
    
    csrf_token = session.cookies.get('csrftoken')
    
    # Deactivate
    response = session.post(
        f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/toggle-active/{TEST_TYPE_ID}/",
        json={'is_active': False},
        headers={
            'Referer': f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/",
            'X-CSRFToken': csrf_token
        }
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, f"Deactivate: {result.get('message', 'Unknown error')}")
    
    # Reactivate
    response = session.post(
        f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/toggle-active/{TEST_TYPE_ID}/",
        json={'is_active': True},
        headers={
            'Referer': f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/",
            'X-CSRFToken': csrf_token
        }
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, f"Reactivate: {result.get('message', 'Unknown error')}")
    return success

def test_type_archive():
    """Test archiving/unarchiving a type"""
    print_step(10, "TOGGLE TYPE ARCHIVE STATUS")
    
    csrf_token = session.cookies.get('csrftoken')
    
    # Archive
    response = session.post(
        f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/archive/{TEST_TYPE_ID}/",
        json={'is_archived': True},
        headers={
            'Referer': f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/",
            'X-CSRFToken': csrf_token
        }
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, f"Archive: {result.get('message', 'Unknown error')}")
    
    # Unarchive
    response = session.post(
        f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/archive/{TEST_TYPE_ID}/",
        json={'is_archived': False},
        headers={
            'Referer': f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/",
            'X-CSRFToken': csrf_token
        }
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, f"Unarchive: {result.get('message', 'Unknown error')}")
    return success

# ============================================
# AREA CRUD TESTS
# ============================================

def test_module_add():
    """Test adding a area"""
    global TEST_AREA_ID
    print_step(11, "ADD AREA")
    
    csrf_token = session.cookies.get('csrftoken')
    
    response = session.post(
        f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/add/",
        data={
            'code': 'TESTMOD001',
            'name': 'Test Area',
            'csrfmiddlewaretoken': csrf_token
        },
        headers={'Referer': f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/"}
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, result.get('message', 'Unknown error'))
    
    if success:
        TEST_AREA_ID = 'TESTMOD001'
        print(f"   Area ID: {TEST_AREA_ID}")
    
    return success

def test_module_get():
    """Test getting area details"""
    print_step(12, "GET AREA DETAILS")
    
    response = session.get(
        f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/get/{TEST_AREA_ID}/"
    )
    
    result = response.json()
    success = result.get('success', False)
    if success:
        area = result.get('area', {})
        print_result(success, f"Retrieved area: {area.get('name')}")
    else:
        print_result(success, result.get('message', 'Unknown error'))
    return success

def test_module_edit():
    """Test editing a area"""
    print_step(13, "EDIT AREA")
    
    csrf_token = session.cookies.get('csrftoken')
    
    response = session.post(
        f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/edit/{TEST_AREA_ID}/",
        data={
            'name': 'Test Area (EDITED)',
            'csrfmiddlewaretoken': csrf_token
        },
        headers={'Referer': f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/"}
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, result.get('message', 'Unknown error'))
    return success

def test_module_toggle_active():
    """Test activating/deactivating a area"""
    print_step(14, "TOGGLE AREA ACTIVE STATUS")
    
    csrf_token = session.cookies.get('csrftoken')
    
    # Deactivate
    response = session.post(
        f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/toggle-active/{TEST_AREA_ID}/",
        json={'is_active': False},
        headers={
            'Referer': f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/",
            'X-CSRFToken': csrf_token
        }
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, f"Deactivate: {result.get('message', 'Unknown error')}")
    
    # Reactivate
    response = session.post(
        f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/toggle-active/{TEST_AREA_ID}/",
        json={'is_active': True},
        headers={
            'Referer': f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/",
            'X-CSRFToken': csrf_token
        }
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, f"Reactivate: {result.get('message', 'Unknown error')}")
    return success

def test_module_archive():
    """Test archiving/unarchiving a area"""
    print_step(15, "TOGGLE AREA ARCHIVE STATUS")
    
    csrf_token = session.cookies.get('csrftoken')
    
    # Archive
    response = session.post(
        f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/archive/{TEST_AREA_ID}/",
        json={'is_archived': True},
        headers={
            'Referer': f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/",
            'X-CSRFToken': csrf_token
        }
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, f"Archive: {result.get('message', 'Unknown error')}")
    
    # Unarchive
    response = session.post(
        f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/archive/{TEST_AREA_ID}/",
        json={'is_archived': False},
        headers={
            'Referer': f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/",
            'X-CSRFToken': csrf_token
        }
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, f"Unarchive: {result.get('message', 'Unknown error')}")
    return success

# ============================================
# CHECKLIST CRUD TESTS
# ============================================

def test_checklist_add():
    """Test adding a checklist"""
    global TEST_CHECKLIST_ID
    print_step(16, "ADD CHECKLIST")
    
    csrf_token = session.cookies.get('csrftoken')
    
    response = session.post(
        f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/{TEST_AREA_ID}/checklists/add/",
        data={
            'code': 'TESTCHK001',
            'name': 'Test Checklist',
            'csrfmiddlewaretoken': csrf_token
        },
        headers={'Referer': f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/{TEST_AREA_ID}/checklists/"}
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, result.get('message', 'Unknown error'))
    
    if success:
        TEST_CHECKLIST_ID = 'TESTCHK001'
        print(f"   Checklist ID: {TEST_CHECKLIST_ID}")
    
    return success

def test_checklist_get():
    """Test getting checklist details"""
    print_step(17, "GET CHECKLIST DETAILS")
    
    response = session.get(
        f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/{TEST_AREA_ID}/checklists/get/{TEST_CHECKLIST_ID}/"
    )
    
    result = response.json()
    success = result.get('success', False)
    if success:
        checklist = result.get('checklist', {})
        print_result(success, f"Retrieved checklist: {checklist.get('name')}")
    else:
        print_result(success, result.get('message', 'Unknown error'))
    return success

def test_checklist_edit():
    """Test editing a checklist"""
    print_step(18, "EDIT CHECKLIST")
    
    csrf_token = session.cookies.get('csrftoken')
    
    response = session.post(
        f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/{TEST_AREA_ID}/checklists/edit/{TEST_CHECKLIST_ID}/",
        data={
            'name': 'Test Checklist (EDITED)',
            'csrfmiddlewaretoken': csrf_token
        },
        headers={'Referer': f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/{TEST_AREA_ID}/checklists/"}
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, result.get('message', 'Unknown error'))
    return success

def test_checklist_toggle_active():
    """Test activating/deactivating a checklist"""
    print_step(19, "TOGGLE CHECKLIST ACTIVE STATUS")
    
    csrf_token = session.cookies.get('csrftoken')
    
    # Deactivate
    response = session.post(
        f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/{TEST_AREA_ID}/checklists/toggle-active/{TEST_CHECKLIST_ID}/",
        json={'is_active': False},
        headers={
            'Referer': f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/{TEST_AREA_ID}/checklists/",
            'X-CSRFToken': csrf_token
        }
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, f"Deactivate: {result.get('message', 'Unknown error')}")
    
    # Reactivate
    response = session.post(
        f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/{TEST_AREA_ID}/checklists/toggle-active/{TEST_CHECKLIST_ID}/",
        json={'is_active': True},
        headers={
            'Referer': f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/{TEST_AREA_ID}/checklists/",
            'X-CSRFToken': csrf_token
        }
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, f"Reactivate: {result.get('message', 'Unknown error')}")
    return success

def test_checklist_archive():
    """Test archiving/unarchiving a checklist"""
    print_step(20, "TOGGLE CHECKLIST ARCHIVE STATUS")
    
    csrf_token = session.cookies.get('csrftoken')
    
    # Archive
    response = session.post(
        f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/{TEST_AREA_ID}/checklists/archive/{TEST_CHECKLIST_ID}/",
        json={'is_archived': True},
        headers={
            'Referer': f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/{TEST_AREA_ID}/checklists/",
            'X-CSRFToken': csrf_token
        }
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, f"Archive: {result.get('message', 'Unknown error')}")
    
    # Unarchive
    response = session.post(
        f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/{TEST_AREA_ID}/checklists/archive/{TEST_CHECKLIST_ID}/",
        json={'is_archived': False},
        headers={
            'Referer': f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/{TEST_AREA_ID}/checklists/",
            'X-CSRFToken': csrf_token
        }
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, f"Unarchive: {result.get('message', 'Unknown error')}")
    return success

# ============================================
# CLEANUP - DELETE ALL TEST DATA
# ============================================

def test_checklist_delete():
    """Test deleting checklist"""
    print_step(21, "DELETE CHECKLIST")
    
    csrf_token = session.cookies.get('csrftoken')
    
    response = session.post(
        f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/{TEST_AREA_ID}/checklists/delete/{TEST_CHECKLIST_ID}/",
        headers={
            'Referer': f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/{TEST_AREA_ID}/checklists/",
            'X-CSRFToken': csrf_token
        }
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, result.get('message', 'Unknown error'))
    return success

def test_module_delete():
    """Test deleting area"""
    print_step(22, "DELETE AREA")
    
    csrf_token = session.cookies.get('csrftoken')
    
    response = session.post(
        f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/delete/{TEST_AREA_ID}/",
        headers={
            'Referer': f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/{TEST_TYPE_ID}/areas/",
            'X-CSRFToken': csrf_token
        }
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, result.get('message', 'Unknown error'))
    return success

def test_type_delete():
    """Test deleting type"""
    print_step(23, "DELETE ACCREDITATION TYPE")
    
    csrf_token = session.cookies.get('csrftoken')
    
    response = session.post(
        f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/delete/{TEST_TYPE_ID}/",
        headers={
            'Referer': f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/{TEST_PROG_CODE}/types/",
            'X-CSRFToken': csrf_token
        }
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, result.get('message', 'Unknown error'))
    return success

def test_program_delete():
    """Test deleting program"""
    print_step(24, "DELETE PROGRAM")
    
    csrf_token = session.cookies.get('csrftoken')
    
    response = session.post(
        f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/delete/{TEST_PROG_CODE}/",
        headers={
            'Referer': f"{BASE_URL}/dashboard/settings/departments/{DEPT_ID}/programs/",
            'X-CSRFToken': csrf_token
        }
    )
    
    result = response.json()
    success = result.get('success', False)
    print_result(success, result.get('message', 'Unknown error'))
    return success

# ============================================
# MAIN TEST RUNNER
# ============================================

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("COMPREHENSIVE CRUD OPERATIONS TEST")
    print("Testing Programs, Types, Areas, and Checklists")
    print("="*80)
    
    # Login
    if not login():
        print("\n❌ LOGIN FAILED - Cannot continue with tests")
        return
    
    # Program tests
    test_program_add()
    test_program_get()
    test_program_edit()
    test_program_toggle_active()
    test_program_archive()
    
    # Type tests
    test_type_add()
    test_type_get()
    test_type_edit()
    test_type_toggle_active()
    test_type_archive()
    
    # Area tests
    test_module_add()
    test_module_get()
    test_module_edit()
    test_module_toggle_active()
    test_module_archive()
    
    # Checklist tests
    test_checklist_add()
    test_checklist_get()
    test_checklist_edit()
    test_checklist_toggle_active()
    test_checklist_archive()
    
    # Cleanup - delete in reverse order
    test_checklist_delete()
    test_module_delete()
    test_type_delete()
    test_program_delete()
    
    print("\n" + "="*80)
    print("✅ ALL TESTS COMPLETED!")
    print("="*80 + "\n")

if __name__ == '__main__':
    main()
