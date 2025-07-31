#!/usr/bin/env python3
"""
Create an admin user for BlockWire News
"""

import os
import sys
import getpass as gp

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User

def create_admin_user():
    """Create an admin user with proper password hashing"""
    print("BlockWire News - Create Admin User")
    print("=" * 50)
    
    with app.app_context():
        # Check if tables exist
        try:
            existing_admins = User.query.filter_by(is_admin=True).all()
            if existing_admins:
                print("\nExisting admin users found:")
                for admin in existing_admins:
                    print(f"  - {admin.username} ({admin.email})")
                print()
        except Exception as e:
            print(f"Note: Could not query existing users: {e}")
            print("Tables may not exist yet. Run 'python init_db.py' first.\n")
        
        # Get admin details
        print("Enter details for new admin user:\n")
        
        username = input("Username (default: admin): ").strip() or "admin"
        email = input("Email (default: admin@blockwirenews.com): ").strip() or "admin@blockwirenews.com"
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"\nUser '{username}' already exists!")
            response = input("Do you want to reset their password and make them admin? (y/n): ")
            if response.lower() != 'y':
                print("Cancelled.")
                return
            
            # Update existing user
            password = gp.getpass("New password: ")
            if not password:
                print("Password cannot be empty!")
                return
                
            existing_user.set_password(password)
            existing_user.is_admin = True
            db.session.commit()
            
            print(f"\n✅ User '{username}' updated successfully!")
            print(f"   - Password has been reset")
            print(f"   - Admin privileges granted")
            
        else:
            # Create new user
            password = gp.getpass("Password (hidden): ")
            if not password:
                print("Password cannot be empty!")
                return
            
            # Create the user
            user = User(username=username, email=email, is_admin=True)
            user.set_password(password)
            
            try:
                db.session.add(user)
                db.session.commit()
                
                print(f"\n✅ Admin user created successfully!")
                print(f"   Username: {username}")
                print(f"   Email: {email}")
                print(f"   Password: [hidden]")
                
            except Exception as e:
                db.session.rollback()
                print(f"\n❌ Error creating user: {e}")
                return
        
        print("\n" + "=" * 50)
        print("You can now login at http://localhost:5000/login")

if __name__ == "__main__":
    create_admin_user()