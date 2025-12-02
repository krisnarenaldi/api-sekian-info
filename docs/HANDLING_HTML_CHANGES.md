# Handling HTML Structure Changes - Complete Guide

## Overview

Web scraping is inherently fragile because websites can change their HTML structure at any time. This guide explains how we handle potential HTML changes in the Flight Arrivals scraper and what to do when the website structure changes.

## 🛡️ Built-in Protection Mechanisms

### 1. **Multiple Selector Fallbacks**

The scraper tries multiple selectors before giving up:

```python
# Primary selector
flights_info = soup.find("div", class_="flights-info")

# Fallback 1: Any div with "flight" in the class name
if not flights_info:
    flights_info = soup.find("div", class_=lambda x: x and "flight" in x.lower())

# Fallback 2: Try table format (in case they switch to tables)
if not flights_info:
    flights_info = soup.find("table")
```

### 2. **Graceful Degradation**

The scraper continues to work even if some fields are missing:
- If origin is found but airline is not, it still returns the flight
- Skips problematic rows instead of crashing the entire scraper
- Returns partial data with warnings

### 3. **Data Validation**

Before adding a flight to the results, we validate:
- Origin is not empty
- Arrival time is not empty
- At least some basic flight information exists

### 4. **Detailed Error Reporting**

When things go wrong, the API provides detailed error messages:

```json
{
  "status": "error",
  "message": "Flight information container not found on the page",
  "troubleshooting": "The HTML structure has likely changed. Check class names: 'flights-info', 'flight-row', 'flight-col__*'",
  "url": "https://www.jakarta-airport.com/cgk-arrivals?tp=12",
  "last_successful_scrape": "Check logs for last working version"
}
```

### 5. **Warning System**

If the scraper encounters many parsing errors (>30% error rate), it includes a warning:

```json
{
  "status": "success",
  "warning": "High parsing error rate: 45 errors while extracting 100 flights. Website structure may have partially changed.",
  "parsing_errors_count": 45,
  "flights": [...]
}
```

## 🔍 Detecting Changes

### Method 1: Monitor API Responses

Check for these indicators that something changed:

1. **No flights returned** (`total_flights: 0`)
2. **High error rates** (warning field present)
3. **Missing data fields** (empty origins, times, etc.)
4. **Error responses** with troubleshooting info

### Method 2: Use the HTML Structure Monitor

Run the monitoring script regularly:

```bash
python monitor_html_structure.py
```

This will:
- ✅ Analyze the current HTML structure
- ✅ Save a snapshot to `html_structure_snapshot.json`
- ✅ Compare with previous snapshots
- ✅ Alert you to any changes

**Recommended frequency:** Run weekly or monthly

### Method 3: Set Up Automated Monitoring

Create a cron job or scheduled task:

```bash
# Run every Monday at 9 AM
0 9 * * 1 cd /path/to/api-stasiun-info && python monitor_html_structure.py >> monitor.log 2>&1
```

## 🔧 When Changes Are Detected

### Step 1: Confirm the Change

1. Visit the website manually: https://www.jakarta-airport.com/cgk-arrivals
2. Right-click on a flight row → "Inspect Element"
3. Check the HTML structure:
   - Container div class name
   - Row class name
   - Column class names

### Step 2: Run the Monitor Script

```bash
python monitor_html_structure.py
```

This will show you exactly what changed:
- New class names added
- Old class names removed
- Container structure changes

### Step 3: Update the Scraper

Open `app.py` and locate the `scrape_flight_arrivals()` function.

#### Update Main Container Selector (if needed)

```python
# Old
flights_info = soup.find("div", class_="flights-info")

# If changed to "flight-container", update to:
flights_info = soup.find("div", class_="flight-container")
```

#### Update Row Selector (if needed)

```python
# Old
flight_rows = flights_info.find_all("div", class_="flight-row")

# If changed to "arrival-row", update to:
flight_rows = flights_info.find_all("div", class_="arrival-row")
```

#### Update Column Selectors (if needed)

Find and update these selectors in the function:

```python
# Origin
origin_col = row.find("div", class_="flight-col__dest-term")  # Update class name here

# Arrival time
arrival_col = row.find("div", class_="flight-col__hour")  # Update class name here

# Flight number
flight_col = row.find("div", class_="flight-col__flight")  # Update class name here

# Airline
airline_col = row.find("div", class_="flight-col__airline")  # Update class name here

# Terminal
terminal_col = row.find("div", class_="flight-col__term")  # Update class name here

# Status
status_col = row.find("div", class_="flight-col__status")  # Update class name here
```

### Step 4: Test the Changes

```bash
# Run the test script
python test_flight_arrivals.py
```

Expected output:
- ✅ Status Code: 200
- ✅ Total Flights: > 0
- ✅ First 5 flights displayed correctly
- ✅ All required fields present

### Step 5: Update the Monitor Baseline

After confirming everything works:

```bash
# Save current snapshot as new baseline
cp html_structure_snapshot.json html_structure_baseline.json
```

## 📋 Common Change Scenarios

### Scenario 1: Class Names Changed

**Symptoms:**
```json
{
  "status": "error",
  "message": "Flight information container not found on the page"
}
```

**Fix:**
1. Run `python monitor_html_structure.py`
2. Check the new class names in the output
3. Update selectors in `app.py`
4. Test with `python test_flight_arrivals.py`

### Scenario 2: HTML Structure Changed (divs → table)

**Symptoms:**
```json
{
  "status": "error",
  "message": "No flight rows found"
}
```

**Fix:**
The scraper already has fallback to table format, but you may need to:
1. Update the row extraction logic
2. Change from `find_all("div")` to `find_all("tr")`
3. Update column extraction to use `<td>` instead of `<div>`

### Scenario 3: Field Renamed or Moved

**Symptoms:**
```json
{
  "status": "success",
  "warning": "High parsing error rate...",
  "flights": [
    {
      "origin": "Singapore (SIN)",
      "arrival_time": "",  // Empty!
      "flight_numbers": [],
      ...
    }
  ]
}
```

**Fix:**
1. Inspect the website to find where the field moved
2. Update the specific selector for that field
3. Test again

### Scenario 4: Dynamic Content Loading Changed

**Symptoms:**
- Scraper returns 0 flights
- No error messages
- Page loads but data doesn't appear

**Fix:**
1. Increase wait time in `app.py`:
   ```python
   wait = WebDriverWait(driver, 30)  # Increase from 15 to 30
   time.sleep(5)  # Increase from 3 to 5
   ```
2. Check if they added new loading indicators
3. Update wait conditions to match new loading behavior

## 🚨 Emergency Workarounds

If the website breaks and you need immediate fixes:

### Option 1: Return Cached Data

Add a simple cache system:
```python
# Save last successful scrape
last_successful_data = {
    "status": "success",
    "flights": [...],
    "cached_at": "2025-12-01 10:00:00",
    "is_fallback": True
}
```

### Option 2: Use Alternative Data Source

If available, switch to:
- Official airport API (if they provide one)
- Alternative flight tracking websites
- Flight data aggregators

### Option 3: Notify Users

Return a maintenance message:
```json
{
  "status": "maintenance",
  "message": "Flight data temporarily unavailable due to website changes. We're working on a fix.",
  "estimated_fix": "Within 24 hours",
  "alternative": "Visit https://www.jakarta-airport.com directly"
}
```

## 🔔 Setting Up Alerts

### Email Alerts on Failure

Add this to your monitoring script:

```python
import smtplib
from email.mime.text import MIMEText

def send_alert(message):
    msg = MIMEText(message)
    msg['Subject'] = '⚠️ Flight Scraper Alert: Website Structure Changed'
    msg['From'] = 'monitor@yourdomain.com'
    msg['To'] = 'admin@yourdomain.com'
    
    with smtplib.SMTP('localhost') as server:
        server.send_message(msg)

# Call when changes detected
if changes_detected:
    send_alert("The Jakarta Airport website structure has changed!")
```

### Slack/Discord Webhooks

```python
import requests

def notify_slack(message):
    webhook_url = "YOUR_SLACK_WEBHOOK_URL"
    payload = {
        "text": f"⚠️ Flight Scraper Alert: {message}"
    }
    requests.post(webhook_url, json=payload)
```

## 📊 Monitoring Checklist

Use this checklist for regular maintenance:

- [ ] **Weekly**: Run `monitor_html_structure.py` to check for changes
- [ ] **Weekly**: Test the API endpoint manually
- [ ] **Monthly**: Review error logs for patterns
- [ ] **Monthly**: Update dependencies (`pip install --upgrade -r requirements.txt`)
- [ ] **Quarterly**: Review and update fallback selectors
- [ ] **After Each Fix**: Update baseline snapshot
- [ ] **After Each Fix**: Document what changed in a changelog

## 📝 Changelog Template

Keep a log of changes in `SCRAPER_CHANGELOG.md`:

```markdown
## 2025-12-01 - HTML Structure Change

**What Changed:**
- Main container class changed from `flights-info` to `flight-data-container`
- Row class changed from `flight-row` to `arrival-item`

**Selectors Updated:**
- Line 495: Updated flights_info selector
- Line 507: Updated flight_rows selector

**Testing:**
- ✅ Test script passes
- ✅ Returns 150+ flights
- ✅ All fields populated correctly

**Baseline Updated:** Yes
```

## 🎯 Best Practices

1. **Never hardcode selectors in multiple places** - Use constants or a config file
2. **Always have fallback selectors** - Primary, secondary, tertiary
3. **Log everything** - Especially when fallbacks are used
4. **Test regularly** - Automated tests should run daily
5. **Monitor proactively** - Don't wait for users to report issues
6. **Document everything** - Future you will thank present you
7. **Version your snapshots** - Keep historical HTML structure data
8. **Graceful degradation** - Partial data is better than no data

## 🔮 Future Improvements

Consider implementing:

- [ ] Machine learning to detect layout changes automatically
- [ ] A/B testing to handle gradual rollouts
- [ ] Multiple scraping strategies with automatic failover
- [ ] Browser fingerprinting resistance
- [ ] Proxy rotation if rate-limited
- [ ] Headless browser alternatives (Playwright, Puppeteer)

## 📚 Additional Resources

- **BeautifulSoup Documentation**: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- **Selenium Documentation**: https://selenium-python.readthedocs.io/
- **CSS Selectors Guide**: https://www.w3schools.com/cssref/css_selectors.asp
- **XPath Tutorial**: https://www.w3schools.com/xml/xpath_intro.asp

## 💡 Quick Reference

### Current Class Names (as of 2025-12-01)

| Element | Class Name |
|---------|-----------|
| Container | `flights-info` |
| Row | `flight-row` |
| Header Row | `flight-titol` |
| Origin | `flight-col__dest-term` |
| Arrival Time | `flight-col__hour` |
| Flight Number | `flight-col__flight` |
| Airline | `flight-col__airline` |
| Terminal | `flight-col__term` |
| Status | `flight-col__status` |

### Files to Update When Structure Changes

1. `app.py` - Main scraper function (lines 469-700)
2. `monitor_html_structure.py` - Update expected class names
3. `test_flight_arrivals.py` - Update test expectations
4. `HANDLING_HTML_CHANGES.md` - Update this guide
5. `html_structure_baseline.json` - Save new baseline

---

**Remember**: Web scraping requires ongoing maintenance. Budget time for periodic updates and monitoring! 🚀