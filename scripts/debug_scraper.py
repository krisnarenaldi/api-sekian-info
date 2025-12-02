"""
Debug script to investigate why scraping returns empty data
"""

import os
import stat
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
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

    driver_path = ChromeDriverManager().install()
    driver_dir = os.path.dirname(driver_path)
    actual_driver = os.path.join(driver_dir, "chromedriver")

    if os.path.isfile(actual_driver):
        driver_path = actual_driver
        if not os.access(driver_path, os.X_OK):
            os.chmod(driver_path, os.stat(driver_path).st_mode | stat.S_IEXEC)

    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def debug_scrape():
    """Debug version of scraping with detailed output"""
    driver = None
    try:
        url = "https://sp2kp.kemendag.go.id/"
        print(f"🌐 Navigating to: {url}")

        # Initialize driver
        driver = get_driver()
        driver.get(url)
        print("✅ Driver initialized and page loaded")

        # Wait for the table to load
        print("\n⏳ Waiting for table element...")
        wait = WebDriverWait(driver, 15)

        try:
            wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "v-table__wrapper"))
            )
            print("✅ Table wrapper found!")
        except Exception as e:
            print(f"❌ Table wrapper NOT found: {e}")
            print("\n🔍 Checking what's on the page...")

            # Save page source for inspection
            with open("debug_page_source.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("💾 Page source saved to: debug_page_source.html")

            # Check for common elements
            soup = BeautifulSoup(driver.page_source, "lxml")
            print(f"\n📊 Page analysis:")
            print(f"   - Total divs: {len(soup.find_all('div'))}")
            print(f"   - Total tables: {len(soup.find_all('table'))}")
            print(
                f"   - v-table__wrapper: {len(soup.find_all('div', class_='v-table__wrapper'))}"
            )
            print(
                f"   - v-data-table: {len(soup.find_all('div', class_='v-data-table'))}"
            )

            # Print first few class names to see what's there
            print(f"\n🏷️  Sample class names found:")
            for div in soup.find_all("div", class_=True)[:10]:
                print(f"   - {div.get('class')}")

            return

        # Give extra time for data to populate
        print("⏳ Waiting 5 seconds for data to load...")
        time.sleep(5)

        # Get the page source
        page_source = driver.page_source
        print(f"✅ Page source retrieved ({len(page_source)} characters)")

        # Parse with BeautifulSoup
        soup = BeautifulSoup(page_source, "lxml")

        # Find the table
        print("\n🔍 Looking for table structure...")
        table_wrapper = soup.find("div", class_="v-table__wrapper")

        if not table_wrapper:
            print("❌ Table wrapper not found")

            # Try alternative selectors
            print("\n🔍 Trying alternative selectors...")
            alt_tables = soup.find_all("table")
            print(f"   Found {len(alt_tables)} table(s) on page")

            if alt_tables:
                print("\n📊 Analyzing first table...")
                table = alt_tables[0]
                tbody = table.find("tbody")
                if tbody:
                    rows = tbody.find_all("tr")
                    print(f"   - Found {len(rows)} rows in tbody")
                    if rows:
                        print(f"\n   Sample row HTML:")
                        print(f"   {rows[0]}")
                else:
                    print("   - No tbody found")

            return

        print("✅ Table wrapper found!")
        table = table_wrapper.find("table")

        if not table:
            print("❌ Table element not found inside wrapper")
            return

        print("✅ Table element found!")

        # Check thead
        thead = table.find("thead")
        if thead:
            headers_row = thead.find("tr")
            th_elements = headers_row.find_all("th")
            print(f"\n📋 Headers ({len(th_elements)} columns):")
            for i, th in enumerate(th_elements):
                print(f"   [{i}] {th.get_text(strip=True)}")
        else:
            print("⚠️  No thead found")

        # Check tbody
        tbody = table.find("tbody")
        if not tbody:
            print("❌ Table body not found")
            return

        print("✅ Table body found!")

        # Extract data rows
        rows = tbody.find_all("tr")
        print(f"\n📊 Found {len(rows)} rows in tbody")

        if len(rows) == 0:
            print("⚠️  No data rows found!")
            print("\nTbody HTML:")
            print(tbody)
            return

        # Parse first few rows
        print("\n📦 Sample data (first 3 rows):")
        for i, row in enumerate(rows[:3]):
            cells = row.find_all("td")
            print(f"\n   Row {i + 1}: {len(cells)} cells")
            if len(cells) >= 5:
                print(f"      Komoditas: {cells[0].get_text(strip=True)}")
                print(f"      Unit: {cells[1].get_text(strip=True)}")
                print(f"      Yesterday: {cells[2].get_text(strip=True)}")
                print(f"      Today: {cells[3].get_text(strip=True)}")
                print(f"      Change: {cells[4].get_text(strip=True)}")
            else:
                print(f"      ⚠️  Row has only {len(cells)} cells (expected 5+)")
                for j, cell in enumerate(cells):
                    print(f"      [{j}] {cell.get_text(strip=True)}")

        # Count total valid rows
        valid_rows = 0
        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 5:
                valid_rows += 1

        print(f"\n✅ Total valid rows: {valid_rows}/{len(rows)}")

        if valid_rows == 0:
            print("\n❌ PROBLEM: No rows with 5+ cells found!")
            print("   This explains why data array is empty.")
        else:
            print(f"\n✅ SUCCESS: Found {valid_rows} items with complete data")

    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
        import traceback

        traceback.print_exc()

    finally:
        if driver:
            print("\n🔄 Closing driver...")
            driver.quit()
            print("✅ Driver closed")


if __name__ == "__main__":
    print("=" * 70)
    print("  DEBUG SCRAPER - Investigating Empty Data Issue")
    print("=" * 70)
    print()

    debug_scrape()

    print("\n" + "=" * 70)
    print("  Debug Complete")
    print("=" * 70)
