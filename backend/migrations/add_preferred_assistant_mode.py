"""
Migration script to add preferred_assistant_mode column to users table
"""

from sqlalchemy import create_engine, MetaData, Table, Column, String, text
from backend.config import ASSISTANT_MODES
from backend.database import DATABASE_URL

def run_migration():
    """Run the migration to add preferred_assistant_mode column to users table"""
    # Create engine and connect to the database
    engine = create_engine(DATABASE_URL)

    # Create a metadata object
    metadata = MetaData()

    # Reflect the users table
    users = Table('users', metadata, autoload_with=engine)

    # Check if the column already exists
    if 'preferred_assistant_mode' not in users.columns:
        # Add the column
        with engine.begin() as conn:
            conn.execute(
                text(f"ALTER TABLE users ADD COLUMN preferred_assistant_mode VARCHAR(10) DEFAULT '{ASSISTANT_MODES['ACT']}'")
            )
            print("Added preferred_assistant_mode column to users table")
    else:
        print("preferred_assistant_mode column already exists in users table")

if __name__ == "__main__":
    run_migration()
