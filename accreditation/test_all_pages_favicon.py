"""
Test script to verify favicon is present in ALL pages
Checks both dashboard pages and auth pages
"""
import os

def check_favicon_in_file(file_path, file_name):
    """Check if a file has favicon link tags"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        has_favicon = 'link rel="icon"' in content or 'link rel="shortcut icon"' in content
        has_logo_url_check = '{% if logo_url %}' in content
        uses_dynamic_logo = 'href="{{ logo_url }}"' in content
        has_fallback = 'PLP_LOGO_ujtdgd.png' in content
        
        return {
            'file': file_name,
            'has_favicon': has_favicon,
            'dynamic': has_logo_url_check and uses_dynamic_logo,
            'fallback': has_fallback,
            'status': '✅' if has_favicon else '❌'
        }
    except Exception as e:
        return {
            'file': file_name,
            'has_favicon': False,
            'dynamic': False,
            'fallback': False,
            'status': '❌',
            'error': str(e)
        }

def main():
    print("\n" + "="*70)
    print("FAVICON PRESENCE TEST - ALL PAGES")
    print("="*70)
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    templates_path = os.path.join(base_path, 'templates')
    
    # Files to check
    files_to_check = [
        # Base template (extends to all dashboard pages)
        ('dashboard_base.html', templates_path),
        
        # Auth pages (standalone)
        ('auth/login.html', templates_path),
        ('auth/verify_otp.html', templates_path),
        ('auth/forgot_password.html', templates_path),
        ('auth/forgot_password_verify_otp.html', templates_path),
        ('auth/reset_password.html', templates_path),
    ]
    
    results = []
    
    print("\n📄 Checking Templates:")
    print("-" * 70)
    
    for file_rel_path, base in files_to_check:
        file_path = os.path.join(base, file_rel_path)
        result = check_favicon_in_file(file_path, file_rel_path)
        results.append(result)
        
        print(f"\n{result['status']} {result['file']}")
        print(f"   Favicon Present: {'✅' if result['has_favicon'] else '❌'}")
        print(f"   Dynamic Logo: {'✅' if result['dynamic'] else '❌'}")
        print(f"   Fallback Logo: {'✅' if result['fallback'] else '❌'}")
        
        if 'error' in result:
            print(f"   Error: {result['error']}")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    total = len(results)
    passed = sum(1 for r in results if r['has_favicon'])
    dynamic = sum(1 for r in results if r['dynamic'])
    fallback = sum(1 for r in results if r['fallback'])
    
    print(f"\nTotal Pages Checked: {total}")
    print(f"✅ With Favicon: {passed}/{total}")
    print(f"✅ With Dynamic Logo: {dynamic}/{total}")
    print(f"✅ With Fallback: {fallback}/{total}")
    
    if passed == total and dynamic == total and fallback == total:
        print("\n" + "🎉 " * 10)
        print("✅ ALL PAGES HAVE FAVICON!")
        print("🎉 " * 10)
        print("\nFavicon will appear on:")
        print("  ✅ Login page")
        print("  ✅ OTP verification page")
        print("  ✅ Forgot password page")
        print("  ✅ Forgot password OTP page")
        print("  ✅ Reset password page")
        print("  ✅ All dashboard pages (via dashboard_base.html)")
        print("\nThe favicon is PERMANENT across ALL pages!")
    else:
        print("\n❌ SOME PAGES MISSING FAVICON")
        print("\nPages without favicon:")
        for r in results:
            if not r['has_favicon']:
                print(f"  ❌ {r['file']}")
    
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
