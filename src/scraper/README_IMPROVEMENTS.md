# Telegram Scraper Improvements

## Issues Addressed

### 1. Rate Limiting & Account Freezing Prevention

**Problem**: The original scraper was making requests too aggressively, causing rate limit violations and account freezing.

**Solutions Implemented**:

- **Rate Limiting**: Added configurable delays between requests (2-3 seconds)
- **Batch Processing**: Reduced batch size from 100 to 20 messages per request
- **Exponential Backoff**: Implemented retry logic with increasing delays
- **Flood Wait Handling**: Automatic handling of Telegram's flood wait errors
- **Random Delays**: Added random jitter to avoid detection patterns

**Key Features**:
```python
# Rate limiting configuration
RATE_LIMIT_DELAY = 2  # seconds between requests
BATCH_SIZE = 20  # messages per batch
BATCH_DELAY = 5  # seconds between batches
MAX_RETRIES = 3  # maximum retry attempts
```

### 2. Keyword-Based Scraping

**Problem**: The original scraper only allowed searching already scraped data, not filtering during scraping.

**Solutions Implemented**:

- **Real-time Keyword Filtering**: Filter messages during scraping process
- **Multiple Keyword Support**: Support for comma-separated keywords
- **Keyword Tracking**: Store which keywords matched each message
- **Bulk Keyword Scraping**: Apply keywords to bulk scraping operations

**Usage Examples**:
```bash
# Scrape specific source with keywords
3. Scrape messages with keywords from a specific source
   Keywords: bitcoin, crypto, trading

# Bulk scrape with keywords
9. Scrape all messages with keywords (bulk scraping)
   Keywords: news, update, announcement
```

## New Features

### Enhanced Menu Options
1. **List all chats and channels**
2. **Scrape messages from a specific source**
3. **Scrape messages with keywords from a specific source** ⭐ NEW
4. **Search messages**
5. **View statistics**
6. **View database contents**
7. **Start real-time message scraping**
8. **Scrape all messages (bulk scraping)**
9. **Scrape all messages with keywords (bulk scraping)** ⭐ NEW
10. **Exit**

### Database Schema Updates
- Added `keywords_matched` column to track which keywords matched each message
- Enhanced search functionality to show keyword matches

### Configuration Management
- Created `config.py` for centralized settings
- Easy adjustment of rate limiting parameters
- Configurable scraping limits

## Safety Features

### Rate Limiting
- **Safe Request Wrapper**: All API calls go through `safe_request()` method
- **Automatic Retry**: Handles temporary failures with exponential backoff
- **Flood Wait Detection**: Automatically waits when rate limits are hit
- **Slow Mode Handling**: Respects channel slow mode restrictions

### Error Handling
- **Graceful Degradation**: Continues scraping even if some sources fail
- **Detailed Logging**: Comprehensive error logging for debugging
- **User Feedback**: Clear progress indicators and status messages

## Usage Recommendations

### For Rate Limit Prevention
1. **Start Conservative**: Use default settings initially
2. **Monitor Logs**: Watch for flood wait errors
3. **Adjust Settings**: Increase delays if you hit rate limits
4. **Use Keywords**: Filter during scraping to reduce data volume

### For Keyword Scraping
1. **Be Specific**: Use targeted keywords to reduce noise
2. **Multiple Keywords**: Use comma-separated lists for broader coverage
3. **Case Insensitive**: Keywords are matched case-insensitively
4. **Track Matches**: Check the "Keywords Matched" column in exports

## Configuration Tips

### Conservative Settings (Recommended for new accounts)
```python
RATE_LIMIT_DELAY = 3  # 3 seconds between requests
BATCH_SIZE = 15       # 15 messages per batch
BATCH_DELAY = 8       # 8 seconds between batches
```

### Aggressive Settings (Use with caution)
```python
RATE_LIMIT_DELAY = 1  # 1 second between requests
BATCH_SIZE = 25       # 25 messages per batch
BATCH_DELAY = 3       # 3 seconds between batches
```

## Monitoring and Debugging

### Log Files
- `telegram_scraper.log`: Detailed operation logs
- Check for "Flood wait error" or "Slow mode error" messages

### Progress Indicators
- Batch progress: "Fetching batch 1/5..."
- Rate limit handling: "Rate limit hit. Waiting X seconds..."
- Success/failure indicators: ✓ for success, ✗ for failure

## Best Practices

1. **Start Small**: Begin with a single source before bulk scraping
2. **Use Keywords**: Filter during scraping to reduce data volume and API calls
3. **Monitor Activity**: Watch for rate limit warnings in logs
4. **Respect Limits**: Don't modify settings to be too aggressive
5. **Backup Data**: Export data regularly to avoid loss

## Troubleshooting

### Account Still Getting Limited?
- Increase `RATE_LIMIT_DELAY` to 5+ seconds
- Reduce `BATCH_SIZE` to 10-15 messages
- Add longer `BATCH_DELAY` (10+ seconds)
- Use keyword filtering to reduce total requests

### Keywords Not Working?
- Check spelling and case (though matching is case-insensitive)
- Try broader keywords first
- Verify the source actually contains relevant content
- Check the "Keywords Matched" column in exports

### Performance Issues?
- Reduce batch sizes
- Increase delays between operations
- Use keyword filtering to reduce data processing
- Consider running during off-peak hours 