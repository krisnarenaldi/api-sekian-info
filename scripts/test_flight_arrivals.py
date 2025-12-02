import json

import requests


# Test the flight arrivals endpoint
def test_flight_arrivals():
    url = "http://localhost:5500/api/flights/arrivals"

    print("Testing Flight Arrivals API...")
    print(f"URL: {url}")
    print("-" * 50)

    try:
        response = requests.get(url)

        print(f"Status Code: {response.status_code}")
        print("-" * 50)

        if response.status_code == 200:
            data = response.json()

            print(f"Status: {data.get('status')}")
            print(f"Airport: {data.get('airport')}")
            print(f"Type: {data.get('type')}")
            print(f"Time Period: {data.get('time_period')}")
            print(f"Scraped At: {data.get('scraped_at')}")
            print(f"Total Flights: {data.get('total_flights')}")
            print("-" * 50)

            # Display first 5 flights
            flights = data.get("flights", [])
            if flights:
                print("\nFirst 5 Flights:")
                print("-" * 50)
                for i, flight in enumerate(flights[:5], 1):
                    print(f"\nFlight #{i}:")
                    print(f"  Origin: {flight.get('origin')}")
                    print(f"  Arrival Time: {flight.get('arrival_time')}")
                    print(
                        f"  Flight Numbers: {', '.join(flight.get('flight_numbers', []))}"
                    )
                    print(f"  Airlines: {', '.join(flight.get('airlines', []))}")
                    print(f"  Terminal: {flight.get('terminal')}")
                    print(f"  Status: {flight.get('status')}")

            # Save full response to file
            with open("flight_arrivals_response.json", "w") as f:
                json.dump(data, f, indent=2)
            print("\n" + "-" * 50)
            print("Full response saved to: flight_arrivals_response.json")

        else:
            print(f"Error: {response.text}")

    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the server.")
        print("Please make sure the Flask app is running on port 5500")
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    test_flight_arrivals()
