# Sembako Price API - Documentation Index 📚

Welcome! This is your guide to navigating all the documentation for the Sembako Price API project.

## 🚀 Quick Navigation

### Getting Started (Start Here!)
1. **[QUICKSTART.md](QUICKSTART.md)** - Get running in 5 minutes
2. **[CHECKLIST.md](CHECKLIST.md)** - Verify your installation step-by-step
3. **[README.md](README.md)** - Complete documentation

### Core Files
- **[app.py](app.py)** - Main Flask application with scraping logic
- **[requirements.txt](requirements.txt)** - Python dependencies
- **[start.sh](start.sh)** - Easy server startup script

### Testing & Examples
- **[test_scraper.py](test_scraper.py)** - Test scraping functionality
- **[test_api.py](test_api.py)** - Test API endpoints
- **[example_usage.py](example_usage.py)** - 8 practical usage examples

### Reference Documentation
- **[COMMANDS.md](COMMANDS.md)** - All available commands
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Technical overview
- **[INDEX.md](INDEX.md)** - This file

## 📖 Documentation by Purpose

### I want to...

#### ...get started quickly
→ Read **[QUICKSTART.md](QUICKSTART.md)**
```bash
cd api-stasiun-info
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

#### ...understand how it works
→ Read **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)**
- Architecture overview
- Technology stack
- How the scraping works
- Data structure

#### ...see all available commands
→ Read **[COMMANDS.md](COMMANDS.md)**
- Setup commands
- Testing commands
- Debugging commands
- Deployment commands

#### ...verify my installation
→ Follow **[CHECKLIST.md](CHECKLIST.md)**
- Pre-installation checks
- Installation steps
- Testing verification
- Troubleshooting

#### ...learn by example
→ Run **[example_usage.py](example_usage.py)**
```bash
python example_usage.py
```
- 8 different usage patterns
- Data export examples
- Price analysis examples

#### ...read comprehensive docs
→ Read **[README.md](README.md)**
- Full installation guide
- API endpoints documentation
- Troubleshooting
- Technical details

## 🎯 Quick Reference

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API documentation |
| `/health` | GET | Health check |
| `/api/sembako` | GET | Sembako prices (main endpoint) |

### Response Format
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
    }
  ],
  "total_items": 16
}
```

## 📂 Project Structure

```
api-stasiun-info/
├── 📄 Documentation
│   ├── INDEX.md                 ← You are here
│   ├── README.md                ← Full documentation
│   ├── QUICKSTART.md            ← 5-minute setup
│   ├── CHECKLIST.md             ← Installation verification
│   ├── COMMANDS.md              ← Command reference
│   └── PROJECT_SUMMARY.md       ← Technical overview
│
├── 🐍 Python Code
│   ├── app.py                   ← Main Flask API
│   ├── test_scraper.py          ← Scraper test
│   ├── test_api.py              ← API test
│   └── example_usage.py         ← Usage examples
│
├── ⚙️  Configuration
│   ├── requirements.txt         ← Dependencies
│   ├── .gitignore              ← Git ignore rules
│   └── start.sh                ← Startup script
│
└── 🗂️  Generated (not in git)
    ├── .venv/                   ← Virtual environment
    └── *.json                   ← Exported data files
```

## 🔧 Technology Stack

- **Python 3.8+** - Programming language
- **Flask 3.0.0** - Web framework
- **Selenium 4.15.2** - Browser automation
- **BeautifulSoup4 4.12.2** - HTML parsing
- **Chrome** - Headless browser

## 🎓 Learning Path

### Beginner
1. Read [QUICKSTART.md](QUICKSTART.md)
2. Follow [CHECKLIST.md](CHECKLIST.md)
3. Run `python test_scraper.py`
4. Run `python app.py`
5. Visit http://localhost:5000/api/sembako

### Intermediate
1. Read [README.md](README.md) in full
2. Run `python example_usage.py`
3. Study [app.py](app.py) code
4. Explore [COMMANDS.md](COMMANDS.md)

### Advanced
1. Read [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
2. Modify scraper for other websites
3. Add caching mechanism
4. Deploy to production

## 🚨 Troubleshooting Guide

### Problem: Can't start server
→ Check [README.md#Troubleshooting](README.md)

### Problem: ChromeDriver errors
```bash
chmod +x ~/.wdm/drivers/chromedriver/*/chromedriver-mac-arm64/chromedriver
```
→ See [COMMANDS.md#Fix ChromeDriver Issues](COMMANDS.md)

### Problem: Port already in use
→ Change port in `app.py` line 201

### Problem: Timeout errors
→ Increase wait time in `app.py` line 85

## 📊 Common Use Cases

### 1. Get Current Prices
```bash
curl http://localhost:5000/api/sembako
```

### 2. Export to JSON
```bash
curl http://localhost:5000/api/sembako > prices.json
```

### 3. Monitor Specific Commodity
```python
import requests
response = requests.get('http://localhost:5000/api/sembako')
data = response.json()
beras = [item for item in data['data'] if 'Beras' in item['komoditas']]
```

### 4. Track Price Changes
```python
response = requests.get('http://localhost:5000/api/sembako')
changes = [item for item in response.json()['data'] if item['change'] != 0]
```

## 🎯 Next Steps

After reading this index:

1. **New users**: Go to [QUICKSTART.md](QUICKSTART.md)
2. **Developers**: Read [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
3. **Troubleshooting**: Check [CHECKLIST.md](CHECKLIST.md)
4. **Reference**: Bookmark [COMMANDS.md](COMMANDS.md)

## 📞 Support

- **Installation issues**: See [CHECKLIST.md](CHECKLIST.md)
- **API usage**: See [example_usage.py](example_usage.py)
- **Commands**: See [COMMANDS.md](COMMANDS.md)
- **Full docs**: See [README.md](README.md)

---

## 📝 Document Purposes at a Glance

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **INDEX.md** | Navigation hub | Start here |
| **QUICKSTART.md** | Fast setup | First time setup |
| **README.md** | Complete guide | Deep dive |
| **CHECKLIST.md** | Verification | After installation |
| **COMMANDS.md** | Command reference | As needed |
| **PROJECT_SUMMARY.md** | Technical overview | Understanding architecture |

---

**Current Status**: ✅ All documentation complete

**Version**: 1.0.0

**Last Updated**: November 2024

---

**Ready to start?** → Go to [QUICKSTART.md](QUICKSTART.md)

**Happy Scraping! 🚀**