# Monitoring Guide

Simple monitoring setup for the TAAPI.IO Technical Analysis Scraper.

---

## Quick Start

### 1. Health Check (API Endpoint)

Check if your deployed API is working:

```bash
# Test production deployment
python3 health_check.py https://your-deployment.vercel.app

# Test local development
vercel dev  # In another terminal
python3 health_check.py http://localhost:3000

# Save to log file
python3 health_check.py https://your-deployment.vercel.app >> health.log
```

**What it checks:**
- ✅ HTTP status code
- ✅ JSON response validity
- ✅ Number of indicators fetched
- ✅ Database save status

**Expected output:**
```
============================================================
Health Check: 2025-11-01 12:00:00
Endpoint: https://your-deployment.vercel.app/api/scrape?crypto=BTC
============================================================

⏳ Fetching BTC technical analysis...
   (This may take up to 5 minutes due to rate limiting)

✅ API is healthy!

Symbol: BTC
Price: $110,000.00
Technical Indicators: 11/12
Moving Averages: 3/3

✅ Data saved to database

============================================================
```

---

### 2. Data Freshness Check (Database)

Check when data was last updated:

```bash
# Check BTC data freshness
python3 check_data_freshness.py

# Check specific crypto
python3 check_data_freshness.py ETH

# Check all supported cryptos
python3 check_data_freshness.py --all

# Get JSON output (for scripts)
python3 check_data_freshness.py BTC --json
```

**Expected output:**
```
============================================================
Data Freshness Check: 2025-11-01 12:00:00
============================================================

✅ BTC:
   Age: 15.3 minutes
   Scraped: 2025-11-01 11:45:00 UTC
   Price: $110,000.00
   Indicators: 11 indicators
   Summary: Strong Buy
```

**Status indicators:**
- ✅ **Fresh** (<1 hour old) - Good for trading
- ⚠️  **Acceptable** (1-2 hours old) - Still usable
- ❌ **Stale** (>2 hours old) - Should wait for fresh data

---

## Vercel Dashboard Monitoring

### Access Logs

1. Go to https://vercel.com/dashboard
2. Select your project
3. Click "Logs" tab
4. Filter by:
   - Function: `/api/scrape`
   - Status: `200`, `500`, etc.
   - Time range

### View Metrics

**Deployments** tab shows:
- Deployment status (success/failed)
- Build time
- Deployment URL

**Analytics** tab shows (requires Pro plan):
- Request count
- Error rate
- Function execution time
- Bandwidth usage

### CLI Logs

```bash
# Real-time logs
vercel logs --follow

# Logs for specific deployment
vercel logs https://your-deployment-url.vercel.app

# Last 100 logs
vercel logs --limit 100
```

---

## Automated Monitoring (Optional)

### Option 1: Cron Job (Linux/Mac)

Run health check daily:

```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 9 AM)
0 9 * * * cd /path/to/eth-trading-bot-scraper && python3 health_check.py https://your-deployment.vercel.app >> logs/health_$(date +\%Y\%m\%d).log 2>&1
```

### Option 2: GitHub Actions (Free)

Create `.github/workflows/health-check.yml`:

```yaml
name: Daily Health Check

on:
  schedule:
    - cron: '0 9 * * *'  # 9 AM daily
  workflow_dispatch:  # Manual trigger

jobs:
  health-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install requests python-dotenv

      - name: Run health check
        run: python3 health_check.py ${{ secrets.VERCEL_URL }}

      - name: Notify on failure
        if: failure()
        run: echo "Health check failed! Check logs."
```

### Option 3: Vercel Cron (Recommended)

Add to `vercel.json`:

```json
{
  "crons": [
    {
      "path": "/api/scrape?crypto=BTC&save=true",
      "schedule": "0 * * * *"
    },
    {
      "path": "/api/scrape?crypto=ETH&save=true",
      "schedule": "5 * * * *"
    }
  ]
}
```

This automatically fetches data hourly and saves to database.

---

## Monitoring from TypeScript Trading Bot

Add this to your `eth-trading-bot-api`:

```typescript
// src/utils/dataFreshness.ts
import { supabase } from './supabase';

export async function checkDataFreshness(
  symbol: string,
  maxAgeHours: number = 2
): Promise<boolean> {
  try {
    const { data, error } = await supabase
      .from('technical_analysis')
      .select('scraped_at')
      .eq('symbol', symbol)
      .order('created_at', { desc: true })
      .limit(1);

    if (error || !data || data.length === 0) {
      console.error(`❌ No data found for ${symbol}`);
      return false;
    }

    const scrapedAt = new Date(data[0].scraped_at);
    const ageMs = Date.now() - scrapedAt.getTime();
    const ageHours = ageMs / (1000 * 60 * 60);

    if (ageHours > maxAgeHours) {
      console.warn(
        `⚠️  ${symbol} data is ${ageHours.toFixed(1)} hours old (max: ${maxAgeHours}h)`
      );
      return false;
    }

    console.log(
      `✅ ${symbol} data is fresh (${(ageMs / 60000).toFixed(1)} minutes old)`
    );
    return true;
  } catch (error) {
    console.error(`❌ Error checking data freshness:`, error);
    return false;
  }
}

// Usage in your trading logic
export async function executeTradeIfDataFresh(symbol: string) {
  const isFresh = await checkDataFreshness(symbol);

  if (!isFresh) {
    console.log(`Skipping ${symbol} trade - waiting for fresh data`);
    return;
  }

  // Your trading logic here
  console.log(`Executing trade for ${symbol}...`);
}
```

---

## Alert Thresholds

### Data Freshness
- ✅ **Fresh** (<1 hour): Excellent - safe to trade
- ⚠️  **Acceptable** (1-2 hours): Usable - proceed with caution
- ❌ **Stale** (>2 hours): Skip trading - wait for update

### Indicator Count
- ✅ **12/12 indicators**: Perfect
- ✅ **10-11/12 indicators**: Good (acceptable with retries)
- ⚠️  **8-9/12 indicators**: Acceptable minimum
- ❌ **<8/12 indicators**: Insufficient data - skip trading

### API Response Time
- ✅ **<5 minutes**: Normal (with rate limiting)
- ⚠️  **5-7 minutes**: Slow (possible retry attempts)
- ❌ **>7 minutes or timeout**: API issue - investigate

---

## Troubleshooting

### Health Check Fails

```bash
❌ HTTP Error: 500
```

**Solutions:**
1. Check Vercel logs: `vercel logs`
2. Verify environment variables are set
3. Test TAAPI.IO API key directly
4. Check TAAPI.IO rate limits

### Data is Stale

```bash
❌ BTC: 3.5 hours old
```

**Solutions:**
1. Check if Vercel Cron is configured
2. Manually trigger update: `curl "https://your-url.vercel.app/api/scrape?crypto=BTC&save=true"`
3. Verify SUPABASE_SERVICE_ROLE_KEY is set
4. Check database logs in Supabase dashboard

### Missing Indicators

```bash
⚠️  Warning: Only 7 indicators fetched (expected 12)
```

**Solutions:**
1. Check TAAPI.IO API status
2. Review logs for specific indicator failures
3. Retry mechanism should handle this automatically
4. If persistent, check TAAPI.IO account limits

---

## Monitoring Best Practices

### Daily Routine
1. ✅ Check Vercel dashboard once a day
2. ✅ Run `check_data_freshness.py` before important trades
3. ✅ Review logs if any trades fail

### Weekly Routine
1. ✅ Run full health check: `python3 health_check.py`
2. ✅ Check TAAPI.IO usage (10% of free tier)
3. ✅ Review error patterns in Vercel logs

### Monthly Routine
1. ✅ Review deployment performance
2. ✅ Check if upgrade to TAAPI.IO Basic plan is needed
3. ✅ Update dependencies if needed

---

## Cost Monitoring

### Free Tier Limits

**TAAPI.IO Free Tier:**
- 5,760 requests/day
- Current usage: ~576 requests/day (10%)
- ✅ Well within limits

**Vercel Free Tier:**
- 100 GB bandwidth/month
- 100,000 function invocations/month
- Current usage: ~720 invocations/month (hourly)
- ✅ Well within limits

**Supabase Free Tier:**
- 500 MB database
- 2 GB bandwidth/month
- Current usage: Minimal (small JSONB records)
- ✅ Well within limits

### Usage Tracking

```bash
# Check TAAPI.IO usage
# Visit: https://taapi.io/account/usage

# Check Vercel usage
vercel inspect

# Check Supabase usage
# Visit: https://supabase.com/dashboard/project/_/settings/billing
```

---

## Summary

**Minimum monitoring setup (5 minutes):**
1. ✅ Bookmark Vercel logs dashboard
2. ✅ Test `health_check.py` once after deployment
3. ✅ Add data freshness check to trading bot

**Recommended monitoring setup (15 minutes):**
1. ✅ Set up Vercel Cron for hourly updates
2. ✅ Add `checkDataFreshness()` to trading bot
3. ✅ Run `check_data_freshness.py` daily

**Advanced monitoring (optional):**
1. GitHub Actions for daily health checks
2. Custom alerting (email/Slack)
3. Grafana dashboard with Supabase metrics

---

**For this project, the minimum setup is sufficient.** Your trading bot's data freshness check is the most important monitoring mechanism.
