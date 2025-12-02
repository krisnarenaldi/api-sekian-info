"""
Test script for caching functionality
"""

import json
import os
import time
from datetime import datetime, timedelta

import requests

BASE_URL = "http://localhost:5500"


def test_cache_status():
    """Test cache status endpoint"""
    print("\n=== Testing Cache Status ===")
    response = requests.get(f"{BASE_URL}/api/sembako/cache-status")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()


def test_get_sembako():
    """Test getting sembako data"""
    print("\n=== Testing Get Sembako Data ===")
    print("Fetching data...")
    start_time = time.time()
    response = requests.get(f"{BASE_URL}/api/sembako")
    elapsed_time = time.time() - start_time

    print(f"Status Code: {response.status_code}")
    print(f"Time taken: {elapsed_time:.2f} seconds")

    if response.status_code == 200:
        data = response.json()
        print(f"From cache: {data.get('from_cache', 'N/A')}")
        print(f"Total items: {data.get('total_items', 0)}")
        if data.get("from_cache"):
            print(f"Cache date: {data.get('cache_date', 'N/A')}")
        else:
            print(f"Scraped at: {data.get('scraped_at', 'N/A')}")

        # Print first 3 items as sample
        if data.get("data"):
            print("\nSample data (first 3 items):")
            for item in data["data"][:3]:
                print(f"  - {item['komoditas']}: Rp {item['today']:,} ({item['unit']})")
    else:
        print(f"Error: {response.json()}")

    return response.json()


def test_refresh_cache():
    """Test force refresh cache endpoint"""
    print("\n=== Testing Force Refresh Cache ===")
    print("Forcing cache refresh...")
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/api/sembako/refresh")
    elapsed_time = time.time() - start_time

    print(f"Status Code: {response.status_code}")
    print(f"Time taken: {elapsed_time:.2f} seconds")

    if response.status_code == 200:
        data = response.json()
        print(f"Force refreshed: {data.get('force_refreshed', 'N/A')}")
        print(f"Total items: {data.get('total_items', 0)}")
        print(f"Scraped at: {data.get('scraped_at', 'N/A')}")
    else:
        print(f"Error: {response.json()}")

    return response.json()


def check_local_cache_file():
    """Check if cache file exists locally"""
    print("\n=== Checking Local Cache File ===")
    cache_file = "sembako_cache.json"

    if os.path.exists(cache_file):
        print(f"✓ Cache file exists: {cache_file}")
        mod_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        print(f"Last modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"File size: {os.path.getsize(cache_file):,} bytes")

        # Check if modified today
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        is_today = mod_time >= today
        print(f"Modified today: {is_today}")
    else:
        print(f"✗ Cache file does not exist: {cache_file}")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Sembako API Caching Test Suite")
    print("=" * 60)

    try:
        # Test 1: Check cache status before any requests
        test_cache_status()

        # Test 2: Get sembako data (first request - should scrape)
        print("\n" + "=" * 60)
        print("FIRST REQUEST (Expected: scrape new data)")
        print("=" * 60)
        test_get_sembako()

        # Test 3: Check cache status after first request
        test_cache_status()

        # Test 4: Get sembako data again (should use cache)
        print("\n" + "=" * 60)
        print("SECOND REQUEST (Expected: use cache)")
        print("=" * 60)
        test_get_sembako()

        # Test 5: Force refresh cache
        print("\n" + "=" * 60)
        print("FORCE REFRESH")
        print("=" * 60)
        test_refresh_cache()

        # Test 6: Get data after force refresh (should still use cache)
        print("\n" + "=" * 60)
        print("AFTER FORCE REFRESH (Expected: use cache)")
        print("=" * 60)
        test_get_sembako()

        # Test 7: Check local cache file
        check_local_cache_file()

        print("\n" + "=" * 60)
        print("✓ All tests completed successfully!")
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to the API server.")
        print("Make sure the server is running on http://localhost:5500")
    except Exception as e:
        print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    main()
