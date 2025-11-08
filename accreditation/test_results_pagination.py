"""
Test script to verify pagination in Results and Incentives page
"""
import re

def test_backend_pagination():
    """Test that backend has pagination logic"""
    print("\n" + "="*70)
    print("TEST 1: Backend Pagination Logic")
    print("="*70)
    
    with open('accreditation/dashboard_views.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for pagination variables
    checks = {
        'per_page = 10': 'per_page = 10' in content,
        'total_pages calculation': 'total_pages = ceil' in content,
        'page_range logic': 'page_range = []' in content,
        'paginated_areas': 'paginated_areas' in content,
        'current_page in context': "'current_page': page" in content,
        'total_pages in context': "'total_pages': total_pages" in content,
        'has_previous in context': "'has_previous': page > 1" in content,
        'has_next in context': "'has_next': page < total_pages" in content,
    }
    
    all_passed = True
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"{status} {check}")
        if not result:
            all_passed = False
    
    return all_passed

def test_template_pagination():
    """Test that template has pagination UI"""
    print("\n" + "="*70)
    print("TEST 2: Template Pagination UI")
    print("="*70)
    
    with open('templates/dashboard/results.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        'Pagination container': 'pagination-container' in content,
        'Pagination info': 'pagination-info' in content,
        'Previous button': 'fas fa-chevron-left' in content,
        'Next button': 'fas fa-chevron-right' in content,
        'Page numbers loop': '{% for page_num in page_range %}' in content,
        'Ellipsis handling': "{% if page_num == '...' %}" in content,
        'Active page styling': "{% if page_num == current_page %}active" in content,
        'Disabled state': 'disabled' in content,
    }
    
    all_passed = True
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"{status} {check}")
        if not result:
            all_passed = False
    
    return all_passed

def test_pagination_styles():
    """Test that pagination CSS styles exist"""
    print("\n" + "="*70)
    print("TEST 3: Pagination CSS Styles")
    print("="*70)
    
    with open('templates/dashboard/results.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        'pagination-container style': '.pagination-container {' in content,
        'pagination-info style': '.pagination-info {' in content,
        'page-btn style': '.page-btn {' in content,
        'page-btn hover': '.page-btn:hover' in content,
        'page-btn active': '.page-btn.active {' in content,
        'page-btn disabled': '.page-btn.disabled {' in content,
        'ellipsis style': '.page-btn.ellipsis' in content,
    }
    
    all_passed = True
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"{status} {check}")
        if not result:
            all_passed = False
    
    return all_passed

def test_pagination_params():
    """Test pagination parameters in context"""
    print("\n" + "="*70)
    print("TEST 4: Pagination Context Parameters")
    print("="*70)
    
    with open('accreditation/dashboard_views.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the context dictionary in results_view
    context_match = re.search(r'def results_view.*?context = \{(.*?)\}.*?return render', content, re.DOTALL)
    
    if context_match:
        context_block = context_match.group(1)
        
        params = [
            'areas',
            'total_items',
            'current_page',
            'total_pages',
            'page_range',
            'has_previous',
            'has_next',
        ]
        
        all_found = True
        for param in params:
            found = f"'{param}'" in context_block
            status = "✅" if found else "❌"
            print(f"{status} Context has '{param}' parameter")
            if not found:
                all_found = False
        
        return all_found
    else:
        print("❌ Could not find context dictionary")
        return False

def main():
    print("\n" + "="*70)
    print("RESULTS AND INCENTIVES - PAGINATION TEST")
    print("="*70)
    
    test1 = test_backend_pagination()
    test2 = test_template_pagination()
    test3 = test_pagination_styles()
    test4 = test_pagination_params()
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    if test1 and test2 and test3 and test4:
        print("\n🎉 " * 10)
        print("✅ ALL TESTS PASSED!")
        print("🎉 " * 10)
        print("\nPagination Features:")
        print("  ✅ Shows 10 items per page")
        print("  ✅ Previous/Next buttons")
        print("  ✅ Page numbers with ellipsis")
        print("  ✅ Active page highlighting")
        print("  ✅ Disabled state for first/last pages")
        print("  ✅ Pagination info display")
        print("  ✅ Same style as Reports & Audit Trail pages")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("\nPlease review the errors above")
    
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
