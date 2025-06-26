import asyncio
import logging
from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel, PeerChat, PeerUser
from telethon.errors import FloodWaitError, SlowModeWaitError, ChatAdminRequiredError
import sqlite3
import os
from datetime import datetime
import csv
import json
import re
import emoji
import time
import random

# Import configuration
try:
    from config import (API_ID, API_HASH, RATE_LIMIT_DELAY, BATCH_SIZE, BATCH_DELAY, 
                       MAX_RETRIES, MAX_BATCHES_PER_SOURCE, MAX_BATCHES_BULK, 
                       SOURCE_DELAY, DAILY_LIMIT, HOURLY_LIMIT, READ_ONLY_MODE, 
                       MAX_SOURCES_PER_DAY, COOLDOWN_PERIOD)
except ImportError:
    # Fallback to EXTRA CONSERVATIVE values for read-only accounts
    API_ID = '25696418'
    API_HASH = '8467e85b7bea4591e39d1fd18c1369b5'
    RATE_LIMIT_DELAY = 8  # 8 seconds between requests
    BATCH_SIZE = 5  # 5 messages per batch
    BATCH_DELAY = 15  # 15 seconds between batches
    MAX_RETRIES = 1  # 1 retry attempt
    MAX_BATCHES_PER_SOURCE = 2  # 2 batches per source
    MAX_BATCHES_BULK = 1  # 1 batch per source in bulk
    SOURCE_DELAY = 30  # 30 seconds between sources
    DAILY_LIMIT = 50  # 50 messages per day
    HOURLY_LIMIT = 10  # 10 messages per hour
    READ_ONLY_MODE = True
    MAX_SOURCES_PER_DAY = 3
    COOLDOWN_PERIOD = 3600

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='telegram_scraper.log'
)
logger = logging.getLogger(__name__)

# Get the absolute path of the current script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, 'data')
DB_FILE = os.path.join(DATA_DIR, 'telegram_messages.db')

class TelegramScraper:
    def __init__(self):
        self.client = None
        self.setup_database()
        self.daily_message_count = 0
        self.hourly_message_count = 0
        self.last_hour_reset = datetime.now()
        self.last_daily_reset = datetime.now().date()
        self.sources_scraped_today = set()
        self.last_session_time = None

    def check_limits(self):
        """Check if we've hit daily or hourly limits"""
        now = datetime.now()
        
        # Reset hourly counter if an hour has passed
        if (now - self.last_hour_reset).total_seconds() > 3600:
            self.hourly_message_count = 0
            self.last_hour_reset = now
        
        # Reset daily counter if a new day has started
        if now.date() > self.last_daily_reset:
            self.daily_message_count = 0
            self.sources_scraped_today.clear()
            self.last_daily_reset = now.date()
        
        # Check cooldown period for read-only accounts
        if READ_ONLY_MODE and self.last_session_time:
            time_since_last = (now - self.last_session_time).total_seconds()
            if time_since_last < COOLDOWN_PERIOD:
                remaining = COOLDOWN_PERIOD - time_since_last
                print(f"⏰ Read-only cooldown: {remaining:.0f} seconds remaining")
                return False
        
        # Check limits
        if self.daily_message_count >= DAILY_LIMIT:
            print(f"⚠️  Daily limit reached ({DAILY_LIMIT} messages). Please wait until tomorrow.")
            return False
        
        if self.hourly_message_count >= HOURLY_LIMIT:
            print(f"⚠️  Hourly limit reached ({HOURLY_LIMIT} messages). Please wait for the next hour.")
            return False
        
        return True

    def check_source_limit(self, source_name):
        """Check if we've hit the daily source limit for read-only accounts"""
        if READ_ONLY_MODE and len(self.sources_scraped_today) >= MAX_SOURCES_PER_DAY:
            print(f"⚠️  Daily source limit reached ({MAX_SOURCES_PER_DAY} sources). Please wait until tomorrow.")
            return False
        
        if source_name in self.sources_scraped_today:
            print(f"⚠️  Source '{source_name}' already scraped today. Please wait until tomorrow.")
            return False
        
        return True

    def increment_counters(self, message_count, source_name=None):
        """Increment daily and hourly message counters"""
        self.daily_message_count += message_count
        self.hourly_message_count += message_count
        
        if source_name and READ_ONLY_MODE:
            self.sources_scraped_today.add(source_name)
        
        self.last_session_time = datetime.now()
        
        print(f"📊 Progress: {self.hourly_message_count}/{HOURLY_LIMIT} (hourly), {self.daily_message_count}/{DAILY_LIMIT} (daily)")
        if READ_ONLY_MODE:
            print(f"📋 Sources today: {len(self.sources_scraped_today)}/{MAX_SOURCES_PER_DAY}")

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
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    keywords_matched TEXT
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

    async def safe_request(self, func, *args, **kwargs):
        """Execute a request with rate limiting and retry logic"""
        for attempt in range(MAX_RETRIES):
            try:
                # Add random delay to avoid detection
                delay = RATE_LIMIT_DELAY + random.uniform(0, 1)
                await asyncio.sleep(delay)
                
                result = await func(*args, **kwargs)
                return result
                
            except FloodWaitError as e:
                wait_time = e.seconds
                logger.warning(f"Flood wait error: waiting {wait_time} seconds")
                print(f"Rate limit hit. Waiting {wait_time} seconds...")
                await asyncio.sleep(wait_time)
                
            except SlowModeWaitError as e:
                wait_time = e.seconds
                logger.warning(f"Slow mode error: waiting {wait_time} seconds")
                print(f"Slow mode activated. Waiting {wait_time} seconds...")
                await asyncio.sleep(wait_time)
                
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)  # Exponential backoff
                    logger.warning(f"Request failed (attempt {attempt + 1}): {str(e)}. Retrying in {wait_time} seconds...")
                    print(f"Request failed. Retrying in {wait_time:.1f} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Request failed after {MAX_RETRIES} attempts: {str(e)}")
                    raise
        
        return None

    def check_keywords(self, text, keywords):
        """Check if text contains any of the specified keywords"""
        if not keywords:
            return True, []
        
        text_lower = text.lower()
        matched_keywords = []
        
        for keyword in keywords:
            if keyword.lower() in text_lower:
                matched_keywords.append(keyword)
        
        return len(matched_keywords) > 0, matched_keywords

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
                    SELECT source_type, source_name, message_text, sender, date, scraped_at, keywords_matched
                    FROM messages
                    WHERE (source_name = ?) AND (message_text LIKE ? OR sender LIKE ?)
                    ORDER BY date DESC
                    LIMIT ?
                ''', (source_name, f'%{query}%', f'%{query}%', user_limit))
            else:
                cursor.execute('''
                    SELECT source_type, source_name, message_text, sender, date, scraped_at, keywords_matched
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
                if msg[6]:  # keywords_matched
                    print(f"Keywords Matched: {msg[6]}")
            
            # Export search results to CSV
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            csv_dir = os.path.join(DATA_DIR, 'search_results')
            if not os.path.exists(csv_dir):
                os.makedirs(csv_dir)
            
            csv_file = os.path.join(csv_dir, f"search_{query}_{timestamp}.csv")
            with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Source Type', 'Source Name', 'Message', 'Sender', 'Date', 'Scraped At', 'Keywords Matched'])
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
            dialogs = await self.safe_request(self.client.get_dialogs)
            print("\n=== Available Chats and Channels ===")
            for i, dialog in enumerate(dialogs, 1):
                print(f"{i}. {dialog.name} ({dialog.entity.__class__.__name__})")
            return dialogs
        except Exception as e:
            logger.error(f"Error listing dialogs: {str(e)}")
            return []

    async def scrape_source(self, source_entity, keywords=None):
        """Scrape messages from a source (group or channel) with keyword filtering"""
        try:
            # Check limits before starting
            if not self.check_limits():
                return False, 0, None
            
            # Get source name with better fallback handling
            if hasattr(source_entity, 'title') and source_entity.title:
                source_name = source_entity.title
            elif hasattr(source_entity, 'username') and source_entity.username:
                source_name = source_entity.username
            elif hasattr(source_entity, 'id'):
                source_name = f"Unknown_{source_entity.id}"
            else:
                source_name = "Unknown_Source"
            
            source_type = 'channel' if isinstance(source_entity, PeerChannel) else 'group'

            # Check source limit for read-only accounts
            if not self.check_source_limit(source_name):
                return False, 0, None

            print(f"📖 Scraping {source_name} with READ-ONLY optimized settings...")
            print(f"⚠️  Read-only mode: {BATCH_SIZE} messages per batch, {BATCH_DELAY}s delays")
            print(f"📋 This is source {len(self.sources_scraped_today) + 1}/{MAX_SOURCES_PER_DAY} today")
            
            # Get messages in batches to avoid rate limiting
            all_messages = []
            offset_id = 0
            
            for batch_num in range(MAX_BATCHES_PER_SOURCE):  # Limit to MAX_BATCHES_PER_SOURCE batches (MAX_BATCHES_PER_SOURCE * BATCH_SIZE messages total)
                try:
                    # Check limits before each batch
                    if not self.check_limits():
                        print("⚠️  Stopping due to limit reached")
                        break
                    
                    print(f"Fetching batch {batch_num + 1}/{MAX_BATCHES_PER_SOURCE}...")
                    
                    # Get messages with safe request
                    messages = await self.safe_request(
                        self.client.get_messages, 
                        source_entity, 
                        limit=BATCH_SIZE,
                        offset_id=offset_id
                    )
                    
                    if not messages:
                        break
                    
                    all_messages.extend(messages)
                    
                    # Update offset for next batch
                    if messages:
                        offset_id = messages[-1].id
                    
                    # Add delay between batches
                    if batch_num < MAX_BATCHES_PER_SOURCE - 1:  # Don't delay after the last batch
                        print(f"Waiting {BATCH_DELAY} seconds before next batch...")
                        await asyncio.sleep(BATCH_DELAY)
                        
                except Exception as e:
                    logger.error(f"Error fetching batch {batch_num + 1}: {str(e)}")
                    break
            
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
            filtered_count = 0
            
            with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Source Type', 'Source Name', 'Message', 'Sender', 'Date', 'Scraped At', 'Keywords Matched'])
                
                for message in all_messages:
                    if message.text:
                        # Remove emojis from message text
                        clean_text = self.remove_emoji(message.text)
                        
                        # Check keywords if provided
                        if keywords:
                            matches_keywords, matched_keywords = self.check_keywords(clean_text, keywords)
                            if not matches_keywords:
                                continue  # Skip this message
                            filtered_count += 1
                            keywords_str = ', '.join(matched_keywords)
                        else:
                            keywords_str = None
                        
                        # Ensure source_name is valid
                        if not source_name:
                            logger.warning("Skipping message with missing source_name")
                            continue
                        
                        # Store in database
                        cursor.execute('''
                            INSERT INTO messages (source_type, source_name, message_text, sender, date, keywords_matched)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            source_type,
                            source_name,
                            clean_text,
                            message.sender_id if message.sender_id else None,
                            message.date.strftime("%Y-%m-%d %H:%M:%S"),
                            keywords_str
                        ))
                        
                        # Write to CSV
                        writer.writerow([
                            source_type,
                            source_name,
                            clean_text,
                            message.sender_id if message.sender_id else None,
                            message.date.strftime("%Y-%m-%d %H:%M:%S"),
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            keywords_str
                        ])
                        
                        message_count += 1
            
            # Update source statistics
            if source_name:
                cursor.execute('''
                    INSERT OR REPLACE INTO sources (source_type, source_name, last_scraped, message_count)
                    VALUES (?, ?, CURRENT_TIMESTAMP, ?)
                ''', (source_type, source_name, message_count))
            else:
                logger.warning("Skipping sources table update due to missing source_name")
            
            conn.commit()
            
            # Update counters
            self.increment_counters(message_count, source_name)
            
            if keywords:
                logger.info(f"Successfully scraped {message_count} messages (filtered from {len(all_messages)} total) from {source_name}")
                print(f"✓ Successfully scraped {message_count} messages matching keywords from {source_name}")
                print(f"  (Filtered from {len(all_messages)} total messages)")
            else:
                logger.info(f"Successfully scraped {message_count} messages from {source_name}")
                print(f"✓ Successfully scraped {message_count} messages from {source_name}")
            
            if READ_ONLY_MODE:
                print(f"⏰ Next session available in {COOLDOWN_PERIOD/3600:.1f} hours")
            
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
                    INSERT INTO messages (source_type, source_name, message_text, sender, date, keywords_matched)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    source_type,
                    source_name,
                    clean_text,
                    message.sender_id if message.sender_id else None,
                    message.date.strftime("%Y-%m-%d %H:%M:%S"),
                    None  # No keywords for real-time messages
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
                        writer.writerow(['Source Type', 'Source Name', 'Message', 'Sender', 'Date', 'Received At', 'Keywords Matched'])
                    
                    writer.writerow([
                        source_type,
                        source_name,
                        clean_text,
                        message.sender_id if message.sender_id else None,
                        message.date.strftime("%Y-%m-%d %H:%M:%S"),
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        None  # No keywords for real-time messages
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

    async def scrape_all_sources(self, keywords=None):
        """Scrape messages from all available sources with rate limiting and keyword filtering"""
        try:
            # Check limits before starting
            if not self.check_limits():
                return 0
            
            print("\nFetching all available chats and channels...")
            dialogs = await self.safe_request(self.client.get_dialogs)
            
            if not dialogs:
                print("No chats or channels found!")
                return 0
            
            total_messages = 0
            successful_sources = 0
            failed_sources = 0
            
            # Create a single CSV file for all messages
            csv_dir = os.path.join(DATA_DIR, 'bulk_exports')
            if not os.path.exists(csv_dir):
                os.makedirs(csv_dir)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            keyword_suffix = f"_keywords_{'_'.join(keywords)}" if keywords else ""
            csv_file = os.path.join(csv_dir, f'all_messages{keyword_suffix}_{timestamp}.csv')
            
            print(f"\nFound {len(dialogs)} sources. Starting VERY CONSERVATIVE bulk scraping...")
            print(f"⚠️  Using conservative settings: {BATCH_SIZE} messages per batch, {BATCH_DELAY}s delays, {SOURCE_DELAY}s between sources")
            if keywords:
                print(f"Filtering for keywords: {', '.join(keywords)}")
            print(f"All messages will be saved to: {csv_file}")
            
            # Open CSV file once for all messages
            with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Source Type', 'Source Name', 'Message', 'Sender', 'Date', 'Scraped At', 'Keywords Matched'])
                
                for i, dialog in enumerate(dialogs, 1):
                    try:
                        # Check limits before each source
                        if not self.check_limits():
                            print("⚠️  Stopping bulk scraping due to limit reached")
                            break
                        
                        print(f"\nScraping {i}/{len(dialogs)}: {dialog.name}")
                        
                        # Get messages for this source with rate limiting
                        all_messages = []
                        offset_id = 0
                        
                        for batch_num in range(MAX_BATCHES_BULK):  # Limit to MAX_BATCHES_BULK batches per source (MAX_BATCHES_BULK * BATCH_SIZE messages total)
                            try:
                                # Check limits before each batch
                                if not self.check_limits():
                                    print("⚠️  Stopping due to limit reached")
                                    break
                                
                                print(f"  Fetching batch {batch_num + 1}/{MAX_BATCHES_BULK}...")
                                
                                messages = await self.safe_request(
                                    self.client.get_messages, 
                                    dialog.entity, 
                                    limit=BATCH_SIZE,
                                    offset_id=offset_id
                                )
                                
                                if not messages:
                                    break
                                
                                all_messages.extend(messages)
                                
                                # Update offset for next batch
                                if messages:
                                    offset_id = messages[-1].id
                                
                                # Add delay between batches
                                if batch_num < MAX_BATCHES_BULK - 1:  # Don't delay after the last batch
                                    await asyncio.sleep(BATCH_DELAY)
                                    
                            except Exception as e:
                                logger.error(f"Error fetching batch {batch_num + 1} for {dialog.name}: {str(e)}")
                                break
                        
                        source_name = dialog.name if dialog.name else f"Unknown_{dialog.entity.id}" if hasattr(dialog.entity, 'id') else "Unknown_Source"
                        source_type = 'channel' if isinstance(dialog.entity, PeerChannel) else 'group' if isinstance(dialog.entity, PeerChat) else 'personal'
                        
                        message_count = 0
                        for message in all_messages:
                            if message.text:
                                # Remove emojis from message text
                                clean_text = self.remove_emoji(message.text)
                                
                                # Check keywords if provided
                                if keywords:
                                    matches_keywords, matched_keywords = self.check_keywords(clean_text, keywords)
                                    if not matches_keywords:
                                        continue  # Skip this message
                                    keywords_str = ', '.join(matched_keywords)
                                else:
                                    keywords_str = None
                                
                                # Ensure source_name is valid
                                if not source_name:
                                    logger.warning("Skipping message with missing source_name (bulk)")
                                    continue
                                
                                # Store in database
                                conn = sqlite3.connect(DB_FILE)
                                cursor = conn.cursor()
                                
                                cursor.execute('''
                                    INSERT INTO messages (source_type, source_name, message_text, sender, date, keywords_matched)
                                    VALUES (?, ?, ?, ?, ?, ?)
                                ''', (
                                    source_type,
                                    source_name,
                                    clean_text,
                                    message.sender_id if message.sender_id else None,
                                    message.date.strftime("%Y-%m-%d %H:%M:%S"),
                                    keywords_str
                                ))
                                
                                # Write to CSV
                                writer.writerow([
                                    source_type,
                                    source_name,
                                    clean_text,
                                    message.sender_id if message.sender_id else None,
                                    message.date.strftime("%Y-%m-%d %H:%M:%S"),
                                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    keywords_str
                                ])
                                
                                message_count += 1
                                total_messages += 1
                                
                                conn.commit()
                                conn.close()
                        
                        if message_count > 0:
                            successful_sources += 1
                            if keywords:
                                print(f"✓ Successfully scraped {message_count} messages matching keywords from {dialog.name}")
                            else:
                                print(f"✓ Successfully scraped {message_count} messages from {dialog.name}")
                        else:
                            failed_sources += 1
                            if keywords:
                                print(f"✗ No messages matching keywords found in {dialog.name}")
                            else:
                                print(f"✗ No messages found in {dialog.name}")
                        
                        # Add delay between sources to avoid rate limiting
                        if i < len(dialogs):
                            print(f"  Waiting {SOURCE_DELAY} seconds before next source...")
                            await asyncio.sleep(SOURCE_DELAY)
                            
                    except Exception as e:
                        failed_sources += 1
                        logger.error(f"Error scraping {dialog.name}: {str(e)}")
                        print(f"✗ Error scraping {dialog.name}: {str(e)}")
            
            print("\n=== Bulk Scraping Summary ===")
            print(f"Total sources processed: {len(dialogs)}")
            print(f"Successful sources: {successful_sources}")
            print(f"Failed sources: {failed_sources}")
            print(f"Total messages scraped: {total_messages}")
            if keywords:
                print(f"Keywords filtered: {', '.join(keywords)}")
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
        print("3. Scrape messages with keywords from a specific source")
        print("4. Search messages")
        print("5. View statistics")
        print("6. View database contents")
        print("7. Start real-time message scraping")
        print("8. Scrape all messages (bulk scraping)")
        print("9. Scrape all messages with keywords (bulk scraping)")
        print("10. Exit")
        
        choice = input("\nEnter your choice (1-10): ")
        
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
            dialogs = await scraper.list_dialogs()
            if dialogs:
                try:
                    index = int(input("\nEnter the number of the source to scrape: ")) - 1
                    if 0 <= index < len(dialogs):
                        keywords_input = input("Enter keywords (comma-separated): ")
                        keywords = [keyword.strip() for keyword in keywords_input.split(',') if keyword.strip()]
                        if keywords:
                            success, count, csv_file = await scraper.scrape_source(dialogs[index].entity, keywords)
                            if success:
                                print(f"\nSuccessfully scraped {count} messages matching keywords")
                                print(f"Data exported to: {csv_file}")
                        else:
                            print("No valid keywords provided!")
                    else:
                        print("Invalid selection!")
                except ValueError:
                    print("Please enter a valid number!")
        elif choice == '4':
            query = input("Enter search query: ")
            source_name = input("Enter source name (optional, press Enter to skip): ").strip()
            source_name = source_name if source_name else None
            scraper.search_messages(query, source_name)
        elif choice == '5':
            scraper.view_statistics()
        elif choice == '6':
            source_name = input("Enter source name (optional, press Enter to skip): ").strip()
            source_name = source_name if source_name else None
            scraper.view_database_contents(source_name)
        elif choice == '7':
            print("\nStarting real-time message scraping...")
            await scraper.start_realtime_scraping()
        elif choice == '8':
            print("\nStarting bulk scraping of all messages...")
            total_messages = await scraper.scrape_all_sources()
            if total_messages > 0:
                print(f"\nBulk scraping completed. Total messages scraped: {total_messages}")
        elif choice == '9':
            keywords_input = input("Enter keywords (comma-separated): ")
            keywords = [keyword.strip() for keyword in keywords_input.split(',') if keyword.strip()]
            if keywords:
                print(f"\nStarting bulk scraping with keywords: {', '.join(keywords)}")
                total_messages = await scraper.scrape_all_sources(keywords)
                if total_messages > 0:
                    print(f"\nBulk scraping completed. Total messages scraped: {total_messages}")
            else:
                print("No valid keywords provided!")
        elif choice == '10':
            print("Goodbye!")
            break
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    asyncio.run(main())
