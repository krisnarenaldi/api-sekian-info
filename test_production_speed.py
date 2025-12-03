#!/usr/bin/env python3
"""
Test script to diagnose production API performance
"""
import requests
import time

PRODUCTION_URL = "https://api-sekian-info.onrender.com"

def test_endpoint_detailed(endpoint_name, url):
    """Test an endpoint with detailed timing breakdown"""
    print(f"\n{'='*70}")
    print(f"Testing: {endpoint_name}")
    print(f"URL: {url}")
    print(f"{'='*70}")
    
    # Measure DNS + Connection + TLS
    start_time = time.time()
    
    try:
        # Make request with detailed timing
        response = requests.get(url, timeout=30)
        total_time = (time.time() - start_time) * 1000
        
        print(f"\n📊 TIMING BREAKDOWN:")
        print(f"   Total Time: {total_time:.2f}ms")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check response metadata
            from_cache = data.get("from_cache", False)
            cache_valid = data.get("cache_valid", "N/A")
            refreshing = data.get("refreshing_in_background", False)
            
            print(f"\n📦 RESPONSE DATA:")
            print(f"   Status Code: {response.status_code}")
            print(f"   From Cache: {from_cache}")
            print(f"   Cache Valid: {cache_valid}")
            print(f"   Refreshing: {refreshing}")
            print(f"   Content Length: {len(response.content)} bytes")
            
            # Show data count
            if "items" in data:
                print(f"   Items Count: {len(data['items'])}")
            elif "trending_searches" in data:
                print(f"   Trending Searches: {len(data['trending_searches'])}")
            
            # Performance analysis
            print(f"\n🔍 PERFORMANCE ANALYSIS:")
            if total_time < 100:
                print(f"   ✅ EXCELLENT! ({total_time:.2f}ms)")
            elif total_time < 500:
                print(f"   ✅ GOOD ({total_time:.2f}ms)")
            elif total_time < 1000:
                print(f"   ⚠️  ACCEPTABLE ({total_time:.2f}ms)")
            elif total_time < 3000:
                print(f"   ⚠️  SLOW ({total_time:.2f}ms)")
            else:
                print(f"   ❌ VERY SLOW ({total_time:.2f}ms)")
                print(f"   Possible causes:")
                print(f"   - Server cold start (Render free tier)")
                print(f"   - Network latency")
                print(f"   - Server overload")
            
            return True, total_time
        else:
            print(f"   ❌ Error: Status {response.status_code}")
            return False, total_time
            
    except requests.exceptions.Timeout:
        total_time = (time.time() - start_time) * 1000
        print(f"   ❌ TIMEOUT after {total_time:.2f}ms")
        return False, total_time
    except Exception as e:
        total_time = (time.time() - start_time) * 1000
        print(f"   ❌ ERROR after {total_time:.2f}ms: {str(e)}")
        return False, total_time


def test_multiple_requests(url, count=3):
    """Test multiple requests to see if subsequent requests are faster"""
    print(f"\n{'='*70}")
    print(f"MULTIPLE REQUEST TEST (Cold Start Detection)")
    print(f"{'='*70}")
    print(f"\nMaking {count} consecutive requests to detect cold start...")
    
    times = []
    for i in range(count):
        print(f"\n🔄 Request {i+1}/{count}:")
        start = time.time()
        try:
            response = requests.get(url, timeout=30)
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)
            
            status = "✅" if response.status_code == 200 else "❌"
            print(f"   {status} Time: {elapsed:.2f}ms")
            
            if i < count - 1:
                time.sleep(1)  # Small delay between requests
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            times.append(None)
    
    # Analysis
    print(f"\n📊 ANALYSIS:")
    valid_times = [t for t in times if t is not None]
    
    if len(valid_times) >= 2:
        first_time = valid_times[0]
        avg_subsequent = sum(valid_times[1:]) / len(valid_times[1:])
        
        print(f"   First Request: {first_time:.2f}ms")
        print(f"   Avg Subsequent: {avg_subsequent:.2f}ms")
        print(f"   Difference: {first_time - avg_subsequent:.2f}ms")
        
        if first_time > avg_subsequent * 2:
            print(f"\n   ⚠️  COLD START DETECTED!")
            print(f"   First request was {first_time/avg_subsequent:.1f}x slower")
            print(f"   This is normal for Render free tier (15min timeout)")
        else:
            print(f"\n   ✅ No significant cold start delay")


def main():
    print("\n" + "="*70)
    print("PRODUCTION API PERFORMANCE DIAGNOSTIC")
    print("="*70)
    print("\nThis script will:")
    print("1. Test each endpoint with detailed timing")
    print("2. Make multiple requests to detect cold start")
    print("3. Provide performance recommendations")
    
    # Test endpoints
    endpoints = [
        ("Cinema API", f"{PRODUCTION_URL}/api/cinema"),
        ("Events API", f"{PRODUCTION_URL}/api/events"),
        ("Google Trends API", f"{PRODUCTION_URL}/api/google_trend"),
    ]
    
    results = []
    for name, url in endpoints:
        success, time_ms = test_endpoint_detailed(name, url)
        results.append((name, success, time_ms))
        time.sleep(1)
    
    # Test cold start with cinema endpoint
    test_multiple_requests(f"{PRODUCTION_URL}/api/cinema", count=3)
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    for name, success, time_ms in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}: {time_ms:.2f}ms")
    
    # Recommendations
    print("\n" + "="*70)
    print("RECOMMENDATIONS")
    print("="*70)
    
    avg_time = sum(t for _, s, t in results if s) / len([r for r in results if r[1]])
    
    if avg_time > 3000:
        print("\n⚠️  SLOW PERFORMANCE DETECTED")
        print("\nPossible solutions:")
        print("1. Upgrade to Render paid tier (no cold starts)")
        print("2. Use a keep-alive service (ping every 10 mins)")
        print("3. Add a CDN in front (Cloudflare, etc.)")
        print("4. Consider serverless functions for better cold start")
    elif avg_time > 1000:
        print("\n⚠️  MODERATE PERFORMANCE")
        print("\nThis is likely due to:")
        print("- Network latency to Render servers")
        print("- Server location distance")
        print("- Consider using a CDN for better global performance")
    else:
        print("\n✅ GOOD PERFORMANCE!")
        print("Your API is responding quickly.")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()

