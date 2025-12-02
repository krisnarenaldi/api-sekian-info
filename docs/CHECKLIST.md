# Installation & Setup Checklist ✅

Use this checklist to verify your Sembako Price API installation is complete and working correctly.

## 📋 Pre-Installation Checklist

- [ ] Python 3.8 or higher installed
  ```bash
  python3 --version
  ```

- [ ] pip package manager available
  ```bash
  pip --version
  ```

- [ ] Google Chrome browser installed
  ```bash
  # macOS
  open -a "Google Chrome" --version
  # Or check if installed
  ls "/Applications/Google Chrome.app"
  ```

- [ ] Internet connection available

## 🔧 Installation Checklist

- [ ] Navigate to project directory
  ```bash
  cd api-stasiun-info
  ```

- [ ] Create virtual environment
  ```bash
  python3 -m venv .venv
  ```
  ✅ Expected: `.venv` directory created

- [ ] Activate virtual environment
  ```bash
  # macOS/Linux
  source .venv/bin/activate
  
  # Windows
  .venv\Scripts\activate
  ```
  ✅ Expected: `(.venv)` appears in terminal prompt

- [ ] Install dependencies
  ```bash
  pip install -r requirements.txt
  ```
  ✅ Expected: All packages installed successfully

- [ ] Verify installations
  ```bash
  pip list
  ```
  ✅ Expected: See flask, selenium, beautifulsoup4, etc.

## 🧪 Testing Checklist

### Test 1: Scraper Functionality
- [ ] Run scraper test
  ```bash
  python test_scraper.py
  ```
  ✅ Expected output:
  - "✓ WebDriver initialized"
  - "✓ Page loaded"
  - "✓ Table element detected"
  - "✓ Successfully scraped X items"
  - Sample data displayed

### Test 2: ChromeDriver
- [ ] ChromeDriver downloaded automatically
  ✅ Expected: Downloaded to `~/.wdm/drivers/chromedriver/`

- [ ] ChromeDriver is executable
  ```bash
  ls -la ~/.wdm/drivers/chromedriver/mac64/*/chromedriver-mac-arm64/chromedriver
  ```
  ✅ Expected: File has execute permissions (-rwxr-xr-x)

- [ ] If not executable, fix it:
  ```bash
  chmod +x ~/.wdm/drivers/chromedriver/mac64/*/chromedriver-mac-arm64/chromedriver
  ```

### Test 3: Flask Server
- [ ] Start the server
  ```bash
  python app.py
  # OR
  ./start.sh
  ```
  ✅ Expected output:
  ```
  * Running on http://0.0.0.0:5000
  * Serving Flask app 'app'
  * Debug mode: on
  ```

- [ ] Server is running on port 5000
  ```bash
  # In another terminal
  lsof -i :5000
  ```
  ✅ Expected: Process shown on port 5000

### Test 4: API Endpoints

**Keep server running for these tests**

- [ ] Test home endpoint
  ```bash
  curl http://localhost:5000/
  ```
  ✅ Expected: JSON with API information

- [ ] Test health endpoint
  ```bash
  curl http://localhost:5000/health
  ```
  ✅ Expected: `{"status": "healthy", "service": "Sembako Price API"}`

- [ ] Test sembako endpoint
  ```bash
  curl http://localhost:5000/api/sembako
  ```
  ✅ Expected: JSON with sembako prices data
  - Contains "status": "success"
  - Contains "data" array with items
  - Contains "total_items" count

- [ ] Test in browser
  - [ ] Open http://localhost:5000/
  - [ ] Open http://localhost:5000/health
  - [ ] Open http://localhost:5000/api/sembako
  
  ✅ Expected: JSON data displayed in browser

### Test 5: API Test Script
- [ ] Run API tests (server must be running)
  ```bash
  # In another terminal
  source .venv/bin/activate
  python test_api.py
  ```
  ✅ Expected: All tests pass

### Test 6: Example Usage
- [ ] Run example script (server must be running)
  ```bash
  python example_usage.py
  ```
  ✅ Expected: 8 examples run successfully

## 📊 Data Validation Checklist

- [ ] Response has correct structure
  - [ ] Contains `status` field
  - [ ] Contains `date_info` with yesterday/today
  - [ ] Contains `data` array
  - [ ] Contains `total_items` count

- [ ] Data items have correct fields
  - [ ] `komoditas` (string)
  - [ ] `unit` (string)
  - [ ] `yesterday` (integer)
  - [ ] `today` (integer)
  - [ ] `change` (integer)

- [ ] Prices are clean integers
  - [ ] No "Rp" prefix
  - [ ] No dots or commas
  - [ ] Example: 14500 not "Rp 14.500"

- [ ] At least 10 items returned
  ```bash
  curl -s http://localhost:5000/api/sembako | grep -o "komoditas" | wc -l
  ```
  ✅ Expected: Number >= 10

## 🎯 Performance Checklist

- [ ] API responds within 15 seconds
  ```bash
  time curl http://localhost:5000/api/sembako
  ```
  ✅ Expected: real time < 15s

- [ ] No memory leaks (browser closes properly)

- [ ] Server handles errors gracefully

## 📁 File Structure Checklist

- [ ] All files present
  - [ ] `app.py` - Main application
  - [ ] `test_scraper.py` - Scraper test
  - [ ] `test_api.py` - API test
  - [ ] `example_usage.py` - Usage examples
  - [ ] `requirements.txt` - Dependencies
  - [ ] `start.sh` - Startup script
  - [ ] `README.md` - Documentation
  - [ ] `QUICKSTART.md` - Quick guide
  - [ ] `COMMANDS.md` - Command reference
  - [ ] `PROJECT_SUMMARY.md` - Project overview
  - [ ] `CHECKLIST.md` - This file
  - [ ] `.gitignore` - Git ignore rules

## 🔒 Security Checklist

- [ ] Virtual environment is activated (not using system Python)

- [ ] `.gitignore` includes:
  - [ ] `.venv/`
  - [ ] `__pycache__/`
  - [ ] `*.pyc`

- [ ] No hardcoded credentials in code

## 📝 Documentation Checklist

- [ ] README.md is readable and complete

- [ ] QUICKSTART.md provides quick setup

- [ ] All example scripts have comments

- [ ] API endpoints are documented

## 🚀 Production Readiness (Optional)

- [ ] Consider adding caching (Redis)

- [ ] Consider adding rate limiting

- [ ] Consider adding authentication

- [ ] Consider containerization (Docker)

- [ ] Consider monitoring/logging

- [ ] Consider database for historical data

## ✅ Final Verification

Complete these final checks:

1. **Clean Test** - Fresh installation works
   ```bash
   # Stop server (Ctrl+C)
   deactivate
   rm -rf .venv
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   python test_scraper.py
   ```
   ✅ Expected: Everything works

2. **Full Workflow Test**
   - [ ] Start server
   - [ ] Make API request
   - [ ] Get valid data
   - [ ] Stop server (Ctrl+C)
   - [ ] No errors or warnings

3. **Documentation Test**
   - [ ] README instructions are clear
   - [ ] QUICKSTART works as described
   - [ ] Commands in COMMANDS.md work

## 🎉 Success Criteria

Your installation is complete and successful if:

✅ All items in this checklist are checked
✅ Server starts without errors
✅ `/api/sembako` returns valid data
✅ Data structure matches documentation
✅ Test scripts pass
✅ No ChromeDriver errors

## 🆘 Troubleshooting

If any checks fail:

1. **ChromeDriver issues**: See README.md "Troubleshooting" section
2. **Port conflicts**: Change port in app.py
3. **Timeout errors**: Increase wait time in app.py
4. **Import errors**: Reinstall dependencies

## 📞 Getting Help

If you're stuck:

1. Check README.md
2. Run `python test_scraper.py` for diagnostics
3. Check error messages carefully
4. Verify Chrome is installed
5. Check Python version compatibility

---

**Installation Status**: 
- [ ] ❌ Not Started
- [ ] 🟡 In Progress
- [ ] ✅ Complete and Working

**Date Completed**: _______________

**Notes**:
_______________________________________
_______________________________________
_______________________________________

---

**Next Steps After Completion**:
1. Read PROJECT_SUMMARY.md for project overview
2. Try example_usage.py for usage patterns
3. Explore COMMANDS.md for all available commands
4. Start building your own integration!

**Happy Coding! 🚀**