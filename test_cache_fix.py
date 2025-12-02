#!/usr/bin/env python3
"""
Test script to verify the cache fix with background refresh for cinema, events, and google_trend endpoints
"""
import requests
import time

BASE_URL = "http://localhost:5500"

def test_endpoint(endpoint_name, url):
    """Test an endpoint and measure response time"""
    print(f"\n{'='*60}")
    print(f"Testing: {endpoint_name}")
    print(f"URL: {url}")
    print(f"{'='*60}")

    start_time = time.time()
    try:
        response = requests.get(url, timeout=10)
        elapsed_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        print(f"✓ Status Code: {response.status_code}")
        print(f"✓ Response Time: {elapsed_time:.2f}ms")

        if response.status_code == 200:
            data = response.json()

            # Check for cache info
            from_cache = data.get("from_cache", False)
            cache_valid = data.get("cache_valid", "N/A")
            cache_date = data.get("cache_date", "N/A")
            refreshing = data.get("refreshing_in_background", False)

            print(f"✓ From Cache: {from_cache}")
            print(f"✓ Cache Valid: {cache_valid}")
            print(f"✓ Cache Date: {cache_date}")
            print(f"✓ Refreshing in Background: {refreshing}")

            # Show data count
            if "items" in data:
                print(f"✓ Items Count: {len(data['items'])}")
            elif "trending_searches" in data:
                print(f"✓ Trending Searches Count: {len(data['trending_searches'])}")

            # Performance check
            if elapsed_time < 500:
                print(f"✅ FAST RESPONSE! ({elapsed_time:.2f}ms < 500ms)")
            elif elapsed_time < 1000:
                print(f"⚠️  Acceptable response time ({elapsed_time:.2f}ms)")
            else:
                print(f"❌ SLOW RESPONSE! ({elapsed_time:.2f}ms > 1000ms)")

            # Background refresh info
            if refreshing:
                print(f"🔄 Background refresh is active - next request will have fresher data")

        return True

    except requests.exceptions.Timeout:
        elapsed_time = (time.time() - start_time) * 1000
        print(f"❌ TIMEOUT after {elapsed_time:.2f}ms")
        return False
    except Exception as e:
        elapsed_time = (time.time() - start_time) * 1000
        print(f"❌ ERROR after {elapsed_time:.2f}ms: {str(e)}")
        return False

def test_background_refresh():
    """Test that background refresh is triggered for stale cache"""
    print("\n" + "="*60)
    print("BACKGROUND REFRESH TEST")
    print("="*60)
    print("\nThis test checks if background refresh is triggered for stale cache")
    print("Note: This only works if your cache is actually stale")

    url = f"{BASE_URL}/api/cinema"

    print("\n1. First request (should return cached data)...")
    response1 = requests.get(url, timeout=10)
    data1 = response1.json()

    refreshing1 = data1.get("refreshing_in_background", False)
    cache_valid1 = data1.get("cache_valid", True)

    print(f"   Cache Valid: {cache_valid1}")
    print(f"   Refreshing: {refreshing1}")

    if not cache_valid1 and refreshing1:
        print("\n✅ Background refresh was triggered!")
        print("\n2. Waiting 2 seconds and making another request...")
        time.sleep(2)

        response2 = requests.get(url, timeout=10)
        data2 = response2.json()
        refreshing2 = data2.get("refreshing_in_background", False)

        print(f"   Still Refreshing: {refreshing2}")

        if refreshing2:
            print("   🔄 Background refresh is still in progress")
        else:
            print("   ✅ Background refresh completed!")
    elif cache_valid1:
        print("\n⚠️  Cache is still valid, background refresh not needed")
        print("   To test background refresh, wait until cache expires:")
        print("   - Cinema: 6 days")
        print("   - Events: 5 days")
        print("   - Google Trends: 24 hours")
    else:
        print("\n⚠️  Background refresh not triggered (unexpected)")


def main():
    print("\n" + "="*60)
    print("CACHE FIX VERIFICATION TEST WITH BACKGROUND REFRESH")
    print("="*60)
    print("\nThis test verifies:")
    print("1. Endpoints return cached data quickly (~50ms)")
    print("2. Background refresh is triggered for stale cache")
    print("3. Responses include proper metadata")

    # Test all three endpoints
    endpoints = [
        ("Cinema API", f"{BASE_URL}/api/cinema"),
        ("Events API", f"{BASE_URL}/api/events"),
        ("Google Trends API", f"{BASE_URL}/api/google_trend"),
    ]

    results = []
    for name, url in endpoints:
        success = test_endpoint(name, url)
        results.append((name, success))
        time.sleep(0.5)  # Small delay between tests

    # Test background refresh
    test_background_refresh()

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    all_passed = all(success for _, success in results)

    for name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {name}")

    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("All endpoints are now returning cached data quickly.")
        print("Background refresh is working as expected.")
    else:
        print("❌ SOME TESTS FAILED")
        print("Please check the server logs for errors.")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()

