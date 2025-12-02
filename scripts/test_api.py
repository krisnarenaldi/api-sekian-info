import json

import requests


def test_home():
    """Test the home endpoint"""
    print("Testing home endpoint...")
    try:
        response = requests.get("http://localhost:5000/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print("-" * 50)
    except Exception as e:
        print(f"Error: {e}")
        print("-" * 50)


def test_health():
    """Test the health check endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get("http://localhost:5000/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print("-" * 50)
    except Exception as e:
        print(f"Error: {e}")
        print("-" * 50)


def test_sembako():
    """Test the sembako price scraping endpoint"""
    print("Testing sembako endpoint...")
    try:
        response = requests.get("http://localhost:5000/api/sembako")
        print(f"Status Code: {response.status_code}")

        data = response.json()

        if data.get("status") == "success":
            print(f"Total Items: {data.get('total_items')}")
            print(f"Date Info: {data.get('date_info')}")
            print("\nSample Data (first 5 items):")
            for i, item in enumerate(data.get("data", [])[:5]):
                print(f"\n{i + 1}. {item['komoditas']}")
                print(f"   Unit: {item['unit']}")
                print(f"   Yesterday: Rp {item['yesterday']:,}")
                print(f"   Today: Rp {item['today']:,}")
                print(f"   Change: Rp {item['change']:,}")
        else:
            print(f"Error Response: {json.dumps(data, indent=2)}")

        print("-" * 50)
    except Exception as e:
        print(f"Error: {e}")
        print("-" * 50)


if __name__ == "__main__":
    print("=" * 50)
    print("Sembako API Test Suite")
    print("=" * 50)
    print("\nMake sure the Flask server is running on http://localhost:5000")
    print("Start it with: python app.py")
    print("=" * 50)
    print()

    test_home()
    test_health()
    test_sembako()

    print("\nAll tests completed!")
