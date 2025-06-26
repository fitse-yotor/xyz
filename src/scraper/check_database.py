#!/usr/bin/env python3
"""
Database Structure Check Script
Check what tables and columns exist in the database
"""

import sqlite3
import os

def check_database_structure():
    """Check the database structure and tables"""
    print("🔍 Checking database structure...")
    
    # Get the database file path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, 'data')
    db_file = os.path.join(data_dir, 'telegram_messages.db')
    
    if not os.path.exists(db_file):
        print(f"❌ Database file not found: {db_file}")
        return
    
    print(f"✅ Database file found: {db_file}")
    
    # Connect to database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    try:
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"\n📋 Found {len(tables)} tables:")
        
        for table in tables:
            table_name = table[0]
            print(f"\n📄 Table: {table_name}")
            
            # Get columns for this table
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print(f"   Columns ({len(columns)}):")
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                not_null_str = " NOT NULL" if not_null else ""
                pk_str = " PRIMARY KEY" if pk else ""
                print(f"     - {col_name} ({col_type}){not_null_str}{pk_str}")
                
                # Highlight source_name column
                if col_name == 'source_name':
                    print(f"       ⭐ This is the source_name column!")
        
        # Check for source_name column specifically
        print(f"\n🔍 Looking for 'source_name' column:")
        source_name_found = False
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            for col in columns:
                if col[1] == 'source_name':
                    source_name_found = True
                    print(f"   ✅ Found 'source_name' in table '{table_name}'")
                    print(f"      Type: {col[2]}")
                    print(f"      NOT NULL: {col[3]}")
        
        if not source_name_found:
            print("   ❌ 'source_name' column not found in any table")
        
        # Check sample data
        print(f"\n📊 Sample data check:")
        for table in tables:
            table_name = table[0]
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"   Table '{table_name}': {count} rows")
                
                if count > 0:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
                    sample = cursor.fetchone()
                    print(f"     Sample row: {sample}")
            except Exception as e:
                print(f"   Error checking table '{table_name}': {e}")
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
    finally:
        conn.close()

def main():
    """Main function"""
    print("=" * 50)
    print("Database Structure Checker")
    print("=" * 50)
    
    check_database_structure()
    
    print("\n" + "=" * 50)
    print("Check completed!")
    print("=" * 50)

if __name__ == "__main__":
    main() 