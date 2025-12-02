# Commands Reference 📝

Quick reference for all available commands in this project.

## 🚀 Setup Commands

### First Time Setup
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment (macOS/Linux)
source .venv/bin/activate

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Upgrade pip (optional)
pip install --upgrade pip
```

## 🏃 Running the Server

### Start Server
```bash
# Option 1: Using startup script (macOS/Linux)
./start.sh

# Option 2: Direct Python command
python app.py

# Option 3: With custom port
python app.py --port 5001

# Option 4: With activated venv
source .venv/bin/activate && python app.py
```

### Stop Server
```
Press Ctrl + C in the terminal
```

## 🧪 Testing Commands

### Test Scraper Functionality
```bash
# Test the scraper without starting the server
python test_scraper.py

# Verbose output
python test_scraper.py -v
```

### Test API Endpoints
```bash
# Test all endpoints (server must be running)
python test_api.py
```

### Run Usage Examples
```bash
# See 8 different usage examples
python example_usage.py
```

### Quick Manual Tests
```bash
# Test home endpoint
curl http://localhost:5000/

# Test sembako endpoint
curl http://localhost:5000/api/sembako

# Test health endpoint
curl http://localhost:5000/health

# Pretty print JSON (with jq)
curl http://localhost:5000/api/sembako | jq

# Save response to file
curl http://localhost:5000/api/sembako > sembako_data.json
```

## 🔧 Maintenance Commands

### Update Dependencies
```bash
# Update all packages
pip install --upgrade -r requirements.txt

# Update specific package
pip install --upgrade selenium

# Show installed packages
pip list

# Show outdated packages
pip list --outdated
```

### Clean Up
```bash
# Remove cached ChromeDriver
rm -rf ~/.wdm

# Remove virtual environment
rm -rf .venv

# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Remove exported JSON files
rm -f sembako_prices_*.json
```

### Fix ChromeDriver Issues
```bash
# Make ChromeDriver executable
chmod +x ~/.wdm/drivers/chromedriver/*/chromedriver-mac-arm64/chromedriver

# Remove and re-download ChromeDriver
rm -rf ~/.wdm
python test_scraper.py
```

## 📊 Data Export Commands

### Export to JSON
```bash
# Export directly from API
curl http://localhost:5000/api/sembako > prices.json

# With timestamp
curl http://localhost:5000/api/sembako > "prices_$(date +%Y%m%d_%H%M%S).json"

# Pretty format
curl http://localhost:5000/api/sembako | python -m json.tool > prices_formatted.json
```

### Export with Python
```python
# In Python script or interactive shell
import requests
import json

response = requests.get('http://localhost:5000/api/sembako')
with open('prices.json', 'w') as f:
    json.dump(response.json(), f, indent=2)
```

## 🐍 Python Interactive Commands

### Start Python Shell with API
```bash
# Activate venv first
source .venv/bin/activate

# Start Python
python

# Then in Python:
>>> import requests
>>> r = requests.get('http://localhost:5000/api/sembako')
>>> data = r.json()
>>> print(data['total_items'])
>>> for item in data['data']:
...     print(f"{item['komoditas']}: Rp {item['today']:,}")
```

## 🔍 Debugging Commands

### Check if Server is Running
```bash
# Check port 5000
lsof -i :5000

# Or
netstat -an | grep 5000

# Or
curl -I http://localhost:5000/health
```

### View Logs
```bash
# Run server with verbose logging
FLASK_DEBUG=1 python app.py

# Or add logging in Python
python -c "
from app import app
app.logger.setLevel('DEBUG')
app.run()
"
```

### Check ChromeDriver
```bash
# Check if Chrome is installed (macOS)
open -a "Google Chrome" --background

# Check ChromeDriver location
ls -la ~/.wdm/drivers/chromedriver/

# Test ChromeDriver
~/.wdm/drivers/chromedriver/mac64/*/chromedriver-mac-arm64/chromedriver --version
```

### Debug Selenium
```bash
# Run scraper with visible browser (edit test_scraper.py)
# Comment out: chrome_options.add_argument("--headless")
python test_scraper.py
```

## 📦 Docker Commands (Future)

### Build Image
```bash
# docker build -t sembako-api .
```

### Run Container
```bash
# docker run -p 5000:5000 sembako-api
```

## 🌐 Network Commands

### Test API from Remote Machine
```bash
# Find your local IP
ifconfig | grep "inet " | grep -v 127.0.0.1

# Test from another machine
curl http://YOUR_IP:5000/api/sembako
```

### Make Server Accessible on Network
```python
# In app.py, change:
app.run(debug=True, host="0.0.0.0", port=5000)
# Now accessible via local network
```

## 📈 Performance Testing

### Time API Request
```bash
# Using time command
time curl http://localhost:5000/api/sembako

# Using httpie (if installed)
http --print=h http://localhost:5000/api/sembako
```

### Multiple Requests
```bash
# Run 10 requests
for i in {1..10}; do
  echo "Request $i"
  time curl -s http://localhost:5000/api/sembako > /dev/null
done
```

## 🔄 Git Commands

### Initialize Git
```bash
# Initialize repository
git init

# Add all files
git add .

# First commit
git commit -m "Initial commit: Sembako Price API"

# Add remote (if needed)
git remote add origin YOUR_REPO_URL
git push -u origin main
```

### Regular Git Workflow
```bash
# Check status
git status

# Add changes
git add .

# Commit
git commit -m "Your commit message"

# Push
git push
```

## 📋 One-Liners

### Complete Setup
```bash
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && python app.py
```

### Test Everything
```bash
source .venv/bin/activate && python test_scraper.py && python test_api.py
```

### Clean and Restart
```bash
rm -rf __pycache__ .pytest_cache && python app.py
```

### Export All Data
```bash
curl http://localhost:5000/api/sembako | python -m json.tool > "backup_$(date +%Y%m%d).json"
```

## 🆘 Emergency Commands

### Kill Process on Port 5000
```bash
# Find process
lsof -ti:5000

# Kill it
kill -9 $(lsof -ti:5000)

# Or one-liner
lsof -ti:5000 | xargs kill -9
```

### Reset Everything
```bash
# Stop server (Ctrl+C)
# Remove everything
rm -rf .venv __pycache__ ~/.wdm *.json page_source.html
# Reinstall
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Restart
python app.py
```

## 📱 Mobile Testing

### Use ngrok for Public URL
```bash
# Install ngrok: https://ngrok.com/
ngrok http 5000

# Use the provided URL to test from mobile device
```

---

## 💡 Tips

- Always activate virtual environment before running commands
- Use `Ctrl+C` to stop the server gracefully
- Check server status with `/health` endpoint
- Use `jq` for pretty JSON output: `curl ... | jq`
- Add `-v` flag to curl for verbose output
- Use `python -m json.tool` to validate JSON

## 🔗 Quick Links

- **Start Server**: `./start.sh` or `python app.py`
- **Test Scraper**: `python test_scraper.py`
- **API URL**: http://localhost:5000/api/sembako
- **Documentation**: See README.md
- **Quick Start**: See QUICKSTART.md

---

**Last Updated**: November 2024
**For help**: Check README.md or run `python app.py --help`
