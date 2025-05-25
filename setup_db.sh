#!/bin/bash

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "PostgreSQL is not installed. Please install it first."
    exit 1
fi

# Update the .env file with the correct database URL
echo "Updating database configuration..."
sed -i "s|DATABASE_URL=postgresql://postgres:password@localhost/todo_ai|DATABASE_URL=postgresql:///$USER|" .env

# Create tables
echo "Creating tables..."
source venv/bin/activate
python3 -c "from backend.database import Base, engine; from backend.models.user import User; from backend.models.task import Task; Base.metadata.create_all(bind=engine)"

echo "Database setup complete!"
