"""
Automated Log Removal Script
Removes all debugging print statements and console logs from the entire system
while preserving functionality.
"""

import os
import re
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Directories to scan
SCAN_DIRS = [
    BASE_DIR / 'accreditation',
    BASE_DIR / 'templates',
    BASE_DIR / 'firebase_app'
]

# Files to scan at root level
ROOT_FILES = [
    'add_document_modal.py',
    'add_modal_to_pages.py',
    'check_data.py',
    'check_lock_status.py',
    'create_my_accreditation_templates.py',
    'fix_modal_files.py',
    'list_users.py',
    'test_*.py',
    'update_*.py',
]

# Counters
stats = {
    'files_processed': 0,
    'files_modified': 0,
    'python_prints_removed': 0,
    'console_logs_removed': 0,
    'errors': 0
}

def remove_python_debug_prints(content):
    """Remove debug print statements from Python files"""
    lines = content.split('\n')
    new_lines = []
    removed_count = 0
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Skip completely empty lines
        if not stripped:
            new_lines.append(line)
            i += 1
            continue
            
        # Check if line is a debug print statement
        is_debug_print = False
        
        # Patterns for debug prints
        debug_patterns = [
            r'^\s*print\s*\(',  # Any print statement
            r'^\s*print\s*\(f["\']',  # f-string prints
            r'^\s*print\s*\(["\']DEBUG',  # DEBUG prefix prints
            r'^\s*print\s*\(["\']\[',  # [TAG] prefix prints
            r'^\s*print\s*\(["\']={3,}',  # Separator lines (===)
            r'^\s*print\s*\(["\']-{3,}',  # Separator lines (---)
            r'^\s*print\s*\(traceback\.format_exc',  # Traceback prints
        ]
        
        for pattern in debug_patterns:
            if re.match(pattern, stripped):
                is_debug_print = True
                break
        
        # Special handling for error handling blocks - keep essential error info
        # But remove the decorative prints
        if is_debug_print:
            # Check if it's a separator or decorative print
            if any(char * 3 in stripped for char in ['=', '-', '*']):
                removed_count += 1
                i += 1
                continue
            
            # Check if it's a debug print with DEBUG, [TAG], or similar markers
            if any(marker in stripped.upper() for marker in ['DEBUG', '[OTP_VERIFY]', '[NOTIFICATION', '[STATUS', '[CLOUDCONVERT]']):
                removed_count += 1
                i += 1
                continue
            
            # Check if it's a traceback print
            if 'traceback.format_exc' in stripped:
                removed_count += 1
                i += 1
                continue
            
            # For other prints, check context - if it's in an except block, might want to keep
            # But for now, remove all prints as requested
            removed_count += 1
            i += 1
            continue
        
        # Keep the line
        new_lines.append(line)
        i += 1
    
    return '\n'.join(new_lines), removed_count


def remove_javascript_console_logs(content):
    """Remove console.log statements from JavaScript/HTML files"""
    removed_count = 0
    
    # Pattern to match console.log, console.debug, console.warn, console.error, console.info
    # Including single line and potential multi-line statements
    patterns = [
        # Single line console statements
        (r'^\s*console\.(log|debug|warn|error|info)\([^)]*\);\s*$', ''),
        # Console statements with // Debug logging comment
        (r'^\s*console\.(log|debug|warn|error|info)\([^)]*\);\s*//.*$', ''),
        # Multi-line scenario - this is tricky, we'll handle line by line
    ]
    
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        original_line = line
        stripped = line.strip()
        
        # Check if line contains console statement
        if re.search(r'console\.(log|debug|warn|error|info)\s*\(', stripped):
            # Remove the entire line
            removed_count += 1
            continue
        
        # Keep the line
        new_lines.append(line)
    
    return '\n'.join(new_lines), removed_count


def process_file(file_path):
    """Process a single file to remove logs"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        removed_prints = 0
        removed_console = 0
        
        # Determine file type and process accordingly
        if file_path.suffix == '.py':
            content, removed_prints = remove_python_debug_prints(content)
        elif file_path.suffix in ['.html', '.js']:
            content, removed_console = remove_javascript_console_logs(content)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            stats['files_modified'] += 1
            stats['python_prints_removed'] += removed_prints
            stats['console_logs_removed'] += removed_console
            
            print(f"✓ Modified: {file_path.relative_to(BASE_DIR)}")
            if removed_prints > 0:
                print(f"  - Removed {removed_prints} print statement(s)")
            if removed_console > 0:
                print(f"  - Removed {removed_console} console log(s)")
        
        stats['files_processed'] += 1
        
    except Exception as e:
        stats['errors'] += 1
        print(f"✗ Error processing {file_path}: {e}")


def scan_directory(directory):
    """Recursively scan directory for files"""
    if not directory.exists():
        print(f"⚠ Directory not found: {directory}")
        return
    
    # Python files
    for py_file in directory.rglob('*.py'):
        # Skip migration files, __init__ files, and this script itself
        if 'migrations' in str(py_file) or py_file.name == '__init__.py' or py_file.name == 'remove_all_logs.py':
            continue
        process_file(py_file)
    
    # HTML and JS files
    for html_file in directory.rglob('*.html'):
        process_file(html_file)
    
    for js_file in directory.rglob('*.js'):
        if 'node_modules' not in str(js_file) and 'venv' not in str(js_file):
            process_file(js_file)


def main():
    """Main execution function"""
    print("=" * 80)
    print("REMOVING ALL DEBUG LOGS FROM THE SYSTEM")
    print("=" * 80)
    print()
    
    # Process root level test and utility files
    print("📁 Processing root level files...")
    for pattern in ROOT_FILES:
        for file_path in BASE_DIR.glob(pattern):
            if file_path.is_file():
                process_file(file_path)
    
    # Process directories
    for scan_dir in SCAN_DIRS:
        if scan_dir.exists():
            print(f"\n📁 Processing directory: {scan_dir.name}/")
            scan_directory(scan_dir)
    
    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Files Processed: {stats['files_processed']}")
    print(f"Files Modified: {stats['files_modified']}")
    print(f"Python print() statements removed: {stats['python_prints_removed']}")
    print(f"JavaScript console logs removed: {stats['console_logs_removed']}")
    print(f"Total logs removed: {stats['python_prints_removed'] + stats['console_logs_removed']}")
    print(f"Errors: {stats['errors']}")
    print("=" * 80)
    print()
    print("✅ LOG REMOVAL COMPLETE!")
    print()
    print("⚠ IMPORTANT: Please test your application thoroughly to ensure")
    print("   that removing these logs hasn't affected any functionality.")
    print()


if __name__ == '__main__':
    main()
