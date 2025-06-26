# 🛡️ Ultra-Safe Telegram Scraper Guide

## ⚠️ Account Protection Settings

Your scraper is now configured with **ULTRA-CONSERVATIVE** settings to prevent account closure:

### 📊 Current Settings
```python
RATE_LIMIT_DELAY = 5      # 5 seconds between requests
BATCH_SIZE = 10           # 10 messages per batch
BATCH_DELAY = 10          # 10 seconds between batches
MAX_RETRIES = 2           # 2 retry attempts
MAX_BATCHES_PER_SOURCE = 3  # 3 batches per source (30 messages max)
MAX_BATCHES_BULK = 2      # 2 batches per source in bulk (20 messages max)
SOURCE_DELAY = 15         # 15 seconds between sources
DAILY_LIMIT = 100         # 100 messages per day
HOURLY_LIMIT = 20         # 20 messages per hour
```

### 🕐 Time Calculations

**Single Source Scraping:**
- 3 batches × 10 messages = 30 messages max
- 3 batches × 10 seconds delay = 30 seconds total
- **Total time: ~1 minute for 30 messages**

**Bulk Scraping:**
- 2 batches × 10 messages = 20 messages per source
- 2 batches × 10 seconds delay = 20 seconds per source
- 15 seconds between sources
- **Total time: ~35 seconds per source for 20 messages**

## 🔄 How to Change Telegram Account

### Step 1: Clear Old Sessions
```bash
cd src/scraper
python clear_sessions.py
```
Choose option 2 to clear all session files.

### Step 2: Run Scraper with New Account
```bash
python telegram_scraper.py
```
The scraper will prompt you to log in with your new Telegram account.

## 🎯 Recommended Usage Strategy

### For New Accounts (First Week)
1. **Start with single source scraping** (Option 2 or 3)
2. **Use keyword filtering** to reduce data volume
3. **Limit to 1-2 sources per day**
4. **Monitor the progress indicators**

### Safe Limits
- **Daily**: Maximum 100 messages
- **Hourly**: Maximum 20 messages
- **Per Source**: Maximum 30 messages
- **Bulk Scraping**: Maximum 20 messages per source

## 📈 Progress Monitoring

The scraper now shows real-time progress:
```
📊 Progress: 15/20 (hourly), 45/100 (daily)
```

**Stop when you see:**
- ⚠️ Hourly limit reached (20 messages)
- ⚠️ Daily limit reached (100 messages)

## 🚨 Warning Signs

**If you see these messages, STOP immediately:**
- "Rate limit hit. Waiting X seconds..."
- "Slow mode activated..."
- "Flood wait error..."

**Recommended actions:**
1. **Wait 24 hours** before trying again
2. **Reduce batch size** in config.py
3. **Increase delays** in config.py
4. **Use keyword filtering** to reduce requests

## ⚙️ Emergency Settings (If Still Getting Limited)

If you're still hitting rate limits, use these **EXTREME** settings:

```python
# In config.py
RATE_LIMIT_DELAY = 10     # 10 seconds between requests
BATCH_SIZE = 5            # 5 messages per batch
BATCH_DELAY = 20          # 20 seconds between batches
MAX_BATCHES_PER_SOURCE = 2  # 2 batches per source (10 messages max)
MAX_BATCHES_BULK = 1      # 1 batch per source in bulk (5 messages max)
SOURCE_DELAY = 30         # 30 seconds between sources
DAILY_LIMIT = 50          # 50 messages per day
HOURLY_LIMIT = 10         # 10 messages per hour
```

## 🔍 Best Practices

### 1. **Start Small**
- Begin with 1 source
- Use keyword filtering
- Monitor progress

### 2. **Spread Out Activity**
- Don't scrape everything at once
- Take breaks between sessions
- Respect daily/hourly limits

### 3. **Use Keywords**
- Filter during scraping
- Reduce data volume
- Focus on relevant content

### 4. **Monitor Logs**
- Check `telegram_scraper.log`
- Look for rate limit warnings
- Stop if you see errors

## 🆘 Troubleshooting

### Account Still Getting Limited?
1. **Increase all delays** by 2x
2. **Reduce batch sizes** by 50%
3. **Use extreme settings** above
4. **Wait 24-48 hours** before retrying

### Session Issues?
1. Run `python clear_sessions.py`
2. Choose option 2 to clear sessions
3. Restart scraper with new account

### Performance Too Slow?
- This is **intentional** for safety
- Better slow than banned
- Use keyword filtering to focus on relevant data

## 📞 Support

If you continue to have issues:
1. **Check the logs** in `telegram_scraper.log`
2. **Use extreme settings** temporarily
3. **Consider using a different account**
4. **Wait longer between sessions**

## 🎯 Success Tips

- **Patience is key** - Slow and steady wins
- **Monitor progress** - Don't exceed limits
- **Use keywords** - Focus on what you need
- **Start conservative** - You can always adjust later
- **Respect limits** - Your account safety comes first

Remember: **It's better to scrape 50 messages safely than 500 messages and lose your account!** 