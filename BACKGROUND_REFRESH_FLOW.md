# Background Refresh Pattern - Flow Diagram

## How It Works

The background refresh pattern ensures **fast responses** while maintaining **data freshness**.

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    API Request Received                          │
│              (GET /api/cinema, /api/events, etc.)               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │ Cache Exists?  │
                    └────┬───────┬───┘
                         │       │
                    YES  │       │  NO
                         │       │
                         ▼       ▼
            ┌────────────────┐  ┌──────────────────┐
            │ Load from Cache│  │ Scrape New Data  │
            │   (~50ms)      │  │  (3-8 seconds)   │
            └────────┬───────┘  └────────┬─────────┘
                     │                   │
                     ▼                   ▼
            ┌────────────────┐  ┌──────────────────┐
            │ Check if Stale?│  │  Save to Cache   │
            └────┬───────┬───┘  └────────┬─────────┘
                 │       │               │
            STALE│       │FRESH          │
                 │       │               │
                 ▼       ▼               ▼
    ┌────────────────┐  │      ┌──────────────────┐
    │ Already        │  │      │ Return Response  │
    │ Refreshing?    │  │      │  to Frontend     │
    └────┬───────┬───┘  │      └──────────────────┘
         │       │      │
    YES  │       │  NO  │
         │       │      │
         ▼       ▼      │
    ┌────────┐  ┌──────┴──────────┐
    │  Skip  │  │ Start Background│
    │        │  │ Refresh Thread  │
    └────┬───┘  └────────┬────────┘
         │               │
         │               ▼
         │      ┌─────────────────┐
         │      │ Scrape New Data │
         │      │  (in background)│
         │      └────────┬────────┘
         │               │
         │               ▼
         │      ┌─────────────────┐
         │      │ Update Cache    │
         │      │     File        │
         │      └────────┬────────┘
         │               │
         │               ▼
         │      ┌─────────────────┐
         │      │ Mark Refresh    │
         │      │   Complete      │
         │      └─────────────────┘
         │
         └───────────────┬
                         ▼
            ┌────────────────────────┐
            │ Return Cached Response │
            │    to Frontend         │
            │  (with metadata)       │
            └────────────────────────┘
```

## Key Benefits

### 1. **Always Fast** ⚡
- First request: Returns cached data in ~50ms
- Subsequent requests: Still ~50ms (even while refreshing)
- No waiting for scraping to complete

### 2. **Always Fresh** 🔄
- Stale cache triggers automatic background refresh
- Next request gets updated data
- No manual intervention needed

### 3. **Resource Efficient** 💰
- Prevents duplicate refresh operations
- Uses threading for non-blocking updates
- Scrapes only when necessary

### 4. **User-Friendly** 😊
- No loading spinners for users
- Instant data display
- Optional "updating" indicator via `refreshing_in_background` flag

## Example Timeline

```
Time    Event                           Response Time    Cache State
─────────────────────────────────────────────────────────────────────
00:00   Request 1 (cache fresh)         50ms            ✅ Fresh
        → Returns cached data

24:01   Request 2 (cache stale)         50ms            ❌ Stale
        → Returns cached data
        → Triggers background refresh

24:01   Background refresh starts       -               🔄 Refreshing
        (scraping in background)

24:08   Background refresh completes    -               ✅ Fresh
        (cache updated)

24:09   Request 3                       50ms            ✅ Fresh
        → Returns NEW cached data
```

## Cache Validity Thresholds

| Endpoint           | Validity Period | Auto-Refresh Trigger |
|--------------------|-----------------|----------------------|
| `/api/cinema`      | 6 days          | After 6 days         |
| `/api/events`      | 5 days          | After 5 days         |
| `/api/google_trend`| 24 hours        | After 24 hours       |

## Response Fields

All endpoints return these metadata fields:

```json
{
  "items": [...],                      // Your data
  "from_cache": true,                  // Always true (except first time)
  "cache_valid": false,                // Is cache still fresh?
  "cache_date": "2025-11-28 10:30:00", // When cache was created
  "refreshing_in_background": true     // Is refresh happening now?
}
```

## Frontend Integration

### Simple Approach (No UI Changes)
```javascript
// Just call the API - everything works automatically
const response = await fetch('/api/cinema');
const data = await response.json();
// Use data.items as normal
```

### Advanced Approach (With Status Indicators)
```javascript
const response = await fetch('/api/cinema');
const data = await response.json();

// Show data immediately
displayMovies(data.items);

// Optional: Show status to user
if (data.refreshing_in_background) {
  showBadge("Updating...");
} else if (!data.cache_valid) {
  showBadge("Data may be outdated");
}
```

## Comparison with Other Patterns

| Pattern                  | Response Time | Data Freshness | Complexity |
|--------------------------|---------------|----------------|------------|
| **No Cache**             | 3-8 seconds   | ✅ Always fresh | Low        |
| **Simple Cache**         | 50ms          | ❌ Can be stale | Low        |
| **Cache + Sync Refresh** | 3-8 seconds   | ✅ Always fresh | Medium     |
| **Background Refresh** ⭐ | 50ms          | ✅ Auto-fresh   | Medium     |

## Thread Safety

The implementation includes safeguards:
- Global `_refresh_tasks` dictionary tracks ongoing refreshes
- Prevents duplicate background threads
- Daemon threads don't block application shutdown

