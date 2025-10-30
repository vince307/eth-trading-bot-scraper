# Vercel + Playwright Solution

## The Problem

Vercel serverless functions for Python don't have built-in Playwright browser support. When you deploy, you get:
```
BrowserType.launch: Executable doesn't exist at /tmp/.playwright/chromium-1140/chrome-linux/chrome
```

## Solution Options

### Option 1: Use Vercel + External Scraping Service (RECOMMENDED)

Instead of running Playwright in Vercel, set up a separate scraping service:

**Architecture:**
```
User → Vercel API → Scraping Service (with Playwright) → Investing.com
                ↓
         Supabase Database
```

**Implementation:**
1. Keep Vercel API for routing and database operations
2. Deploy Playwright scraper to a service that supports it:
   - **Railway.app** (Python + Docker support)
   - **Fly.io** (Docker support)
   - **AWS Lambda with Docker** (custom runtime)
   - **Google Cloud Run** (Docker support)

3. Vercel API calls the scraping service when needed

### Option 2: Use Vercel with HTTP Scraper + Warning

Accept that technical indicators won't work in Vercel and return a clear message:

```python
# api/scrape.py
result = {
    "success": True,
    "warning": "Technical indicators unavailable in Vercel environment. Deploy scraper separately.",
    "data": {
        "parsed": {
            "technicalIndicators": [],  # Empty
            "movingAverages": [],        # Empty
            "pivotPoints": [...]         # Works
        }
    }
}
```

### Option 3: Use BrowserBase or Similar Service

Use a managed browser automation service:

1. **BrowserBase.com** - Managed Playwright/Puppeteer
2. **Browserless.io** - Browser automation API
3. **ScrapingBee** - Web scraping API

These services provide browser automation via API, no local installation needed.

### Option 4: Deploy to Railway.app Instead (EASIEST)

Railway.app supports Python + Playwright out of the box.

**Steps:**
1. Create `railway.json`:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn api.wsgi:app",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

2. Create `Procfile`:
```
web: gunicorn api.wsgi:app --bind 0.0.0.0:$PORT
```

3. Deploy to Railway:
```bash
railway login
railway init
railway up
```

Railway will automatically:
- Install Python dependencies
- Run `playwright install chromium`
- Set up environment variables
- Deploy your API

### Option 5: Use Vercel + Scheduled Scraping

If you don't need real-time scraping:

1. Run scraper on a schedule (cron job) from a machine with Playwright
2. Store results in Supabase
3. Vercel API just reads from database

```python
# Separate cron job (runs every hour on Railway/Docker)
def scheduled_scrape():
    for crypto in ['BTC', 'ETH', 'ADA', ...]:
        result = scrape_crypto_technical(crypto=crypto)
        save_to_database(result)

# Vercel API (just reads from DB)
def api_handler():
    return get_latest_from_database(crypto)
```

## Recommended Approach

For your use case, I recommend **Option 4 (Railway.app)** or **Option 5 (Scheduled Scraping)**:

### Why Railway.app?
- ✅ Native Python + Playwright support
- ✅ Automatic browser installation
- ✅ Same API structure as Vercel
- ✅ Free tier available
- ✅ Easy migration (just change deployment target)

### Why Scheduled Scraping?
- ✅ Keep Vercel for API
- ✅ Run scraper separately (Railway, Docker, etc.)
- ✅ Lower costs (scrape once, serve many times)
- ✅ Better performance (no wait for scraping)
- ✅ Works with your existing database

## Implementation: Railway.app Migration

1. **Create Railway account**: https://railway.app

2. **Add Railway configuration** (already have most files):
   - `requirements.txt` ✅
   - `runtime.txt` (optional - specify Python version)
   - Start command in Railway dashboard

3. **Deploy**:
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up
```

4. **Set environment variables** in Railway dashboard:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`

5. **Railway automatically runs**:
```bash
pip install -r requirements.txt
playwright install chromium
```

## Implementation: Scheduled Scraping

1. **Keep Vercel API** for endpoints (reading data)

2. **Create separate scraper service** (Railway/Docker):
```python
# scraper_cron.py
import schedule
import time
from src.scrapers.investing_scraper import scrape_crypto_technical
from src.database.supabase_client import insert_technical_analysis_data

def scrape_all_cryptos():
    cryptos = ['BTC', 'ETH', 'ADA', 'SOL', 'DOT', 'LINK', 'MATIC', 'LTC', 'XRP', 'DOGE']
    for crypto in cryptos:
        try:
            result = scrape_crypto_technical(crypto=crypto)
            if result['success']:
                insert_technical_analysis_data(result['parsed'], use_service_role=True)
                print(f"✓ Scraped and saved {crypto}")
        except Exception as e:
            print(f"✗ Failed to scrape {crypto}: {e}")

# Run every hour
schedule.every().hour.do(scrape_all_cryptos)

while True:
    schedule.run_pending()
    time.sleep(60)
```

3. **Vercel API reads from database**:
```python
# api/read.py
from src.database.supabase_client import SupabaseClient

def handler(request):
    crypto = request.args.get('crypto', 'BTC')
    client = SupabaseClient()
    data = client.get_latest_technical_analysis(symbol=crypto, limit=1)
    return {"success": True, "data": data}
```

## Next Steps

Choose your approach:

- **Quick Fix**: Option 2 (accept limited functionality)
- **Best Performance**: Option 5 (scheduled scraping)
- **Easiest Migration**: Option 4 (Railway.app)
- **Enterprise**: Option 3 (BrowserBase/Browserless)

Let me know which approach you prefer and I'll help implement it!
