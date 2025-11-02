# Multi-Cryptocurrency Setup Guide

Configure the scraper to fetch technical analysis for multiple cryptocurrencies.

---

## Default Configuration

By default, the scraper is configured for **3 cryptocurrencies**:
- **BTC** (Bitcoin)
- **ETH** (Ethereum)
- **SOL** (Solana)

---

## Environment Variable Configuration

### SUPPORTED_CRYPTOS

Control which cryptocurrencies to fetch using the `SUPPORTED_CRYPTOS` environment variable.

**.env file:**
```bash
# Comma-separated list of cryptocurrency symbols
SUPPORTED_CRYPTOS=BTC,ETH,SOL
```

**Supported symbols:**
- BTC (Bitcoin)
- ETH (Ethereum)
- SOL (Solana)
- ADA (Cardano)
- DOT (Polkadot)
- LINK (Chainlink)
- MATIC (Polygon)
- LTC (Litecoin)
- XRP (XRP)
- DOGE (Dogecoin)

---

## Usage Examples

### 1. Fetch All Enabled Cryptos (API Endpoint)

```bash
# Fetch BTC → ETH → SOL synchronously (uses SUPPORTED_CRYPTOS env var)
curl "https://your-url.vercel.app/api/scrape_all"

# Without saving to database (testing only)
curl "https://your-url.vercel.app/api/scrape_all?save=false"
```

**Response:**
```json
{
  "success": true,
  "message": "Fetched 3 cryptocurrencies synchronously",
  "data": {
    "cryptos": [
      {
        "symbol": "BTC",
        "success": true,
        "data": {
          "symbol": "BTC",
          "price": 110000,
          "indicator_count": 11,
          "ma_count": 3,
          "summary": "Strong Buy"
        },
        "saved_to_database": true,
        "fetch_time_seconds": 234.5
      },
      {
        "symbol": "ETH",
        "success": true,
        "data": {
          "symbol": "ETH",
          "price": 4200,
          "indicator_count": 12,
          "ma_count": 3,
          "summary": "Buy"
        },
        "saved_to_database": true,
        "fetch_time_seconds": 238.2
      },
      {
        "symbol": "SOL",
        "success": true,
        "data": {
          "symbol": "SOL",
          "price": 180,
          "indicator_count": 11,
          "ma_count": 3,
          "summary": "Neutral"
        },
        "saved_to_database": true,
        "fetch_time_seconds": 241.1
      }
    ],
    "summary": {
      "total": 3,
      "successful": 3,
      "failed": 0,
      "total_time_seconds": 723.8
    }
  }
}
```

**Execution Order (Synchronous):**
1. Fetches BTC first (~4 minutes)
2. Waits 5 seconds
3. Fetches ETH second (~4 minutes)
4. Waits 5 seconds
5. Fetches SOL third (~4 minutes)
6. Returns combined results

**Total time: ~12 minutes for all 3 cryptos**

### 2. Fetch All Enabled Cryptos (Python Script)

```bash
# Uses SUPPORTED_CRYPTOS from .env (BTC,ETH,SOL)
python3 fetch_all_cryptos.py
```

**Console Output:**
```
============================================================
Fetching Technical Analysis
Started: 2025-11-01 12:00:00
============================================================

Cryptocurrencies: BTC, ETH, SOL
Total: 3 cryptos
Save to database: True

Estimated time: ~12 minutes
(~4 minutes per crypto with retry mechanism)

============================================================

[1/3] Fetching BTC...
────────────────────────────────────────────────────────────
✅ BTC fetch successful
   Price: $110,000.00
   Indicators: 11/12
   Moving Averages: 3/3
   Summary: Strong Buy
   ✅ Saved to database
   Time: 234.5s

⏳ Waiting 5 seconds before next crypto...

[2/3] Fetching ETH...
────────────────────────────────────────────────────────────
✅ ETH fetch successful
   Price: $4,200.00
   Indicators: 12/12
   Moving Averages: 3/3
   Summary: Buy
   ✅ Saved to database
   Time: 238.2s

⏳ Waiting 5 seconds before next crypto...

[3/3] Fetching SOL...
────────────────────────────────────────────────────────────
✅ SOL fetch successful
   Price: $180.00
   Indicators: 11/12
   Moving Averages: 3/3
   Summary: Neutral
   ✅ Saved to database
   Time: 241.1s

============================================================
FETCH COMPLETE
============================================================
Success: 3/3 cryptos
  ✅ BTC, ETH, SOL
Failed: 0/3 cryptos

Total time: 12.1 minutes
Average per crypto: 241.3 seconds
============================================================
```

### 2. Fetch Specific Cryptos (Override Env Var)

```bash
# Fetch only BTC and ETH
python3 fetch_all_cryptos.py BTC ETH

# Fetch only SOL
python3 fetch_all_cryptos.py SOL
```

### 3. Dry Run (Don't Save to Database)

```bash
# Test without saving to database
python3 fetch_all_cryptos.py --dry-run
```

---

## Vercel Cron Configuration

The scraper includes **automatic hourly fetching** via Vercel Cron using a **single endpoint** that fetches all cryptos **synchronously** (one by one).

### vercel.json

```json
{
  "functions": {
    "api/**/*.py": {
      "memory": 512,
      "maxDuration": 900
    }
  },
  "crons": [
    {
      "path": "/api/scrape_all",
      "schedule": "0 * * * *"
    }
  ]
}
```

**Schedule:**
- **Every hour at :00** (12:00, 1:00, 2:00, ...)
- Fetches BTC → ETH → SOL **sequentially in that order**
- Total time: ~12 minutes for all 3 cryptos

**Important:**
- `maxDuration: 900` (15 minutes) allows time for all 3 cryptos
- Vercel Pro plan required for >10 minute function execution
- Free tier limited to 10 seconds (won't work for multi-crypto)

---

## Rate Limit Calculations

### Free Tier Limits
- **5,760 requests/day** (TAAPI.IO free tier)
- **1 request per 15 seconds**

### Usage for 3 Cryptos (BTC, ETH, SOL)

**Per crypto:**
- 12 indicators × 18 seconds = ~4 minutes
- 24 hours × 3 cryptos = 72 fetches/day
- 72 fetches × 12 requests = **864 requests/day**

**Free tier usage: 864 / 5,760 = 15%** ✅

### Adding More Cryptos

| Cryptos | Requests/Day | Free Tier % | Status |
|---------|--------------|-------------|--------|
| 2 (BTC, ETH) | 576 | 10% | ✅ Excellent |
| 3 (BTC, ETH, SOL) | 864 | 15% | ✅ Great |
| 4 | 1,152 | 20% | ✅ Good |
| 5 | 1,440 | 25% | ✅ Acceptable |
| 10 (all supported) | 2,880 | 50% | ⚠️ High usage |

**Recommendation:** Stick to 3-5 cryptos for comfortable free tier usage.

---

## Monitoring Multiple Cryptos

### Check Data Freshness for All

```bash
# Check all enabled cryptos
python3 check_data_freshness.py --all
```

**Output:**
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

✅ ETH:
   Age: 10.2 minutes
   Scraped: 2025-11-01 11:50:00 UTC
   Price: $4,200.00
   Indicators: 12 indicators
   Summary: Buy

✅ SOL:
   Age: 5.1 minutes
   Scraped: 2025-11-01 11:55:00 UTC
   Price: $180.00
   Indicators: 11 indicators
   Summary: Neutral
```

### Check Specific Crypto

```bash
python3 check_data_freshness.py SOL
```

---

## Deployment Configuration

### Vercel Environment Variables

Set in Vercel dashboard (Settings → Environment Variables):

```bash
# Required
TAAPI_API_KEY=your_taapi_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Optional (defaults to BTC,ETH,SOL)
SUPPORTED_CRYPTOS=BTC,ETH,SOL
DEFAULT_CRYPTO=BTC
DEFAULT_EXCHANGE=binance
DEFAULT_INTERVAL=1h
```

### Deploy

```bash
# Deploy to production
vercel --prod

# Verify environment variables
vercel env ls

# Test each crypto endpoint
curl "https://your-url.vercel.app/api/scrape?crypto=BTC&save=true"
curl "https://your-url.vercel.app/api/scrape?crypto=ETH&save=true"
curl "https://your-url.vercel.app/api/scrape?crypto=SOL&save=true"
```

---

## Troubleshooting

### 1. "Warning: SOL is not a supported cryptocurrency"

**Cause:** Typo in SUPPORTED_CRYPTOS or unsupported symbol

**Solution:**
```bash
# Check .env file
cat .env | grep SUPPORTED_CRYPTOS

# Should be uppercase, comma-separated
SUPPORTED_CRYPTOS=BTC,ETH,SOL  # ✅ Correct
SUPPORTED_CRYPTOS=btc,eth,sol  # ✅ Also works (auto-converted)
SUPPORTED_CRYPTOS=BTC, ETH, SOL  # ⚠️ Extra spaces (trimmed automatically)
```

### 2. Rate Limit Errors (429)

**Cause:** Too many cryptos or too frequent fetching

**Solution:**
```bash
# Reduce number of cryptos
SUPPORTED_CRYPTOS=BTC,ETH

# Or increase cron interval (every 2 hours instead of hourly)
"schedule": "0 */2 * * *"
```

### 3. Fetch Takes Too Long

**Expected times:**
- 1 crypto: ~4 minutes
- 2 cryptos: ~8 minutes
- 3 cryptos: ~12 minutes

**If slower:**
- Check internet connection
- Verify TAAPI.IO API status
- Review retry mechanism logs

---

## Best Practices

### 1. Start Small
```bash
# Start with 2 cryptos
SUPPORTED_CRYPTOS=BTC,ETH

# Test for a day

# Then add more
SUPPORTED_CRYPTOS=BTC,ETH,SOL
```

### 2. Monitor Usage
```bash
# Check TAAPI.IO usage dashboard
# https://taapi.io/account/usage

# Ensure you're under 50% of daily quota
```

### 3. Stagger Cron Jobs
```bash
# Good (5-10 minute stagger)
BTC: 0 * * * *
ETH: 5 * * * *
SOL: 10 * * * *

# Bad (all at same time - may cause issues)
BTC: 0 * * * *
ETH: 0 * * * *
SOL: 0 * * * *
```

### 4. Data Freshness Checks
```bash
# Before making trades, check data age
python3 check_data_freshness.py --all

# In your trading bot, check age < 2 hours
```

---

## Example: Adding a New Cryptocurrency

### 1. Update Environment Variable

```bash
# In .env
SUPPORTED_CRYPTOS=BTC,ETH,SOL,ADA
```

### 2. Deploy

The `/api/scrape_all` endpoint automatically reads from `SUPPORTED_CRYPTOS` env var, so no vercel.json changes needed!

### 3. Test

```bash
# Test deployed endpoint (fetches ALL enabled cryptos synchronously)
curl "https://your-url.vercel.app/api/scrape_all"

# Check database for new crypto
python3 check_data_freshness.py ADA
```

### 4. Done!

The hourly cron will now automatically fetch all enabled cryptos (BTC, ETH, SOL, ADA) sequentially.

---

## Summary

**Default setup (BTC, ETH, SOL):**
- ✅ 15% of free tier usage
- ✅ Hourly updates via Vercel Cron
- ✅ ~12 minutes total fetch time
- ✅ Automatic database saves
- ✅ Production ready

**To change cryptos:**
1. Update `SUPPORTED_CRYPTOS` in .env
2. Update `vercel.json` crons (optional)
3. Deploy: `vercel --prod`
4. Test: `python3 fetch_all_cryptos.py`

**Monitor usage:**
- Check TAAPI.IO dashboard regularly
- Keep under 50% of daily quota
- Run `check_data_freshness.py` before trading
