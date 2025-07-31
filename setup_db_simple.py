#!/usr/bin/env python3
"""
Simple database setup for BlockWire News
Uses your macOS username for PostgreSQL connection
"""

import os
import sys
import getpass
import subprocess

def run_command(cmd):
    """Run a shell command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("BlockWire News - Simple Database Setup")
    print("=" * 50)
    
    # Get current username
    username = getpass.getuser()
    print(f"Using PostgreSQL with your macOS user: {username}")
    
    # Step 1: Create database
    print("\n1. Creating database 'blockwire'...")
    success, stdout, stderr = run_command("createdb blockwire")
    
    if success:
        print("   ✓ Database created successfully")
    else:
        if "already exists" in stderr:
            print("   ✓ Database already exists")
        else:
            print(f"   ✗ Error creating database: {stderr}")
            print("\n   Make sure PostgreSQL is installed and running:")
            print("   brew install postgresql@15")
            print("   brew services start postgresql@15")
            return
    
    # Step 2: Create .env file
    print("\n2. Creating .env file...")
    env_content = f"""# Flask Configuration
SECRET_KEY=dev-secret-key-change-this-in-production
FLASK_ENV=development

# Database Configuration (using macOS username)
DATABASE_URL=postgresql://{username}@localhost/blockwire

# Application Settings
ENABLE_REGISTRATION=true
AUTO_UPDATE_NEWS=true
UPDATE_INTERVAL_HOURS=1
"""
    
    if os.path.exists('.env'):
        print("   ! .env file already exists, skipping...")
    else:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("   ✓ .env file created")
    
    # Step 3: Test database connection
    print("\n3. Testing database connection...")
    test_cmd = f'psql -U {username} -d blockwire -c "SELECT version();" -q'
    success, stdout, stderr = run_command(test_cmd)
    
    if success:
        print("   ✓ Database connection successful")
    else:
        print(f"   ✗ Could not connect to database: {stderr}")
        return
    
    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Install Python dependencies:")
    print("   pip install -r requirements.txt")
    print("\n2. Initialize the database:")
    print("   python init_db.py")
    print("\n3. Run the application:")
    print("   python app.py")
    
    print("\n✨ Your database URL is:")
    print(f"   postgresql://{username}@localhost/blockwire")

if __name__ == "__main__":
    main()