#!/usr/bin/env python3
"""
Quick script to reset admin password
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User

def reset_admin():
    """Reset admin password to 'admin123'"""
    with app.app_context():
        print("Resetting admin password...")
        
        # Try to find admin user
        admin = User.query.filter_by(username='admin').first()
        
        if not admin:
            # Create admin user
            print("Creating admin user...")
            admin = User(
                username='admin',
                email='admin@blockwirenews.com',
                is_admin=True
            )
            db.session.add(admin)
        else:
            print(f"Found existing admin user: {admin.email}")
            admin.is_admin = True  # Ensure they're admin
        
        # Set password
        admin.set_password('admin123')
        
        try:
            db.session.commit()
            print("\n✅ Success!")
            print("   Username: admin")
            print("   Password: admin123")
            print("\nLogin at: http://localhost:5000/login")
        except Exception as e:
            print(f"Error: {e}")
            db.session.rollback()

if __name__ == "__main__":
    reset_admin()