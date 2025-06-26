#!/usr/bin/env python3
"""
Database Schema Fix Script
Adds missing columns to the messages table
"""

import sqlite3
import os
from datetime import datetime

def fix_database_schema():
    """Fix the database schema by adding missing columns"""
    print("🔧 Fixing database schema...")
    
    # Get the database file path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, 'data')
    db_file = os.path.join(data_dir, 'telegram_messages.db')
    
    # Create data directory if it doesn't exist
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"✓ Created data directory: {data_dir}")
    
    # Connect to database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    try:
        # Check if messages table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages'")
        if not cursor.fetchone():
            print("❌ Messages table does not exist. Creating it...")
            create_messages_table(cursor)
        else:
            print("✓ Messages table exists")
        
        # Get current columns in messages table
        cursor.execute("PRAGMA table_info(messages)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Current columns: {columns}")
        
        # Add missing columns for the simplified schema
        missing_columns = []
        
        if 'keywords_matched' not in columns:
            missing_columns.append('keywords_matched TEXT')
        
        # Add missing columns
        for column_def in missing_columns:
            column_name = column_def.split()[0]
            try:
                cursor.execute(f"ALTER TABLE messages ADD COLUMN {column_def}")
                print(f"✓ Added column: {column_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"ℹ️  Column {column_name} already exists")
                else:
                    print(f"⚠️  Error adding column {column_name}: {e}")
        
        # Commit changes
        conn.commit()
        
        # Verify the fix
        cursor.execute("PRAGMA table_info(messages)")
        final_columns = [column[1] for column in cursor.fetchall()]
        print(f"\n✅ Final columns: {final_columns}")
        
        if 'keywords_matched' in final_columns:
            print("✅ Database schema fixed successfully!")
            print("🔄 You can now run the scraper without errors")
        else:
            print("❌ Failed to add keywords_matched column")
        
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        conn.rollback()
    finally:
        conn.close()

def create_messages_table(cursor):
    """Create the messages table with the simplified schema"""
    create_table_sql = '''
        CREATE TABLE messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_type TEXT NOT NULL,
            source_name TEXT NOT NULL,
            message_text TEXT NOT NULL,
            sender TEXT,
            date TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            keywords_matched TEXT
        )
    '''
    
    cursor.execute(create_table_sql)
    print("✓ Created messages table with simplified schema")

def main():
    """Main function"""
    print("=" * 50)
    print("Database Schema Fix Tool")
    print("=" * 50)
    
    fix_database_schema()
    
    print("\n" + "=" * 50)
    print("Fix completed!")
    print("=" * 50)

if __name__ == "__main__":
    main() 