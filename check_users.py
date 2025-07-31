#!/usr/bin/env python3
"""
Check existing users in the database
"""

import os
import sys
import psycopg2
import getpass

def check_users_direct():
    """Check users directly via SQL"""
    username = getpass.getuser()
    print(f"Checking users in database (as {username})...")
    print("=" * 50)
    
    try:
        # Connect directly to PostgreSQL
        conn = psycopg2.connect(
            dbname='blockwire',
            user=username,
            host='localhost'
        )
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'users'
            );
        """)
        
        if not cursor.fetchone()[0]:
            print("❌ The 'users' table does not exist!")
            print("\nRun these commands to fix:")
            print("  python fix_database_final.py")
            print("  python create_admin.py")
            return
        
        # Get all users
        cursor.execute("""
            SELECT id, username, email, is_admin, created_at 
            FROM users 
            ORDER BY created_at
        """)
        
        users = cursor.fetchall()
        
        if not users:
            print("No users found in the database.")
            print("\nCreate an admin user with:")
            print("  python create_admin.py")
        else:
            print(f"Found {len(users)} user(s):\n")
            print("ID | Username      | Email                        | Admin | Created")
            print("-" * 80)
            
            for user in users:
                user_id, username, email, is_admin, created = user
                admin_badge = "✓" if is_admin else " "
                created_str = created.strftime("%Y-%m-%d %H:%M") if created else "Unknown"
                print(f"{user_id:2d} | {username:13s} | {email:28s} | {admin_badge:5s} | {created_str}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure:")
        print("1. PostgreSQL is running")
        print("2. The 'blockwire' database exists")
        print("3. You have permission to access it")

if __name__ == "__main__":
    check_users_direct()