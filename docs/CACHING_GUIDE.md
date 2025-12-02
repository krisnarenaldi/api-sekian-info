# Caching System Guide 💾

This document explains the new caching system implemented in the Sembako Price API.

## Overview

The API now implements a smart daily caching system that stores scraped data in a JSON file. This significantly improves performance and reduces load on the source website.

## How It Works

### Cache Flow

```
┌─────────────────────┐
│ Request Received    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Check Cache File    │
│ - Exists?           │
│ - Modified today?   │
└──────────┬──────────┘
           │
     ┌─────┴─────┐
     │           │
     ▼           ▼
┌─────────┐  ┌──────────┐
│ Valid   │  │ Invalid  │
│ Cache   │  │ or None  │
└────┬────┘  └────┬─────┘
     │            │
     ▼            ▼
┌─────────┐  ┌──────────────┐
│ Return  │  │ Scrape Fresh │
│ Cache   │  │ Data         │
│ (~50ms) │  │ (~5-10 sec)  │
└─────────┘  └──────┬───────┘
                    │
                    ▼
             ┌──────────────┐
             │ Save to Cache│
             └──────┬───────┘
                    │
                    ▼
             ┌──────────────┐
             │ Return Data  │
             └──────────────┘
```

## Cache File

**Location:** `sembako_cache.json` (in project root)

**Format:**
```json
{
  "status": "success",
  "from_cache": false,
  "scraped_at": "2024-11-26 08:30:15",
  "date_info": {
    "yesterday": "25 Nov",
    "today": "26 Nov"
  },
  "data": [
    {
      "komoditas": "Beras Medium",
      "unit": "kg",
      "yesterday": 14500,
      "today": 14500,
      "change": 0
    }
  ],
  "total_items": 16
}
```

## Cache Validity Rules

The cache is considered **VALID** if:
- ✅ The cache file exists
- ✅ File was last modified TODAY (on or after midnight)

The cache is considered **INVALID** if:
- ❌ The cache file doesn't exist
- ❌ File was last modified YESTERDAY or earlier

## API Endpoints

### 1. Get Sembako Prices (with caching)

```bash
GET /api/sembako
```

**Behavior:**
- Checks cache validity automatically
- Returns cached data if valid (fast ~50ms)
- Scrapes new data if cache is invalid (~5-10 seconds)
- Saves freshly scraped data to cache

**Response Fields:**
- `from_cache`: Boolean indicating if data came from cache
- `cache_date`: Timestamp when cache was created (if from cache)
- `scraped_at`: Timestamp when data was scraped (if freshly scraped)

### 2. Check Cache Status

```bash
GET /api/sembako/cache-status
```

**Response:**
```json
{
  "status": "success",
  "cache_exists": true,
  "cache_valid": true,
  "last_modified": "2024-11-26 08:30:15",
  "file_size": 12458
}
```

### 3. Force Refresh Cache

```bash
POST /api/sembako/refresh
```

**Behavior:**
- Ignores cache validity
- Always scrapes fresh data
- Updates the cache file
- Returns the newly scraped data

**Use Cases:**
- Manual data refresh
- Testing
- When you need the absolute latest data

## Performance Comparison

### Before Caching
- Every request: ~5-10 seconds
- Server load: High
- Network usage: High

### After Caching
- First request of day: ~5-10 seconds (scrape)
- Subsequent requests: ~50-100ms (cache hit)
- Server load: Minimal
- Network usage: One scrape per day

### Example Performance
```
Request 1 (cold): 8.2 seconds  🔄 (scraping)
Request 2 (warm): 0.05 seconds 📦 (cached) → 164x faster!
Request 3 (warm): 0.04 seconds 📦 (cached) → 205x faster!
```

## Daily Update Cycle

```
Midnight (00:00)
    │
    ▼
Cache becomes invalid
    │
    ▼
First request after midnight
    │
    ▼
Scrapes fresh data (~5-10s)
    │
    ▼
Saves to cache
    │
    ▼
All subsequent requests use cache (~50ms)
    │
    ▼
Midnight (00:00) - Cycle repeats
```

## Code Examples

### Python

```python
import requests

# Regular request (uses cache if valid)
response = requests.get('http://localhost:5500/api/sembako')
data = response.json()

if data.get('from_cache'):
    print(f"✅ Using cached data from {data.get('cache_date')}")
else:
    print(f"🔄 Fresh data scraped at {data.get('scraped_at')}")

# Check cache status
status = requests.get('http://localhost:5500/api/sembako/cache-status')
print(status.json())

# Force refresh
refresh = requests.post('http://localhost:5500/api/sembako/refresh')
print(f"Cache refreshed! Total items: {refresh.json()['total_items']}")
```

### JavaScript (fetch)

```javascript
// Regular request
const response = await fetch('http://localhost:5500/api/sembako');
const data = await response.json();

if (data.from_cache) {
  console.log(`✅ Using cached data from ${data.cache_date}`);
} else {
  console.log(`🔄 Fresh data scraped at ${data.scraped_at}`);
}

// Check cache status
const status = await fetch('http://localhost:5500/api/sembako/cache-status');
const cacheInfo = await status.json();
console.log(`Cache valid: ${cacheInfo.cache_valid}`);

// Force refresh
const refresh = await fetch('http://localhost:5500/api/sembako/refresh', {
  method: 'POST'
});
const freshData = await refresh.json();
console.log(`Cache refreshed! Items: ${freshData.total_items}`);
```

### cURL

```bash
# Regular request
curl http://localhost:5500/api/sembako

# Check cache status
curl http://localhost:5500/api/sembako/cache-status

# Force refresh
curl -X POST http://localhost:5500/api/sembako/refresh
```

## Testing

Run the comprehensive caching test suite:

```bash
python test_caching.py
```

This will test:
1. Cache status endpoint
2. First request (cold start)
3. Second request (cache hit)
4. Force refresh functionality
5. Local cache file verification

## Configuration

### Cache File Location

The cache file path is defined in `app.py`:

```python
CACHE_FILE = "sembako_cache.json"
```

To change the location, modify this constant:

```python
CACHE_FILE = "/path/to/your/cache/sembako_cache.json"
```

### Cache Validity Logic

Cache validity is determined by the `is_cache_valid()` function:

```python
def is_cache_valid():
    """Check if cache file exists and was modified today"""
    if not os.path.exists(CACHE_FILE):
        return False
    
    mod_time = datetime.fromtimestamp(os.path.getmtime(CACHE_FILE))
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    return mod_time >= today
```

## Best Practices

### ✅ Do:
- Use the regular `/api/sembako` endpoint for most requests
- Let the caching system handle data freshness automatically
- Use cache status endpoint to monitor cache health
- Force refresh only when necessary (testing, critical updates)

### ❌ Don't:
- Don't repeatedly call force refresh endpoint (unnecessary load)
- Don't manually edit the cache file (it will be overwritten)
- Don't delete cache file during operation (it will be recreated)
- Don't bypass the cache for normal operations

## Troubleshooting

### Cache not being created

**Problem:** Requests always scrape fresh data

**Solution:**
1. Check file permissions in project directory
2. Verify `CACHE_FILE` path is writable
3. Check logs for save errors

### Cache not updating after midnight

**Problem:** Using old data even though it's a new day

**Solution:**
1. Check server system time
2. Verify cache file modification time
3. Force refresh manually to reset

### Cache file corrupted

**Problem:** JSON parsing errors

**Solution:**
```bash
# Delete cache file and let it regenerate
rm sembako_cache.json
```

### Permission denied errors

**Problem:** Cannot read/write cache file

**Solution:**
```bash
# Fix permissions
chmod 644 sembako_cache.json

# Or if the directory needs fixing
chmod 755 .
```

## Benefits

### 🚀 Performance
- 100-200x faster response times for cached requests
- Reduced server CPU usage
- Lower memory consumption

### 🌐 Network
- Minimal impact on source website
- Only one scrape per day (max)
- Respectful to upstream servers

### 📊 Reliability
- Data consistency throughout the day
- Works offline with cached data
- Graceful fallback to scraping

### 💰 Cost
- Reduced bandwidth usage
- Lower computational costs
- Fewer failed requests

## Monitoring

### Check Cache Health

```bash
# Quick status check
curl http://localhost:5500/api/sembako/cache-status | jq

# Monitor file system
ls -lh sembako_cache.json
stat sembako_cache.json
```

### Log Monitoring

The application logs cache operations:
- Cache hits
- Cache misses
- Save operations
- Errors

## Future Enhancements

Potential improvements to consider:

- [ ] Configurable cache duration (hourly, daily, custom)
- [ ] Multiple cache files for different regions
- [ ] Cache compression for large datasets
- [ ] Redis/Memcached integration
- [ ] Cache warming on startup
- [ ] Automated cache cleanup
- [ ] Cache versioning
- [ ] Distributed cache support

## Summary

The caching system provides:
- ⚡ **Fast responses** - Sub-second for cached data
- 🔄 **Automatic refresh** - Daily updates without manual intervention
- 🎯 **Smart logic** - Only scrapes when needed
- 🛡️ **Reliability** - Graceful error handling
- 📊 **Transparency** - Clear indication of cache status
- 🔧 **Control** - Manual refresh when needed

---

**Updated:** November 2024  
**Version:** 1.0.0  
**Author:** Sembako Price API Team