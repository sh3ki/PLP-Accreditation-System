"""
Test script to verify dashboard data is loading correctly from Firestore
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'accreditation.settings')
django.setup()

from accreditation.firebase_utils import get_all_documents
from accreditation.dashboard_views import (
    get_qa_head_dashboard_data,
    get_qa_admin_dashboard_data,
    get_department_dashboard_data
)

def test_database_collections():
    """Test if all required collections have data"""
    print("\n" + "="*80)
    print("TESTING DATABASE COLLECTIONS")
    print("="*80)
    
    collections = ['users', 'documents', 'departments', 'programs', 'areas', 'checklists', 'audit_logs']
    
    for collection in collections:
        try:
            data = get_all_documents(collection)
            print(f"✓ {collection:20} : {len(data):3} documents")
        except Exception as e:
            print(f"✗ {collection:20} : ERROR - {str(e)}")

def test_qa_head_dashboard():
    """Test QA Head dashboard data"""
    print("\n" + "="*80)
    print("TESTING QA HEAD DASHBOARD DATA")
    print("="*80)
    
    user = {'id': 'test', 'email': 'test@plp.edu.ph', 'role': 'qa_head'}
    
    try:
        data = get_qa_head_dashboard_data(user)
        stats = data.get('stats', {})
        
        print(f"\nStatistics:")
        print(f"  Total Users:         {stats.get('total_users', 0)}")
        print(f"  Total Documents:     {stats.get('total_documents', 0)}")
        print(f"  Total Programs:      {stats.get('total_programs', 0)}")
        print(f"  Pending Approvals:   {stats.get('pending_approvals', 0)}")
        print(f"  Active Departments:  {stats.get('active_departments', 0)}")
        print(f"  Completion Rate:     {stats.get('completion_rate', 0)}%")
        
        print(f"\nRecent Activities:     {len(data.get('recent_activities', []))}")
        print(f"Department Progress:   {len(data.get('department_progress', []))}")
        
        print("\n✓ QA Head dashboard data loaded successfully!")
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

def test_qa_admin_dashboard():
    """Test QA Admin dashboard data"""
    print("\n" + "="*80)
    print("TESTING QA ADMIN DASHBOARD DATA")
    print("="*80)
    
    user = {'id': 'test', 'email': 'test@plp.edu.ph', 'role': 'qa_admin'}
    
    try:
        data = get_qa_admin_dashboard_data(user)
        stats = data.get('stats', {})
        
        print(f"\nStatistics:")
        print(f"  Total Documents:     {stats.get('total_documents', 0)}")
        print(f"  Pending Reviews:     {stats.get('pending_reviews', 0)}")
        print(f"  Approved Documents:  {stats.get('approved_documents', 0)}")
        print(f"  Rejected Documents:  {stats.get('rejected_documents', 0)}")
        print(f"  Active Programs:     {stats.get('active_programs', 0)}")
        print(f"  Completion Rate:     {stats.get('completion_rate', 0)}%")
        
        print(f"\nRecent Documents:      {len(data.get('recent_documents', []))}")
        print(f"Area Progress:         {len(data.get('area_progress', []))}")
        
        print("\n✓ QA Admin dashboard data loaded successfully!")
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

def test_department_dashboard():
    """Test Department User dashboard data"""
    print("\n" + "="*80)
    print("TESTING DEPARTMENT USER DASHBOARD DATA")
    print("="*80)
    
    # Get a real department ID from database
    departments = get_all_documents('departments')
    if departments:
        dept_id = departments[0].get('id') or departments[0].get('code')
        print(f"Using department ID: {dept_id}")
    else:
        print("No departments found in database")
        return
    
    user = {
        'id': 'test', 
        'email': 'test@plp.edu.ph', 
        'role': 'department_user',
        'department_id': dept_id
    }
    
    try:
        data = get_department_dashboard_data(user)
        stats = data.get('stats', {})
        
        print(f"\nStatistics:")
        print(f"  My Documents:        {stats.get('my_documents', 0)}")
        print(f"  Pending Uploads:     {stats.get('pending_uploads', 0)}")
        print(f"  Approved:            {stats.get('approved', 0)}")
        print(f"  Needs Revision:      {stats.get('needs_revision', 0)}")
        print(f"  Completion %:        {stats.get('completion_percentage', 0)}%")
        print(f"  Days to Deadline:    {stats.get('days_to_deadline', 'N/A')}")
        
        print(f"\nArea Progress:         {len(data.get('area_progress', []))}")
        print(f"Recent Activities:     {len(data.get('recent_activities', []))}")
        
        print("\n✓ Department dashboard data loaded successfully!")
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("\nDASHBOARD DATA VERIFICATION TEST")
    print("Testing all dashboard data functions...\n")
    
    test_database_collections()
    test_qa_head_dashboard()
    test_qa_admin_dashboard()
    test_department_dashboard()
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")
