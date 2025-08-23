Last login: Sat Aug  9 19:20:13 on ttys002
ryanpate@MacBook-Pro-7 ~ % ssh root@178.128.154.8                                
Enter passphrase for key '/Users/ryanpate/.ssh/id_ed25519': 
Welcome to Ubuntu 22.04.5 LTS (GNU/Linux 5.15.0-151-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro

 System information as of Sun Aug 10 00:20:41 UTC 2025

  System load:  0.03              Processes:             116
  Usage of /:   5.3% of 67.66GB   Users logged in:       1
  Memory usage: 29%               IPv4 address for eth0: 178.128.154.8
  Swap usage:   0%                IPv4 address for eth0: 10.10.0.5

Expanded Security Maintenance for Applications is not enabled.

0 updates can be applied immediately.

Enable ESM Apps to receive additional future security updates.
See https://ubuntu.com/esm or run: sudo pro status


Last login: Sat Aug  9 12:16:48 2025 from 72.9.118.153
root@blockwirenews:~# su - blockwire
blockwire@blockwirenews:~$ cd blockwirenews.
-bash: cd: blockwirenews.: No such file or directory
blockwire@blockwirenews:~$ cd blockwirenews
blockwire@blockwirenews:~/blockwirenews$ ls
__pycache__              app_enhanced.py              debug_flask.sh          init_db.py               run_with_env.sh          templates
ads.txt                  check_templates.py           diagnose_blockwire.sh   instance                 seo_config.py            test_app.py
ads.txt.backup           check_users.py               fix_502_blockwire.sh    logs                     seo_routes.py            test_scraper.py
app.py                   config.py                    fix_database_final.py   models.py                setup_db_simple.py       venv
app.py.backup            create_admin.py              fix_duplicate_route.sh  quick_fix_ads.sh         setup_local.sh           wsgi.py
app.py.backup_duplicate  create_missing_templates.py  fix_flask_port.sh       requirements.txt         simple_app.py
app.py.backup_port5000   crypto_news.json             fix_permissions.sh      reset_admin_password.py  standardize_pot_5000.sh
app.py.bak               crypto_news_rss.json         fix_port_8000.sh        restart_flask.sh         start.sh
app_bk.py                crypto_news_scraper.py       forms.py                run.sh                   static
blockwire@blockwirenews:~/blockwirenews$ sudo nano crytpo_news_rss.json
[sudo] password for blockwire: 
blockwire@blockwirenews:~/blockwirenews$ sudo nano crytpo_news.json
blockwire@blockwirenews:~/blockwirenews$ cat > integrate_scraper_with_db.py << 'EOF'
> #!/usr/bin/env python3
"""
Diagnostic script to identify why news isn't showing on BlockWire News
"""

import os
import sys
import json
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def diagnose():
    print("\nBlockWire News - Diagnostic Check")
    print("="*50)
    
    # 1. Check if crypto_news_scraper.py exists
    print("\n1. Checking for scraper file...")
    if os.path.exists('crypto_news_scraper.py'):
        print("   ✓ crypto_news_scraper.py found")
    else:
        print("   ✗ crypto_news_scraper.py NOT FOUND")
        return
    
    # 2. Check if JSON file exists and has content
    print("\n2. Checking for JSON output file...")
    json_file = 'crypto_news_rss.json'
    if os.path.exists(json_file):
        print(f"   ✓ {json_file} found")
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                article_count = data.get('article_count', 0)
                last_updated = data.get('last_updated', 'Unknown')
                print(f"   - Articles in JSON: {article_count}")
                print(f"   - Last updated: {last_updated}")
                
                if article_count > 0:
                    print(f"   - First article: {data['articles'][0]['title'][:50]}...")
        except Exception as e:
            print(f"   ✗ Error reading JSON: {e}")
    else:
        print(f"   ✗ {json_file} NOT FOUND")
    diagnose() "__main__":to_news_scraper.py && python3 integrate_scraper_with_db.py")st:5000 2>/dev/null || echo '   ✗ Web server not responding'")
> EOF
blockwire@blockwirenews:~/blockwirenews$ cat > integrate_scraper_with_db.py << 'EOF'
#!/usr/bin/env python3                   sudo nano crytpo_news.json
                                         cat > integrate_scraper_with_db.py << 'EOF'
#!/usr/bin/env python3
                                         cat > diagnose_news.py << 'EOF'
> 
> eof
> EOF
blockwire@blockwirenews:~/blockwirenews$ cat > diagnose_news.py << 'EOF'
> #!/usr/bin/env python3
"""
Diagnostic script to identify why news isn't showing on BlockWire News
"""

import os
import sys
import json
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def diagnose():
    print("\nBlockWire News - Diagnostic Check")
    print("="*50)
    
    # 1. Check if crypto_news_scraper.py exists
    print("\n1. Checking for scraper file...")
    if os.path.exists('crypto_news_scraper.py'):
        print("   ✓ crypto_news_scraper.py found")
    else:
        print("   ✗ crypto_news_scraper.py NOT FOUND")
        return
    
    # 2. Check if JSON file exists and has content
    print("\n2. Checking for JSON output file...")
    json_file = 'crypto_news_rss.json'
    if os.path.exists(json_file):
        print(f"   ✓ {json_file} found")
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                article_count = data.get('article_count', 0)
                last_updated = data.get('last_updated', 'Unknown')
                print(f"   - Articles in JSON: {article_count}")
                print(f"   - Last updated: {last_updated}")
                
                if article_count > 0:
                    print(f"   - First article: {data['articles'][0]['title'][:50]}...")
        except Exception as e:
            print(f"   ✗ Error reading JSON: {e}")
    else:
        print(f"   ✗ {json_file} NOT FOUND")
    diagnose() "__main__":to_news_scraper.py && python3 integrate_scraper_with_db.py")st:5000 2>/dev/null || echo '   ✗ Web server not responding'")
> EOF
blockwire@blockwirenews:~/blockwirenews$ python3 diagnose_news.py

BlockWire News - Diagnostic Check
==================================================

1. Checking for scraper file...
   ✓ crypto_news_scraper.py found

2. Checking for JSON output file...
   ✓ crypto_news_rss.json found
   - Articles in JSON: 20
   - Last updated: 2025-07-31T11:28:16.490147
   - First article: Blockstream debuts Simplicity as Bitcoin’s answer ...

3. Checking database connection...
Using PostgreSQL with system user: blockwire
   ✗ Database error: Textual SQL expression 'SELECT 1' should be explicitly declared as text('SELECT 1')
   Check DATABASE_URL environment variable

4. Checking for running processes...

5. Checking environment variables...
   DATABASE_URL: Not set

6. Testing scraper functionality...

Starting RSS feed scraping...
----------------------------------------
Fetching CoinDesk...
  No entries found in CoinDesk feed
Fetching Cointelegraph...
  Found 5 articles
Fetching Bitcoin.com...
  Found 5 articles
Fetching Decrypt...
  Found 5 articles
Fetching CryptoSlate...
  Found 5 articles
----------------------------------------
Total articles found: 20

   ✓ Scraper works! Found 20 articles

7. Checking web server...
   HTTP Status: 200

==================================================
DIAGNOSTIC COMPLETE
==================================================

RECOMMENDED ACTIONS:
1. If JSON has articles but database is empty:
   python3 integrate_scraper_with_db.py

2. If scraper isn't running continuously:
   python3 integrate_scraper_with_db.py --continuous &

3. To manually update news now:
   python3 crypto_news_scraper.py && python3 integrate_scraper_with_db.py
blockwire@blockwirenews:~/blockwirenews$ sudo nano crypto_news.json
blockwire@blockwirenews:~/blockwirenews$ sudo nano crypto_news_rss.json
blockwire@blockwirenews:~/blockwirenews$ sudo nano fix_digitalocean_database.py
blockwire@blockwirenews:~/blockwirenews$ python3 fix_digitalocean_database.py
✓ Set DATABASE_URL environment variable
✓ Successfully imported app components

BlockWire News - Database Fix and News Import
==================================================
✗ Database connection failed: (psycopg2.OperationalError) connection to server at "localhost" (::1), port 5432 failed: FATAL:  password authentication failed for user "blockwire"
connection to server at "localhost" (::1), port 5432 failed: FATAL:  password authentication failed for user "blockwire"

(Background on this error at: https://sqlalche.me/e/20/e3q8)

✗ Cannot proceed without database connection

Troubleshooting:
1. Check if PostgreSQL is running:
   sudo systemctl status postgresql
2. Check if database exists:
   sudo -u postgres psql -l | grep blockwire
3. Create database if needed:
   sudo -u postgres createdb blockwire
   sudo -u postgres psql -c "CREATE USER blockwire WITH PASSWORD 'blockwire123';"
   sudo -u postgres psql -c "GRANT ALL ON DATABASE blockwire TO blockwire;"
blockwire@blockwirenews:~/blockwirenews$ sudo systemctl status postgresql
● postgresql.service - PostgreSQL RDBMS
     Loaded: loaded (/lib/systemd/system/postgresql.service; enabled; vendor preset: enabled)
     Active: active (exited) since Sat 2025-08-02 13:05:40 UTC; 1 week 0 days ago
   Main PID: 3298 (code=exited, status=0/SUCCESS)
        CPU: 1ms

Aug 02 13:05:40 blockwirenews systemd[1]: Starting PostgreSQL RDBMS...
Aug 02 13:05:40 blockwirenews systemd[1]: Finished PostgreSQL RDBMS.
blockwire@blockwirenews:~/blockwirenews$ sudo -u postgres psql -l | grep blockwire
 blockwire | blockwire | UTF8     | C.UTF-8 | C.UTF-8 | =Tc/blockwire          +
           |           |          |         |         | blockwire=CTc/blockwire
blockwire@blockwirenews:~/blockwirenews$    sudo -u postgres createdb blockwire
   sudo -u postgres psql -c "CREATE USER blockwire WITH PASSWORD 'blockwire123';"
   sudo -u postgres psql -c "GRANT ALL ON DATABASE blockwire TO blockwire;"
createdb: error: database creation failed: ERROR:  database "blockwire" already exists
ERROR:  role "blockwire" already exists
GRANT
blockwire@blockwirenews:~/blockwirenews$ python3 fix_digitalocean_database.py
✓ Set DATABASE_URL environment variable
✓ Successfully imported app components

BlockWire News - Database Fix and News Import
==================================================
✗ Database connection failed: (psycopg2.OperationalError) connection to server at "localhost" (::1), port 5432 failed: FATAL:  password authentication failed for user "blockwire"
connection to server at "localhost" (::1), port 5432 failed: FATAL:  password authentication failed for user "blockwire"

(Background on this error at: https://sqlalche.me/e/20/e3q8)

✗ Cannot proceed without database connection

Troubleshooting:
1. Check if PostgreSQL is running:
   sudo systemctl status postgresql
2. Check if database exists:
   sudo -u postgres psql -l | grep blockwire
3. Create database if needed:
   sudo -u postgres createdb blockwire
   sudo -u postgres psql -c "CREATE USER blockwire WITH PASSWORD 'blockwire123';"
   sudo -u postgres psql -c "GRANT ALL ON DATABASE blockwire TO blockwire;"
blockwire@blockwirenews:~/blockwirenews$ sudo nano .env
blockwire@blockwirenews:~/blockwirenews$ # Patch app.py to load .env first
sed -i '1a\\nfrom dotenv import load_dotenv\nload_dotenv()\n' app.py
blockwire@blockwirenews:~/blockwirenews$ python3 fix_digitalocean_database.py
✓ Set DATABASE_URL environment variable
✓ Successfully imported app components

BlockWire News - Database Fix and News Import
==================================================
✗ Database connection failed: (psycopg2.OperationalError) connection to server at "localhost" (::1), port 5432 failed: FATAL:  password authentication failed for user "blockwire"
connection to server at "localhost" (::1), port 5432 failed: FATAL:  password authentication failed for user "blockwire"

(Background on this error at: https://sqlalche.me/e/20/e3q8)

✗ Cannot proceed without database connection

Troubleshooting:
1. Check if PostgreSQL is running:
   sudo systemctl status postgresql
2. Check if database exists:
   sudo -u postgres psql -l | grep blockwire
3. Create database if needed:
   sudo -u postgres createdb blockwire
   sudo -u postgres psql -c "CREATE USER blockwire WITH PASSWORD 'blockwire123';"
   sudo -u postgres psql -c "GRANT ALL ON DATABASE blockwire TO blockwire;"
blockwire@blockwirenews:~/blockwirenews$ cat > complete_fix.sh << 'EOF'
> #!/bin/bash

# Complete fix for BlockWire News to use Digital Ocean database
echo "BlockWire News - Complete Digital Ocean Database Fix"
echo "===================================================="
echo ""

# Step 1: Install python-dotenv
echo "Step 1: Installing python-dotenv..."
pip install python-dotenv
echo "✓ python-dotenv installed"
echo ""

# Step 2: Verify .env file exists
echo "Step 2: Checking .env file..."
if [ -f .env ]; then
    if grep -q "digitalocean.com" .env; then
        echo "✓ .env file contains Digital Ocean database URL"
    else
        echo "✗ .env file does not contain Digital Ocean database URL"
        echo "Adding it now..."
        echo "" >> .env
        echo "# Digital Ocean Database" >> .env
        echo "DATABASE_URL=postgresql://doadmin:AVNS_A-t8v7cZcKSamFH3i0J@blockwirenews-db-do-user-23625312-0.h.db.ondigitalocean.com:25060/defaultdb?sslmode=require" >> .env
    fi
else
    echo "Creating .env file..."
    cat > .env << 'EOF'
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=43cc1897069a8c0c260a948bc2cfb525d2034515e7189e0d334f114e711e5568

# Database Configuration (Digital Ocean)
DATABASE_URL=postgresql://doadmin:AVNS_A-t8v7cZcKSamFH3i0J@blockwirenews-db-do-user-23625312-0.h.db.ondigitalocean.com:25060/defaultdb?sslmode=require

# Application Settings
ENABLE_REGISTRATION=true
AUTO_UPDATE_NEWS=true
UPDATE_INTERVAL_HOURS=1
EOF
    echo "✓ Created .env file"
fi
echo "2. Database connection: python3 -c 'from dotenv import load_dotenv; load_dotenv(); from app import db; db.session.execute(\"SELECT 1\")'"
✓ Created .env file
-bash: syntax error near unexpected token `fi'

Step 3: Patching app.py to load .env file...
✓ app.py already loads .env

Step 4: Running news scraper...
Crypto News Scraper v2.0
========================


Starting RSS feed scraping...
----------------------------------------
Fetching CoinDesk...
  No entries found in CoinDesk feed
Fetching Cointelegraph...
  Found 5 articles
Fetching Bitcoin.com...
  Found 5 articles
EFetching Decrypt...
O  Found 5 articles
FFetching CryptoSlate...
  Found 5 articles
----------------------------------------
Total articles found: 20

Saved 20 articles to crypto_news_rss.json

Testing JSON file...
Successfully loaded 20 articles

First article: Robert Kiyosaki Eyes Bitcoin Crashing to $90K This Month to Double His BTC Position

Step 5: Importing news to Digital Ocean database...
Traceback (most recent call last):
  File "<stdin>", line 3, in <module>
  File "/home/blockwire/.local/lib/python3.10/site-packages/dotenv/main.py", line 346, in load_dotenv
    dotenv_path = find_dotenv()
  File "/home/blockwire/.local/lib/python3.10/site-packages/dotenv/main.py", line 305, in find_dotenv
    assert frame.f_back is not None
AssertionError

Step 6: Restarting application...
✓ Reloaded gunicorn

====================================================
✅ COMPLETE!
====================================================

Your website should now show news articles!
Visit: http://178.128.154.8

If you still see no news, check:
1. Application logs: tail -f app.log
2. Database connection: python3 -c 'from dotenv import load_dotenv; load_dotenv(); from app import db; db.session.execute("SELECT 1")'
blockwire@blockwirenews:~/blockwirenews$ cat > complete_fix.sh << 'EOF'
> #!/bin/bash

# Complete fix for BlockWire News to use Digital Ocean database
echo "BlockWire News - Complete Digital Ocean Database Fix"
echo "===================================================="
echo ""

# Step 1: Install python-dotenv
echo "Step 1: Installing python-dotenv..."
pip install python-dotenv
echo "✓ python-dotenv installed"
echo ""

# Step 2: Verify .env file exists
echo "Step 2: Checking .env file..."
if [ -f .env ]; then
    if grep -q "digitalocean.com" .env; then
        echo "✓ .env file contains Digital Ocean database URL"
    else
        echo "✗ .env file does not contain Digital Ocean database URL"
        echo "Adding it now..."
        echo "" >> .env
        echo "# Digital Ocean Database" >> .env
        echo "DATABASE_URL=postgresql://doadmin:AVNS_A-t8v7cZcKSamFH3i0J@blockwirenews-db-do-user-23625312-0.h.db.ondigitalocean.com:25060/defaultdb?sslmode=require" >> .env
    fi
else
    echo "Creating .env file..."
    cat > .env << 'EOF'
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=43cc1897069a8c0c260a948bc2cfb525d2034515e7189e0d334f114e711e5568

# Database Configuration (Digital Ocean)
DATABASE_URL=postgresql://doadmin:AVNS_A-t8v7cZcKSamFH3i0J@blockwirenews-db-do-user-23625312-0.h.db.ondigitalocean.com:25060/defaultdb?sslmode=require

# Application Settings
ENABLE_REGISTRATION=true
AUTO_UPDATE_NEWS=true
UPDATE_INTERVAL_HOURS=1
EOF
    echo "✓ Created .env file"
fi
echo "2. Database connection: python3 -c 'from dotenv import load_dotenv; load_dotenv(); from app import db; db.session.execute(\"SELECT 1\")'"
✓ Created .env file
-bash: syntax error near unexpected token `fi'

Step 3: Patching app.py to load .env file...
✓ app.py already loads .env

Step 4: Running news scraper...
Crypto News Scraper v2.0
========================


Starting RSS feed scraping...
----------------------------------------
Fetching CoinDesk...
  No entries found in CoinDesk feed
Fetching Cointelegraph...
  Found 5 articles
Fetching Bitcoin.com...
  Found 5 articles
Fetching Decrypt...
  Found 5 articles
Fetching CryptoSlate...
  Found 5 articles
----------------------------------------
Total articles found: 20

Saved 20 articles to crypto_news_rss.json

Testing JSON file...
Successfully loaded 20 articles

First article: Robert Kiyosaki Eyes Bitcoin Crashing to $90K This Month to Double His BTC Position

Step 5: Importing news to Digital Ocean database...
Traceback (most recent call last):
  File "<stdin>", line 3, in <module>
  File "/home/blockwire/.local/lib/python3.10/site-packages/dotenv/main.py", line 346, in load_dotenv
    dotenv_path = find_dotenv()
  File "/home/blockwire/.local/lib/python3.10/site-packages/dotenv/main.py", line 305, in find_dotenv
    assert frame.f_back is not None
AssertionError

Step 6: Restarting application...
✓ Reloaded gunicorn

====================================================
✅ COMPLETE!
====================================================

Your website should now show news articles!
Visit: http://178.128.154.8

If you still see no news, check:
1. Application logs: tail -f app.log
2. Database connection: python3 -c 'from dotenv import load_dotenv; load_dotenv(); from app import db; db.session.execute("SELECT 1")'
blockwire@blockwirenews:~/blockwirenews$ #!/bin/bash

# Complete fix for BlockWire News to use Digital Ocean database
echo "BlockWire News - Complete Digital Ocean Database Fix"
echo "===================================================="
echo ""

# Step 1: Install python-dotenv
echo "Step 1: Installing python-dotenv..."
pip install python-dotenv
echo "✓ python-dotenv installed"
echo ""

# Step 2: Verify .env file exists
echo "Step 2: Checking .env file..."
if [ -f .env ]; then
    if grep -q "digitalocean.com" .env; then
        echo "✓ .env file contains Digital Ocean database URL"
    else
        echo "✗ .env file does not contain Digital Ocean database URL"
        echo "Adding it now..."
        echo "" >> .env
        echo "# Digital Ocean Database" >> .env
        echo "DATABASE_URL=postgresql://doadmin:AVNS_A-t8v7cZcKSamFH3i0J@blockwirenews-db-do-user-23625312-0.h.db.ondigitalocean.com:25060/defaultdb?sslmode=require" >> .env
    fi
else
    echo "Creating .env file..."
    cat > .env << 'EOF'
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=43cc1897069a8c0c260a948bc2cfb525d2034515e7189e0d334f114e711e5568

# Database Configuration (Digital Ocean)
DATABASE_URL=postgresql://doadmin:AVNS_A-t8v7cZcKSamFH3i0J@blockwirenews-db-do-user-23625312-0.h.db.ondigitalocean.com:25060/defaultdb?sslmode=require

# Application Settings
ENABLE_REGISTRATION=true
AUTO_UPDATE_NEWS=true
UPDATE_INTERVAL_HOURS=1
EOF
    echo "✓ Created .env file"
fi
echo "2. Database connection: python3 -c 'from dotenv import load_dotenv; load_dotenv(); from app import db; db.session.execute(\"SELECT 1\")'"
BlockWire News - Complete Digital Ocean Database Fix
====================================================

Step 1: Installing python-dotenv...
Defaulting to user installation because normal site-packages is not writeable
Requirement already satisfied: python-dotenv in /home/blockwire/.local/lib/python3.10/site-packages (1.0.1)
✓ python-dotenv installed

Step 2: Checking .env file...
✓ .env file contains Digital Ocean database URL

Step 3: Patching app.py to load .env file...
✓ app.py already loads .env

Step 4: Running news scraper...
Crypto News Scraper v2.0
========================


Starting RSS feed scraping...
----------------------------------------
Fetching CoinDesk...
  No entries found in CoinDesk feed
Fetching Cointelegraph...
  Found 5 articles
Fetching Bitcoin.com...
  Found 5 articles
Fetching Decrypt...
  Found 5 articles
Fetching CryptoSlate...
  Found 5 articles
----------------------------------------
Total articles found: 20

Saved 20 articles to crypto_news_rss.json

Testing JSON file...
Successfully loaded 20 articles

First article: Robert Kiyosaki Eyes Bitcoin Crashing to $90K This Month to Double His BTC Position

Step 5: Importing news to Digital Ocean database...
Traceback (most recent call last):
  File "<stdin>", line 3, in <module>
  File "/home/blockwire/.local/lib/python3.10/site-packages/dotenv/main.py", line 346, in load_dotenv
    dotenv_path = find_dotenv()
  File "/home/blockwire/.local/lib/python3.10/site-packages/dotenv/main.py", line 305, in find_dotenv
    assert frame.f_back is not None
AssertionError

Step 6: Restarting application...
✓ Reloaded gunicorn

====================================================
✅ COMPLETE!
====================================================

Your website should now show news articles!
Visit: http://178.128.154.8

If you still see no news, check:
1. Application logs: tail -f app.log
2. Database connection: python3 -c 'from dotenv import load_dotenv; load_dotenv(); from app import db; db.session.execute("SELECT 1")'
blockwire@blockwirenews:~/blockwirenews$ cat > complete_fix.sh << 'EOF'
> #!/bin/bash

# Complete fix for BlockWire News to use Digital Ocean database
echo "BlockWire News - Complete Digital Ocean Database Fix"
echo "===================================================="
echo ""

# Step 1: Install python-dotenv
echo "Step 1: Installing python-dotenv..."
pip install python-dotenv
echo "✓ python-dotenv installed"
echo ""

# Step 2: Verify .env file exists
echo "Step 2: Checking .env file..."
if [ -f .env ]; then
    if grep -q "digitalocean.com" .env; then
        echo "✓ .env file contains Digital Ocean database URL"
    else
        echo "✗ .env file does not contain Digital Ocean database URL"
        echo "Adding it now..."
        echo "" >> .env
        echo "# Digital Ocean Database" >> .env
        echo "DATABASE_URL=postgresql://doadmin:AVNS_A-t8v7cZcKSamFH3i0J@blockwirenews-db-do-user-23625312-0.h.db.ondigitalocean.com:25060/defaultdb?sslmode=require" >> .env
    fi
else
    echo "Creating .env file..."
    cat > .env << 'EOF'
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=43cc1897069a8c0c260a948bc2cfb525d2034515e7189e0d334f114e711e5568

# Database Configuration (Digital Ocean)
DATABASE_URL=postgresql://doadmin:AVNS_A-t8v7cZcKSamFH3i0J@blockwirenews-db-do-user-23625312-0.h.db.ondigitalocean.com:25060/defaultdb?sslmode=require

# Application Settings
ENABLE_REGISTRATION=true
AUTO_UPDATE_NEWS=true
UPDATE_INTERVAL_HOURS=1
EOF
    echo "✓ Created .env file"
fi
echo "2. Database connection: python3 -c 'from dotenv import load_dotenv; load_dotenv(); from app import db; db.session.execute(\"SELECT 1\")'"
✓ Created .env file
-bash: syntax error near unexpected token `fi'

Step 3: Patching app.py to load .env file...
✓ app.py already loads .env

Step 4: Running news scraper...
Crypto News Scraper v2.0
========================


Starting RSS feed scraping...
----------------------------------------
Fetching CoinDesk...
  No entries found in CoinDesk feed
Fetching Cointelegraph...
  Found 5 articles
Fetching Bitcoin.com...
  Found 5 articles
Fetching Decrypt...
  Found 5 articles
Fetching CryptoSlate...
  Found 5 articles
----------------------------------------
Total articles found: 20

Saved 20 articles to crypto_news_rss.json

Testing JSON file...
Successfully loaded 20 articles

First article: Robert Kiyosaki Eyes Bitcoin Crashing to $90K This Month to Double His BTC Position

Step 5: Importing news to Digital Ocean database...
Traceback (most recent call last):
  File "<stdin>", line 3, in <module>
  File "/home/blockwire/.local/lib/python3.10/site-packages/dotenv/main.py", line 346, in load_dotenv
    dotenv_path = find_dotenv()
  File "/home/blockwire/.local/lib/python3.10/site-packages/dotenv/main.py", line 305, in find_dotenv
    assert frame.f_back is not None
AssertionError

Step 6: Restarting application...
✓ Reloaded gunicorn

====================================================
✅ COMPLETE!
====================================================

Your website should now show news articles!
Visit: http://178.128.154.8

If you still see no news, check:
1. Application logs: tail -f app.log
2. Database connection: python3 -c 'from dotenv import load_dotenv; load_dotenv(); from app import db; db.session.execute("SELECT 1")'
blockwire@blockwirenews:~/blockwirenews$ sudo nano complete_fix.sh
blockwire@blockwirenews:~/blockwirenews$ chmod +x complete_fix.sh
./complete_fix.sh
BlockWire News - Complete Digital Ocean Database Fix
====================================================

Step 1: Installing python-dotenv...
Defaulting to user installation because normal site-packages is not writeable
Requirement already satisfied: python-dotenv in /home/blockwire/.local/lib/python3.10/site-packages (1.0.1)
✓ python-dotenv installed

Step 2: Checking .env file...
✓ .env file contains Digital Ocean database URL

Step 3: Patching app.py to load .env file...
✓ app.py already loads .env

Step 4: Running news scraper...
Crypto News Scraper v2.0
========================


Starting RSS feed scraping...
----------------------------------------
Fetching CoinDesk...
  No entries found in CoinDesk feed
Fetching Cointelegraph...
  Found 5 articles
Fetching Bitcoin.com...
  Found 5 articles
Fetching Decrypt...
  Found 5 articles
Fetching CryptoSlate...
  Found 5 articles
----------------------------------------
Total articles found: 20

Saved 20 articles to crypto_news_rss.json

Testing JSON file...
Successfully loaded 20 articles

First article: Robert Kiyosaki Eyes Bitcoin Crashing to $90K This Month to Double His BTC Position

Step 5: Importing news to Digital Ocean database...
Traceback (most recent call last):
  File "<stdin>", line 3, in <module>
  File "/home/blockwire/.local/lib/python3.10/site-packages/dotenv/main.py", line 346, in load_dotenv
    dotenv_path = find_dotenv()
  File "/home/blockwire/.local/lib/python3.10/site-packages/dotenv/main.py", line 305, in find_dotenv
    assert frame.f_back is not None
AssertionError

Step 6: Restarting application...
✓ Reloaded gunicorn

====================================================
✅ COMPLETE!
====================================================

Your website should now show news articles!
Visit: http://178.128.154.8

If you still see no news, check:
1. Application logs: tail -f app.log
2. Database connection: python3 -c 'from dotenv import load_dotenv; load_dotenv(); from app import db; db.session.execute("SELECT 1")'
blockwire@blockwirenews:~/blockwirenews$ sed -i '1a\\nfrom dotenv import load_dotenv\nload_dotenv()\n' app.py
blockwire@blockwirenews:~/blockwirenews$ sudo nano app_bk.py

  GNU nano 6.2                                                           app_bk.py *                                                                   

            # Check if we need to run initial setup
            user_count = 0
            try:
                user_count = User.query.count()
                articles_count = Article.query.filter_by(
                    published=True).count()
                news_count = NewsItem.query.count()

                print(f"✓ Found {user_count} users in database")
                print(f"✓ Found {articles_count} published articles")
                print(f"✓ Found {news_count} news items")

            except:
                print("! Could not access database tables")
                print("! Run 'python init_db.py' to initialize the database")

            if user_count == 0:
                print("\n! No users found in database")
                print("! Run 'python init_db.py' to create admin user")

            # Display SEO endpoints
            print("\n✓ SEO Features Active:")
            print("  - Sitemap: http://localhost:8000/sitemap.xml")
            print("  - RSS Feed: http://localhost:8000/rss")
            print("  - Robots.txt: http://localhost:8000/robots.txt")
            print("  - Search: http://localhost:8000/search")

        except Exception as e:
            print(f"\n✗ Database error: {e}")
            print("\nTroubleshooting:")
            print("1. Make sure PostgreSQL is running")
            print("2. Create database: createdb blockwire")
            print("3. Run: python init_db.py")

    print("\nStarting Flask application on http://localhost:8000")
    print("Press Ctrl+C to stop\n")

    app.run(debug=True, port=5000)
