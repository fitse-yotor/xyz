# 📖 Read-Only Telegram Scraper Guide

## 🎯 Optimized for Read-Only Accounts

Your scraper is now **SPECIALLY CONFIGURED** for read-only Telegram accounts with **EXTRA-CONSERVATIVE** settings:

### 📊 Read-Only Optimized Settings
```python
RATE_LIMIT_DELAY = 8      # 8 seconds between requests
BATCH_SIZE = 5            # 5 messages per batch
BATCH_DELAY = 15          # 15 seconds between batches
MAX_RETRIES = 1           # 1 retry attempt only
MAX_BATCHES_PER_SOURCE = 2  # 2 batches per source (10 messages max)
MAX_BATCHES_BULK = 1      # 1 batch per source in bulk (5 messages max)
SOURCE_DELAY = 30         # 30 seconds between sources
DAILY_LIMIT = 50          # 50 messages per day
HOURLY_LIMIT = 10         # 10 messages per hour
MAX_SOURCES_PER_DAY = 3   # 3 different sources per day
COOLDOWN_PERIOD = 3600    # 1 hour cooldown between sessions
```

## 🕐 Time Calculations for Read-Only

**Single Source Scraping:**
- 2 batches × 5 messages = 10 messages max
- 2 batches × 15 seconds delay = 30 seconds total
- **Total time: ~30 seconds for 10 messages**

**Bulk Scraping:**
- 1 batch × 5 messages = 5 messages per source
- 1 batch × 15 seconds delay = 15 seconds per source
- 30 seconds between sources
- **Total time: ~45 seconds per source for 5 messages**

## 🔄 How to Use with Read-Only Account

### Step 1: Clear Sessions (if needed)
```bash
cd src/scraper
python clear_sessions.py
# Choose option 2 to clear sessions
```

### Step 2: Run Scraper
```bash
python telegram_scraper.py
# Login with your read-only account
```

### Step 3: Start Conservatively
- **Use Option 2 or 3** (single source with keywords)
- **Monitor progress indicators**
- **Stop when you hit limits**

## 📈 Read-Only Progress Tracking

The scraper shows special indicators for read-only accounts:
```
📊 Progress: 8/10 (hourly), 25/50 (daily)
📋 Sources today: 2/3
⏰ Next session available in 1.0 hours
```

## 🎯 Recommended Strategy for Read-Only

### Day 1-3: Very Conservative
- **1 source per day** maximum
- **Use keywords** to focus on relevant data
- **5-10 messages** per session
- **Wait 2-3 hours** between sessions

### Day 4-7: Moderate
- **2 sources per day** maximum
- **10-20 messages** per session
- **Wait 1-2 hours** between sessions

### Week 2+: Normal
- **3 sources per day** maximum
- **20-50 messages** per session
- **Wait 1 hour** between sessions

## 🚨 Read-Only Warning Signs

**STOP immediately if you see:**
- "Rate limit hit. Waiting X seconds..."
- "Slow mode activated..."
- "Flood wait error..."
- "Read-only cooldown: X seconds remaining"

**Recommended actions:**
1. **Wait 24-48 hours** before trying again
2. **Reduce to 1 source per day**
3. **Use extreme keywords** to filter data
4. **Consider using a different account**

## ⚙️ Emergency Settings for Read-Only

If you're still hitting limits, use these **EXTREME** settings:

```python
# In config.py
RATE_LIMIT_DELAY = 15     # 15 seconds between requests
BATCH_SIZE = 3            # 3 messages per batch
BATCH_DELAY = 30          # 30 seconds between batches
MAX_BATCHES_PER_SOURCE = 1  # 1 batch per source (3 messages max)
MAX_BATCHES_BULK = 1      # 1 batch per source in bulk (3 messages max)
SOURCE_DELAY = 60         # 60 seconds between sources
DAILY_LIMIT = 20          # 20 messages per day
HOURLY_LIMIT = 5          # 5 messages per hour
MAX_SOURCES_PER_DAY = 1   # 1 source per day
COOLDOWN_PERIOD = 7200    # 2 hour cooldown
```

## 🔍 Read-Only Best Practices

### 1. **Use Keywords Effectively**
- **Specific keywords**: "bitcoin", "crypto", "trading"
- **Avoid broad terms**: "news", "update", "info"
- **Combine keywords**: "bitcoin price", "crypto news"

### 2. **Choose Sources Wisely**
- **Public channels** are safer than private groups
- **Large channels** (>10k members) are more stable
- **Avoid spam channels** or recently created ones

### 3. **Time Your Sessions**
- **Avoid peak hours** (evening in your timezone)
- **Spread sessions** throughout the day
- **Respect cooldown periods**

### 4. **Monitor Activity**
- **Check progress** indicators regularly
- **Stop at limits** (don't push boundaries)
- **Log all activity** for troubleshooting

## 📊 Read-Only Limits Summary

| Limit Type | Maximum | Reset Time |
|------------|---------|------------|
| **Hourly Messages** | 10 | Every hour |
| **Daily Messages** | 50 | Every day |
| **Daily Sources** | 3 | Every day |
| **Session Cooldown** | 1 hour | After each session |
| **Messages per Source** | 10 | Per source |
| **Bulk Messages per Source** | 5 | Per source in bulk |

## 🆘 Read-Only Troubleshooting

### Account Still Getting Limited?
1. **Use extreme settings** above
2. **Wait 48-72 hours** before retrying
3. **Use only 1 source per day**
4. **Consider different account**

### Session Issues?
1. Run `python clear_sessions.py`
2. Choose option 2 to clear sessions
3. Restart with new read-only account

### Performance Too Slow?
- **This is intentional** for read-only safety
- **Better slow than banned**
- **Use keywords** to focus on relevant data
- **Consider multiple accounts** for more data

## 🎯 Success Tips for Read-Only

- **Patience is crucial** - Read-only accounts are more sensitive
- **Start very small** - 1 source, 5 messages
- **Use specific keywords** - Focus on what you need
- **Respect all limits** - Don't push boundaries
- **Monitor progress** - Stop at first warning
- **Plan ahead** - Schedule sessions with cooldowns

## 📞 Read-Only Support

If you continue to have issues:
1. **Check logs** in `telegram_scraper.log`
2. **Use extreme settings** temporarily
3. **Consider multiple accounts** for rotation
4. **Wait longer** between sessions (2-3 days)

## 🎯 Key Message

**For read-only accounts:**
- **Quality over quantity** - Focus on relevant data
- **Slow and steady** - Don't rush the process
- **Respect limits** - Your account safety is priority
- **Use keywords** - Filter during scraping
- **Monitor progress** - Stop at first warning

**Remember: It's better to scrape 10 relevant messages safely than 100 messages and lose your read-only account!** 