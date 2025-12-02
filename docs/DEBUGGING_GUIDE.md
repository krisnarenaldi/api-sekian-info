# Debugging Guide - Empty Data Issue 🔍

## Problem Summary

The cache file shows `total_items: 0` and `data: []`, meaning the scraping succeeded but returned no data.

## Current Status

- ✅ Scraper can access the website
- ✅ Table structure is found correctly
- ✅ Headers are parsed (shows "26 Nov", "27 Nov", etc.)
- ❌ Data array is empty (0 items)

## Changes Made to Fix

### 1. Increased Wait Time
Changed from 2 seconds to 5 seconds to ensure data loads:
```python
time.sleep(5)  # Was: time.sleep(2)
```

### 2. Added Debug Logging
Added console output to track the scraping process:
- Row count found
- Cell count per row
- Items extracted
- Any errors encountered

### 3. Added Empty Row Filtering
Skip rows where komoditas (commodity name) is empty:
```python
if komoditas:
    data.append({...})
```

## Testing Steps

### Step 1: Delete Old Cache
```bash
cd api-stasiun-info
rm sembako_cache.json
```

### Step 2: Start Flask Server
```bash
python app.py
```

**Watch the console output!** You should see DEBUG messages when scraping.

### Step 3: Test Fresh Scrape (in another terminal)
```bash
python test_fresh_scrape.py
```

This will:
- Make a request to `/api/sembako`
- Show the response details
- Save response to `last_response.json`
- Display timing and item count

### Step 4: Check Server Console

Look for these DEBUG messages in the Flask server console:
```
DEBUG: Found 16 rows in tbody
DEBUG: Extracted 16 items with complete data
```

If you see:
```
DEBUG: Found 16 rows in tbody
DEBUG: Extracted 0 items with complete data
```

Then rows are being skipped. Check for:
- "Skipping row with only X cells" messages
- Error messages about parsing

### Step 5: Verify Cache File
```bash
cat sembako_cache.json | jq '.'
```

Should show `total_items: 16` (not 0) and populated `data` array.

## Debug Script

We created `debug_scraper.py` which provides detailed analysis:

```bash
python debug_scraper.py
```

**Last run results:**
- ✅ Found 16 rows in tbody
- ✅ All rows have 5 cells
- ✅ Successfully extracted data from all rows

This proves the website is accessible and data is available.

## Possible Causes

### 1. Timing Issue (FIXED)
**Problem:** Table loads but data populates slowly  
**Solution:** Increased wait from 2s to 5s

### 2. Empty Rows (FIXED)
**Problem:** Rows exist but have empty commodity names  
**Solution:** Added filter to skip empty rows

### 3. Cell Count Mismatch
**Problem:** Rows don't have expected 5 cells  
**Solution:** Debug logging will show "Skipping row with only X cells"

### 4. Exception During Parsing
**Problem:** Error occurs during data extraction  
**Solution:** Added try-catch with traceback printing

## What to Check

### In Server Console (app.py output)
Look for:
```
DEBUG: Found 16 rows in tbody
DEBUG: Extracted 16 items with complete data
```

Or error messages:
```
ERROR: Table wrapper not found
ERROR: Table body not found
ERROR: Exception during scraping: ...
```

### In Cache File
```bash
# Check if cache exists
ls -lh sembako_cache.json

# View cache content
cat sembako_cache.json

# Pretty print
python -m json.tool sembako_cache.json
```

### In Response
```bash
curl http://localhost:5500/api/sembako | jq '.total_items'
```

Should return: `16` (not `0`)

## Manual Test Commands

### Delete cache and force fresh scrape
```bash
rm sembako_cache.json
curl http://localhost:5500/api/sembako
```

### Force refresh endpoint
```bash
curl -X POST http://localhost:5500/api/sembako/refresh
```

### Check cache status
```bash
curl http://localhost:5500/api/sembako/cache-status
```

## Expected vs Actual

### Expected Behavior
1. Request comes in
2. Cache is invalid/missing
3. Selenium opens website
4. Waits for table (✅ working)
5. Waits 5 seconds for data
6. Finds 16 rows (✅ working per debug_scraper.py)
7. Parses all 16 rows
8. Returns 16 items (❌ returns 0)

### The Gap
Between step 6 and 7, something is causing rows to be skipped.

## Debug Output Example

**Good output (what we want):**
```
DEBUG: Found 16 rows in tbody
DEBUG: Extracted 16 items with complete data
```

**Bad output (current problem):**
```
DEBUG: Found 16 rows in tbody
DEBUG: Skipping row with only 3 cells
DEBUG: Skipping row with only 3 cells
...
DEBUG: Extracted 0 items with complete data
```

**Or with errors:**
```
DEBUG: Found 16 rows in tbody
ERROR: Exception during scraping: 'NoneType' object has no attribute 'find'
```

## Next Steps

1. **Start the Flask server** with the updated code
2. **Watch the console** for DEBUG messages
3. **Make a test request** using test_fresh_scrape.py
4. **Share the DEBUG output** you see in the console

The debug messages will tell us exactly where the issue is:
- Are rows being found?
- Are cells being found?
- Are rows being skipped?
- Is there an exception?

## Quick Diagnosis

Run these commands and share the output:

```bash
# 1. Delete old cache
rm sembako_cache.json

# 2. Run debug scraper (standalone test)
python debug_scraper.py | tail -20

# 3. Start Flask server (in one terminal)
python app.py

# 4. Make test request (in another terminal)
curl http://localhost:5500/api/sembako | jq '.total_items'
```

The standalone debug script (`debug_scraper.py`) proved the data is accessible, so the issue must be in the Flask app's scraping logic.

## Additional Debug Script

If needed, create a minimal test:

```python
# test_minimal.py
from app import scrape_sembako_data

print("Testing scrape_sembako_data() directly...")
response, status_code = scrape_sembako_data()
data = response.get_json()

print(f"Status: {status_code}")
print(f"Total items: {data.get('total_items')}")
print(f"Data array length: {len(data.get('data', []))}")

if data.get('total_items', 0) == 0:
    print("\n⚠️  PROBLEM: Still getting 0 items")
else:
    print(f"\n✅ SUCCESS: Got {data.get('total_items')} items")
```

Run with:
```bash
python test_minimal.py
```

## Files to Check

- `app.py` - Main scraping logic (updated)
- `debug_scraper.py` - Standalone debug script
- `test_fresh_scrape.py` - Test with server running
- `sembako_cache.json` - Cache file (check total_items)
- `last_response.json` - Last API response (created by test script)

## Summary

The issue is that while the debug script successfully finds 16 rows with data, the Flask app returns 0 items. With the added debug logging, we'll be able to see exactly where the data is being lost in the Flask app's scraping process.

**Action Required:** Run the Flask server and check console output for DEBUG messages!