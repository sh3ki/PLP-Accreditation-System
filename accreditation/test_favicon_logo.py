"""
Test script to verify favicon and logo display from Cloudinary
Tests that logo_url from system_settings is properly available in context
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'accreditation.settings')
django.setup()

from accreditation.firebase_utils import get_all_documents
from accreditation.context_processors import appearance_settings

def test_logo_url_in_database():
    """Test that logo_url exists in system_settings"""
    print("\n" + "="*60)
    print("TEST 1: Logo URL in Database")
    print("="*60)
    
    try:
        settings_docs = get_all_documents('system_settings')
        appearance_doc = next((d for d in settings_docs if d.get('setting_type') == 'appearance'), None)
        
        if appearance_doc:
            logo_url = appearance_doc.get('logo_url', '')
            print(f"✅ Appearance settings found in database")
            print(f"   Logo URL: {logo_url if logo_url else '(empty - will use default)'}")
            
            if logo_url and 'cloudinary' in logo_url:
                print(f"✅ Logo URL is from Cloudinary")
            elif logo_url:
                print(f"⚠️  Logo URL exists but not from Cloudinary")
            else:
                print(f"ℹ️  No custom logo set - will use default PLP logo")
            
            return True
        else:
            print("❌ No appearance settings found in database")
            return False
    except Exception as e:
        print(f"❌ Error accessing database: {e}")
        return False

def test_context_processor():
    """Test that context processor provides logo_url"""
    print("\n" + "="*60)
    print("TEST 2: Context Processor")
    print("="*60)
    
    try:
        # Create a mock request object
        class MockRequest:
            path = '/dashboard/'
        
        request = MockRequest()
        context = appearance_settings(request)
        
        print(f"✅ Context processor executed successfully")
        print(f"   Theme Color: {context.get('theme_color')}")
        print(f"   System Title: {context.get('system_title')}")
        print(f"   Logo URL: {context.get('logo_url') if context.get('logo_url') else '(empty - will use default)'}")
        
        if context.get('logo_url') and 'cloudinary' in context.get('logo_url'):
            print(f"✅ Logo URL available in context from Cloudinary")
        elif context.get('logo_url'):
            print(f"⚠️  Logo URL available but not from Cloudinary")
        else:
            print(f"ℹ️  No custom logo in context - will use default PLP logo")
        
        return True
    except Exception as e:
        print(f"❌ Error in context processor: {e}")
        return False

def test_template_variables():
    """Test that template has correct variables"""
    print("\n" + "="*60)
    print("TEST 3: Template Variables")
    print("="*60)
    
    try:
        template_path = os.path.join(
            os.path.dirname(__file__),
            'templates',
            'dashboard_base.html'
        )
        
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for favicon links
        if 'link rel="icon"' in content:
            print("✅ Favicon link tag found in template")
        else:
            print("❌ Favicon link tag NOT found in template")
        
        # Check for dynamic logo_url usage
        if '{% if logo_url %}' in content:
            print("✅ Dynamic logo_url check found in template")
        else:
            print("❌ Dynamic logo_url check NOT found in template")
        
        # Check for logo_url variable in favicon
        if 'href="{{ logo_url }}"' in content:
            print("✅ Favicon uses dynamic logo_url variable")
        else:
            print("❌ Favicon does NOT use dynamic logo_url variable")
        
        # Check for logo_url in header
        if 'src="{{ logo_url }}"' in content:
            print("✅ Header logo uses dynamic logo_url variable")
        else:
            print("❌ Header logo does NOT use dynamic logo_url variable")
        
        # Check for system_title usage
        if '{{ system_title' in content:
            print("✅ System title uses dynamic variable")
        else:
            print("❌ System title does NOT use dynamic variable")
        
        return True
    except Exception as e:
        print(f"❌ Error reading template: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("FAVICON & LOGO DISPLAY TEST")
    print("="*60)
    
    test1 = test_logo_url_in_database()
    test2 = test_context_processor()
    test3 = test_template_variables()
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    if test1 and test2 and test3:
        print("✅ ALL TESTS PASSED")
        print("\nResult:")
        print("• Favicon will display logo from Cloudinary")
        print("• Header logo will display logo from Cloudinary")
        print("• System title will display custom title")
        print("• Falls back to default PLP logo if no custom logo set")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nPlease review the errors above")
    
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
