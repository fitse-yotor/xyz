#!/usr/bin/env python3
"""
Debug script to diagnose empty CSV files after scraping
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram_scraper import TelegramScraper

async def debug_scraping():
    """Debug the scraping process to identify why CSV files are empty"""
    print("🔍 Debugging Telegram Scraper - Empty CSV Issue")
    print("=" * 60)
    
    scraper = TelegramScraper()
    
    try:
        # Initialize client
        print("1. Initializing Telegram client...")
        await scraper.initialize_client()
        print("✅ Client initialized successfully")
        
        # List dialogs
        print("\n2. Fetching available dialogs...")
        dialogs = await scraper.list_dialogs()
        
        if not dialogs:
            print("❌ No dialogs found! This could be the issue.")
            print("   - Check if your account has access to any channels/groups")
            print("   - Verify your account is not restricted")
            return
        
        print(f"✅ Found {len(dialogs)} dialogs")
        
        # Test with first dialog
        if dialogs:
            test_dialog = dialogs[0]
            print(f"\n3. Testing with first dialog: {test_dialog.name}")
            
            # Test message fetching
            print("   Fetching messages...")
            messages = await scraper.safe_request(
                scraper.client.get_messages,
                test_dialog.entity,
                limit=5  # Just 5 messages for testing
            )
            
            if not messages:
                print("❌ No messages found in this dialog!")
                print("   Possible reasons:")
                print("   - Dialog is empty")
                print("   - No text messages (only media)")
                print("   - Access restrictions")
                return
            
            print(f"✅ Found {len(messages)} messages")
            
            # Check message content
            text_messages = 0
            for msg in messages:
                if msg.text:
                    text_messages += 1
                    print(f"   Sample message: {msg.text[:50]}...")
            
            print(f"✅ {text_messages} messages contain text")
            
            if text_messages == 0:
                print("❌ No text messages found!")
                print("   - All messages might be media-only")
                print("   - Try a different channel/group")
                return
            
            # Test keyword filtering
            print("\n4. Testing keyword filtering...")
            test_keywords = ["test", "hello", "message"]
            for msg in messages[:3]:  # Test first 3 messages
                if msg.text:
                    matches, matched = scraper.check_keywords(msg.text, test_keywords)
                    print(f"   Message: '{msg.text[:30]}...'")
                    print(f"   Matches keywords: {matches}, Matched: {matched}")
            
            print("\n5. Testing CSV creation...")
            
            # Create a test CSV
            csv_dir = os.path.join(scraper.DATA_DIR, 'debug_test')
            if not os.path.exists(csv_dir):
                os.makedirs(csv_dir)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            test_csv = os.path.join(csv_dir, f"debug_test_{timestamp}.csv")
            
            import csv
            with open(test_csv, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Source Type', 'Source Name', 'Message', 'Sender', 'Date', 'Scraped At', 'Keywords Matched'])
                
                for msg in messages:
                    if msg.text:
                        clean_text = scraper.remove_emoji(msg.text)
                        writer.writerow([
                            'test',
                            test_dialog.name,
                            clean_text,
                            msg.sender_id if msg.sender_id else None,
                            msg.date.strftime("%Y-%m-%d %H:%M:%S"),
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'test'
                        ])
            
            # Check if CSV was created and has content
            if os.path.exists(test_csv):
                file_size = os.path.getsize(test_csv)
                print(f"✅ Test CSV created: {test_csv}")
                print(f"   File size: {file_size} bytes")
                
                if file_size > 0:
                    print("✅ CSV has content!")
                else:
                    print("❌ CSV is empty!")
            else:
                print("❌ CSV file was not created!")
            
            print(f"\n6. Checking database...")
            try:
                import sqlite3
                conn = sqlite3.connect(scraper.DB_FILE)
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*) FROM messages')
                total_messages = cursor.fetchone()[0]
                print(f"✅ Database has {total_messages} messages")
                
                if total_messages > 0:
                    cursor.execute('SELECT source_name, message_text FROM messages LIMIT 3')
                    sample_messages = cursor.fetchall()
                    print("   Sample messages in database:")
                    for msg in sample_messages:
                        print(f"   - {msg[0]}: {msg[1][:50]}...")
                
                conn.close()
            except Exception as e:
                print(f"❌ Database error: {str(e)}")
        
        print("\n" + "=" * 60)
        print("🔍 DIAGNOSIS SUMMARY:")
        print("=" * 60)
        
        if not dialogs:
            print("❌ ISSUE: No dialogs found")
            print("   SOLUTION: Check account access and restrictions")
        elif not messages:
            print("❌ ISSUE: No messages found in dialogs")
            print("   SOLUTION: Try different channels/groups")
        elif text_messages == 0:
            print("❌ ISSUE: No text messages found")
            print("   SOLUTION: Channels may have only media content")
        else:
            print("✅ Messages found and accessible")
            print("   Check if keyword filtering is too restrictive")
            print("   Try scraping without keywords first")
        
        print("\n📋 NEXT STEPS:")
        print("1. Try scraping without keywords (Option 2)")
        print("2. Check the logs in telegram_scraper.log")
        print("3. Try a different channel/group")
        print("4. Verify your account has proper access")
        
    except Exception as e:
        print(f"❌ Error during debugging: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        if scraper.client:
            await scraper.client.disconnect()

if __name__ == "__main__":
    asyncio.run(debug_scraping()) 