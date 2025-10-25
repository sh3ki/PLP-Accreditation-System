"""
Test script for Enhanced Document Header Validator
Tests the header validation functionality with strict formatting checks
"""

import os
import sys

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'accreditation.settings')

import django
django.setup()

from accreditation.document_validator import get_validator


def test_validator():
    """Test the enhanced document validator"""
    print("=" * 70)
    print("ENHANCED DOCUMENT HEADER VALIDATOR TEST")
    print("WITH STRICT FORMATTING VALIDATION")
    print("=" * 70)
    
    try:
        # Get validator instance
        validator = get_validator()
        print("✓ Enhanced validator initialized successfully")
        
        # Display template header with full formatting details
        print("\n" + "=" * 70)
        print("TEMPLATE HEADER STRUCTURE (WITH FORMATTING)")
        print("=" * 70)
        template_preview = validator.get_template_header_preview()
        print(template_preview)
        
        # Test with the template itself (should pass)
        print("\n" + "=" * 70)
        print("TEST 1: Validating Template.docx against itself")
        print("=" * 70)
        
        template_path = validator.TEMPLATE_PATH
        is_valid, error_msg = validator.validate_document(template_path)
        
        if is_valid:
            print("✓ PASS: Template validates against itself")
            print("  All formatting, fonts, sizes, and images match!")
        else:
            print(f"✗ FAIL: {error_msg}")
        
        print("\n" + "=" * 70)
        print("ENHANCED VALIDATOR TEST COMPLETED")
        print("=" * 70)
        print("\n✨ The enhanced validator is ready to use!")
        print("\n📋 What will be validated:")
        print("   ✓ Header text (CASE-SENSITIVE)")
        print("   ✓ Font families (e.g., Arial, Times New Roman)")
        print("   ✓ Font sizes (exact point sizes)")
        print("   ✓ Text formatting (bold, italic, underline)")
        print("   ✓ Text alignment (left, center, right)")
        print("   ✓ Images/logos in header")
        print("   ✓ Tables in header")
        print("\n⚠️  Documents must match Template.docx EXACTLY!")
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_validator()
