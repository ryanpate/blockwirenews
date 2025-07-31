#!/usr/bin/env python3
"""
Final database fix - creates tables with correct permissions
"""

import os
import sys
import getpass
import psycopg2
from psycopg2 import sql

def fix_database():
    print("BlockWire News - Database Permission Fix")
    print("=" * 50)
    
    # Get current username
    username = getpass.getuser()
    print(f"Using PostgreSQL with system user: {username}")
    
    try:
        # Connect to PostgreSQL
        print("\nConnecting to PostgreSQL...")
        conn = psycopg2.connect(
            dbname='postgres',
            user=username,
            host='localhost'
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Drop and recreate database
        print("Recreating database...")
        
        # Terminate existing connections
        cursor.execute("""
            SELECT pg_terminate_backend(pid) 
            FROM pg_stat_activity 
            WHERE datname = 'blockwire' AND pid <> pg_backend_pid()
        """)
        
        # Drop database if exists
        cursor.execute("DROP DATABASE IF EXISTS blockwire")
        
        # Create fresh database
        cursor.execute("CREATE DATABASE blockwire")
        print("✓ Database 'blockwire' created")
        
        cursor.close()
        conn.close()
        
        # Connect to the new database
        print("\nConnecting to blockwire database...")
        conn = psycopg2.connect(
            dbname='blockwire',
            user=username,
            host='localhost'
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Create tables with correct structure
        print("Creating tables...")
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(255),
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)
        
        # Articles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id SERIAL PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                slug VARCHAR(200) UNIQUE NOT NULL,
                content TEXT NOT NULL,
                summary VARCHAR(500),
                author_id INTEGER REFERENCES users(id) NOT NULL,
                published BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                published_at TIMESTAMP,
                views INTEGER DEFAULT 0
            )
        """)
        
        # News items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS news_items (
                id SERIAL PRIMARY KEY,
                external_id VARCHAR(50) UNIQUE,
                title VARCHAR(300) NOT NULL,
                url VARCHAR(500) NOT NULL,
                summary TEXT,
                source VARCHAR(100),
                published_date TIMESTAMP,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_featured BOOLEAN DEFAULT FALSE
            )
        """)
        
        # Price data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_data (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR(20) NOT NULL,
                name VARCHAR(50),
                price_usd FLOAT,
                change_24h FLOAT,
                market_cap BIGINT,
                volume_24h BIGINT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Site settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS site_settings (
                id SERIAL PRIMARY KEY,
                key VARCHAR(50) UNIQUE NOT NULL,
                value TEXT,
                description VARCHAR(200),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        print("✓ All tables created")
        
        # Create indexes
        print("\nCreating indexes...")
        cursor.execute("CREATE INDEX idx_news_published ON news_items(published_date DESC)")
        cursor.execute("CREATE INDEX idx_articles_published ON articles(published, published_at DESC)")
        cursor.execute("CREATE INDEX idx_price_symbol ON price_data(symbol, timestamp DESC)")
        print("✓ Indexes created")
        
        # Insert default admin user
        print("\nCreating default admin user...")
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, is_admin)
            VALUES ('admin', 'admin@blockwirenews.com', 
                    'pbkdf2:sha256:600000$TH8GjPqL$c31f5eff088f62c42cb024cd1045643e96a0cb3275bb7393858d6350e51d0013',
                    TRUE)
            ON CONFLICT (username) DO NOTHING
        """)
        print("✓ Admin user created (username: admin, password: changeme123)")
        
        cursor.close()
        conn.close()
        
        # Update .env file
        print("\nUpdating .env file...")
        env_content = f"""# Flask Configuration
SECRET_KEY=dev-secret-key-change-this-in-production
FLASK_ENV=development

# Database Configuration
DATABASE_URL=postgresql://{username}@localhost/blockwire

# Application Settings
ENABLE_REGISTRATION=true
AUTO_UPDATE_NEWS=true
UPDATE_INTERVAL_HOURS=1
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✓ .env file updated")
        
        print("\n" + "=" * 50)
        print("✅ Database setup complete!")
        print("=" * 50)
        print("\nYou can now run the application:")
        print("  python app.py")
        print("\nLogin with:")
        print("  Username: admin")
        print("  Password: changeme123")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure PostgreSQL is running:")
        print("   brew services start postgresql@15")
        print("2. Try running as superuser:")
        print("   sudo -u postgres psql")

if __name__ == "__main__":
    response = input("This will DROP and RECREATE the blockwire database. Continue? (y/n): ")
    if response.lower() == 'y':
        fix_database()
    else:
        print("Cancelled.")