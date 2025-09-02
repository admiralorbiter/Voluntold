#!/usr/bin/env python3
"""
Database migration script to add virtual event fields to the upcoming_events table.
This script adds the new columns needed for virtual events support.
"""

import os
import sys
import sqlite3
from datetime import datetime

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def migrate_database():
    """Add virtual event columns to the upcoming_events table"""
    
    # Database path
    db_path = os.path.join(project_root, "instance", "your_database.db")
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        print("Please run the app first to create the database.")
        return False
    
    print(f"📊 Migrating database: {db_path}")
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(upcoming_events)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"📋 Current columns: {columns}")
        
        # Define the new columns to add
        new_columns = [
            ("source", "VARCHAR(20) DEFAULT 'salesforce'"),
            ("spreadsheet_id", "VARCHAR(255)"),
            ("presenter_name", "VARCHAR(255)"),
            ("presenter_organization", "VARCHAR(255)"),
            ("presenter_location", "VARCHAR(100)"),
            ("topic_theme", "VARCHAR(255)"),
            ("teacher_name", "VARCHAR(255)"),
            ("school_level", "VARCHAR(50)")
        ]
        
        # Add columns that don't exist
        added_columns = []
        for column_name, column_type in new_columns:
            if column_name not in columns:
                try:
                    alter_sql = f"ALTER TABLE upcoming_events ADD COLUMN {column_name} {column_type}"
                    cursor.execute(alter_sql)
                    added_columns.append(column_name)
                    print(f"✅ Added column: {column_name}")
                except sqlite3.Error as e:
                    print(f"❌ Error adding column {column_name}: {e}")
            else:
                print(f"⏭️  Column {column_name} already exists")
        
        # Make salesforce_id nullable (it's currently NOT NULL)
        try:
            # SQLite doesn't support ALTER COLUMN, so we need to recreate the table
            print("🔄 Making salesforce_id nullable...")
            
            # Get the current table structure
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='upcoming_events'")
            create_sql = cursor.fetchone()[0]
            
            # Replace NOT NULL with NULL for salesforce_id
            new_create_sql = create_sql.replace(
                "salesforce_id VARCHAR(18) UNIQUE NOT NULL",
                "salesforce_id VARCHAR(18) UNIQUE"
            )
            
            # Create new table with updated structure
            cursor.execute("CREATE TABLE upcoming_events_new AS SELECT * FROM upcoming_events")
            cursor.execute("DROP TABLE upcoming_events")
            cursor.execute(new_create_sql.replace("upcoming_events", "upcoming_events_new"))
            cursor.execute("INSERT INTO upcoming_events SELECT * FROM upcoming_events_new")
            cursor.execute("DROP TABLE upcoming_events_new")
            
            print("✅ Made salesforce_id nullable")
            
        except sqlite3.Error as e:
            print(f"⚠️  Warning: Could not make salesforce_id nullable: {e}")
            print("   This is not critical for virtual events functionality")
        
        # Create indexes for new columns
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_upcoming_events_source ON upcoming_events(source)")
            print("✅ Created index on source column")
        except sqlite3.Error as e:
            print(f"⚠️  Warning: Could not create index on source: {e}")
        
        # Commit changes
        conn.commit()
        
        # Verify the changes
        cursor.execute("PRAGMA table_info(upcoming_events)")
        updated_columns = [column[1] for column in cursor.fetchall()]
        
        print(f"\n📋 Updated columns: {updated_columns}")
        
        if added_columns:
            print(f"\n🎉 Migration completed successfully!")
            print(f"✅ Added {len(added_columns)} new columns: {', '.join(added_columns)}")
        else:
            print(f"\n✅ Migration completed - no new columns needed")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def backup_database():
    """Create a backup of the database before migration"""
    db_path = os.path.join(project_root, "instance", "your_database.db")
    backup_path = os.path.join(project_root, "instance", f"your_database_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
    
    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"💾 Database backed up to: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"⚠️  Warning: Could not create backup: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Starting Virtual Events Database Migration")
    print("=" * 50)
    
    # Create backup
    backup_path = backup_database()
    
    # Run migration
    success = migrate_database()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        if backup_path:
            print(f"💾 Backup available at: {backup_path}")
        print("\n✅ You can now run the virtual event model test.")
    else:
        print("\n❌ Migration failed!")
        if backup_path:
            print(f"💾 You can restore from backup: {backup_path}")
        sys.exit(1)
