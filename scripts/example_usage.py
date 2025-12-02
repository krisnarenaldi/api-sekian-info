"""
Example usage of the Sembako Price API with caching features
"""

import json
import time

import requests

# API base URL
BASE_URL = "http://localhost:5500"


def print_separator(title=""):
    """Print a nice separator"""
    print("\n" + "=" * 60)
    if title:
        print(f"  {title}")
        print("=" * 60)
    print()


def example_get_prices():
    """Example: Get sembako prices"""
    print_separator("Example 1: Get Sembako Prices")

    print("📊 Fetching sembako prices...")
    start_time = time.time()

    response = requests.get(f"{BASE_URL}/api/sembako")
    elapsed = time.time() - start_time

    if response.status_code == 200:
        data = response.json()

        # Show cache information
        if data.get("from_cache"):
            print(f"✅ Data retrieved from cache (cached at: {data.get('cache_date')})")
        else:
            print(f"🔄 Fresh data scraped (scraped at: {data.get('scraped_at')})")

        print(f"⏱️  Response time: {elapsed:.2f} seconds")
        print(f"📈 Total items: {data.get('total_items')}")

        # Print date info
        date_info = data.get("date_info", {})
        print(
            f"\n📅 Date Range: {date_info.get('yesterday')} → {date_info.get('today')}"
        )

        # Print first 5 items
        print("\n📦 Sample Prices (first 5 items):")
        print("-" * 60)
        for item in data["data"][:5]:
            change_symbol = (
                "📈" if item["change"] > 0 else "📉" if item["change"] < 0 else "➡️"
            )
            print(
                f"{item['komoditas']:.<30} Rp {item['today']:>7,} /{item['unit']:<3} {change_symbol} {item['change']:+,}"
            )

        return data
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.json())
        return None


def example_check_cache_status():
    """Example: Check cache status"""
    print_separator("Example 2: Check Cache Status")

    print("🔍 Checking cache status...")
    response = requests.get(f"{BASE_URL}/api/sembako/cache-status")

    if response.status_code == 200:
        data = response.json()

        if data.get("cache_exists"):
            print("✅ Cache file exists")
            print(f"   📅 Last modified: {data.get('last_modified')}")
            print(f"   📏 File size: {data.get('file_size'):,} bytes")
            print(
                f"   {'✅ Cache is VALID (today)' if data.get('cache_valid') else '⚠️  Cache is OUTDATED (needs refresh)'}"
            )
        else:
            print("❌ No cache file found")
            print("   💡 Make a request to /api/sembako to create cache")

        return data
    else:
        print(f"❌ Error: {response.status_code}")
        return None


def example_force_refresh():
    """Example: Force refresh the cache"""
    print_separator("Example 3: Force Refresh Cache")

    print("🔄 Forcing cache refresh (this will take 5-10 seconds)...")
    start_time = time.time()

    response = requests.post(f"{BASE_URL}/api/sembako/refresh")
    elapsed = time.time() - start_time

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Cache refreshed successfully!")
        print(f"⏱️  Time taken: {elapsed:.2f} seconds")
        print(f"📅 Scraped at: {data.get('scraped_at')}")
        print(f"📈 Total items: {data.get('total_items')}")

        return data
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.json())
        return None


def example_compare_cache_performance():
    """Example: Compare cached vs fresh scraping performance"""
    print_separator("Example 4: Performance Comparison")

    print("⚡ Testing response times...\n")

    # First request (might be cached or fresh)
    print("1️⃣  First request:")
    start1 = time.time()
    response1 = requests.get(f"{BASE_URL}/api/sembako")
    time1 = time.time() - start1
    data1 = response1.json()
    is_cached1 = data1.get("from_cache", False)
    print(
        f"   {'📦 From cache' if is_cached1 else '🔄 Fresh scrape'}: {time1:.2f} seconds"
    )

    # Second request (should be cached)
    print("\n2️⃣  Second request:")
    start2 = time.time()
    response2 = requests.get(f"{BASE_URL}/api/sembako")
    time2 = time.time() - start2
    data2 = response2.json()
    is_cached2 = data2.get("from_cache", False)
    print(
        f"   {'📦 From cache' if is_cached2 else '🔄 Fresh scrape'}: {time2:.2f} seconds"
    )

    # Show speedup if applicable
    if is_cached2 and not is_cached1:
        speedup = time1 / time2
        print(f"\n🚀 Speedup: {speedup:.1f}x faster with cache!")
    elif is_cached2 and is_cached1:
        print("\n💾 Both requests used cache - consistently fast!")


def example_monitor_price_changes():
    """Example: Monitor price changes"""
    print_separator("Example 5: Monitor Price Changes")

    print("📊 Fetching and analyzing price changes...\n")
    response = requests.get(f"{BASE_URL}/api/sembako")

    if response.status_code == 200:
        data = response.json()

        # Categorize items by price change
        increased = [item for item in data["data"] if item["change"] > 0]
        decreased = [item for item in data["data"] if item["change"] < 0]
        unchanged = [item for item in data["data"] if item["change"] == 0]

        print(f"📈 Increased: {len(increased)} items")
        if increased:
            for item in increased[:3]:  # Show top 3
                print(f"   • {item['komoditas']}: +Rp {item['change']:,}")

        print(f"\n📉 Decreased: {len(decreased)} items")
        if decreased:
            for item in decreased[:3]:  # Show top 3
                print(f"   • {item['komoditas']}: -Rp {abs(item['change']):,}")

        print(f"\n➡️  Unchanged: {len(unchanged)} items")

        return data
    else:
        print(f"❌ Error: {response.status_code}")
        return None


def example_filter_by_commodity():
    """Example: Filter specific commodities"""
    print_separator("Example 6: Filter Specific Commodities")

    print("🔍 Searching for rice and sugar prices...\n")
    response = requests.get(f"{BASE_URL}/api/sembako")

    if response.status_code == 200:
        data = response.json()

        # Filter items containing "Beras" (rice) or "Gula" (sugar)
        keywords = ["Beras", "Gula"]

        for keyword in keywords:
            filtered = [
                item
                for item in data["data"]
                if keyword.lower() in item["komoditas"].lower()
            ]

            if filtered:
                print(f"🌾 {keyword} items found: {len(filtered)}")
                for item in filtered:
                    print(
                        f"   • {item['komoditas']:.<30} Rp {item['today']:>7,}/{item['unit']}"
                    )
                print()

        return data
    else:
        print(f"❌ Error: {response.status_code}")
        return None


def main():
    """Run all examples"""
    print("\n" + "🛒" * 30)
    print("   Sembako Price API - Usage Examples")
    print("🛒" * 30)

    try:
        # Example 1: Get prices
        example_get_prices()

        # Example 2: Check cache status
        example_check_cache_status()

        # Example 3: Force refresh (commented out by default to save time)
        # Uncomment the line below to test force refresh
        # example_force_refresh()

        # Example 4: Performance comparison
        example_compare_cache_performance()

        # Example 5: Monitor price changes
        example_monitor_price_changes()

        # Example 6: Filter by commodity
        example_filter_by_commodity()

        print_separator("✅ All Examples Completed!")

        print("💡 Tips:")
        print("   • Cache is automatically refreshed daily")
        print("   • Use /api/sembako for regular requests")
        print("   • Use /api/sembako/refresh (POST) to force update")
        print("   • Check cache status with /api/sembako/cache-status")
        print()

    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the API")
        print("💡 Make sure the server is running:")
        print("   python app.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
