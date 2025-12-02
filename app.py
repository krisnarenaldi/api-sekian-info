import json
import os
import pathlib
import re
import time
from datetime import datetime

from bs4 import BeautifulSoup
from flask import Flask, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from serpapi import GoogleSearch
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)
CORS(app)

# Cache file paths
CACHE_FILE = "sembako_cache.json"
CINEMA_CACHE_FILE = "cinema.json"
EVENTS_CACHE_FILE = "events_tix.json"


def get_driver():
    """Initialize and return a Chrome WebDriver with headless options"""
    chrome_options = Options()
    # Use the new headless mode which is more stable
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--disable-software-rasterizer")
    
    # Memory optimization flags for low-memory environments (Render free tier = 512MB)
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-background-networking")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-breakpad")
    chrome_options.add_argument("--disable-component-extensions-with-background-pages")
    chrome_options.add_argument("--disable-features=TranslateUI,BlinkGenPropertyTrees")
    chrome_options.add_argument("--disable-ipc-flooding-protection")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--enable-features=NetworkService,NetworkServiceInProcess")
    chrome_options.add_argument("--force-color-profile=srgb")
    chrome_options.add_argument("--hide-scrollbars")
    chrome_options.add_argument("--metrics-recording-only")
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--disable-setuid-sandbox")
    # Removed --single-process as it causes crashes with newer Chrome versions
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--window-size=1280,720")  # Smaller window
    
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )

    # Check if we are running in a container with specific env vars
    chrome_bin = os.environ.get("CHROME_BIN")
    chromedriver_path = os.environ.get("CHROMEDRIVER_PATH")

    if chrome_bin:
        chrome_options.binary_location = chrome_bin

    if chromedriver_path and os.path.exists(chromedriver_path):
        service = Service(chromedriver_path)
    else:
        # Fallback to webdriver_manager for local development
        try:
            # Get the chromedriver path and ensure it points to the actual executable
            import stat

            driver_path = ChromeDriverManager().install()

            # Fix for webdriver-manager issue where it may point to wrong file
            driver_dir = os.path.dirname(driver_path)
            actual_driver = os.path.join(driver_dir, "chromedriver")

            # Check if chromedriver exists in the directory
            if os.path.isfile(actual_driver):
                driver_path = actual_driver
                # Make sure it's executable
                if not os.access(driver_path, os.X_OK):
                    os.chmod(driver_path, os.stat(driver_path).st_mode | stat.S_IEXEC)

            service = Service(driver_path)
        except Exception as e:
            print(f"Error installing chromedriver: {e}")
            raise e

    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def clean_price(price_str):
    """Extract numeric value from price string like 'Rp 14.500'"""
    cleaned = re.sub(r"[^\d]", "", price_str)
    return int(cleaned) if cleaned else 0


def clean_change(change_str):
    """Extract numeric value from change string, keeping negative sign if present"""
    if not change_str or change_str.strip() == "-":
        return 0

    # Check if it's a decrease (contains -)
    is_negative = "-" in change_str

    # Remove everything except digits
    cleaned = re.sub(r"[^\d]", "", change_str)

    if not cleaned:
        return 0

    value = int(cleaned)
    return -value if is_negative else value


def is_cache_valid():
    """Check if cache file exists and was modified today"""
    if not os.path.exists(CACHE_FILE):
        return False

    # Get the modification time of the cache file
    mod_time = datetime.fromtimestamp(os.path.getmtime(CACHE_FILE))

    # Get today's date at midnight
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # Cache is valid if it was modified today (on or after midnight)
    return mod_time >= today


def load_cache():
    """Load data from cache file"""
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading cache: {e}")
        return None


def save_cache(data):
    """Save data to cache file"""
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving cache: {e}")
        return False


def scrape_sembako_data():
    """Scrape sembako prices from sp2kp.kemendag.go.id using Selenium"""
    driver = None
    try:
        url = "https://sp2kp.kemendag.go.id/"

        # Initialize driver
        driver = get_driver()
        driver.get(url)

        # Wait for the table to load (wait for table element)
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "v-table__wrapper")))

        # Give extra time for data to populate
        time.sleep(5)

        # Get the page source after JavaScript has rendered
        page_source = driver.page_source

        # Parse with BeautifulSoup
        soup = BeautifulSoup(page_source, "lxml")

        # Find the table with class v-table__wrapper
        table_wrapper = soup.find("div", class_="v-table__wrapper")

        if not table_wrapper:
            print("ERROR: Table wrapper not found")
            return jsonify(
                {"status": "error", "message": "Table not found on the page"}
            ), 404

        table = table_wrapper.find("table")
        tbody = table.find("tbody")

        if not tbody:
            print("ERROR: Table body not found")
            return jsonify({"status": "error", "message": "Table body not found"}), 404

        # Extract header dates
        thead = table.find("thead")
        headers_row = thead.find("tr")
        th_elements = headers_row.find_all("th")

        # Get date labels from headers (indices 2 and 3)
        date_yesterday = (
            th_elements[2].get_text(strip=True) if len(th_elements) > 2 else "Yesterday"
        )
        date_today = (
            th_elements[3].get_text(strip=True) if len(th_elements) > 3 else "Today"
        )

        # Extract data rows
        rows = tbody.find_all("tr")
        print(f"DEBUG: Found {len(rows)} rows in tbody")
        data = []

        for row in rows:
            cells = row.find_all("td")

            if len(cells) >= 5:
                komoditas = cells[0].get_text(strip=True)
                unit = cells[1].get_text(strip=True)
                yesterday_price = clean_price(cells[2].get_text(strip=True))
                today_price = clean_price(cells[3].get_text(strip=True))
                change_value = clean_change(cells[4].get_text(strip=True))

                # Skip empty rows
                if komoditas:
                    data.append(
                        {
                            "komoditas": komoditas,
                            "unit": unit,
                            "yesterday": yesterday_price,
                            "today": today_price,
                            "change": change_value,
                        }
                    )
            else:
                print(f"DEBUG: Skipping row with only {len(cells)} cells")

        print(f"DEBUG: Extracted {len(data)} items with complete data")

        return jsonify(
            {
                "status": "success",
                "date_info": {"yesterday": date_yesterday, "today": date_today},
                "data": data,
                "total_items": len(data),
            }
        ), 200

    except Exception as e:
        print(f"ERROR: Exception during scraping: {str(e)}")
        import traceback

        traceback.print_exc()
        return jsonify(
            {"status": "error", "message": f"An error occurred: {str(e)}"}
        ), 500

    finally:
        if driver:
            driver.quit()


@app.route("/api/sembako", methods=["GET"])
def get_sembako_prices():
    """Get sembako prices - from cache if valid, otherwise scrape new data"""
    try:
        # Check if cache is valid (modified today)
        if is_cache_valid():
            cached_data = load_cache()
            if cached_data:
                cached_data["from_cache"] = True
                cached_data["cache_date"] = datetime.fromtimestamp(
                    os.path.getmtime(CACHE_FILE)
                ).strftime("%Y-%m-%d %H:%M:%S")
                return jsonify(cached_data), 200

        # Cache is invalid or doesn't exist, scrape new data
        response_data = scrape_sembako_data()

        # If scraping was successful, save to cache
        if response_data[1] == 200:  # Check status code
            response_json = response_data[0].get_json()
            response_json["from_cache"] = False
            response_json["scraped_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_cache(response_json)
            return jsonify(response_json), 200
        else:
            return response_data

    except Exception as e:
        return jsonify(
            {"status": "error", "message": f"An error occurred: {str(e)}"}
        ), 500


@app.route("/api/sembako/cache-status", methods=["GET"])
def cache_status():
    """Get cache file status"""
    if not os.path.exists(CACHE_FILE):
        return jsonify(
            {
                "status": "success",
                "cache_exists": False,
                "message": "No cache file found",
            }
        ), 200

    mod_time = datetime.fromtimestamp(os.path.getmtime(CACHE_FILE))
    is_valid = is_cache_valid()

    return jsonify(
        {
            "status": "success",
            "cache_exists": True,
            "cache_valid": is_valid,
            "last_modified": mod_time.strftime("%Y-%m-%d %H:%M:%S"),
            "file_size": os.path.getsize(CACHE_FILE),
        }
    ), 200


@app.route("/api/sembako/refresh", methods=["POST"])
def refresh_cache():
    """Force refresh the cache by scraping new data"""
    try:
        response_data = scrape_sembako_data()

        # If scraping was successful, save to cache
        if response_data[1] == 200:  # Check status code
            response_json = response_data[0].get_json()
            response_json["from_cache"] = False
            response_json["scraped_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            response_json["force_refreshed"] = True
            save_cache(response_json)
            return jsonify(response_json), 200
        else:
            return response_data

    except Exception as e:
        return jsonify(
            {"status": "error", "message": f"An error occurred: {str(e)}"}
        ), 500


@app.route("/", methods=["GET"])
def home():
    """Home endpoint with API documentation"""
    return jsonify(
        {
            "message": "Sembako Price API",
            "version": "1.0.0",
            "description": "API for scraping sembako prices from sp2kp.kemendag.go.id with daily caching",
            "endpoints": {
                "/": {
                    "method": "GET",
                    "description": "API documentation and information",
                },
                "/health": {"method": "GET", "description": "Health check endpoint"},
                "/api/sembako": {
                    "method": "GET",
                    "description": "Get current sembako prices (from cache if valid, otherwise scrapes new data)",
                    "note": "Cache is valid if it was created/updated today. Data is only updated once daily.",
                },
                "/api/sembako/cache-status": {
                    "method": "GET",
                    "description": "Check the status of the cache file",
                },
                "/api/sembako/refresh": {
                    "method": "POST",
                    "description": "Force refresh the cache by scraping new data",
                },
                "/api/flights/arrivals": {
                    "method": "GET",
                    "description": "Get real-time flight arrivals for Soekarno-Hatta International Airport (CGK). Automatically selects the appropriate time period based on current hour.",
                },
                "/api/cinema": {
                    "method": "GET",
                    "description": "Get cinema/movie data from tix.id (from cache if valid, otherwise scrapes new data)",
                    "note": "Cache is valid for 6 days. Data is automatically refreshed every 6 days.",
                },
                "/api/events": {
                    "method": "GET",
                    "description": "Get events data from tix.id/tix-events (from cache if valid, otherwise scrapes new data)",
                    "note": "Cache is valid for 5 days. Data is automatically refreshed every 5 days. Returns max 15 events.",
                },
            },
            "example_usage": {
                "curl_get": "curl http://localhost:5000/api/sembako",
                "curl_refresh": "curl -X POST http://localhost:5000/api/sembako/refresh",
                "curl_cache_status": "curl http://localhost:5000/api/sembako/cache-status",
                "curl_flights": "curl http://localhost:5000/api/flights/arrivals",
                "curl_cinema": "curl http://localhost:5000/api/cinema",
                "curl_events": "curl http://localhost:5000/api/events",
                "browser": "http://localhost:5000/api/sembako",
            },
            "response_format": {
                "status": "success or error",
                "from_cache": "boolean indicating if data is from cache",
                "cache_date": "when cache was created (if from cache)",
                "scraped_at": "when data was scraped (if freshly scraped)",
                "date_info": {"yesterday": "date string", "today": "date string"},
                "data": [
                    {
                        "komoditas": "commodity name",
                        "unit": "unit of measurement",
                        "yesterday": "price as integer",
                        "today": "price as integer",
                        "change": "price change as integer",
                    }
                ],
                "total_items": "number of items",
            },
        }
    ), 200


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "Sembako Price API"}), 200


@app.route("/api/google_trend", methods=["GET"])
def get_trend():
    """Get Google Trend data"""
    # return jsonify({"status": "success", "data": []}), 200
    file_path = "trending_now.json"

    my_json_file = pathlib.Path(file_path)
    now = time.time()
    modification_timestamp = 0

    if my_json_file.exists():
        modification_timestamp = my_json_file.stat().st_mtime
    else:
        print(f"{my_json_file} does not exist")

    selisih = (now - modification_timestamp) / 60 / 60

    if selisih <= 24.00:
        with open(file_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)

        # Format the data to return only query, search_volume, and category (limit to 10 items)
        formatted_trends = []
        for item in data["trending_searches"][:10]:
            formatted_item = {
                "query": item["query"],
                "search_volume": item.get("search_volume", 0),
                "category": item["categories"][0]["name"]
                if item.get("categories")
                else "Unknown",
            }
            formatted_trends.append(formatted_item)

        return jsonify({"status": "success", "trending_searches": formatted_trends})

    else:
        print("ambil trend langsung")
        serpapi_key = os.environ.get("SERPAPI_KEY")
        if not serpapi_key:
            return jsonify({
                "status": "error",
                "message": "SERPAPI_KEY environment variable not set"
            }), 500
        
        search = GoogleSearch(
            {
                "api_key": serpapi_key,
                "engine": "google_trends_trending_now",
                "hl": "id",
                "geo": "ID",
            }
        )
        result = search.get_dict()

        # replace file json with the latest
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(result, json_file, indent=4)

        # Format the data to return only query, search_volume, and category (limit to 10 items)
        formatted_trends = []
        for item in result["trending_searches"][:10]:
            formatted_item = {
                "query": item["query"],
                "search_volume": item.get("search_volume", 0),
                "category": item["categories"][0]["name"]
                if item.get("categories")
                else "Unknown",
            }
            formatted_trends.append(formatted_item)

        return jsonify({"status": "success", "trending_searches": formatted_trends})


def get_flight_url_by_time():
    """Get the appropriate flight URL based on current hour"""
    current_hour = datetime.now().hour

    if 0 <= current_hour < 6:
        tp = 0
    elif 6 <= current_hour < 12:
        tp = 6
    elif 12 <= current_hour < 18:
        tp = 12
    else:  # 18 <= current_hour < 24
        tp = 18

    return f"https://www.jakarta-airport.com/cgk-arrivals?tp={tp}", tp


def scrape_flight_arrivals():
    """Scrape flight arrivals from Jakarta Airport (Soekarno-Hatta)

    Includes robust error handling for HTML structure changes:
    - Multiple selector fallbacks
    - Data validation
    - Detailed error logging
    - Graceful degradation
    """
    driver = None
    try:
        url, time_period = get_flight_url_by_time()

        print(f"Scraping flights from: {url}")

        # Initialize driver
        driver = get_driver()
        driver.get(url)

        # Wait for the flights info section to load with multiple fallback selectors
        wait = WebDriverWait(driver, 15)

        # Try multiple selectors in case the HTML structure changes
        selectors_to_try = [
            (By.CLASS_NAME, "flights-info"),
            (By.CLASS_NAME, "flight-row"),
            (By.TAG_NAME, "table"),  # Fallback if they switch to table
        ]

        page_loaded = False
        for selector_type, selector_value in selectors_to_try:
            try:
                wait.until(
                    EC.presence_of_element_located((selector_type, selector_value))
                )
                page_loaded = True
                print(
                    f"DEBUG: Page loaded using selector: {selector_type}={selector_value}"
                )
                break
            except Exception as e:
                print(
                    f"DEBUG: Selector {selector_type}={selector_value} failed, trying next..."
                )
                continue

        if not page_loaded:
            return jsonify(
                {
                    "status": "error",
                    "message": "Page structure has changed. Unable to locate flight data container.",
                    "troubleshooting": "The website HTML structure may have been updated. Please check the source website and update the scraper.",
                    "url": url,
                }
            ), 404

        # Give extra time for data to populate
        time.sleep(3)

        # Get the page source after JavaScript has rendered
        page_source = driver.page_source

        # Parse with BeautifulSoup
        soup = BeautifulSoup(page_source, "lxml")

        # Try to find the flights-info div with fallbacks
        flights_info = soup.find("div", class_="flights-info")

        if not flights_info:
            # Fallback: try to find any div containing flight data
            print("WARNING: flights-info div not found, trying fallback selectors...")
            flights_info = soup.find(
                "div", class_=lambda x: x and "flight" in x.lower()
            )

            if not flights_info:
                # Last resort: try to find table
                flights_info = soup.find("table")

                if not flights_info:
                    print("ERROR: No flight container found with any selector")
                    return jsonify(
                        {
                            "status": "error",
                            "message": "Flight information container not found on the page",
                            "troubleshooting": "The HTML structure has likely changed. Check class names: 'flights-info', 'flight-row', 'flight-col__*'",
                            "url": url,
                            "last_successful_scrape": "Check logs for last working version",
                        }
                    ), 404

        # Find all flight rows (skip the header row with class "flight-titol")
        flight_rows = flights_info.find_all("div", class_="flight-row")

        if not flight_rows:
            print("WARNING: No flight-row divs found, trying alternative selectors...")
            # Try alternative row selectors
            flight_rows = flights_info.find_all(
                "div", class_=lambda x: x and "row" in x.lower()
            )

            if not flight_rows:
                flight_rows = flights_info.find_all("tr")  # Fallback to table rows

        if not flight_rows:
            print("ERROR: No flight rows found")
            return jsonify(
                {
                    "status": "error",
                    "message": "No flight rows found",
                    "troubleshooting": "The website structure has changed. Expected class 'flight-row' not found.",
                    "url": url,
                }
            ), 404

        flights = []
        parsing_errors = []

        for idx, row in enumerate(flight_rows):
            # Skip the header row
            if "flight-titol" in row.get("class", []):
                continue

            try:
                # Extract flight data from columns
                cols = row.find_all("div", class_="flight-col")

                if len(cols) >= 6:
                    # Extract origin with fallbacks
                    origin_col = row.find("div", class_="flight-col__dest-term")
                    if not origin_col:
                        origin_col = row.find(
                            "div", class_=lambda x: x and "dest" in x.lower()
                        )
                    origin = origin_col.get_text(strip=True) if origin_col else ""

                    # Extract arrival time with fallbacks
                    arrival_col = row.find("div", class_="flight-col__hour")
                    if not arrival_col:
                        arrival_col = row.find(
                            "div",
                            class_=lambda x: x
                            and "hour" in x.lower()
                            or "time" in x.lower(),
                        )
                    arrival_time = (
                        arrival_col.get_text(strip=True) if arrival_col else ""
                    )

                    # Extract flight number(s) with fallbacks
                    flight_col = row.find("div", class_="flight-col__flight")
                    if not flight_col:
                        flight_col = row.find(
                            "div", class_=lambda x: x and "flight" in x.lower()
                        )

                    flight_numbers = ""
                    if flight_col:
                        # Find first flight number link
                        flight_link = flight_col.find("a")
                        if flight_link:
                            flight_numbers = flight_link.get_text(strip=True)

                    # Extract airline(s) with fallbacks
                    airline_col = row.find("div", class_="flight-col__airline")
                    if not airline_col:
                        airline_col = row.find(
                            "div", class_=lambda x: x and "airline" in x.lower()
                        )

                    airlines = ""
                    if airline_col:
                        # Get first airline name
                        airline_span = airline_col.find("span")
                        if airline_span:
                            airlines = airline_span.get_text(strip=True)
                        else:
                            # Fallback: get first stripped string
                            strings = list(airline_col.stripped_strings)
                            if strings:
                                airlines = strings[0]

                    # Extract terminal with fallbacks
                    terminal_col = row.find("div", class_="flight-col__term")
                    if not terminal_col:
                        terminal_col = row.find(
                            "div", class_=lambda x: x and "term" in x.lower()
                        )
                    terminal = terminal_col.get_text(strip=True) if terminal_col else ""

                    # Extract status with fallbacks
                    status_col = row.find("div", class_="flight-col__status")
                    if not status_col:
                        status_col = row.find(
                            "div", class_=lambda x: x and "status" in x.lower()
                        )
                    status = status_col.get_text(strip=True) if status_col else ""

                    # Data validation - only add if we have at least origin and arrival time
                    if origin and arrival_time:
                        flight_data = {
                            "origin": origin,
                            "arrival_time": arrival_time,
                            "flight_numbers": flight_numbers,
                            "airlines": airlines,
                            "terminal": terminal,
                            "status": status,
                        }
                        flights.append(flight_data)
                    else:
                        parsing_errors.append(
                            f"Row {idx}: Missing required fields (origin or arrival_time)"
                        )

            except Exception as e:
                error_msg = f"Row {idx}: {str(e)}"
                parsing_errors.append(error_msg)
                print(f"Error parsing flight row: {error_msg}")
                continue

        print(
            f"DEBUG: Extracted {len(flights)} flights with {len(parsing_errors)} errors"
        )

        # If we have too many parsing errors, the structure likely changed
        if len(parsing_errors) > 0 and len(flights) == 0:
            return jsonify(
                {
                    "status": "error",
                    "message": "Unable to parse any flight data. The website structure may have changed.",
                    "parsing_errors": parsing_errors[:5],  # Show first 5 errors
                    "troubleshooting": "Check if class names changed: flight-col__dest-term, flight-col__hour, flight-col__flight, etc.",
                    "url": url,
                }
            ), 500

        # Warning if we got some flights but many errors
        warning = None
        if len(parsing_errors) > len(flights) * 0.3:  # More than 30% errors
            warning = f"High parsing error rate: {len(parsing_errors)} errors while extracting {len(flights)} flights. Website structure may have partially changed."

        response_data = {
            "status": "success",
            "airport": "Soekarno-Hatta International Airport (CGK)",
            "type": "arrivals",
            "time_period": time_period,
            "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_flights": len(flights),
            # "flights": flights[:],
            "flights": flights,
        }

        if warning:
            response_data["warning"] = warning
            response_data["parsing_errors_count"] = len(parsing_errors)

        if len(flights) == 0:
            response_data["status"] = "error"
            response_data["message"] = (
                "No flights extracted. The website structure has likely changed."
            )
            return jsonify(response_data), 500

        return jsonify(response_data), 200

    except Exception as e:
        print(f"ERROR: Exception during flight scraping: {str(e)}")
        import traceback

        traceback.print_exc()

        error_details = {
            "status": "error",
            "message": f"An error occurred: {str(e)}",
            "error_type": type(e).__name__,
            "troubleshooting": {
                "timeout_error": "Increase wait time or check if website is down",
                "no_such_element": "HTML structure has changed, update selectors",
                "connection_error": "Check network or if website is accessible",
            },
            "url": url if "url" in locals() else "Unknown",
            "traceback": traceback.format_exc()[-500:],  # Last 500 chars of traceback
        }

        return jsonify(error_details), 500

    finally:
        if driver:
            driver.quit()


@app.route("/api/flights/arrivals", methods=["GET"])
def get_flight_arrivals():
    """Get flight arrivals for Soekarno-Hatta Airport"""
    try:
        return scrape_flight_arrivals()
    except Exception as e:
        return jsonify(
            {"status": "error", "message": f"An error occurred: {str(e)}"}
        ), 500


def scrape_cinema_data():
    """Scrape movie data from tix.id"""
    driver = None
    try:
        url = "https://www.tix.id/"
        print(f"Scraping cinema data from: {url}")

        driver = get_driver()
        driver.get(url)

        # Wait for glide slides to load
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "glide__slides")))

        time.sleep(3)  # Extra wait for dynamic content

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "lxml")

        # Find all glide__slides lists
        glide_lists = soup.find_all("ul", class_="glide__slides")
        
        movies = []
        
        for i, glide_list in enumerate(glide_lists):
            # Check if this list contains movie links
            items = glide_list.find_all("li", class_="glide__slide")
            
            temp_movies = []
            for idx, item in enumerate(items):
                link = item.find("a")
                if not link:
                    continue
                
                href = link.get("href", "")
                
                # Only process links with movie-detail
                if "movie-detail" not in href:
                    continue
                
                # Find img tag - it might be nested
                img_tag = link.find("img")
                if not img_tag:
                    continue
                
                img_src = img_tag.get("src", "")
                if not img_src:
                    continue
                
                # Title extraction - try multiple methods
                title = ""
                
                # Method 1: Look for span with title
                span = link.find("span")
                if span:
                    title = span.get_text(strip=True)
                
                # Method 2: Try title attribute on link
                if not title:
                    title = link.get("title", "")
                
                # Method 3: Try alt attribute on img
                if not title:
                    title = img_tag.get("alt", "")
                
                # Method 4: Get all text from link
                if not title:
                    title = link.get_text(strip=True)
                
                # Method 5: Check parent li for title info
                if not title:
                    # Look for any text in the entire li element
                    all_text = item.get_text(strip=True)
                    if all_text:
                        title = all_text
                
                # Add if we have both img and title
                if img_src and title:
                    temp_movies.append({
                        "img": img_src,
                        "title": title
                    })
            
            # If we found movies in this list, add them
            if temp_movies:
                movies.extend(temp_movies)
        
        # If no movies found with "movie-detail" in href, try to be more lenient 
        # or check if the structure matches the user's example exactly.
        # The user said: get list element, and take <img> and title of movie in tag <a ... href="...movie-detail..." />
        
        # Let's deduplicate based on title just in case
        unique_movies = []
        seen_titles = set()
        for m in movies:
            if m["title"] not in seen_titles:
                unique_movies.append(m)
                seen_titles.add(m["title"])
        
        return jsonify({
            "items": unique_movies[:17]
        }), 200

    except Exception as e:
        print(f"ERROR: Exception during cinema scraping: {str(e)}")
        return jsonify(
            {"status": "error", "message": f"An error occurred: {str(e)}"}
        ), 500
    finally:
        if driver:
            driver.quit()


def is_cinema_cache_valid():
    """Check if cinema cache file exists and is less than 6 days old"""
    if not os.path.exists(CINEMA_CACHE_FILE):
        return False

    # Get the modification time of the cache file
    cinema_file = pathlib.Path(CINEMA_CACHE_FILE)
    mod_timestamp = cinema_file.stat().st_mtime
    
    # Get current timestamp
    current_timestamp = time.time()
    
    # Calculate delta in seconds (6 days = 6 * 24 * 60 * 60 seconds)
    delta = current_timestamp - mod_timestamp
    six_days_in_seconds = 6 * 24 * 60 * 60
    
    # Cache is valid if it's less than 6 days old
    return delta < six_days_in_seconds


def load_cinema_cache():
    """Load cinema data from cache file"""
    try:
        with open(CINEMA_CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading cinema cache: {e}")
        return None


def save_cinema_cache(data):
    """Save cinema data to cache file"""
    try:
        with open(CINEMA_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving cinema cache: {e}")
        return False


@app.route("/api/cinema", methods=["GET"])
def get_cinema_data():
    """Get cinema data from tix.id - from cache if valid (< 6 days old), otherwise scrape new data"""
    try:
        # Check if cache is valid (less than 6 days old)
        if is_cinema_cache_valid():
            cached_data = load_cinema_cache()
            if cached_data and "items" in cached_data:
                cinema_file = pathlib.Path(CINEMA_CACHE_FILE)
                # Add metadata to response
                response = {
                    "items": cached_data["items"],
                    "from_cache": True,
                    "cache_date": datetime.fromtimestamp(
                        cinema_file.stat().st_mtime
                    ).strftime("%Y-%m-%d %H:%M:%S")
                }
                return jsonify(response), 200

        # Cache is invalid or doesn't exist, scrape new data
        response_data = scrape_cinema_data()

        # If scraping was successful, save to cache
        if response_data[1] == 200:  # Check status code
            response_json = response_data[0].get_json()
            response_json["from_cache"] = False
            response_json["scraped_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_cinema_cache(response_json)
            return jsonify(response_json), 200
        else:
            return response_data

    except Exception as e:
        return jsonify(
            {"status": "error", "message": f"An error occurred: {str(e)}"}
        ), 500


def is_events_cache_valid():
    """Check if events cache file exists and is less than 5 days old"""
    if not os.path.exists(EVENTS_CACHE_FILE):
        return False

    # Get the modification time of the cache file
    events_file = pathlib.Path(EVENTS_CACHE_FILE)
    mod_timestamp = events_file.stat().st_mtime

    # Get current timestamp
    current_timestamp = time.time()

    # Calculate delta in seconds (5 days = 5 * 24 * 60 * 60 seconds)
    delta = current_timestamp - mod_timestamp
    five_days_in_seconds = 5 * 24 * 60 * 60

    # Cache is valid if it's less than 5 days old
    return delta < five_days_in_seconds


def load_events_cache():
    """Load events data from cache file"""
    try:
        with open(EVENTS_CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading events cache: {e}")
        return None


def save_events_cache(data):
    """Save events data to cache file"""
    try:
        with open(EVENTS_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving events cache: {e}")
        return False


def scrape_events_data():
    """Scrape events data from tix.id/tix-events"""
    driver = None
    try:
        url = "https://www.tix.id/tix-events/"
        print(f"Scraping events data from: {url}")

        driver = get_driver()
        driver.get(url)

        # Wait for swiper-wrapper to load
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "swiper-wrapper")))

        time.sleep(3)  # Extra wait for dynamic content

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "lxml")

        # Find the swiper-wrapper div
        swiper_wrapper = soup.find("div", class_="swiper-wrapper")

        if not swiper_wrapper:
            print("ERROR: swiper-wrapper not found")
            return jsonify(
                {"status": "error", "message": "swiper-wrapper not found on the page"}
            ), 404

        # Get all swiper-slide elements
        slides = swiper_wrapper.find_all("div", class_="swiper-slide")

        events = []

        for idx, slide in enumerate(slides[:19]):  # Limit to 19 elements
            try:
                # Find img tag for poster
                img_tag = slide.find("img")
                if not img_tag:
                    continue

                poster = img_tag.get("src", "")
                if not poster:
                    continue

                # Find event title - try multiple methods
                event_title = ""

                # Method 1: Look for title in img alt
                event_title = img_tag.get("alt", "")

                # Method 2: Look for any link with title
                if not event_title:
                    link = slide.find("a")
                    if link:
                        event_title = link.get("title", "")

                # Method 3: Look for text content
                if not event_title:
                    # Try to find any text in the slide
                    text_content = slide.get_text(strip=True)
                    if text_content:
                        event_title = text_content

                # Add if we have both poster and title
                if poster and event_title:
                    events.append({"poster": poster, "event_title": event_title})

            except Exception as e:
                print(f"Error parsing event slide {idx}: {str(e)}")
                continue

        print(f"DEBUG: Extracted {len(events)} events")

        return jsonify({"items": events}), 200

    except Exception as e:
        print(f"ERROR: Exception during events scraping: {str(e)}")
        import traceback

        traceback.print_exc()
        return jsonify(
            {"status": "error", "message": f"An error occurred: {str(e)}"}
        ), 500
    finally:
        if driver:
            driver.quit()


@app.route("/api/events", methods=["GET"])
def get_events_data():
    """Get events data from tix.id - from cache if valid (< 5 days old), otherwise scrape new data"""
    try:
        # Check if cache is valid (less than 5 days old)
        if is_events_cache_valid():
            cached_data = load_events_cache()
            if cached_data:
                events_file = pathlib.Path(EVENTS_CACHE_FILE)
                cached_data["from_cache"] = True
                cached_data["cache_date"] = datetime.fromtimestamp(
                    events_file.stat().st_mtime
                ).strftime("%Y-%m-%d %H:%M:%S")
                return jsonify(cached_data), 200

        # Cache is invalid or doesn't exist, scrape new data
        response_data = scrape_events_data()

        # If scraping was successful, save to cache
        if response_data[1] == 200:  # Check status code
            response_json = response_data[0].get_json()
            response_json["from_cache"] = False
            response_json["scraped_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_events_cache(response_json)
            return jsonify(response_json), 200
        else:
            return response_data

    except Exception as e:
        return jsonify(
            {"status": "error", "message": f"An error occurred: {str(e)}"}
        ), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5500))
    app.run(debug=True, host="0.0.0.0", port=port)
