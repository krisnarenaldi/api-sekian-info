import json
import os
from datetime import datetime

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

    import stat

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


def analyze_html_structure(url="https://www.jakarta-airport.com/cgk-arrivals?tp=12"):
    """
    Analyze and document the HTML structure of the flight arrivals page.
    This helps detect when the website structure changes.
    """
    driver = None
    try:
        print(f"Analyzing HTML structure from: {url}")
        print("=" * 80)

        driver = get_driver()
        driver.get(url)

        # Wait for page to load
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "flights-info")))

        import time

        time.sleep(3)

        # Get page source
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "lxml")

        # Analyze structure
        structure_info = {
            "analyzed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "url": url,
            "containers": {},
            "class_names": [],
            "sample_html": {},
        }

        # 1. Find main container
        flights_info = soup.find("div", class_="flights-info")
        if flights_info:
            structure_info["containers"]["flights-info"] = {
                "found": True,
                "tag": flights_info.name,
                "classes": flights_info.get("class", []),
            }
            print("✓ Found: <div class='flights-info'>")
        else:
            structure_info["containers"]["flights-info"] = {"found": False}
            print("✗ NOT FOUND: <div class='flights-info'>")

        # 2. Find flight rows
        flight_rows = soup.find_all("div", class_="flight-row")
        structure_info["containers"]["flight-row"] = {
            "found": len(flight_rows) > 0,
            "count": len(flight_rows),
            "sample_classes": flight_rows[0].get("class", []) if flight_rows else [],
        }
        print(f"✓ Found: {len(flight_rows)} flight rows")

        # 3. Analyze column classes
        if flight_rows:
            first_row = flight_rows[0]
            cols = first_row.find_all("div", class_=lambda x: x and "flight-col" in x)

            print(f"\nColumn classes found in first row: {len(cols)}")
            print("-" * 80)

            column_classes = []
            for col in cols:
                col_classes = col.get("class", [])
                column_classes.extend(col_classes)
                print(f"  - {' '.join(col_classes)}")

            structure_info["class_names"] = list(set(column_classes))

        # 4. Extract detailed structure from first few rows
        print("\n" + "=" * 80)
        print("DETAILED STRUCTURE ANALYSIS (First 3 rows):")
        print("=" * 80)

        for idx, row in enumerate(flight_rows[:3], 1):
            if "flight-titol" in row.get("class", []):
                print(f"\nRow {idx}: HEADER ROW")
                continue

            print(f"\nRow {idx}:")
            print("-" * 40)

            # Origin
            origin_col = row.find("div", class_="flight-col__dest-term")
            if origin_col:
                print(f"  Origin class: flight-col__dest-term ✓")
                print(f"    Value: {origin_col.get_text(strip=True)}")
            else:
                print(f"  Origin class: flight-col__dest-term ✗")

            # Arrival time
            arrival_col = row.find("div", class_="flight-col__hour")
            if arrival_col:
                print(f"  Arrival class: flight-col__hour ✓")
                print(f"    Value: {arrival_col.get_text(strip=True)}")
            else:
                print(f"  Arrival class: flight-col__hour ✗")

            # Flight number
            flight_col = row.find("div", class_="flight-col__flight")
            if flight_col:
                print(f"  Flight class: flight-col__flight ✓")
                flight_links = flight_col.find_all("a")
                print(f"    Links found: {len(flight_links)}")
            else:
                print(f"  Flight class: flight-col__flight ✗")

            # Airline
            airline_col = row.find("div", class_="flight-col__airline")
            if airline_col:
                print(f"  Airline class: flight-col__airline ✓")
                airline_spans = airline_col.find_all("span")
                print(f"    Spans found: {len(airline_spans)}")
            else:
                print(f"  Airline class: flight-col__airline ✗")

            # Terminal
            terminal_col = row.find("div", class_="flight-col__term")
            if terminal_col:
                print(f"  Terminal class: flight-col__term ✓")
                print(f"    Value: {terminal_col.get_text(strip=True)}")
            else:
                print(f"  Terminal class: flight-col__term ✗")

            # Status
            status_col = row.find("div", class_="flight-col__status")
            if status_col:
                print(f"  Status class: flight-col__status ✓")
                print(f"    Value: {status_col.get_text(strip=True)}")
            else:
                print(f"  Status class: flight-col__status ✗")

        # 5. Save sample HTML
        if flight_rows:
            structure_info["sample_html"]["first_row"] = str(flight_rows[0])[:1000]

        # 6. Save structure snapshot to file
        snapshot_file = "html_structure_snapshot.json"
        with open(snapshot_file, "w") as f:
            json.dump(structure_info, f, indent=2)

        print("\n" + "=" * 80)
        print(f"✓ Structure snapshot saved to: {snapshot_file}")
        print("=" * 80)

        # 7. Compare with previous snapshot if exists
        previous_snapshot = "html_structure_snapshot_previous.json"
        if os.path.exists(previous_snapshot):
            print("\n" + "=" * 80)
            print("COMPARING WITH PREVIOUS SNAPSHOT:")
            print("=" * 80)

            with open(previous_snapshot, "r") as f:
                prev_structure = json.load(f)

            # Compare class names
            prev_classes = set(prev_structure.get("class_names", []))
            current_classes = set(structure_info["class_names"])

            new_classes = current_classes - prev_classes
            removed_classes = prev_classes - current_classes

            if new_classes:
                print(f"\n⚠️  NEW CLASSES DETECTED:")
                for cls in new_classes:
                    print(f"  + {cls}")

            if removed_classes:
                print(f"\n⚠️  REMOVED CLASSES DETECTED:")
                for cls in removed_classes:
                    print(f"  - {cls}")

            if not new_classes and not removed_classes:
                print("\n✓ No changes detected in class names")

            # Compare containers
            if (
                prev_structure.get("containers", {}).get("flight-row", {}).get("count")
                != structure_info["containers"]["flight-row"]["count"]
            ):
                print(
                    f"\n⚠️  FLIGHT COUNT CHANGED: {prev_structure.get('containers', {}).get('flight-row', {}).get('count')} → {structure_info['containers']['flight-row']['count']}"
                )

        else:
            print(
                f"\nNo previous snapshot found. Run this script again later to detect changes."
            )

        # 8. Generate update guide
        print("\n" + "=" * 80)
        print("SCRAPER UPDATE GUIDE:")
        print("=" * 80)
        print("""
If the website structure changes, update these selectors in app.py:

1. Main container: 'flights-info'
2. Flight rows: 'flight-row'
3. Column classes:
   - Origin: 'flight-col__dest-term'
   - Arrival: 'flight-col__hour'
   - Flight: 'flight-col__flight'
   - Airline: 'flight-col__airline'
   - Terminal: 'flight-col__term'
   - Status: 'flight-col__status'

To update the scraper:
1. Inspect the website HTML manually
2. Find the new class names
3. Update the selectors in scrape_flight_arrivals() function
4. Run this monitor script again to verify
5. Test with test_flight_arrivals.py
        """)

        return structure_info

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()
        return None

    finally:
        if driver:
            driver.quit()


def compare_snapshots(current_file="html_structure_snapshot.json"):
    """
    Compare current snapshot with a baseline to detect changes
    """
    if not os.path.exists(current_file):
        print("No current snapshot found. Run analyze_html_structure() first.")
        return

    baseline_file = "html_structure_baseline.json"

    if not os.path.exists(baseline_file):
        # Create baseline from current
        import shutil

        shutil.copy(current_file, baseline_file)
        print(f"Created baseline snapshot: {baseline_file}")
        return

    with open(current_file, "r") as f:
        current = json.load(f)

    with open(baseline_file, "r") as f:
        baseline = json.load(f)

    print("\n" + "=" * 80)
    print("SNAPSHOT COMPARISON REPORT")
    print("=" * 80)
    print(f"Baseline: {baseline.get('analyzed_at')}")
    print(f"Current:  {current.get('analyzed_at')}")
    print("=" * 80)

    changes_detected = False

    # Compare class names
    baseline_classes = set(baseline.get("class_names", []))
    current_classes = set(current.get("class_names", []))

    new_classes = current_classes - baseline_classes
    removed_classes = baseline_classes - current_classes

    if new_classes or removed_classes:
        changes_detected = True
        print("\n⚠️  CLASS NAME CHANGES DETECTED!")
        if new_classes:
            print("\nNew classes:")
            for cls in sorted(new_classes):
                print(f"  + {cls}")
        if removed_classes:
            print("\nRemoved classes:")
            for cls in sorted(removed_classes):
                print(f"  - {cls}")
    else:
        print("\n✓ No class name changes")

    # Compare container availability
    baseline_containers = baseline.get("containers", {})
    current_containers = current.get("containers", {})

    for container_name in baseline_containers:
        baseline_found = baseline_containers[container_name].get("found")
        current_found = current_containers.get(container_name, {}).get("found")

        if baseline_found != current_found:
            changes_detected = True
            print(
                f"\n⚠️  Container '{container_name}' status changed: {baseline_found} → {current_found}"
            )

    if changes_detected:
        print("\n" + "=" * 80)
        print("⚠️  WEBSITE STRUCTURE HAS CHANGED!")
        print("ACTION REQUIRED: Update the scraper in app.py")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("✓ No significant changes detected")
        print("=" * 80)


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                   HTML STRUCTURE MONITORING TOOL                              ║
║              Jakarta Airport Flight Arrivals Scraper                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

This tool helps detect when the website HTML structure changes,
which would require updating the scraper code.

Usage:
1. Run this script regularly (e.g., weekly) to monitor for changes
2. Compare snapshots to detect structural changes
3. Update app.py if changes are detected

    """)

    # Analyze current structure
    analyze_html_structure()

    # Compare with baseline if it exists
    print("\n\n")
    compare_snapshots()

    print(
        "\n\nTIP: Save this snapshot as baseline by renaming it to 'html_structure_baseline.json'"
    )
