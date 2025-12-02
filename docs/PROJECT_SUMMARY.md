# Sembako Price API - Project Summary

## 📋 Project Overview

This project provides a RESTful API that scrapes real-time sembako (staple goods) prices from the official Indonesian government website (sp2kp.kemendag.go.id). The API is built with Flask and uses Selenium for scraping JavaScript-rendered content.

## 🎯 Main Objective

Create an API endpoint that returns sembako prices in clean JSON format, making it easy for developers to integrate Indonesian staple goods pricing data into their applications.

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────────┐      ┌──────────────┐
│   Client    │─────▶│  Flask API   │─────▶│    Selenium     │─────▶│   Website    │
│  (Browser/  │      │  (app.py)    │      │  + Chrome       │      │  (sp2kp)     │
│   curl/etc) │◀─────│              │◀─────│  WebDriver      │◀─────│              │
└─────────────┘      └──────────────┘      └─────────────────┘      └──────────────┘
                              │
                              ▼
                     ┌──────────────┐
                     │ BeautifulSoup│
                     │   (Parser)   │
                     └──────────────┘
                              │
                              ▼
                        JSON Response
```

## 🚀 Key Features

1. **Real-time Scraping**: Uses Selenium to handle JavaScript-rendered content
2. **Clean JSON Output**: Structured data with commodity name, unit, prices, and changes
3. **RESTful API**: Standard HTTP GET endpoints with proper status codes
4. **CORS Enabled**: Ready for frontend integration
5. **Error Handling**: Comprehensive error handling for various failure scenarios
6. **Automatic Driver Management**: webdriver-manager handles ChromeDriver installation

## 📁 Project Structure

```
api-stasiun-info/
├── app.py                      # Main Flask application with scraping logic
├── test_scraper.py             # Standalone scraper test
├── test_api.py                 # API endpoint tests
├── example_usage.py            # Usage examples and demonstrations
├── requirements.txt            # Python dependencies
├── start.sh                    # Startup script (macOS/Linux)
├── README.md                   # Comprehensive documentation
├── QUICKSTART.md               # Quick start guide
├── PROJECT_SUMMARY.md          # This file
├── .gitignore                  # Git ignore rules
└── .venv/                      # Virtual environment (not in git)
```

## 🔧 Technology Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.8+ | Programming language |
| Flask | 3.0.0 | Web framework |
| Selenium | 4.15.2 | Browser automation |
| BeautifulSoup4 | 4.12.2 | HTML parsing |
| Chrome | Latest | Headless browser |
| lxml | 5.1.0 | XML/HTML parser |
| flask-cors | 4.0.0 | CORS support |
| webdriver-manager | 4.0.1 | ChromeDriver management |

## 📡 API Endpoints

### 1. Home (`GET /`)
Returns API documentation and information

### 2. Sembako Prices (`GET /api/sembako`)
Returns current sembako prices
- **Response Time**: 5-10 seconds (due to browser automation)
- **Data Format**: JSON with array of price objects

### 3. Health Check (`GET /health`)
Returns API health status

## 📊 Data Structure

```json
{
  "status": "success",
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

### Field Descriptions

- `komoditas`: Commodity name (string)
- `unit`: Unit of measurement - "kg" or "lt" (string)
- `yesterday`: Previous day price in Rupiah (integer)
- `today`: Current day price in Rupiah (integer)
- `change`: Price difference in Rupiah (integer, can be negative)

## 🔄 How It Works

1. **Request Received**: Client sends GET request to `/api/sembako`
2. **Browser Launch**: Selenium starts Chrome in headless mode
3. **Page Load**: Navigates to sp2kp.kemendag.go.id
4. **Wait for Content**: Waits up to 15 seconds for table to appear
5. **Extract HTML**: Gets fully-rendered page source
6. **Parse Data**: BeautifulSoup extracts table rows
7. **Clean Data**: Removes formatting, converts to integers
8. **Return JSON**: Sends structured JSON response
9. **Cleanup**: Closes browser and releases resources

## 🎯 Use Cases

1. **Price Monitoring Apps**: Track sembako prices over time
2. **Budget Planning Tools**: Help users plan grocery budgets
3. **Market Analysis**: Analyze price trends and changes
4. **Educational Projects**: Learn web scraping and API development
5. **Data Aggregation**: Collect data for research or reporting

## ✅ Testing

### Available Test Scripts

1. **test_scraper.py**: Tests scraping functionality independently
2. **test_api.py**: Tests all API endpoints
3. **example_usage.py**: Demonstrates 8 different usage examples

### Run Tests

```bash
# Test scraper
python test_scraper.py

# Test API (server must be running)
python test_api.py

# See usage examples
python example_usage.py
```

## 🚦 Getting Started

### Quick Start (3 steps)

1. **Install dependencies**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Start server**:
   ```bash
   ./start.sh
   # OR
   python app.py
   ```

3. **Test**:
   ```bash
   curl http://localhost:5000/api/sembako
   ```

## 🐛 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| ChromeDriver permission denied | `chmod +x ~/.wdm/drivers/chromedriver/*/chromedriver-mac-arm64/chromedriver` |
| Port 5000 in use | Change port in `app.py` |
| Chrome not found | Install Google Chrome |
| Timeout errors | Increase wait time in `app.py` |

## 📈 Performance Considerations

- **Response Time**: 5-10 seconds per request
- **Resource Usage**: Spawns new Chrome instance per request
- **Scalability**: Consider implementing caching for production use
- **Rate Limiting**: Recommend adding rate limits to avoid overloading source

## 🔮 Future Enhancements

- [ ] Redis caching to reduce scraping frequency
- [ ] Database storage for historical data
- [ ] Scheduled scraping with cron jobs
- [ ] Docker containerization
- [ ] API rate limiting
- [ ] Multiple region support
- [ ] Price alerts/notifications
- [ ] GraphQL endpoint
- [ ] WebSocket for real-time updates
- [ ] Admin dashboard

## 📝 Development Notes

### Why Selenium?

The target website uses Nuxt.js (Vue.js framework) which renders content client-side with JavaScript. Simple HTTP requests won't work because:
- Table data is loaded dynamically
- No direct API endpoints available
- Content requires JavaScript execution

Selenium allows us to:
- Execute JavaScript
- Wait for dynamic content
- Scrape fully-rendered pages

### Alternative Approaches Considered

1. ❌ **requests + BeautifulSoup**: Won't work (no JS execution)
2. ❌ **Scrapy**: Still needs Selenium for JS rendering
3. ✅ **Selenium + BeautifulSoup**: Current approach (works!)
4. 🤔 **Playwright**: Could be alternative, similar to Selenium
5. 🤔 **Puppeteer**: Node.js option, would require rewrite

## 🔐 Security & Ethics

- ✅ Uses public data from government website
- ✅ Respects robots.txt (if present)
- ✅ Uses reasonable request delays
- ✅ Proper user agent strings
- ⚠️ Use responsibly, don't overload server
- ⚠️ Consider caching to minimize requests

## 📄 License

This project is for educational and informational purposes.

## 👨‍💻 Author

Created for scraping sembako prices from Indonesian government's SP2KP Kemendag system.

---

## 📚 Documentation Files

- **README.md**: Full documentation with detailed instructions
- **QUICKSTART.md**: Get started in 5 minutes
- **PROJECT_SUMMARY.md**: This file - project overview
- **Code comments**: Inline documentation in source files

## 🎓 Learning Outcomes

This project demonstrates:
- Web scraping with Selenium
- RESTful API development with Flask
- HTML parsing with BeautifulSoup
- Error handling and logging
- API testing and documentation
- Python best practices

---

**Status**: ✅ Functional and ready for use  
**Last Updated**: November 2024  
**Python Version**: 3.8+  
**Maintenance**: Active