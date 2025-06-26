#!/usr/bin/env python3
"""
Telegram Scraper Data Structure Definition
Comprehensive schema for storing Telegram message data
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

class MessageType(Enum):
    """Types of Telegram messages"""
    TEXT = "text"
    PHOTO = "photo"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    STICKER = "sticker"
    VOICE = "voice"
    VIDEO_NOTE = "video_note"
    LOCATION = "location"
    CONTACT = "contact"
    POLL = "poll"
    FORWARDED = "forwarded"
    REPLY = "reply"
    EDIT = "edit"
    DELETE = "delete"

class SourceType(Enum):
    """Types of Telegram sources"""
    CHANNEL = "channel"
    GROUP = "group"
    SUPERGROUP = "supergroup"
    PRIVATE = "private"
    BOT = "bot"

class UserType(Enum):
    """Types of Telegram users"""
    USER = "user"
    BOT = "bot"
    CHANNEL = "channel"
    GROUP = "group"
    UNKNOWN = "unknown"

@dataclass
class UserInfo:
    """User information structure"""
    user_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    is_bot: bool
    is_verified: bool
    is_premium: bool
    is_scam: bool
    is_fake: bool
    user_type: UserType
    created_at: Optional[datetime]
    last_seen: Optional[datetime]

@dataclass
class MediaInfo:
    """Media file information"""
    file_id: str
    file_unique_id: str
    file_size: Optional[int]
    mime_type: Optional[str]
    file_name: Optional[str]
    duration: Optional[int]  # For audio/video
    width: Optional[int]     # For images/videos
    height: Optional[int]    # For images/videos
    thumbnail: Optional[str]
    caption: Optional[str]

@dataclass
class LocationInfo:
    """Location information"""
    latitude: float
    longitude: float
    accuracy: Optional[float]
    live_period: Optional[int]
    heading: Optional[int]
    proximity_alert_radius: Optional[int]

@dataclass
class ContactInfo:
    """Contact information"""
    phone_number: str
    first_name: str
    last_name: Optional[str]
    user_id: Optional[int]
    vcard: Optional[str]

@dataclass
class PollInfo:
    """Poll information"""
    question: str
    options: List[str]
    total_voter_count: int
    is_closed: bool
    is_anonymous: bool
    type: str
    allows_multiple_answers: bool
    correct_option_id: Optional[int]
    explanation: Optional[str]

@dataclass
class ForwardInfo:
    """Forwarded message information"""
    from_user_id: Optional[int]
    from_chat_id: Optional[int]
    from_message_id: Optional[int]
    from_chat_type: Optional[str]
    from_chat_title: Optional[str]
    from_chat_username: Optional[str]
    forward_date: Optional[datetime]
    is_automatic_forward: bool

@dataclass
class ReplyInfo:
    """Reply message information"""
    reply_to_message_id: int
    reply_to_user_id: Optional[int]
    reply_to_chat_id: Optional[int]
    reply_to_message_text: Optional[str]

@dataclass
class TelegramMessage:
    """Complete Telegram message structure"""
    # Basic message information
    message_id: int
    chat_id: int
    chat_type: SourceType
    chat_title: Optional[str]
    chat_username: Optional[str]
    chat_member_count: Optional[int]
    
    # Sender information
    sender_id: Optional[int]
    sender_info: Optional[UserInfo]
    
    # Message content
    message_type: MessageType
    text: Optional[str]
    text_clean: Optional[str]  # Without emojis
    text_length: int
    
    # Media information
    media_info: Optional[MediaInfo]
    
    # Location and contact
    location_info: Optional[LocationInfo]
    contact_info: Optional[ContactInfo]
    poll_info: Optional[PollInfo]
    
    # Message relationships
    forward_info: Optional[ForwardInfo]
    reply_info: Optional[ReplyInfo]
    
    # Message metadata
    date: datetime
    edit_date: Optional[datetime]
    views: Optional[int]
    forwards: Optional[int]
    
    # Scraping metadata
    scraped_at: datetime
    scraper_version: str
    keywords_matched: Optional[List[str]]
    source_name: str
    source_type: str
    
    # Additional metadata
    is_deleted: bool = False
    is_edited: bool = False
    has_media: bool = False
    has_links: bool = False
    has_mentions: bool = False
    has_hashtags: bool = False
    language: Optional[str] = None
    sentiment_score: Optional[float] = None

@dataclass
class ScrapingSession:
    """Scraping session information"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    source_name: str
    source_type: SourceType
    total_messages_fetched: int
    total_messages_saved: int
    keywords_used: Optional[List[str]]
    rate_limit_hits: int
    errors_encountered: int
    scraper_version: str
    config_used: Dict[str, Any]

@dataclass
class SourceMetadata:
    """Source (channel/group) metadata"""
    source_id: int
    source_name: str
    source_type: SourceType
    username: Optional[str]
    title: str
    description: Optional[str]
    member_count: Optional[int]
    is_verified: bool
    is_restricted: bool
    is_scam: bool
    is_fake: bool
    created_at: Optional[datetime]
    last_activity: Optional[datetime]
    first_scraped: datetime
    last_scraped: datetime
    total_messages_scraped: int
    scraping_frequency: Optional[str]

# Database Schema Definitions
DATABASE_SCHEMA = {
    "messages": """
        CREATE TABLE messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER NOT NULL,
            chat_id INTEGER NOT NULL,
            chat_type TEXT NOT NULL,
            chat_title TEXT,
            chat_username TEXT,
            chat_member_count INTEGER,
            
            sender_id INTEGER,
            sender_username TEXT,
            sender_first_name TEXT,
            sender_last_name TEXT,
            sender_is_bot BOOLEAN,
            sender_is_verified BOOLEAN,
            sender_is_premium BOOLEAN,
            
            message_type TEXT NOT NULL,
            text TEXT,
            text_clean TEXT,
            text_length INTEGER DEFAULT 0,
            
            file_id TEXT,
            file_size INTEGER,
            mime_type TEXT,
            file_name TEXT,
            duration INTEGER,
            width INTEGER,
            height INTEGER,
            caption TEXT,
            
            latitude REAL,
            longitude REAL,
            location_accuracy REAL,
            
            contact_phone TEXT,
            contact_first_name TEXT,
            contact_last_name TEXT,
            contact_user_id INTEGER,
            
            poll_question TEXT,
            poll_options TEXT,  -- JSON array
            poll_total_voters INTEGER,
            poll_is_closed BOOLEAN,
            
            forward_from_user_id INTEGER,
            forward_from_chat_id INTEGER,
            forward_from_message_id INTEGER,
            forward_from_chat_type TEXT,
            forward_from_chat_title TEXT,
            forward_date DATETIME,
            
            reply_to_message_id INTEGER,
            reply_to_user_id INTEGER,
            reply_to_message_text TEXT,
            
            date DATETIME NOT NULL,
            edit_date DATETIME,
            views INTEGER,
            forwards INTEGER,
            
            scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            scraper_version TEXT,
            keywords_matched TEXT,  -- JSON array
            source_name TEXT NOT NULL,
            source_type TEXT NOT NULL,
            
            is_deleted BOOLEAN DEFAULT FALSE,
            is_edited BOOLEAN DEFAULT FALSE,
            has_media BOOLEAN DEFAULT FALSE,
            has_links BOOLEAN DEFAULT FALSE,
            has_mentions BOOLEAN DEFAULT FALSE,
            has_hashtags BOOLEAN DEFAULT FALSE,
            language TEXT,
            sentiment_score REAL,
            
            UNIQUE(message_id, chat_id)
        )
    """,
    
    "sources": """
        CREATE TABLE sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id INTEGER UNIQUE NOT NULL,
            source_name TEXT NOT NULL,
            source_type TEXT NOT NULL,
            username TEXT,
            title TEXT NOT NULL,
            description TEXT,
            member_count INTEGER,
            is_verified BOOLEAN DEFAULT FALSE,
            is_restricted BOOLEAN DEFAULT FALSE,
            is_scam BOOLEAN DEFAULT FALSE,
            is_fake BOOLEAN DEFAULT FALSE,
            created_at DATETIME,
            last_activity DATETIME,
            first_scraped DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_scraped DATETIME DEFAULT CURRENT_TIMESTAMP,
            total_messages_scraped INTEGER DEFAULT 0,
            scraping_frequency TEXT
        )
    """,
    
    "scraping_sessions": """
        CREATE TABLE scraping_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            start_time DATETIME NOT NULL,
            end_time DATETIME,
            source_name TEXT NOT NULL,
            source_type TEXT NOT NULL,
            total_messages_fetched INTEGER DEFAULT 0,
            total_messages_saved INTEGER DEFAULT 0,
            keywords_used TEXT,  -- JSON array
            rate_limit_hits INTEGER DEFAULT 0,
            errors_encountered INTEGER DEFAULT 0,
            scraper_version TEXT,
            config_used TEXT  -- JSON object
        )
    """,
    
    "users": """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            phone TEXT,
            is_bot BOOLEAN DEFAULT FALSE,
            is_verified BOOLEAN DEFAULT FALSE,
            is_premium BOOLEAN DEFAULT FALSE,
            is_scam BOOLEAN DEFAULT FALSE,
            is_fake BOOLEAN DEFAULT FALSE,
            user_type TEXT NOT NULL,
            created_at DATETIME,
            last_seen DATETIME,
            first_encountered DATETIME DEFAULT CURRENT_TIMESTAMP,
            message_count INTEGER DEFAULT 0
        )
    """,
    
    "keywords": """
        CREATE TABLE keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT NOT NULL,
            category TEXT,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            usage_count INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE
        )
    """,
    
    "keyword_matches": """
        CREATE TABLE keyword_matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER NOT NULL,
            keyword_id INTEGER NOT NULL,
            matched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (message_id) REFERENCES messages (id),
            FOREIGN KEY (keyword_id) REFERENCES keywords (id)
        )
    """
}

# CSV Export Structure
CSV_STRUCTURE = {
    "basic_export": [
        "message_id", "chat_id", "chat_type", "chat_title", "chat_username",
        "sender_id", "sender_username", "sender_first_name", "sender_last_name",
        "message_type", "text", "text_clean", "text_length",
        "date", "edit_date", "views", "forwards",
        "scraped_at", "keywords_matched", "source_name", "source_type"
    ],
    
    "detailed_export": [
        "message_id", "chat_id", "chat_type", "chat_title", "chat_username", "chat_member_count",
        "sender_id", "sender_username", "sender_first_name", "sender_last_name", 
        "sender_is_bot", "sender_is_verified", "sender_is_premium",
        "message_type", "text", "text_clean", "text_length",
        "file_id", "file_size", "mime_type", "file_name", "duration", "width", "height", "caption",
        "latitude", "longitude", "location_accuracy",
        "contact_phone", "contact_first_name", "contact_last_name", "contact_user_id",
        "poll_question", "poll_options", "poll_total_voters", "poll_is_closed",
        "forward_from_user_id", "forward_from_chat_id", "forward_from_message_id", 
        "forward_from_chat_type", "forward_from_chat_title", "forward_date",
        "reply_to_message_id", "reply_to_user_id", "reply_to_message_text",
        "date", "edit_date", "views", "forwards",
        "scraped_at", "scraper_version", "keywords_matched", "source_name", "source_type",
        "is_deleted", "is_edited", "has_media", "has_links", "has_mentions", "has_hashtags",
        "language", "sentiment_score"
    ],
    
    "analytics_export": [
        "source_name", "source_type", "message_count", "unique_users", "date_range",
        "avg_message_length", "most_active_user", "most_used_keywords",
        "media_count", "forward_count", "reply_count", "engagement_rate"
    ]
}

# JSON Export Structure
JSON_STRUCTURE = {
    "message_format": {
        "message_id": "int",
        "chat": {
            "id": "int",
            "type": "string",
            "title": "string",
            "username": "string",
            "member_count": "int"
        },
        "sender": {
            "id": "int",
            "username": "string",
            "first_name": "string",
            "last_name": "string",
            "is_bot": "boolean",
            "is_verified": "boolean",
            "is_premium": "boolean"
        },
        "content": {
            "type": "string",
            "text": "string",
            "text_clean": "string",
            "text_length": "int",
            "media": "object",
            "location": "object",
            "contact": "object",
            "poll": "object"
        },
        "metadata": {
            "date": "datetime",
            "edit_date": "datetime",
            "views": "int",
            "forwards": "int",
            "is_deleted": "boolean",
            "is_edited": "boolean"
        },
        "relationships": {
            "forward": "object",
            "reply": "object"
        },
        "scraping": {
            "scraped_at": "datetime",
            "scraper_version": "string",
            "keywords_matched": "array",
            "source_name": "string",
            "source_type": "string"
        }
    }
}

if __name__ == "__main__":
    print("📊 Telegram Scraper Data Structure")
    print("=" * 50)
    print(f"Message fields: {len(TelegramMessage.__dataclass_fields__)}")
    print(f"Database tables: {len(DATABASE_SCHEMA)}")
    print(f"CSV export formats: {len(CSV_STRUCTURE)}")
    print(f"JSON export format: Available")
    print("\n✅ Data structure ready for implementation!") 