import asyncio
import logging
from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel, PeerChat, PeerUser
import sqlite3
import os
from datetime import datetime
import csv
import json
import re
import emoji

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='telegram_scraper.log'
)
logger = logging.getLogger(__name__)

# Telegram API credentials
API_ID = '29621739'
API_HASH = 'ba5a611c63982176cdc2f06fea026090'

# Get the absolute path of the current script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, 'data')
DB_FILE = os.path.join(DATA_DIR, 'telegram_messages.db')

class TelegramScraper:
    def __init__(self):
        self.client = None
        self.setup_database()

    def setup_database(self):
        """Set up the database and create necessary tables"""
        try:
            if not os.path.exists(DATA_DIR):
                os.makedirs(DATA_DIR)
                logger.info(f"Created data directory at: {DATA_DIR}")

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            # Create messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_type TEXT NOT NULL,
                    source_name TEXT NOT NULL,
                    message_text TEXT NOT NULL,
                    sender TEXT,
                    date TEXT,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create sources table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_type TEXT NOT NULL,
                    source_name TEXT UNIQUE NOT NULL,
                    last_scraped TIMESTAMP,
                    message_count INTEGER DEFAULT 0
                )
            ''')

            # Create search index
            cursor.execute('''
                CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts 
                USING fts5(source_type, source_name, message_text, sender, date)
            ''')

            conn.commit()
            logger.info("Database setup completed successfully")
            return conn

        except Exception as e:
            logger.error(f"Error setting up database: {str(e)}")
            raise
        finally:
            if 'conn' in locals():
                conn.close()

    def remove_emoji(self, text):
        """Remove emojis from text"""
        return emoji.replace_emoji(text, '')

    def search_messages(self, query, source_name=None, limit=1000):
        """Search messages in the database with increased limit"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # First, get the total count of matching messages
            if source_name:
                cursor.execute('''
                    SELECT COUNT(*) as count
                    FROM messages
                    WHERE (source_name = ?) AND (message_text LIKE ? OR sender LIKE ?)
                ''', (source_name, f'%{query}%', f'%{query}%'))
            else:
                cursor.execute('''
                    SELECT COUNT(*) as count
                    FROM messages
                    WHERE message_text LIKE ? OR sender LIKE ?
                ''', (f'%{query}%', f'%{query}%'))
            
            total_matches = cursor.fetchone()[0]
            
            if total_matches == 0:
                print("No messages found matching your search!")
                input("\nPress Enter to return to main menu...")
                return
            
            print(f"\nFound {total_matches} matching messages")
            
            # Ask user for the number of messages to display
            if total_matches > limit:
                print(f"\nMaximum limit is {limit} messages")
                try:
                    user_limit = int(input(f"How many messages would you like to see? (1-{limit}): "))
                    if user_limit > limit:
                        print(f"Limit exceeded. Setting to maximum of {limit} messages")
                        user_limit = limit
                    elif user_limit < 1:
                        print("Invalid input. Setting to default of 50 messages")
                        user_limit = 50
                except ValueError:
                    print("Invalid input. Setting to default of 50 messages")
                    user_limit = 50
            else:
                user_limit = total_matches
            
            # Get the messages
            if source_name:
                cursor.execute('''
                    SELECT source_type, source_name, message_text, sender, date, scraped_at
                    FROM messages
                    WHERE (source_name = ?) AND (message_text LIKE ? OR sender LIKE ?)
                    ORDER BY date DESC
                    LIMIT ?
                ''', (source_name, f'%{query}%', f'%{query}%', user_limit))
            else:
                cursor.execute('''
                    SELECT source_type, source_name, message_text, sender, date, scraped_at
                    FROM messages
                    WHERE message_text LIKE ? OR sender LIKE ?
                    ORDER BY date DESC
                    LIMIT ?
                ''', (f'%{query}%', f'%{query}%', user_limit))
            
            messages = cursor.fetchall()
            
            print(f"\n=== Search Results for '{query}' ===")
            print(f"Showing {len(messages)} of {total_matches} matches")
            
            for msg in messages:
                print("\n" + "="*50)
                print(f"Source: {msg[1]} ({msg[0]})")
                print(f"Message: {msg[2]}")
                print(f"Sender: {msg[3]}")
                print(f"Date: {msg[4]}")
                print(f"Scraped At: {msg[5]}")
            
            # Export search results to CSV
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            csv_dir = os.path.join(DATA_DIR, 'search_results')
            if not os.path.exists(csv_dir):
                os.makedirs(csv_dir)
            
            csv_file = os.path.join(csv_dir, f"search_{query}_{timestamp}.csv")
            with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Source Type', 'Source Name', 'Message', 'Sender', 'Date', 'Scraped At'])
                writer.writerows(messages)
            
            print(f"\nSearch results exported to: {csv_file}")
            input("\nPress Enter to return to main menu...")
            
        except Exception as e:
            logger.error(f"Error searching messages: {str(e)}")
            print(f"Error searching messages: {str(e)}")
            input("\nPress Enter to return to main menu...")
        finally:
            if 'conn' in locals():
                conn.close()

    async def initialize_client(self):
        """Initialize the Telegram client"""
        self.client = TelegramClient('anon', API_ID, API_HASH)
        await self.client.start()
        logger.info("Telegram client initialized successfully")

    async def list_dialogs(self):
        """List all available chats and channels"""
        try:
            dialogs = await self.client.get_dialogs()
            print("\n=== Available Chats and Channels ===")
            for i, dialog in enumerate(dialogs, 1):
                print(f"{i}. {dialog.name} ({dialog.entity.__class__.__name__})")
            return dialogs
        except Exception as e:
            logger.error(f"Error listing dialogs: {str(e)}")
            return []

    async def scrape_source(self, source_entity):
        """Scrape messages from a source (group or channel)"""
        try:
            source_name = source_entity.title if hasattr(source_entity, 'title') else source_entity.username
            source_type = 'channel' if isinstance(source_entity, PeerChannel) else 'group'

            # Get messages
            messages = await self.client.get_messages(source_entity, limit=100)
            
            # Store in database and CSV
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # Prepare CSV file
            csv_dir = os.path.join(DATA_DIR, 'exports')
            if not os.path.exists(csv_dir):
                os.makedirs(csv_dir)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            csv_file = os.path.join(csv_dir, f"{source_name}_{timestamp}.csv")
            
            message_count = 0
            with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Source Type', 'Source Name', 'Message', 'Sender', 'Date', 'Scraped At'])
                
                for message in messages:
                    if message.text:
                        # Remove emojis from message text
                        clean_text = self.remove_emoji(message.text)
                        
                        # Store in database
                        cursor.execute('''
                            INSERT INTO messages (source_type, source_name, message_text, sender, date)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (
                            source_type,
                            source_name,
                            clean_text,
                            message.sender_id if message.sender_id else None,
                            message.date.strftime("%Y-%m-%d %H:%M:%S")
                        ))
                        
                        # Write to CSV
                        writer.writerow([
                            source_type,
                            source_name,
                            clean_text,
                            message.sender_id if message.sender_id else None,
                            message.date.strftime("%Y-%m-%d %H:%M:%S"),
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        ])
                        
                        message_count += 1
            
            # Update source statistics
            cursor.execute('''
                INSERT OR REPLACE INTO sources (source_type, source_name, last_scraped, message_count)
                VALUES (?, ?, CURRENT_TIMESTAMP, ?)
            ''', (source_type, source_name, message_count))
            
            conn.commit()
            logger.info(f"Successfully scraped {message_count} messages from {source_name}")
            return True, message_count, csv_file
            
        except Exception as e:
            logger.error(f"Error scraping source {source_name}: {str(e)}")
            return False, 0, None
        finally:
            if 'conn' in locals():
                conn.close()

    def view_statistics(self):
        """View scraping statistics"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # Get source statistics
            cursor.execute('''
                SELECT source_type, source_name, message_count, last_scraped
                FROM sources
                ORDER BY last_scraped DESC
            ''')
            
            sources = cursor.fetchall()
            
            if not sources:
                print("No sources have been scraped yet!")
                input("\nPress Enter to return to main menu...")
                return
            
            print("\n=== Scraping Statistics ===")
            print(f"Total sources: {len(sources)}")
            
            for source in sources:
                print("\n" + "="*50)
                print(f"Source: {source[1]} ({source[0]})")
                print(f"Message Count: {source[2]}")
                print(f"Last Scraped: {source[3]}")
            
            input("\nPress Enter to return to main menu...")
            
        except Exception as e:
            logger.error(f"Error viewing statistics: {str(e)}")
            print(f"Error viewing statistics: {str(e)}")
            input("\nPress Enter to return to main menu...")
        finally:
            if 'conn' in locals():
                conn.close()

    def view_database_contents(self, source_name=None, limit=50):
        """View contents of the database"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            if source_name:
                cursor.execute('''
                    SELECT source_type, source_name, message_text, sender, date
                    FROM messages
                    WHERE source_name = ?
                    ORDER BY date DESC
                    LIMIT ?
                ''', (source_name, limit))
            else:
                cursor.execute('''
                    SELECT source_type, source_name, message_text, sender, date
                    FROM messages
                    ORDER BY date DESC
                    LIMIT ?
                ''', (limit,))
            
            messages = cursor.fetchall()
            
            if not messages:
                print("No messages found!")
                input("\nPress Enter to return to main menu...")
                return
            
            print("\n=== Database Contents ===")
            for msg in messages:
                print("\n" + "="*50)
                print(f"Source: {msg[1]} ({msg[0]})")
                print(f"Message: {msg[2]}")
                print(f"Sender: {msg[3]}")
                print(f"Date: {msg[4]}")
            
            input("\nPress Enter to return to main menu...")
            
        except Exception as e:
            logger.error(f"Error viewing database contents: {str(e)}")
            print(f"Error viewing database contents: {str(e)}")
            input("\nPress Enter to return to main menu...")
        finally:
            if 'conn' in locals():
                conn.close()

    def get_database_stats(self):
        """Get statistics about the database contents"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # Get total message count
            cursor.execute('SELECT COUNT(*) FROM messages')
            total_messages = cursor.fetchone()[0]
            
            # Get message count by source
            cursor.execute('''
                SELECT source_name, COUNT(*) as count
                FROM messages
                GROUP BY source_name
                ORDER BY count DESC
            ''')
            source_stats = cursor.fetchall()
            
            # Get date range
            cursor.execute('''
                SELECT MIN(date), MAX(date)
                FROM messages
            ''')
            date_range = cursor.fetchone()
            
            print("\n=== Database Statistics ===")
            print(f"Total Messages: {total_messages}")
            print("\nMessages by Source:")
            for source in source_stats:
                print(f"{source[0]}: {source[1]} messages")
            
            if date_range[0] and date_range[1]:
                print(f"\nDate Range: {date_range[0]} to {date_range[1]}")
            
        except Exception as e:
            logger.error(f"Error getting database statistics: {str(e)}")
            print(f"Error getting database statistics: {str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    async def handle_new_message(self, event):
        """Handle new incoming messages in real-time"""
        try:
            message = event.message
            chat = await event.get_chat()
            
            # Determine source type and name
            if isinstance(chat, PeerChannel):
                source_type = 'channel'
                source_name = chat.title
            elif isinstance(chat, PeerChat):
                source_type = 'group'
                source_name = chat.title
            else:
                source_type = 'personal'
                source_name = chat.username or str(chat.id)

            if message.text:
                # Remove emojis from message text
                clean_text = self.remove_emoji(message.text)
                
                # Store in database
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO messages (source_type, source_name, message_text, sender, date)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    source_type,
                    source_name,
                    clean_text,
                    message.sender_id if message.sender_id else None,
                    message.date.strftime("%Y-%m-%d %H:%M:%S")
                ))
                
                # Update source statistics
                cursor.execute('''
                    INSERT OR REPLACE INTO sources (source_type, source_name, last_scraped, message_count)
                    VALUES (?, ?, CURRENT_TIMESTAMP, 
                        (SELECT COALESCE(MAX(message_count), 0) + 1 
                         FROM sources 
                         WHERE source_name = ?))
                ''', (source_type, source_name, source_name))
                
                conn.commit()
                
                # Store in real-time CSV file
                csv_dir = os.path.join(DATA_DIR, 'realtime')
                if not os.path.exists(csv_dir):
                    os.makedirs(csv_dir)
                
                csv_file = os.path.join(csv_dir, 'realtime_messages.csv')
                file_exists = os.path.exists(csv_file)
                
                with open(csv_file, 'a', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    if not file_exists:
                        writer.writerow(['Source Type', 'Source Name', 'Message', 'Sender', 'Date', 'Received At'])
                    
                    writer.writerow([
                        source_type,
                        source_name,
                        clean_text,
                        message.sender_id if message.sender_id else None,
                        message.date.strftime("%Y-%m-%d %H:%M:%S"),
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ])
                
                logger.info(f"New message received from {source_name}: {clean_text[:50]}...")
                print(f"\nNew message from {source_name}: {clean_text[:100]}...")
                
        except Exception as e:
            logger.error(f"Error handling new message: {str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    async def start_realtime_scraping(self):
        """Start real-time message scraping"""
        try:
            # Register event handler for new messages
            @self.client.on(events.NewMessage)
            async def new_message_handler(event):
                await self.handle_new_message(event)
            
            logger.info("Real-time message scraping started")
            print("Real-time message scraping is now active. Press Ctrl+C to stop.")
            
            # Keep the script running
            await self.client.run_until_disconnected()
            
        except Exception as e:
            logger.error(f"Error in real-time scraping: {str(e)}")
            print(f"Error in real-time scraping: {str(e)}")

    async def scrape_all_sources(self):
        """Scrape messages from all available sources and store in a single CSV file"""
        try:
            print("\nFetching all available chats and channels...")
            dialogs = await self.client.get_dialogs()
            
            if not dialogs:
                print("No chats or channels found!")
                return
            
            total_messages = 0
            successful_sources = 0
            failed_sources = 0
            
            # Create a single CSV file for all messages
            csv_dir = os.path.join(DATA_DIR, 'bulk_exports')
            if not os.path.exists(csv_dir):
                os.makedirs(csv_dir)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            csv_file = os.path.join(csv_dir, f'all_messages_{timestamp}.csv')
            
            print(f"\nFound {len(dialogs)} sources. Starting bulk scraping...")
            print(f"All messages will be saved to: {csv_file}")
            
            # Open CSV file once for all messages
            with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Source Type', 'Source Name', 'Message', 'Sender', 'Date', 'Scraped At'])
                
                for i, dialog in enumerate(dialogs, 1):
                    try:
                        print(f"\nScraping {i}/{len(dialogs)}: {dialog.name}")
                        
                        # Get messages for this source
                        messages = await self.client.get_messages(dialog.entity, limit=100)
                        source_name = dialog.name
                        source_type = 'channel' if isinstance(dialog.entity, PeerChannel) else 'group' if isinstance(dialog.entity, PeerChat) else 'personal'
                        
                        message_count = 0
                        for message in messages:
                            if message.text:
                                # Remove emojis from message text
                                clean_text = self.remove_emoji(message.text)
                                
                                # Store in database
                                conn = sqlite3.connect(DB_FILE)
                                cursor = conn.cursor()
                                
                                cursor.execute('''
                                    INSERT INTO messages (source_type, source_name, message_text, sender, date)
                                    VALUES (?, ?, ?, ?, ?)
                                ''', (
                                    source_type,
                                    source_name,
                                    clean_text,
                                    message.sender_id if message.sender_id else None,
                                    message.date.strftime("%Y-%m-%d %H:%M:%S")
                                ))
                                
                                # Write to CSV
                                writer.writerow([
                                    source_type,
                                    source_name,
                                    clean_text,
                                    message.sender_id if message.sender_id else None,
                                    message.date.strftime("%Y-%m-%d %H:%M:%S"),
                                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                ])
                                
                                message_count += 1
                                total_messages += 1
                                
                                conn.commit()
                                conn.close()
                        
                        if message_count > 0:
                            successful_sources += 1
                            print(f"✓ Successfully scraped {message_count} messages from {dialog.name}")
                        else:
                            failed_sources += 1
                            print(f"✗ No messages found in {dialog.name}")
                            
                    except Exception as e:
                        failed_sources += 1
                        logger.error(f"Error scraping {dialog.name}: {str(e)}")
                        print(f"✗ Error scraping {dialog.name}: {str(e)}")
            
            print("\n=== Bulk Scraping Summary ===")
            print(f"Total sources processed: {len(dialogs)}")
            print(f"Successful sources: {successful_sources}")
            print(f"Failed sources: {failed_sources}")
            print(f"Total messages scraped: {total_messages}")
            print(f"All messages saved to: {csv_file}")
            
            return total_messages
            
        except Exception as e:
            logger.error(f"Error in bulk scraping: {str(e)}")
            print(f"Error in bulk scraping: {str(e)}")
            return 0

async def main():
    scraper = TelegramScraper()
    await scraper.initialize_client()
    
    while True:
        print("\n=== Telegram Scraper Menu ===")
        print("1. List all chats and channels")
        print("2. Scrape messages from a specific source")
        print("3. Search messages")
        print("4. View statistics")
        print("5. View database contents")
        print("6. Start real-time message scraping")
        print("7. Scrape all messages (bulk scraping)")
        print("8. Exit")
        
        choice = input("\nEnter your choice (1-8): ")
        
        if choice == '1':
            await scraper.list_dialogs()
        elif choice == '2':
            dialogs = await scraper.list_dialogs()
            if dialogs:
                try:
                    index = int(input("\nEnter the number of the source to scrape: ")) - 1
                    if 0 <= index < len(dialogs):
                        success, count, csv_file = await scraper.scrape_source(dialogs[index].entity)
                        if success:
                            print(f"\nSuccessfully scraped {count} messages")
                            print(f"Data exported to: {csv_file}")
                    else:
                        print("Invalid selection!")
                except ValueError:
                    print("Please enter a valid number!")
        elif choice == '3':
            query = input("Enter search query: ")
            source_name = input("Enter source name (optional, press Enter to skip): ").strip()
            source_name = source_name if source_name else None
            scraper.search_messages(query, source_name)
        elif choice == '4':
            scraper.view_statistics()
        elif choice == '5':
            source_name = input("Enter source name (optional, press Enter to skip): ").strip()
            source_name = source_name if source_name else None
            scraper.view_database_contents(source_name)
        elif choice == '6':
            print("\nStarting real-time message scraping...")
            await scraper.start_realtime_scraping()
        elif choice == '7':
            print("\nStarting bulk scraping of all messages...")
            total_messages = await scraper.scrape_all_sources()
            if total_messages > 0:
                print(f"\nBulk scraping completed. Total messages scraped: {total_messages}")
        elif choice == '8':
            print("Goodbye!")
            break
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    asyncio.run(main())
