"""
VERIFICATION REPORT - LOG REMOVAL
==================================

This script verifies that all debugging logs have been successfully removed.
Run this to confirm the cleanup was successful.
"""

import os
import re
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

def check_file_for_logs(file_path):
    """Check if file contains any debugging logs"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        
        if file_path.suffix == '.py':
            # Check for debug print statements
            debug_patterns = [
                r'print\s*\(f?["\']DEBUG',
                r'print\s*\(["\']={3,}',
                r'print\s*\(["\']-{3,}',
                r'print\s*\(["\'][\\[]',
                r'print\s*\(traceback\.format_exc',
            ]
            
            for pattern in debug_patterns:
                matches = re.findall(pattern, content, re.MULTILINE)
                if matches:
                    issues.append(f"Found {len(matches)} debug print(s) matching: {pattern}")
        
        elif file_path.suffix in ['.html', '.js']:
            # Check for console logs
            console_pattern = r'console\.(log|debug|warn|error|info)\s*\('
            matches = re.findall(console_pattern, content, re.MULTILINE)
            if matches:
                issues.append(f"Found {len(matches)} console log(s)")
        
        return issues
    except Exception as e:
        return [f"Error reading file: {e}"]


def main():
    """Main verification function"""
    print("=" * 80)
    print("VERIFICATION REPORT - DEBUGGING LOG REMOVAL")
    print("=" * 80)
    print()
    
    # Key files to verify
    key_files = [
        'accreditation/dashboard_views.py',
        'accreditation/auth_views.py',
        'accreditation/firebase_utils.py',
        'templates/components/document_upload_modal.html',
        'templates/dashboard/checklist_documents.html',
        'templates/auth/verify_otp.html',
    ]
    
    all_clean = True
    
    for file_rel in key_files:
        file_path = BASE_DIR / file_rel
        if file_path.exists():
            issues = check_file_for_logs(file_path)
            if issues:
                all_clean = False
                print(f"❌ {file_rel}")
                for issue in issues:
                    print(f"   - {issue}")
            else:
                print(f"✅ {file_rel}")
        else:
            print(f"⚠  {file_rel} - NOT FOUND")
    
    print()
    print("=" * 80)
    
    if all_clean:
        print("✅ VERIFICATION PASSED!")
        print("All key files are clean - no debugging logs found.")
    else:
        print("❌ VERIFICATION FAILED!")
        print("Some files still contain debugging logs.")
    
    print("=" * 80)


if __name__ == '__main__':
    main()
