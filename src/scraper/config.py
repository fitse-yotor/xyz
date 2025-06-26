# Telegram Scraper Configuration - COOLDOWN DISABLED

# Rate limiting configuration - MODERATE settings
RATE_LIMIT_DELAY = 5  # seconds between requests
BATCH_SIZE = 10  # messages per batch
BATCH_DELAY = 10  # seconds between batches
MAX_RETRIES = 2  # maximum retry attempts

# Scraping limits - MODERATE
MAX_BATCHES_PER_SOURCE = 3  # maximum batches per source (3 * 10 = 30 messages)
MAX_BATCHES_BULK = 2  # maximum batches per source in bulk scraping (2 * 10 = 20 messages)

# Additional safety delays - MODERATE
SOURCE_DELAY = 15  # seconds between different sources
DAILY_LIMIT = 100  # maximum messages per day
HOURLY_LIMIT = 20  # maximum messages per hour

# Read-only account specific settings - DISABLED
READ_ONLY_MODE = False  # Disable read-only optimizations
MAX_SOURCES_PER_DAY = 10  # Increased sources per day
COOLDOWN_PERIOD = 0  # No cooldown between sessions

# Telegram API credentials
API_ID = '20731881'
API_HASH = '19b701428f5db0389a8b797ed50b7773'

# Database settings
DB_FILE = 'telegram_messages.db'

# Logging settings
LOG_LEVEL = 'INFO'
LOG_FILE = 'telegram_scraper.log'

# Export settings
CSV_ENCODING = 'utf-8'
EXPORT_DIR = 'exports'
BULK_EXPORT_DIR = 'bulk_exports'
SEARCH_RESULTS_DIR = 'search_results'
REALTIME_DIR = 'realtime' 