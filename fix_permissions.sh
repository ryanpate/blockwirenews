#!/bin/bash

# Fix PostgreSQL permissions for BlockWire News

echo "Fixing PostgreSQL permissions for BlockWire..."
echo "============================================"

# Reset the database completely
psql postgres << EOF
-- Terminate existing connections
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE datname = 'blockwire' AND pid <> pg_backend_pid();

-- Drop and recreate database
DROP DATABASE IF EXISTS blockwire;
DROP USER IF EXISTS blockwire;

-- Create user with proper permissions
CREATE USER blockwire WITH PASSWORD 'blockwire123' CREATEDB;
CREATE DATABASE blockwire OWNER blockwire;

-- Connect to the new database
\c blockwire

-- Grant all permissions
GRANT ALL PRIVILEGES ON DATABASE blockwire TO blockwire;
GRANT ALL ON SCHEMA public TO blockwire;

-- Ensure blockwire owns the public schema
ALTER SCHEMA public OWNER TO blockwire;

\echo 'Permissions fixed!'
EOF

echo ""
echo "Database has been reset. Now run:"
echo "  python init_db.py"
echo "to recreate the tables with proper ownership."