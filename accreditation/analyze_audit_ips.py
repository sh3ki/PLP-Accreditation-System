"""
Script to analyze all log_audit() calls and identify which ones are missing IP address parameter
"""
import re
import os

def analyze_file(filepath):
    """Analyze a Python file for log_audit calls"""
    results = {
        'with_ip': [],
        'without_ip': []
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Find all log_audit calls
        i = 0
        while i < len(lines):
            line = lines[i]
            if 'log_audit(' in line:
                # Get the full log_audit call (might span multiple lines)
                full_call = line
                line_num = i + 1
                
                # Check if it spans multiple lines
                open_parens = line.count('(')
                close_parens = line.count(')')
                j = i + 1
                
                while open_parens > close_parens and j < len(lines):
                    full_call += '\n' + lines[j]
                    open_parens += lines[j].count('(')
                    close_parens += lines[j].count(')')
                    j += 1
                
                # Check if IP is present
                has_ip = 'ip=' in full_call or 'ip =' in full_call
                
                # Clean up the call for display
                display_call = full_call.strip()
                if len(display_call) > 150:
                    display_call = display_call[:150] + '...'
                
                entry = {
                    'line': line_num,
                    'call': display_call
                }
                
                if has_ip:
                    results['with_ip'].append(entry)
                else:
                    results['without_ip'].append(entry)
                
                i = j
            else:
                i += 1
                
    except Exception as e:
        print(f"Error analyzing {filepath}: {e}")
    
    return results

def main():
    # Files to analyze
    files_to_check = [
        'accreditation/dashboard_views.py',
        'accreditation/auth_views.py',
        'accreditation/firebase_views.py'
    ]
    
    print("=" * 80)
    print("AUDIT LOG IP ADDRESS ANALYSIS")
    print("=" * 80)
    print()
    
    total_with_ip = 0
    total_without_ip = 0
    
    for rel_path in files_to_check:
        filepath = os.path.join(os.path.dirname(__file__), rel_path)
        if not os.path.exists(filepath):
            print(f"⚠️  File not found: {rel_path}")
            continue
        
        print(f"\n📄 Analyzing: {rel_path}")
        print("-" * 80)
        
        results = analyze_file(filepath)
        
        with_ip_count = len(results['with_ip'])
        without_ip_count = len(results['without_ip'])
        
        total_with_ip += with_ip_count
        total_without_ip += without_ip_count
        
        print(f"\n✅ Calls WITH IP address: {with_ip_count}")
        if results['with_ip']:
            for entry in results['with_ip']:
                print(f"   Line {entry['line']}: {entry['call']}")
        
        print(f"\n❌ Calls WITHOUT IP address: {without_ip_count}")
        if results['without_ip']:
            for entry in results['without_ip']:
                print(f"   Line {entry['line']}: {entry['call']}")
        
        print()
    
    print("\n" + "=" * 80)
    print(f"SUMMARY")
    print("=" * 80)
    print(f"Total audit logs WITH IP address: {total_with_ip}")
    print(f"Total audit logs WITHOUT IP address: {total_without_ip}")
    print(f"Total audit logs: {total_with_ip + total_without_ip}")
    print()
    
    if total_without_ip > 0:
        print(f"⚠️  {total_without_ip} audit log(s) need to be fixed to include IP address!")
    else:
        print("✅ All audit logs are correctly saving IP addresses!")
    print("=" * 80)

if __name__ == '__main__':
    main()
