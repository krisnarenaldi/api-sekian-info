# Quick Reference Guide - Caching System ⚡

**TL;DR:** Data is cached daily. First request scrapes (~8s), subsequent requests use cache (~50ms).

## Endpoints

| Endpoint | Method | Purpose | Speed |
|----------|--------|---------|-------|
| `/api/sembako` | GET | Get prices (auto-cached) | 50ms (cached) / 8s (fresh) |
| `/api/sembako/cache-status` | GET | Check cache status | <10ms |
| `/api/sembako/refresh` | POST | Force refresh cache | ~8s |

## Quick Commands

```bash
# Get prices (uses cache if valid)
curl http://localhost:5500/api/sembako

# Check cache status
curl http://localhost:5500/api/sembako/cache-status

# Force refresh
curl -X POST http://localhost:5500/api/sembako/refresh
```

## Response Indicators

### Cached Response
```json
{
  "from_cache": true,
  "cache_date": "2024-11-26 08:30:15",
  ...
}
```

### Fresh Response
```json
{
  "from_cache": false,
  "scraped_at": "2024-11-26 14:30:22",
  ...
}
```

## Cache Rules

✅ **Valid Cache:**
- File exists
- Modified TODAY (since midnight)

❌ **Invalid Cache:**
- File doesn't exist
- Modified YESTERDAY or earlier

## Daily Cycle

```
00:00 → Cache invalidates
08:00 → First request → Scrapes fresh (8s) → Saves cache
08:30 → Second request → Returns cache (0.05s)
10:00 → Third request → Returns cache (0.04s)
...   → All day → Uses cache
23:59 → Last request → Uses cache (0.05s)
00:00 → Cache invalidates → Cycle repeats
```

## Python Example

```python
import requests

# Regular request
r = requests.get('http://localhost:5500/api/sembako')
data = r.json()

if data['from_cache']:
    print(f"✅ Cached: {data['cache_date']}")
else:
    print(f"🔄 Fresh: {data['scraped_at']}")

# Check status
status = requests.get('http://localhost:5500/api/sembako/cache-status').json()
print(f"Valid: {status['cache_valid']}")

# Force refresh
fresh = requests.post('http://localhost:5500/api/sembako/refresh').json()
print(f"Items: {fresh['total_items']}")
```

## JavaScript Example

```javascript
// Regular request
const data = await fetch('http://localhost:5500/api/sembako').then(r => r.json());
console.log(data.from_cache ? `✅ Cached` : `🔄 Fresh`);

// Check status
const status = await fetch('http://localhost:5500/api/sembako/cache-status').then(r => r.json());
console.log(`Valid: ${status.cache_valid}`);

// Force refresh
const fresh = await fetch('http://localhost:5500/api/sembako/refresh', {
  method: 'POST'
}).then(r => r.json());
```

## Testing

```bash
# Run caching test suite
python test_caching.py

# Run all tests
python test_api.py
python test_scraper.py
python test_caching.py
```

## File Location

- **Cache file:** `sembako_cache.json` (auto-generated)
- **Location:** Project root directory
- **Git:** Ignored (not committed)

## Performance

| Scenario | Time | Source |
|----------|------|--------|
| First request (cold) | ~8 seconds | Scraping |
| Cached request | ~50ms | JSON file |
| Force refresh | ~8 seconds | Scraping |
| Cache status check | <10ms | File system |

**Speedup:** 160x faster with cache! 🚀

## Common Issues

### Cache not updating?
```bash
# Check file modification time
ls -l sembako_cache.json

# Force refresh
curl -X POST http://localhost:5500/api/sembako/refresh
```

### Cache file missing?
No problem! It will be created on first request.

### Permission errors?
```bash
chmod 644 sembako_cache.json
```

## When to Force Refresh

✅ **Do force refresh:**
- Testing new features
- Urgent data update needed
- Cache appears corrupted

❌ **Don't force refresh:**
- Normal operations (automatic is fine)
- Multiple times per day
- In production without reason

## Cache Status Response

```json
{
  "status": "success",
  "cache_exists": true,
  "cache_valid": true,
  "last_modified": "2024-11-26 08:30:15",
  "file_size": 12458
}
```

## Best Practices

1. ✅ Use `/api/sembako` for normal requests
2. ✅ Let cache handle freshness automatically
3. ✅ Monitor with `/cache-status` endpoint
4. ✅ Force refresh only when necessary
5. ❌ Don't delete cache file manually
6. ❌ Don't edit cache JSON directly
7. ❌ Don't spam force refresh

## Key Benefits

- ⚡ **Speed:** 160x faster responses
- 🌐 **Network:** Minimal upstream requests
- 💰 **Cost:** Reduced bandwidth/CPU
- 📊 **Reliability:** Consistent daily data
- 🛡️ **Resilience:** Works offline with cache

## Documentation

- `README.md` - General API documentation
- `CACHING_GUIDE.md` - Complete caching documentation
- `CACHE_FLOW.txt` - Visual flow diagrams
- `CHANGELOG.md` - Version history

## Need Help?

1. Check cache status: `GET /api/sembako/cache-status`
2. View cache file: `cat sembako_cache.json`
3. Check modification time: `stat sembako_cache.json`
4. Force refresh: `POST /api/sembako/refresh`
5. Check logs for errors

---

**Version:** 1.1.0  
**Updated:** November 2024