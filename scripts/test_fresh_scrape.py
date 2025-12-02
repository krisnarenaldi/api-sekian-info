"""
Quick test script to test fresh scraping
Run this while the Flask server is running
"""

import json

import requests

BASE_URL = "http://localhost:5500"

print("=" * 70)
print("Testing Fresh Scrape")
print("=" * 70)

print("\n1. Testing /api/sembako endpoint...")
print("   (This may take 5-10 seconds for scraping)")

try:
    response = requests.get(f"{BASE_URL}/api/sembako", timeout=30)

    print(f"\nStatus Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\nResponse:")
        print(f"  Status: {data.get('status')}")
        print(f"  From Cache: {data.get('from_cache')}")
        print(f"  Total Items: {data.get('total_items')}")

        if data.get("from_cache"):
            print(f"  Cache Date: {data.get('cache_date')}")
        else:
            print(f"  Scraped At: {data.get('scraped_at')}")

        print(f"\nDate Info:")
        date_info = data.get("date_info", {})
        print(f"  Yesterday: {date_info.get('yesterday')}")
        print(f"  Today: {date_info.get('today')}")

        if data.get("total_items", 0) > 0:
            print(f"\nFirst 3 items:")
            for i, item in enumerate(data.get("data", [])[:3], 1):
                print(
                    f"  {i}. {item.get('komoditas')}: Rp {item.get('today'):,}/{item.get('unit')}"
                )
        else:
            print("\n⚠️  WARNING: No items returned!")
            print("   Check server console for DEBUG messages")

        # Save full response to file for inspection
        with open("last_response.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("\n📝 Full response saved to: last_response.json")

    else:
        print(f"\nError Response:")
        print(json.dumps(response.json(), indent=2))

except requests.exceptions.Timeout:
    print("\n❌ Request timed out (took more than 30 seconds)")
except requests.exceptions.ConnectionError:
    print("\n❌ Could not connect to server")
    print("   Make sure Flask server is running: python app.py")
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "=" * 70)
print("Test Complete - Check server console for DEBUG output")
print("=" * 70)
