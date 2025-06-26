#!/usr/bin/env python3
"""
Scrape Messages with Keywords
Helper script to scrape messages containing specific keywords
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram_scraper import TelegramScraper

async def scrape_with_keywords():
    """Scrape messages with specific keywords"""
    print("🔍 Scraping Messages with Keywords")
    print("=" * 50)
    
    # Define keywords - FOCUSED on specific terms only
    keywords = ['tplf', 'tdf', 'ህወሓት']
    
    print(f"📋 Keywords to search for: {', '.join(keywords)}")
    print("This will scrape messages containing any of these keywords ONLY.")
    print("Keywords: tplf, tdf, ህወሓት")
    
    # Initialize scraper
    scraper = TelegramScraper()
    await scraper.initialize_client()
    
    try:
        # List available sources
        print("\n📋 Available sources:")
        dialogs = await scraper.list_dialogs()
        
        if not dialogs:
            print("❌ No dialogs found")
            return
        
        # Ask user to choose source
        print(f"\nChoose a source to scrape (1-{len(dialogs)}):")
        print("Or enter 'bulk' to scrape all sources with keywords")
        
        choice = input("Your choice: ").strip().lower()
        
        if choice == 'bulk':
            print(f"\n🚀 Starting bulk scraping with keywords: {', '.join(keywords)}")
            total_messages = await scraper.scrape_all_sources(keywords)
            print(f"✅ Bulk scraping completed. Total messages with keywords: {total_messages}")
            
        else:
            try:
                index = int(choice) - 1
                if 0 <= index < len(dialogs):
                    selected_dialog = dialogs[index]
                    print(f"\n🚀 Scraping {selected_dialog.name} with keywords: {', '.join(keywords)}")
                    
                    success, count, csv_file = await scraper.scrape_source(selected_dialog.entity, keywords)
                    
                    if success:
                        print(f"✅ Successfully scraped {count} messages with keywords from {selected_dialog.name}")
                        print(f"📄 Results saved to: {csv_file}")
                    else:
                        print(f"❌ Failed to scrape from {selected_dialog.name}")
                else:
                    print("❌ Invalid selection")
            except ValueError:
                print("❌ Invalid input")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if scraper.client:
            await scraper.client.disconnect()

def main():
    """Main function"""
    print("=" * 50)
    print("Keyword-Based Message Scraper")
    print("=" * 50)
    
    asyncio.run(scrape_with_keywords())
    
    print("\n" + "=" * 50)
    print("Scraping completed!")
    print("=" * 50)

if __name__ == "__main__":
    main() 