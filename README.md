# Sembako Price API 🛒

API for scraping sembako (staple goods) prices from the official Indonesian government website [sp2kp.kemendag.go.id](https://sp2kp.kemendag.go.id/)

## Features

- 🕷️ Real-time web scraping using Selenium for JavaScript-rendered content
- 💾 Smart caching system - data cached daily to minimize scraping
- 📊 Clean JSON format output
- 🔄 Automatic price change calculation
- 🌐 CORS enabled for frontend integration
- 🚀 RESTful API with Flask
- 💰 Includes commodity name, unit, yesterday's price, today's price, and price change
- ⚡ Fast response times with cache (data updated once daily)

## Prerequisites

- Python 3.8 or higher
- Google Chrome browser (required for Selenium)
- pip (Python package installer)

## Installation

### 1. Clone or navigate to the project directory

```bash
cd api-stasiun-info
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

### 3. Activate the virtual environment

**On macOS/Linux:**
```bash
source .venv/bin/activate
```

**On Windows:**
```bash
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Verify Chrome is installed

Make sure Google Chrome is installed on your system. Selenium will use ChromeDriver to control Chrome in headless mode.

## Usage

### Start the Flask server

```bash
python app.py
```

The server will start on `http://localhost:5000`

You should see output like:
```
 * Running on http://0.0.0.0:5000
 * Serving Flask app 'app'
 * Debug mode: on
```

## API Endpoints

### 🏠 `GET /`

Home endpoint with API documentation

**Example Request:**
```bash
curl http://localhost:5000/
```

**Response:**
```json
{
  "message": "Sembako Price API",
  "version": "1.0.0",
  "description": "API for scraping sembako prices from sp2kp.kemendag.go.id",
  "endpoints": {
    "/": {
      "method": "GET",
      "description": "API documentation and information"
    },
    "/health": {
      "method": "GET",
      "description": "Health check endpoint"
    },
    "/api/sembako": {
      "method": "GET",
      "description": "Get current sembako prices (from cache if valid, otherwise scrapes new data)",
      "note": "Cache is valid if it was created/updated today. Data is only updated once daily."
    },
    "/api/sembako/cache-status": {
      "method": "GET",
      "description": "Check the status of the cache file"
    },
    "/api/sembako/refresh": {
      "method": "POST",
      "description": "Force refresh the cache by scraping new data"
    }
  }
}
```

### 💰 `GET /api/sembako`

Get current sembako prices. This endpoint uses a smart caching system:
- **First request of the day**: Scrapes fresh data from the website (~5-10 seconds)
- **Subsequent requests**: Returns cached data instantly
- **Cache validity**: Cache is valid if it was created/updated today (since midnight)

**Example Request:**
```bash
curl http://localhost:5000/api/sembako
```

**Response (from cache):**
```json
{
  "status": "success",
  "from_cache": true,
  "cache_date": "2024-11-26 08:30:15",
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
    },
    {
      "komoditas": "Beras Premium",
      "unit": "kg",
      "yesterday": 16300,
      "today": 16300,
      "change": 0
    },
    {
      "komoditas": "Gula Pasir Curah",
      "unit": "kg",
      "yesterday": 18100,
      "today": 18100,
      "change": 0
    }
  ],
  "total_items": 16
}
```

**Response (freshly scraped):**
```json
{
  "status": "success",
  "from_cache": false,
  "scraped_at": "2024-11-26 08:30:15",
  "date_info": {
    "yesterday": "25 Nov",
    "today": "26 Nov"
  },
  "data": [...],
  "total_items": 16
}
```

### 📋 `GET /api/sembako/cache-status`

Check the status of the cache file

**Example Request:**
```bash
curl http://localhost:5000/api/sembako/cache-status
```

**Response (cache exists):**
```json
{
  "status": "success",
  "cache_exists": true,
  "cache_valid": true,
  "last_modified": "2024-11-26 08:30:15",
  "file_size": 12458
}
```

**Response (no cache):**
```json
{
  "status": "success",
  "cache_exists": false,
  "message": "No cache file found"
}
```

### 🔄 `POST /api/sembako/refresh`

Force refresh the cache by scraping new data (regardless of cache validity)

**Example Request:**
```bash
curl -X POST http://localhost:5000/api/sembako/refresh
```

**Response:**
```json
{
  "status": "success",
  "from_cache": false,
  "scraped_at": "2024-11-26 09:15:30",
  "force_refreshed": true,
  "date_info": {
    "yesterday": "25 Nov",
    "today": "26 Nov"
  },
  "data": [...],
  "total_items": 16
}
```

### ❤️ `GET /health`

Health check endpoint

**Example Request:**
```bash
curl http://localhost:5000/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Sembako Price API"
}
```

## Testing

### Test the scraper directly

```bash
python test_scraper.py
```

This will test the scraping functionality without starting the Flask server.

### Test the caching functionality

Make sure the Flask server is running, then in another terminal:

```bash
python test_caching.py
```

This comprehensive test will:
- Check cache status
- Make first request (should scrape)
- Make second request (should use cache)
- Force refresh the cache
- Verify cache file locally

### Test the API endpoints

Make sure the Flask server is running, then in another terminal:

```bash
python test_api.py
```

Or use curl:

```bash
# Test home endpoint
curl http://localhost:5000/

# Test sembako endpoint
curl http://localhost:5000/api/sembako

# Test health endpoint
curl http://localhost:5000/health

# Test cache status
curl http://localhost:5000/api/sembako/cache-status

# Force refresh cache
curl -X POST http://localhost:5000/api/sembako/refresh
```

### Using a browser

Simply open these URLs in your browser:
- http://localhost:5000/
- http://localhost:5000/api/sembako
- http://localhost:5000/api/sembako/cache-status
- http://localhost:5000/health

### Using Python requests

```python
import requests

response = requests.get('http://localhost:5000/api/sembako')
data = response.json()

if data['status'] == 'success':
    for item in data['data']:
        print(f"{item['komoditas']}: Rp {item['today']:,}")
```

## Data Structure

Each item in the `data` array contains:

| Field | Type | Description |
|-------|------|-------------|
| `komoditas` | string | Name of the commodity (e.g., "Beras Medium") |
| `unit` | string | Unit of measurement (e.g., "kg", "lt") |
| `yesterday` | integer | Price from yesterday in Rupiah (without formatting) |
| `today` | integer | Current price in Rupiah (without formatting) |
| `change` | integer | Price change in Rupiah (positive = increase, negative = decrease) |

**Note:** All prices are returned as integers without the "Rp" prefix or thousand separators.

## Error Handling

The API includes comprehensive error handling for:
- ❌ Network request failures
- ❌ Missing table data on the source website
- ❌ Parsing errors
- ❌ Timeout issues
- ❌ ChromeDriver initialization problems

Error responses follow this format:

```json
{
  "status": "error",
  "message": "Description of the error"
}
```

## Technical Details

### How it works

1. **Cache Check**: On each request, the system first checks if a valid cache file exists (created/modified today)
2. **Return Cache**: If cache is valid, returns the cached data immediately (< 1ms response time)
3. **Selenium WebDriver**: If no valid cache, uses Selenium with Chrome in headless mode to load the JavaScript-rendered website
4. **Wait for Content**: Waits for the table element to appear (up to 15 seconds)
5. **BeautifulSoup**: Parses the rendered HTML to extract table data
6. **Data Cleaning**: Cleans and formats prices and changes into integers
7. **Save Cache**: Saves the scraped data to a JSON file for future requests
8. **JSON Response**: Returns structured JSON data

### Caching System

The API implements a daily caching system to improve performance and reduce load on the source website:

- **Cache File**: `sembako_cache.json` (stored in the project root)
- **Cache Validity**: Cache is valid if modified on the current day (since midnight)
- **Automatic Refresh**: Cache automatically refreshes on the first request after midnight
- **Manual Refresh**: Use `POST /api/sembako/refresh` to force a refresh
- **Benefits**:
  - ⚡ Near-instant response times for cached data
  - 🌐 Reduced load on the source website
  - 📊 Data consistency throughout the day
  - 💾 Offline capability with cached data

### Why Selenium?

The target website (sp2kp.kemendag.go.id) uses Nuxt.js (Vue.js framework) for client-side rendering. The table data is loaded dynamically with JavaScript, which means simple HTTP requests won't work. Selenium allows us to:
- Execute JavaScript
- Wait for dynamic content to load
- Scrape the fully-rendered page

### Performance

**With Caching (Most Requests):**
- ⚡ Response time: < 100ms
- 💾 Serves data from JSON file

**First Request of the Day (Cache Miss):**
- 🕐 Response time: 5-10 seconds (due to page loading and rendering)
- 🔄 Scrapes fresh data and updates cache

**Manual Refresh:**
- 🕐 Response time: 5-10 seconds
- 🔄 Forces new scrape regardless of cache validity

ChromeDriver is downloaded and cached automatically on first run.

## Dependencies

```
flask==3.0.0              # Web framework
beautifulsoup4==4.12.2    # HTML parsing
requests==2.31.0          # HTTP library (for future use)
lxml==5.1.0               # Fast XML/HTML parser
flask-cors==4.0.0         # CORS support
selenium==4.15.2          # Browser automation
webdriver-manager==4.0.1  # Automatic ChromeDriver management
```

## Project Structure

```
api-stasiun-info/
├── app.py                 # Main Flask application
├── test_scraper.py        # Test script for scraper functionality
├── test_api.py            # Test script for API endpoints
├── test_caching.py        # Test script for caching functionality
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── .gitignore            # Git ignore rules
├── sembako_cache.json     # Cache file (auto-generated, git-ignored)
└── .venv/                # Virtual environment (created during setup)
```

## Troubleshooting

### ChromeDriver issues

If you encounter ChromeDriver errors:

1. Make sure Chrome browser is installed
2. Delete the cached driver: `rm -rf ~/.wdm`
3. Reinstall: `pip install --upgrade selenium webdriver-manager`
4. Run the test script: `python test_scraper.py`

### Permission errors

If you get permission errors for ChromeDriver:

```bash
chmod +x ~/.wdm/drivers/chromedriver/*/chromedriver-mac-arm64/chromedriver
```

### Port already in use

If port 5000 is already in use, you can change it in `app.py`:

```python
app.run(debug=True, host="0.0.0.0", port=5001)  # Change to 5001 or any available port
```

### Timeout errors

If requests timeout, the website might be:
- Down or under maintenance
- Blocking your requests
- Taking longer than expected to load

Try increasing the timeout in `app.py`:

```python
wait = WebDriverWait(driver, 30)  # Increase from 15 to 30 seconds
```

## Notes

- ⚖️ The scraper targets the official Indonesian government website
- 📅 Data availability depends on the source website
- 🔢 Prices are returned as integers in Rupiah (without "Rp" prefix or formatting)
- 🤖 The API respects the source website by using appropriate user agents
- ⏱️ Each request takes 5-10 seconds due to browser automation

## Legal & Ethical Considerations

This tool is intended for:
- ✅ Educational purposes
- ✅ Personal use
- ✅ Public information aggregation

Please:
- ✅ Respect the source website's terms of service
- ✅ Don't overload the server with too many requests
- ✅ The built-in caching system minimizes requests to the source
- ✅ Use responsibly

## Future Improvements

Potential enhancements:
- [x] Add caching to reduce scraping frequency (✅ Implemented)
- [ ] Support for multiple regions/cities
- [ ] Historical price tracking
- [ ] Price alerts and notifications
- [ ] Docker containerization
- [ ] API rate limiting
- [ ] Database integration
- [ ] Scheduled scraping with cron jobs

## License

This project is for educational and informational purposes.

## Author

Created for scraping sembako prices from the Indonesian government's price monitoring system (SP2KP Kemendag).

---

**Happy Scraping! 🚀**

For issues or questions, please check the troubleshooting section or test the scraper directly with `python test_scraper.py`.