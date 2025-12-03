# Troubleshooting Slow Production API

## Issue: Production API Still Takes >3 Seconds

If you're experiencing slow response times on production (https://api-sekian-info.onrender.com), here are the most common causes and solutions:

## 🔍 Diagnosis

### Step 1: Run the Diagnostic Script

```bash
python test_production_speed.py
```

This will tell you:
- Exact response times
- Whether it's a cold start issue
- Network latency measurements

### Step 2: Check Server Logs

Look at your Render logs for these messages:
- `⚡ Cinema API: Returned cached data in XXms` - Should be <100ms
- `⚠️  No cinema cache found, scraping synchronously...` - This is the problem!

## 🐛 Common Causes & Solutions

### 1. **Cold Start (Most Common)** ❄️

**Symptoms:**
- First request takes 30-60 seconds
- Subsequent requests are fast (<500ms)
- Happens after 15 minutes of inactivity

**Cause:** Render free tier spins down your service after 15 minutes of no traffic.

**Solutions:**

#### Option A: Keep-Alive Service (Free)
Use a service to ping your API every 10 minutes:
- [UptimeRobot](https://uptimerobot.com/) (Free, 5-minute intervals)
- [Cron-Job.org](https://cron-job.org/) (Free, custom intervals)
- [BetterUptime](https://betterstack.com/better-uptime) (Free tier available)

Setup:
```
URL to ping: https://api-sekian-info.onrender.com/health
Interval: Every 10 minutes
```

#### Option B: Upgrade to Render Paid Tier ($7/month)
- No cold starts
- Always-on service
- Better performance

#### Option C: Use Render Cron Jobs
Add to your `render.yaml`:
```yaml
services:
  - type: web
    # ... your existing config
  
  - type: cron
    name: keep-alive
    env: python
    schedule: "*/10 * * * *"  # Every 10 minutes
    buildCommand: "pip install requests"
    startCommand: "python -c 'import requests; requests.get(\"https://api-sekian-info.onrender.com/health\")'"
```

### 2. **Cache Files Missing on Server** 📁

**Symptoms:**
- Every request takes 3-8 seconds
- Logs show: `⚠️  No cinema cache found, scraping synchronously...`
- Response has `from_cache: false`

**Cause:** Cache files (`cinema.json`, `events_tix.json`, `trending_now.json`) don't exist on the server.

**Solutions:**

#### Option A: Pre-populate Cache Files
Add cache files to your git repository:
```bash
git add cinema.json events_tix.json trending_now.json
git commit -m "Add cache files"
git push
```

#### Option B: Use Persistent Storage
Render free tier has ephemeral storage (resets on deploy). Consider:
- Render Disks (paid feature)
- External storage (S3, etc.)
- Database storage

#### Option C: Warm-up Script
Add a post-deploy script to populate cache:
```bash
# In render.yaml or as a post-deploy hook
curl -X POST https://api-sekian-info.onrender.com/api/cinema/refresh
curl -X POST https://api-sekian-info.onrender.com/api/events/refresh
```

### 3. **Network Latency** 🌐

**Symptoms:**
- Consistent 1-3 second delays
- Same delay for all requests
- Logs show fast server response (<100ms)

**Cause:** Distance between you and Render's servers.

**Solutions:**

#### Option A: Use a CDN
Add Cloudflare in front of your API:
1. Point your domain to Cloudflare
2. Enable caching for API responses
3. Set cache TTL to match your cache validity periods

#### Option B: Deploy Closer to Users
If most users are in a specific region, deploy there:
- Render: Choose region closest to users
- Vercel: Automatic edge deployment
- AWS Lambda: Regional deployment

### 4. **Server Performance Issues** 🐌

**Symptoms:**
- Server logs show slow response times (>500ms)
- Even cached responses are slow
- CPU/Memory usage is high

**Cause:** Server is overloaded or under-resourced.

**Solutions:**

#### Option A: Optimize Code
- Reduce JSON file size (remove unnecessary data)
- Use faster JSON library (`orjson` instead of `json`)
- Enable gzip compression

#### Option B: Upgrade Server Resources
- Render: Upgrade to higher tier
- More RAM/CPU

#### Option C: Add Response Caching
Use Flask-Caching to cache responses in memory:
```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route("/api/cinema")
@cache.cached(timeout=300)  # Cache for 5 minutes
def get_cinema_data():
    # ... your code
```

## 🧪 Testing After Fixes

### Test 1: Cold Start
```bash
# Wait 20 minutes, then:
curl -w "\nTime: %{time_total}s\n" https://api-sekian-info.onrender.com/api/cinema
```

### Test 2: Warm Server
```bash
# Make 3 requests in a row:
for i in {1..3}; do
  curl -w "\nTime: %{time_total}s\n" https://api-sekian-info.onrender.com/api/cinema
  sleep 1
done
```

### Test 3: Check Server Response Time
```bash
curl https://api-sekian-info.onrender.com/api/cinema | jq '.server_response_time_ms'
```

Expected: <100ms

## 📊 Performance Targets

| Scenario | Target | Acceptable | Slow |
|----------|--------|------------|------|
| Warm server, cached | <100ms | <500ms | >500ms |
| Cold start (free tier) | N/A | <60s | >60s |
| First request (no cache) | <8s | <15s | >15s |

## 🚀 Recommended Setup for Production

1. **Keep-Alive Service** (UptimeRobot) - Prevents cold starts
2. **Pre-populated Cache Files** - Fast first response
3. **CDN** (Cloudflare) - Reduces network latency
4. **Monitoring** (BetterUptime) - Alert on downtime

This setup is **100% free** and will give you:
- <500ms response times
- 99.9% uptime
- Global performance

## 📞 Still Having Issues?

Check the server logs on Render:
1. Go to Render Dashboard
2. Select your service
3. Click "Logs"
4. Look for the emoji indicators:
   - ⚡ = Fast cached response (good!)
   - ⚠️  = Cache miss, scraping (bad!)
   - 🔄 = Background refresh triggered (good!)
   - ❌ = Error (investigate!)

The `server_response_time_ms` field in the API response will tell you if the delay is on the server or network.

