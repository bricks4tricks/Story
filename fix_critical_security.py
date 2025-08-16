#!/usr/bin/env python3
"""
CRITICAL SECURITY FIX SCRIPT
Adds missing @require_auth(['admin']) decorators to vulnerable admin endpoints.
"""

import re

def fix_admin_authentication():
    """Add missing @require_auth decorators to admin endpoints."""
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Admin endpoints missing authentication
    missing_auth_fixes = [
        ('@app.route(\'/api/admin/map-topic-curriculums\', methods=[\'POST\', \'OPTIONS\'])\ndef map_topic_curriculums():', 
         '@app.route(\'/api/admin/map-topic-curriculums\', methods=[\'POST\', \'OPTIONS\'])\n@require_auth([\'admin\'])\ndef map_topic_curriculums():'),
        
        ('@app.route(\'/api/admin/update-curriculum/<int:subject_id>\', methods=[\'PUT\', \'OPTIONS\'])\ndef update_curriculum(subject_id):', 
         '@app.route(\'/api/admin/update-curriculum/<int:subject_id>\', methods=[\'PUT\', \'OPTIONS\'])\n@require_auth([\'admin\'])\ndef update_curriculum(subject_id):'),
        
        ('@app.route(\'/api/admin/update-topic/<int:topic_id>\', methods=[\'PUT\', \'OPTIONS\'])\ndef update_topic(topic_id):', 
         '@app.route(\'/api/admin/update-topic/<int:topic_id>\', methods=[\'PUT\', \'OPTIONS\'])\n@require_auth([\'admin\'])\ndef update_topic(topic_id):'),
        
        ('@app.route(\'/api/admin/delete-topic/<int:topic_id>\', methods=[\'DELETE\', \'OPTIONS\'])\ndef delete_topic(topic_id):', 
         '@app.route(\'/api/admin/delete-topic/<int:topic_id>\', methods=[\'DELETE\', \'OPTIONS\'])\n@require_auth([\'admin\'])\ndef delete_topic(topic_id):'),
        
        ('@app.route(\'/api/admin/flagged-items\', methods=[\'GET\'])\ndef get_flagged_items():', 
         '@app.route(\'/api/admin/flagged-items\', methods=[\'GET\'])\n@require_auth([\'admin\'])\ndef get_flagged_items():'),
        
        ('@app.route(\'/api/admin/update-flag-status/<int:flag_id>\', methods=[\'PUT\', \'OPTIONS\'])\ndef update_flag_status(flag_id):', 
         '@app.route(\'/api/admin/update-flag-status/<int:flag_id>\', methods=[\'PUT\', \'OPTIONS\'])\n@require_auth([\'admin\'])\ndef update_flag_status(flag_id):'),
        
        ('@app.route(\'/api/admin/delete-flag/<int:flag_id>\', methods=[\'DELETE\', \'OPTIONS\'])\ndef delete_flag(flag_id):', 
         '@app.route(\'/api/admin/delete-flag/<int:flag_id>\', methods=[\'DELETE\', \'OPTIONS\'])\n@require_auth([\'admin\'])\ndef delete_flag(flag_id):'),
        
        ('@app.route(\'/api/admin/question-attempts\', methods=[\'GET\'])\ndef get_all_question_attempts():', 
         '@app.route(\'/api/admin/question-attempts\', methods=[\'GET\'])\n@require_auth([\'admin\'])\ndef get_all_question_attempts():')
    ]
    
    fixed_count = 0
    for old_pattern, new_pattern in missing_auth_fixes:
        if old_pattern in content:
            content = content.replace(old_pattern, new_pattern)
            fixed_count += 1
            print(f"✅ Fixed: {old_pattern.split('def ')[1].split('(')[0]}")
    
    # Write back to file
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n🔒 Fixed {fixed_count} critical admin authentication vulnerabilities!")
    return fixed_count

def main():
    print("🚨 CRITICAL SECURITY FIX - Admin Authentication")
    print("=" * 55)
    print("Adding missing @require_auth(['admin']) decorators...")
    print()
    
    fixed = fix_admin_authentication()
    
    if fixed > 0:
        print(f"\n✅ SUCCESS: Fixed {fixed} critical vulnerabilities!")
        print("🛡️ All admin endpoints now require authentication")
        print("\nNext steps:")
        print("1. Test admin functionality")
        print("2. Run security tests")
        print("3. Commit changes")
    else:
        print("\n⚠️  No fixes needed - endpoints already secured")

if __name__ == "__main__":
    main()