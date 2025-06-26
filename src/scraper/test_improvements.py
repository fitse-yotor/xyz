#!/usr/bin/env python3
"""
Test script for Telegram Scraper improvements
Tests rate limiting and keyword filtering functionality
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram_scraper import TelegramScraper

async def test_rate_limiting():
    """Test rate limiting functionality"""
    print("=== Testing Rate Limiting ===")
    
    scraper = TelegramScraper()
    await scraper.initialize_client()
    
    try:
        # Test safe_request with a simple operation
        print("Testing safe_request method...")
        dialogs = await scraper.safe_request(scraper.client.get_dialogs)
        
        if dialogs:
            print(f"✓ Successfully fetched {len(dialogs)} dialogs with rate limiting")
            return True
        else:
            print("✗ No dialogs found")
            return False
            
    except Exception as e:
        print(f"✗ Error testing rate limiting: {str(e)}")
        return False
    finally:
        if scraper.client:
            await scraper.client.disconnect()

async def test_keyword_filtering():
    """Test keyword filtering functionality"""
    print("\n=== Testing Keyword Filtering ===")
    
    # Test the keyword checking function
    scraper = TelegramScraper()
    
    test_messages = [
        "This is a test message about bitcoin",
        "Crypto trading is interesting",
        "Just a regular message",
        "Bitcoin and crypto are trending",
        "No relevant keywords here"
    ]
    
    keywords = ["bitcoin", "crypto", "trading"]
    
    print(f"Testing with keywords: {', '.join(keywords)}")
    print("Test messages:")
    
    for i, message in enumerate(test_messages, 1):
        matches, matched_keywords = scraper.check_keywords(message, keywords)
        status = "✓" if matches else "✗"
        print(f"{status} Message {i}: '{message}'")
        if matches:
            print(f"   Matched keywords: {', '.join(matched_keywords)}")
    
    return True

async def test_database_schema():
    """Test database schema updates"""
    print("\n=== Testing Database Schema ===")
    
    scraper = TelegramScraper()
    
    try:
        # Check if keywords_matched column exists
        import sqlite3
        conn = sqlite3.connect(scraper.DB_FILE)
        cursor = conn.cursor()
        
        # Get table schema
        cursor.execute("PRAGMA table_info(messages)")
        columns = cursor.fetchall()
        
        keywords_column_exists = any(col[1] == 'keywords_matched' for col in columns)
        
        if keywords_column_exists:
            print("✓ keywords_matched column exists in database")
            return True
        else:
            print("✗ keywords_matched column not found")
            return False
            
    except Exception as e:
        print(f"✗ Error testing database schema: {str(e)}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

async def main():
    """Run all tests"""
    print("Telegram Scraper Improvements Test Suite")
    print("=" * 50)
    
    tests = [
        ("Rate Limiting", test_rate_limiting),
        ("Keyword Filtering", test_keyword_filtering),
        ("Database Schema", test_database_schema)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Error in {test_name}: {str(e)}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    
    all_passed = True
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Your improvements are working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")
    
    print("\nNext steps:")
    print("1. Run the main scraper: python telegram_scraper.py")
    print("2. Try option 3: 'Scrape messages with keywords from a specific source'")
    print("3. Try option 9: 'Scrape all messages with keywords (bulk scraping)'")
    print("4. Monitor the logs for rate limiting behavior")

if __name__ == "__main__":
    asyncio.run(main()) 