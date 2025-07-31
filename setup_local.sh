#!/bin/bash

# BlockWire News - Local Setup Script
# This script sets up PostgreSQL and the application for local development

echo "BlockWire News - Local Development Setup"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for PostgreSQL
echo -e "\n${YELLOW}Checking for PostgreSQL...${NC}"
if command_exists psql; then
    echo -e "${GREEN}✓ PostgreSQL is installed${NC}"
else
    echo -e "${RED}✗ PostgreSQL is not installed${NC}"
    echo "Please install PostgreSQL first:"
    echo "  macOS: brew install postgresql@15 && brew services start postgresql@15"
    echo "  Ubuntu: sudo apt install postgresql postgresql-contrib"
    exit 1
fi

# Check if PostgreSQL is running
if pg_isready >/dev/null 2>&1; then
    echo -e "${GREEN}✓ PostgreSQL is running${NC}"
else
    echo -e "${RED}✗ PostgreSQL is not running${NC}"
    echo "Please start PostgreSQL:"
    echo "  macOS: brew services start postgresql@15"
    echo "  Ubuntu: sudo systemctl start postgresql"
    exit 1
fi

# Create database and user
echo -e "\n${YELLOW}Setting up database...${NC}"
echo "This will create a 'blockwire' user and database."
echo "You may be prompted for your system password."

# Create user and database
psql postgres << EOF
-- Drop existing connections to the database if it exists
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE datname = 'blockwire' AND pid <> pg_backend_pid();

-- Drop database if exists
DROP DATABASE IF EXISTS blockwire;

-- Drop user if exists
DROP USER IF EXISTS blockwire;

-- Create user
CREATE USER blockwire WITH PASSWORD 'blockwire123';

-- Create database
CREATE DATABASE blockwire OWNER blockwire;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE blockwire TO blockwire;

-- Show confirmation
\echo 'Database setup complete!'
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Database created successfully${NC}"
else
    echo -e "${RED}✗ Database creation failed${NC}"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "\n${YELLOW}Creating .env file...${NC}"
    cat > .env << EOF
# Flask Configuration
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
FLASK_ENV=development

# Database Configuration
DATABASE_URL=postgresql://blockwire:blockwire123@localhost/blockwire

# Application Settings
ENABLE_REGISTRATION=true
AUTO_UPDATE_NEWS=true
UPDATE_INTERVAL_HOURS=1
EOF
    echo -e "${GREEN}✓ .env file created${NC}"
else
    echo -e "${YELLOW}! .env file already exists, skipping...${NC}"
fi

# Check Python virtual environment
if [ ! -d "venv" ]; then
    echo -e "\n${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment and install dependencies
echo -e "\n${YELLOW}Installing Python dependencies...${NC}"
source venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Initialize database
echo -e "\n${YELLOW}Initializing database...${NC}"
python init_db.py << EOF
y
EOF

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Setup complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "\nTo start the application:"
echo -e "  ${YELLOW}source venv/bin/activate${NC}"
echo -e "  ${YELLOW}python app_enhanced.py${NC}"
echo -e "\nDefault admin credentials:"
echo -e "  Username: ${YELLOW}admin${NC}"
echo -e "  Password: ${YELLOW}changeme123${NC}"
echo -e "\n${RED}⚠️  Remember to change the admin password after first login!${NC}"