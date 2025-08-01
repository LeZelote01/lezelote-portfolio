#!/usr/bin/env python3
"""
Script to fix authentication on all admin endpoints
"""
import re

# Read the file
with open('/app/backend/admin_routes.py', 'r') as f:
    content = f.read()

# Find all POST, PUT, DELETE endpoints that don't have authentication
patterns = [
    # POST endpoints
    (r'(@admin_router\.post\([^)]+\)\s*\n)(async def (\w+)\(([^)]+)\):\s*\n\s*"""([^"]+)""")',
     r'\1async def \3(\4, current_user: AdminUser = Depends(get_current_user)):\n    """\5 (requires authentication)"""'),
    
    # PUT endpoints 
    (r'(@admin_router\.put\([^)]+\)\s*\n)(async def (\w+)\(([^)]+)\):\s*\n\s*"""([^"]+)""")',
     r'\1async def \3(\4, current_user: AdminUser = Depends(get_current_user)):\n    """\5 (requires authentication)"""'),
    
    # DELETE endpoints
    (r'(@admin_router\.delete\([^)]+\)\s*\n)(async def (\w+)\(([^)]+)\):\s*\n\s*"""([^"]+)""")',
     r'\1async def \3(\4, current_user: AdminUser = Depends(get_current_user)):\n    """\5 (requires authentication)"""'),
]

# Apply replacements only if authentication is not already present
for pattern, replacement in patterns:
    # Only replace if current_user is not already in the function signature
    def replace_if_no_auth(match):
        full_match = match.group(0)
        if 'current_user' not in full_match:
            return re.sub(pattern, replacement, full_match)
        return full_match
    
    content = re.sub(pattern, replace_if_no_auth, content, flags=re.MULTILINE)

# Write back to file
with open('/app/backend/admin_routes.py', 'w') as f:
    f.write(content)

print("✅ Authentication fixed on all admin endpoints")