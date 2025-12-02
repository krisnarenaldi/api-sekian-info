# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2024-11-26

### 🎉 Added - Caching System

#### New Features
- **Daily caching system**: Data is now cached in a JSON file and automatically refreshed once per day
- **Smart cache validation**: Automatically checks if cache was created today before serving data
- **Three new API endpoints**:
  - `GET /api/sembako` - Enhanced with automatic caching (existing endpoint improved)
  - `GET /api/sembako/cache-status` - Check cache file status and validity
  - `POST /api/sembako/refresh` - Force refresh the cache regardless of validity

#### Performance Improvements
- **100-200x faster response times** for cached requests (~50ms vs ~5-10 seconds)
- Reduced load on source website (only one scrape per day)
- Lower server resource usage (CPU, memory, network)

#### New Files
- `sembako_cache.json` - Cache file for storing daily scraped data (auto-generated, git-ignored)
- `test_caching.py` - Comprehensive test suite for caching functionality
- `CACHING_GUIDE.md` - Complete documentation for the caching system
- `CHANGELOG.md` - This file

#### Code Changes
- Added cache management functions: `is_cache_valid()`, `load_cache()`, `save_cache()`
- Refactored scraping logic into separate `scrape_sembako_data()` function
- Enhanced `/api/sembako` endpoint to check cache before scraping
- Updated response format to include cache metadata (`from_cache`, `cache_date`, `scraped_at`)

#### Documentation Updates
- Updated `README.md` with caching system documentation
- Added cache-related examples to `example_usage.py`
- Updated `.gitignore` to exclude `sembako_cache.json`
- Updated API home endpoint (`/`) with new endpoint documentation

### 🔧 Fixed
- Fixed incorrect import for `WebDriverWait` (now imports from `selenium.webdriver.support.wait`)
- Removed unused `timedelta` import

### 📝 Changed
- API responses now include cache status indicators
- Port remains at `5500` for consistency
- Enhanced error handling for cache operations

### 🎯 Benefits

#### For Users
- ⚡ Near-instant response times for cached data
- 📊 Transparent cache status in responses
- 🔄 Automatic daily updates without manual intervention
- 🛡️ Reliable data consistency throughout the day

#### For Developers
- 🧪 New test suite for caching functionality
- 📚 Comprehensive caching documentation
- 🔧 Manual refresh capability for testing
- 📊 Cache monitoring endpoints

#### For System
- 🌐 Respectful to source website (one request per day)
- 💰 Reduced bandwidth and computational costs
- 📈 Better scalability for multiple users
- 🔒 Offline capability with cached data

### 🚀 Usage Examples

#### Get Data (with automatic caching)
```bash
curl http://localhost:5500/api/sembako
```

#### Check Cache Status
```bash
curl http://localhost:5500/api/sembako/cache-status
```

#### Force Refresh
```bash
curl -X POST http://localhost:5500/api/sembako/refresh
```

### 📊 Response Format Changes

The `/api/sembako` endpoint now includes additional fields:

**New Fields:**
- `from_cache` (boolean) - Indicates if data came from cache
- `cache_date` (string) - Timestamp when cache was created (if from cache)
- `scraped_at` (string) - Timestamp when data was scraped (if fresh)

**Example Response:**
```json
{
  "status": "success",
  "from_cache": true,
  "cache_date": "2024-11-26 08:30:15",
  "date_info": {...},
  "data": [...],
  "total_items": 16
}
```

### 🧪 Testing

New test file added:
```bash
python test_caching.py
```

Tests include:
- Cache status checking
- First request (cold start)
- Second request (cache hit)
- Force refresh functionality
- Performance comparison
- Local cache file verification

### 📚 Documentation

New documentation added:
- **CACHING_GUIDE.md** - Complete guide to the caching system
- **Updated README.md** - Added caching sections
- **Updated example_usage.py** - New caching examples

### ⚙️ Technical Details

#### Cache Validity Logic
- Cache is valid if file exists and was modified today (since midnight)
- Automatically invalidates at midnight
- First request after midnight triggers fresh scrape

#### File Structure
```
api-stasiun-info/
├── app.py                 # Enhanced with caching
├── sembako_cache.json     # Cache file (auto-generated)
├── test_caching.py        # New test suite
├── CACHING_GUIDE.md       # New documentation
├── CHANGELOG.md           # This file
└── ...
```

### 🔄 Migration Notes

**No breaking changes!** The API is fully backward compatible.

- Existing clients will work without modification
- New response fields are additive only
- Cache is created automatically on first request
- No configuration changes required

### 🐛 Known Issues

None at this time.

### 🔮 Future Improvements

Potential enhancements for future versions:
- [ ] Configurable cache duration
- [ ] Multi-region cache support
- [ ] Cache compression
- [ ] Redis/Memcached integration
- [ ] Cache warming on startup
- [ ] Historical data tracking

---

## [1.0.0] - 2024-11-25

### Initial Release

- Web scraping using Selenium
- RESTful API with Flask
- JSON response format
- Price change calculations
- CORS support
- Health check endpoint
- Basic error handling
- Comprehensive documentation

---

**Format:** This changelog follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)  
**Versioning:** This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)