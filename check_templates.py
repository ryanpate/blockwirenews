#!/usr/bin/env python3
"""
Check if all required templates are in place
"""

import os

# List of required templates
required_templates = [
    'base_enhanced.html',
    'index_enhanced.html',
    'login.html',
    'register.html',
    'profile.html',
    'article_form.html',
    'article.html',
    '404.html',
    '500.html',
    'admin/dashboard.html',
    'admin/users.html',
    'admin/articles.html',
    'admin/news.html',
    'admin/settings.html'
]

def check_templates():
    print("Checking templates...")
    print("=" * 50)
    
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
        print("Created templates/ directory")
    
    # Create admin subdirectory if it doesn't exist
    if not os.path.exists('templates/admin'):
        os.makedirs('templates/admin')
        print("Created templates/admin/ directory")
    
    missing = []
    for template in required_templates:
        path = os.path.join('templates', template)
        if os.path.exists(path):
            print(f"✓ {template}")
        else:
            print(f"✗ {template} (MISSING)")
            missing.append(template)
    
    print("=" * 50)
    
    if missing:
        print(f"\n❌ Missing {len(missing)} templates:")
        for t in missing:
            print(f"   - {t}")
        print("\nPlease create the missing templates or copy them from the artifacts.")
    else:
        print("\n✅ All templates are in place!")
    
    return len(missing) == 0

if __name__ == "__main__":
    check_templates()