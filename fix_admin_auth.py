#!/usr/bin/env python3
"""
Script to add @require_auth(['admin']) to all admin endpoints missing authentication.
"""

import re
import os

# Read the app.py file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to match admin routes without @require_auth
admin_route_pattern = r"(@app\.route\('/api/admin/[^']+',\s*methods=\[[^\]]+\])\s*\n(def\s+\w+)"

def fix_admin_endpoints(content):
    """Add @require_auth(['admin']) to admin endpoints that don't have it."""
    
    # Find all admin routes
    matches = list(re.finditer(admin_route_pattern, content))
    
    # Process matches in reverse order to avoid offset issues
    for match in reversed(matches):
        route_decorator = match.group(1)
        function_def = match.group(2)
        
        # Check if this route already has @require_auth
        start_pos = match.start()
        end_pos = match.end()
        
        # Look ahead to see if @require_auth is already there
        next_lines = content[end_pos:end_pos+200]
        if '@require_auth' in next_lines[:50]:  # Only check nearby
            continue
            
        # Look behind to see if @require_auth is before the route
        prev_lines = content[max(0, start_pos-200):start_pos]
        if '@require_auth' in prev_lines[-50:]:  # Only check nearby
            continue
            
        # Add @require_auth(['admin']) before the function definition
        new_block = f"{route_decorator}\n@require_auth(['admin'])\n{function_def}"
        content = content[:match.start()] + new_block + content[match.end():]
        print(f"✅ Added auth to: {function_def}")
    
    return content

# Apply the fixes
fixed_content = fix_admin_endpoints(content)

# Write back to file
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("🔒 Admin authentication fix completed!")