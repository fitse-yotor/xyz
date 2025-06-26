#!/usr/bin/env python3
"""
Check Messages in Database
See what messages are currently stored
"""

import sqlite3
import os

def check_messages():
    """Check what messages are in the database"""
    print("📋 Checking Messages in Database")
    print("=" * 50)
    
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
        # Get total count
        cursor.execute('SELECT COUNT(*) FROM messages')
        total_count = cursor.fetchone()[0]
        print(f"\n📊 Total messages: {total_count}")
        
        if total_count == 0:
            print("❌ No messages found in database")
            return
        
        # Get all messages
        cursor.execute('''
            SELECT source_name, message_text, sender, date, keywords_matched
            FROM messages
            ORDER BY date DESC
        ''')
        
        messages = cursor.fetchall()
        
        print(f"\n📝 All messages in database:")
        for i, msg in enumerate(messages, 1):
            print(f"\n{i}. Source: {msg[0]}")
            print(f"   Message: {msg[1]}")
            print(f"   Sender: {msg[2]}")
            print(f"   Date: {msg[3]}")
            print(f"   Keywords: {msg[4]}")
            print("-" * 40)
        
        # Check sources
        cursor.execute('SELECT DISTINCT source_name FROM messages')
        sources = cursor.fetchall()
        print(f"\n📋 Sources in database:")
        for source in sources:
            print(f"  - {source[0]}")
        
        # Check for any messages containing your keywords
        keywords_to_check = ['tplf', 'tdf', 'ህወሓት', 'TPLF', 'TDF', 'tigray', 'ethiopia']
        
        print(f"\n🔍 Checking for keywords in existing messages:")
        for keyword in keywords_to_check:
            cursor.execute('''
                SELECT COUNT(*) FROM messages 
                WHERE message_text LIKE ?
            ''', (f'%{keyword}%',))
            
            count = cursor.fetchone()[0]
            if count > 0:
                print(f"  ✅ '{keyword}': {count} messages")
                
                # Show sample
                cursor.execute('''
                    SELECT source_name, message_text 
                    FROM messages 
                    WHERE message_text LIKE ?
                    LIMIT 1
                ''', (f'%{keyword}%',))
                
                sample = cursor.fetchone()
                if sample:
                    print(f"     Sample: {sample[1][:100]}...")
            else:
                print(f"  ❌ '{keyword}': 0 messages")
        
    except Exception as e:
        print(f"❌ Error checking messages: {e}")
    finally:
        conn.close()

def main():
    """Main function"""
    print("=" * 50)
    print("Message Checker")
    print("=" * 50)
    
    check_messages()
    
    print("\n" + "=" * 50)
    print("Check completed!")
    print("=" * 50)

if __name__ == "__main__":
    main() 