import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def get_driver():
    """Initialize and return a Chrome WebDriver with headless options"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )

    # Get the chromedriver path and ensure it points to the actual executable
    import os
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

    is_negative = "-" in change_str
    cleaned = re.sub(r"[^\d]", "", change_str)

    if not cleaned:
        return 0

    value = int(cleaned)
    return -value if is_negative else value


def test_scraper():
    """Test scraping sembako prices using Selenium"""
    driver = None
    try:
        url = "https://sp2kp.kemendag.go.id/"

        print("Initializing Chrome WebDriver...")
        driver = get_driver()
        print("✓ WebDriver initialized")

        print(f"\nFetching data from: {url}")
        driver.get(url)
        print("✓ Page loaded")

        print("\nWaiting for table to render...")
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "v-table__wrapper")))
        print("✓ Table element detected")

        # Give extra time for data to populate
        time.sleep(2)
        print("✓ Waited for data to populate")

        # Get the page source after JavaScript has rendered
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "lxml")

        table_wrapper = soup.find("div", class_="v-table__wrapper")

        if not table_wrapper:
            print("✗ Table wrapper not found!")
            return

        print("✓ Found table wrapper")

        table = table_wrapper.find("table")
        tbody = table.find("tbody")

        if not tbody:
            print("✗ Table body not found!")
            return

        print("✓ Found table body")

        thead = table.find("thead")
        headers_row = thead.find("tr")
        th_elements = headers_row.find_all("th")

        date_yesterday = (
            th_elements[2].get_text(strip=True) if len(th_elements) > 2 else "Yesterday"
        )
        date_today = (
            th_elements[3].get_text(strip=True) if len(th_elements) > 3 else "Today"
        )

        print(f"✓ Date columns: {date_yesterday} | {date_today}")

        rows = tbody.find_all("tr")
        data = []

        for row in rows:
            cells = row.find_all("td")

            if len(cells) >= 5:
                komoditas = cells[0].get_text(strip=True)
                unit = cells[1].get_text(strip=True)
                yesterday_price = clean_price(cells[2].get_text(strip=True))
                today_price = clean_price(cells[3].get_text(strip=True))
                change_value = clean_change(cells[4].get_text(strip=True))

                data.append(
                    {
                        "komoditas": komoditas,
                        "unit": unit,
                        "yesterday": yesterday_price,
                        "today": today_price,
                        "change": change_value,
                    }
                )

        print(f"\n✓ Successfully scraped {len(data)} items\n")
        print("=" * 70)
        print("Sample Data (first 5 items):")
        print("=" * 70)

        for i, item in enumerate(data[:5]):
            print(f"\n{i + 1}. {item['komoditas']}")
            print(f"   Unit: {item['unit']}")
            print(f"   {date_yesterday}: Rp {item['yesterday']:,}")
            print(f"   {date_today}: Rp {item['today']:,}")
            change_symbol = "+" if item["change"] > 0 else ""
            print(f"   Change: {change_symbol}Rp {item['change']:,}")

        print("\n" + "=" * 70)
        print(f"Total items scraped: {len(data)}")
        print("=" * 70)

        print("\n✓ Test completed successfully!")

        # Show JSON format
        print("\n" + "=" * 70)
        print("Sample JSON format:")
        print("=" * 70)
        import json

        print(json.dumps(data[:3], indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback

        traceback.print_exc()

    finally:
        if driver:
            print("\nClosing WebDriver...")
            driver.quit()
            print("✓ WebDriver closed")


if __name__ == "__main__":
    print("=" * 70)
    print("Testing Sembako Scraper with Selenium")
    print("=" * 70)
    print(
        "\nThis test uses Chrome in headless mode to scrape JavaScript-rendered content."
    )
    print("=" * 70)
    test_scraper()
