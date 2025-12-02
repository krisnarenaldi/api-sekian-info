# Flight Arrivals API Documentation

## Overview
This API endpoint provides real-time flight arrival information for **Soekarno-Hatta International Airport (CGK)** in Jakarta, Indonesia. The data is scraped from the official Jakarta Airport website and automatically selects the appropriate time period based on the current hour.

## Endpoint

### GET `/api/flights/arrivals`

Retrieves current flight arrivals for Soekarno-Hatta Airport.

**URL:** `http://localhost:5500/api/flights/arrivals`

**Method:** `GET`

**Authentication:** None required

## Time Period Logic

The API automatically determines which time period to scrape based on the current hour:

| Current Time Range | Query Parameter (`tp`) | URL |
|-------------------|------------------------|-----|
| 00:00 - 05:59 | `tp=0` | `https://www.jakarta-airport.com/cgk-arrivals?tp=0` |
| 06:00 - 11:59 | `tp=6` | `https://www.jakarta-airport.com/cgk-arrivals?tp=6` |
| 12:00 - 17:59 | `tp=12` | `https://www.jakarta-airport.com/cgk-arrivals?tp=12` |
| 18:00 - 23:59 | `tp=18` | `https://www.jakarta-airport.com/cgk-arrivals?tp=18` |

## Response Format

### Success Response (200 OK)

```json
{
  "status": "success",
  "airport": "Soekarno-Hatta International Airport (CGK)",
  "type": "arrivals",
  "time_period": 12,
  "scraped_at": "2025-12-01 13:45:30",
  "total_flights": 150,
  "flights": [
    {
      "origin": "Singapore (SIN)",
      "arrival_time": "12:10",
      "flight_numbers": ["ID7154"],
      "airlines": ["Batik Air"],
      "terminal": "Terminal 2",
      "status": "Landed - On-time"
    },
    {
      "origin": "Kuala Lumpur (KUL)",
      "arrival_time": "13:00",
      "flight_numbers": ["AK351"],
      "airlines": ["AirAsia"],
      "terminal": "Terminal 2",
      "status": "Landed - Delayed"
    }
  ]
}
```

### Error Response (404/500)

```json
{
  "status": "error",
  "message": "Description of the error"
}
```

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Response status: "success" or "error" |
| `airport` | string | Airport name and code |
| `type` | string | Flight type: "arrivals" |
| `time_period` | integer | Time period parameter used (0, 6, 12, or 18) |
| `scraped_at` | string | Timestamp when data was scraped (YYYY-MM-DD HH:MM:SS) |
| `total_flights` | integer | Total number of flights found |
| `flights` | array | Array of flight objects |

### Flight Object Fields

| Field | Type | Description |
|-------|------|-------------|
| `origin` | string | Origin city and airport code |
| `arrival_time` | string | Scheduled/estimated arrival time (HH:MM format) |
| `flight_numbers` | array | List of flight numbers (e.g., ["GA123", "SQ456"]) |
| `airlines` | array | List of airline names operating the flight |
| `terminal` | string | Arrival terminal (e.g., "Terminal 1", "Terminal 2", "Terminal 3") |
| `status` | string | Flight status (e.g., "Landed - On-time", "En Route - Delayed", "Scheduled - On-time") |

## Flight Status Types

Common status values you may encounter:

- **Landed - On-time**: Flight has landed at the scheduled time
- **Landed - Delayed**: Flight has landed but was delayed
- **En Route - On-time**: Flight is currently in the air, expected on time
- **En Route - Delayed**: Flight is in the air but expected to be delayed
- **Scheduled - On-time**: Flight is scheduled and expected on time
- **Scheduled - Delayed**: Flight is scheduled but expected to be delayed

## Usage Examples

### cURL

```bash
curl http://localhost:5500/api/flights/arrivals
```

### Python (requests)

```python
import requests

response = requests.get('http://localhost:5500/api/flights/arrivals')
data = response.json()

if data['status'] == 'success':
    print(f"Total flights: {data['total_flights']}")
    for flight in data['flights'][:5]:
        print(f"{flight['arrival_time']} - {flight['origin']} - {flight['status']}")
```

### JavaScript (fetch)

```javascript
fetch('http://localhost:5500/api/flights/arrivals')
  .then(response => response.json())
  .then(data => {
    if (data.status === 'success') {
      console.log(`Total flights: ${data.total_flights}`);
      data.flights.forEach(flight => {
        console.log(`${flight.arrival_time} - ${flight.origin} - ${flight.status}`);
      });
    }
  });
```

### Testing Script

A test script is provided: `test_flight_arrivals.py`

```bash
python test_flight_arrivals.py
```

This will:
1. Make a request to the flight arrivals endpoint
2. Display summary information
3. Show the first 5 flights
4. Save the complete response to `flight_arrivals_response.json`

## Implementation Details

### Technology Stack

- **Web Scraping**: Selenium WebDriver with Chrome (headless mode)
- **HTML Parsing**: BeautifulSoup4 with lxml parser
- **Framework**: Flask

### Scraping Process

1. Determines current hour to select appropriate time period
2. Constructs URL with correct `tp` parameter
3. Initializes headless Chrome browser
4. Waits for flight information to load (up to 15 seconds)
5. Extracts data from the `flights-info` div structure
6. Parses flight rows and columns
7. Returns structured JSON response

### Performance

- **Typical Response Time**: 5-10 seconds (depends on network and page load time)
- **Data Freshness**: Real-time (scraped on each request)
- **No Caching**: Data is scraped fresh on every request to ensure accuracy

## Error Handling

The API handles various error scenarios:

1. **Network Issues**: Returns 500 error with connection details
2. **Page Load Timeout**: Returns 500 error after 15 seconds
3. **Missing Data**: Returns 404 if flight information div is not found
4. **Parse Errors**: Individual flight rows with errors are skipped; others are still returned

## Limitations

1. **Response Time**: Scraping requires 5-10 seconds per request
2. **Rate Limiting**: No built-in rate limiting; be considerate with request frequency
3. **Source Website Changes**: If jakarta-airport.com changes their HTML structure, the scraper may need updates
4. **Browser Requirements**: Requires Chrome/Chromium and ChromeDriver installed

## Dependencies

Required Python packages (from `requirements.txt`):

```
selenium==4.15.2
beautifulsoup4==4.12.2
lxml==5.1.0
flask==3.0.0
flask-cors==4.0.0
webdriver-manager==4.0.1
```

## Future Enhancements

Potential improvements:

- [ ] Add caching mechanism (e.g., 5-minute cache)
- [ ] Add departure flights endpoint
- [ ] Filter by airline, terminal, or status
- [ ] Search by flight number
- [ ] Add pagination for large result sets
- [ ] Historical flight data storage
- [ ] Flight delay statistics

## Contributing

If you encounter issues or have suggestions:

1. Check if the jakarta-airport.com website structure has changed
2. Verify Chrome/ChromeDriver compatibility
3. Review error logs for detailed stack traces

## License

This API is for educational and informational purposes. Please respect the source website's terms of service and robots.txt file.

## Data Source

Data is scraped from: [https://www.jakarta-airport.com/cgk-arrivals](https://www.jakarta-airport.com/cgk-arrivals)

**Disclaimer**: This is not an official airport API. Always verify flight information with official airline or airport sources.