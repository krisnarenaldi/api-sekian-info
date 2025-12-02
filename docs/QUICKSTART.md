# Quick Start Guide 🚀

Get the Sembako Price API running in 5 minutes!

## 1. Setup (First Time Only)

```bash
# Navigate to project directory
cd api-stasiun-info

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On macOS/Linux
# OR
.venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

## 2. Start the Server

### Option A: Using the startup script (macOS/Linux)
```bash
./start.sh
```

### Option B: Manual start
```bash
source .venv/bin/activate  # Activate venv first
python app.py
```

## 3. Test the API

Open your browser and visit:
- **Home**: http://localhost:5000/
- **Sembako Prices**: http://localhost:5000/api/sembako
- **Health Check**: http://localhost:5000/health

Or use curl:
```bash
curl http://localhost:5000/api/sembako
```

## Expected Response

```json
{
  "status": "success",
  "date_info": {
    "yesterday": "25 Nov",
    "today": "26 Nov"
  },
  "data": [
    {
      "komoditas": "Beras Medium",
      "unit": "kg",
      "yesterday": 14500,
      "today": 14500,
      "change": 0
    },
    ...
  ],
  "total_items": 16
}
```

## Common Issues

### Issue: Port 5000 already in use
**Solution**: Change the port in `app.py` (line 201):
```python
app.run(debug=True, host="0.0.0.0", port=5001)
```

### Issue: ChromeDriver permission denied
**Solution**: Make it executable:
```bash
chmod +x ~/.wdm/drivers/chromedriver/*/chromedriver-mac-arm64/chromedriver
```

### Issue: Chrome not found
**Solution**: Install Google Chrome from https://www.google.com/chrome/

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Test the scraper: `python test_scraper.py`
- Test the API: `python test_api.py`
- Check [API endpoints documentation](README.md#api-endpoints)

## Stop the Server

Press `Ctrl + C` in the terminal where the server is running.

---

Need help? Check the [README.md](README.md) or run the test scripts!