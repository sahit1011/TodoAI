"""
Script to run database migrations
"""

from backend.migrations.add_preferred_assistant_mode import run_migration

if __name__ == "__main__":
    print("Running migrations...")
    run_migration()
    print("Migrations completed.")
