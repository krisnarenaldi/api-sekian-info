
import sys
import os

# Add current directory to path so we can import app
sys.path.append(os.getcwd())

from app import get_driver

def test_driver():
    print("Attempting to initialize driver...")
    try:
        driver = get_driver()
        print("Driver initialized successfully!")
        driver.get("https://www.google.com")
        print("Page load successful!")
        print(f"Title: {driver.title}")
        driver.quit()
        print("Driver quit successfully.")
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_driver()
