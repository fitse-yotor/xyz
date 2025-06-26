#!/usr/bin/env python3
"""
Test Keyword Search Functionality
Debug and test the keyword searching feature
"""

import sqlite3
import os
import json

def test_keyword_search():
    """Test keyword searching functionality"""
    print("🔍 Testing Keyword Search Functionality")
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
        # Check total messages in database
        cursor.execute('SELECT COUNT(*) FROM messages')
        total_messages = cursor.fetchone()[0]
        print(f"\n📊 Total messages in database: {total_messages}")
        
        if total_messages == 0:
            print("❌ No messages found in database. Please scrape some messages first.")
            return
        
        # Check for messages with keywords_matched
        cursor.execute('SELECT COUNT(*) FROM messages WHERE keywords_matched IS NOT NULL AND keywords_matched != ""')
        messages_with_keywords = cursor.fetchone()[0]
        print(f"📋 Messages with keywords_matched: {messages_with_keywords}")
        
        # Show sample messages with keywords
        cursor.execute('''
            SELECT source_name, message_text, keywords_matched 
            FROM messages 
            WHERE keywords_matched IS NOT NULL AND keywords_matched != ""
            LIMIT 5
        ''')
        sample_keyword_messages = cursor.fetchall()
        
        if sample_keyword_messages:
            print(f"\n📝 Sample messages with keywords:")
            for i, msg in enumerate(sample_keyword_messages, 1):
                print(f"\n{i}. Source: {msg[0]}")
                print(f"   Message: {msg[1][:100]}...")
                print(f"   Keywords: {msg[2]}")
        
        # Test specific keywords
        test_keywords = ['tplf', 'tdf', 'ህወሓት', 'TPLF', 'TDF']
        
        print(f"\n🔍 Testing search for keywords: {test_keywords}")
        
        for keyword in test_keywords:
            # Test LIKE search
            cursor.execute('''
                SELECT COUNT(*) FROM messages 
                WHERE message_text LIKE ? OR sender LIKE ?
            ''', (f'%{keyword}%', f'%{keyword}%'))
            
            like_count = cursor.fetchone()[0]
            
            # Test keywords_matched search
            cursor.execute('''
                SELECT COUNT(*) FROM messages 
                WHERE keywords_matched LIKE ?
            ''', (f'%{keyword}%',))
            
            keywords_count = cursor.fetchone()[0]
            
            print(f"\nKeyword: '{keyword}'")
            print(f"  - LIKE search found: {like_count} messages")
            print(f"  - keywords_matched search found: {keywords_count} messages")
            
            # Show sample results for LIKE search
            if like_count > 0:
                cursor.execute('''
                    SELECT source_name, message_text, keywords_matched 
                    FROM messages 
                    WHERE message_text LIKE ? OR sender LIKE ?
                    LIMIT 3
                ''', (f'%{keyword}%', f'%{keyword}%'))
                
                samples = cursor.fetchall()
                print(f"  - Sample LIKE results:")
                for j, sample in enumerate(samples, 1):
                    print(f"    {j}. {sample[0]}: {sample[1][:50]}...")
                    print(f"       Keywords: {sample[2]}")
        
        # Check for case sensitivity issues
        print(f"\n🔍 Testing case sensitivity:")
        
        # Test lowercase
        cursor.execute('SELECT COUNT(*) FROM messages WHERE message_text LIKE ?', ('%tplf%',))
        lowercase_count = cursor.fetchone()[0]
        
        # Test uppercase
        cursor.execute('SELECT COUNT(*) FROM messages WHERE message_text LIKE ?', ('%TPLF%',))
        uppercase_count = cursor.fetchone()[0]
        
        print(f"  - 'tplf' (lowercase): {lowercase_count} messages")
        print(f"  - 'TPLF' (uppercase): {uppercase_count} messages")
        
        # Check for Amharic text
        print(f"\n🔍 Testing Amharic text search:")
        cursor.execute('SELECT COUNT(*) FROM messages WHERE message_text LIKE ?', ('%ህወሓት%',))
        amharic_count = cursor.fetchone()[0]
        print(f"  - 'ህወሓት': {amharic_count} messages")
        
        # Show all unique keywords_matched values
        cursor.execute('''
            SELECT DISTINCT keywords_matched 
            FROM messages 
            WHERE keywords_matched IS NOT NULL AND keywords_matched != ""
            ORDER BY keywords_matched
        ''')
        
        unique_keywords = cursor.fetchall()
        if unique_keywords:
            print(f"\n📋 All unique keywords_matched values:")
            for keyword_set in unique_keywords:
                print(f"  - {keyword_set[0]}")
        
        # Test the search function logic
        print(f"\n🔍 Testing search function logic:")
        
        # Simulate the search function
        query = "tplf"
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM messages
            WHERE message_text LIKE ? OR sender LIKE ?
        ''', (f'%{query}%', f'%{query}%'))
        
        search_count = cursor.fetchone()[0]
        print(f"  - Search function would find: {search_count} messages for '{query}'")
        
        if search_count > 0:
            cursor.execute('''
                SELECT source_type, source_name, message_text, sender, date, scraped_at, keywords_matched
                FROM messages
                WHERE message_text LIKE ? OR sender LIKE ?
                ORDER BY date DESC
                LIMIT 3
            ''', (f'%{query}%', f'%{query}%'))
            
            search_results = cursor.fetchall()
            print(f"  - Sample search results:")
            for i, result in enumerate(search_results, 1):
                print(f"    {i}. Source: {result[1]}")
                print(f"       Message: {result[2][:100]}...")
                print(f"       Keywords: {result[6]}")
        
    except Exception as e:
        print(f"❌ Error testing keyword search: {e}")
    finally:
        conn.close()

def check_keyword_filtering():
    """Check how keyword filtering works during scraping"""
    print(f"\n🔍 Checking Keyword Filtering Logic")
    print("=" * 50)
    
    # Test the check_keywords function logic
    def check_keywords(text, keywords):
        """Check if text contains any of the specified keywords"""
        if not keywords:
            return True, []
        
        text_lower = text.lower()
        matched_keywords = []
        
        for keyword in keywords:
            if keyword.lower() in text_lower:
                matched_keywords.append(keyword)
        
        return len(matched_keywords) > 0, matched_keywords
    
    # Test cases
    test_cases = [
        ("TPLF is mentioned here", ["tplf", "tdf"]),
        ("ህወሓት በዚህ ጊዜ", ["ህወሓት", "tplf"]),
        ("No keywords here", ["tplf", "tdf"]),
        ("TPLF and TDF both mentioned", ["tplf", "tdf"]),
        ("ህወሓት እና TPLF", ["ህወሓት", "tplf"]),
    ]
    
    print("Testing keyword matching logic:")
    for text, keywords in test_cases:
        matches, matched = check_keywords(text, keywords)
        print(f"\nText: '{text}'")
        print(f"Keywords: {keywords}")
        print(f"Matches: {matches}")
        print(f"Matched keywords: {matched}")

def main():
    """Main function"""
    print("=" * 50)
    print("Keyword Search Debug Tool")
    print("=" * 50)
    
    test_keyword_search()
    check_keyword_filtering()
    
    print("\n" + "=" * 50)
    print("Debug completed!")
    print("=" * 50)

if __name__ == "__main__":
    main() 