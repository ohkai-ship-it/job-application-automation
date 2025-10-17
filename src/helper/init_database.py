"""
Database Initialization Script
Creates the SQLite database with proper schema for job application tracking.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import ApplicationDB


def main():
    """Initialize the production database."""
    print("=" * 80)
    print("DATABASE INITIALIZATION")
    print("=" * 80)
    
    db_path = "data/applications.db"
    
    print(f"\nInitializing database at: {db_path}")
    print("This will create:")
    print("  - processed_jobs table (duplicate detection)")
    print("  - generation_metadata table (AI tracking)")
    print("  - Indexes for fast lookups")
    
    # Create database
    db = ApplicationDB(db_path)
    
    print("\n✅ Database initialized successfully!")
    print(f"\nDatabase file: {Path(db_path).absolute()}")
    print("\nYou can now:")
    print("  1. Start processing jobs (duplicates will be detected)")
    print("  2. View stats: python -c \"from database import get_db; print(get_db().get_stats())\"")
    print("  3. Inspect with SQLite: sqlite3 data/applications.db")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
