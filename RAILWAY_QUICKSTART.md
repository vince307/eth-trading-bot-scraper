# Railway Quick Start Guide

Deploy your crypto scraper to Railway.app in **10 minutes**. This guide gets you from zero to production quickly.

## Prerequisites

- [Railway.app account](https://railway.app) (sign up with GitHub)
- [Supabase project](https://supabase.com) with database schema created
- GitHub repository (optional, but recommended)

## Step 1: Prepare Supabase Database (5 minutes)

### 1.1 Create Supabase Project

1. Go to https://app.supabase.com
2. Click "New Project"
3. Choose organization, name your project
4. Wait for database initialization (~2 minutes)

### 1.2 Run Database Schema

1. In Supabase dashboard, click **SQL Editor**
2. Click "New Query"
3. Copy and paste this SQL:

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create technical_analysis table
CREATE TABLE IF NOT EXISTS technical_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(10) NOT NULL,
    price DECIMAL(20, 8),
    price_change DECIMAL(20, 8),
    price_change_percent DECIMAL(10, 4),
    overall_summary VARCHAR(50),
    technical_indicators_summary VARCHAR(50),
    moving_averages_summary VARCHAR(50),
    technical_indicators JSONB,
    moving_averages JSONB,
    pivot_points JSONB,
    source_url TEXT,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_technical_analysis_symbol ON technical_analysis(symbol);
CREATE INDEX IF NOT EXISTS idx_technical_analysis_scraped_at ON technical_analysis(scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_technical_analysis_symbol_scraped_at ON technical_analysis(symbol, scraped_at DESC);
```

4. Click "Run" (bottom right)
5. Verify: You should see "Success. No rows returned"

### 1.3 Get API Credentials

1. Go to **Project Settings** → **API**
2. Copy these three values (you'll need them in Step 2):
   - **Project URL** → `SUPABASE_URL`
   - **anon public** key → `SUPABASE_ANON_KEY`
   - **service_role** key (click "Reveal") → `SUPABASE_SERVICE_ROLE_KEY`

⚠️ **Keep service_role key secret!** It has full database access.

## Step 2: Deploy to Railway (5 minutes)

### 2.1 Create Railway Project

**Option A: Deploy from GitHub (Recommended)**

1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Authorize Railway to access GitHub
4. Select your `eth-trading-bot-scraper` repository
5. Click "Deploy Now"

Railway will automatically:
- Detect the `Dockerfile`
- Build Docker image
- Start the container

**Option B: Deploy from CLI**

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project (in your repo directory)
railway init

# Deploy
railway up
```

### 2.2 Configure Environment Variables

1. In Railway dashboard, click on your deployed service
2. Go to **Variables** tab
3. Click "Raw Editor" (easier for bulk paste)
4. Paste this (replace with your Supabase values):

```bash
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
SCRAPER_INTERVAL_MINUTES=60
SCRAPER_CRYPTOS=BTC,ETH
```

5. Click "Update Variables"

**Environment Variables Explained:**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SUPABASE_URL` | ✅ Yes | - | Your Supabase project URL |
| `SUPABASE_ANON_KEY` | ✅ Yes | - | Public API key |
| `SUPABASE_SERVICE_ROLE_KEY` | ✅ Yes | - | Private key for database writes |
| `SCRAPER_INTERVAL_MINUTES` | ❌ No | `60` | How often to scrape (in minutes) |
| `SCRAPER_CRYPTOS` | ❌ No | `BTC,ETH` | Comma-separated crypto symbols |

### 2.3 Verify Deployment

1. Railway will automatically redeploy with new environment variables
2. Check **Logs** tab in Railway dashboard
3. Look for these success messages:

```
Starting scheduled scraper (interval: 60 minutes)
Running initial scrape...
Scraping BTC...
✓ Successfully saved BTC to database
Scraping ETH...
✓ Successfully saved ETH to database
Scrape completed: 2 successful, 0 failed
```

If you see errors, check:
- Environment variables are correct (no typos)
- Supabase credentials are valid
- Database schema was created successfully

## Step 3: Verify Data in Supabase (2 minutes)

1. Go back to Supabase dashboard
2. Click **Table Editor** → **technical_analysis**
3. You should see rows of scraped data with BTC, ETH, etc.

Or run this SQL query:

```sql
-- Check latest scraped data
SELECT symbol, price, price_change_percent, overall_summary, scraped_at
FROM technical_analysis
ORDER BY scraped_at DESC
LIMIT 10;
```

You should see recent data (within the last few minutes).

## Step 4: Deploy Vercel API (3 minutes)

Now deploy the read-only API to Vercel:

```bash
# Install Vercel CLI (if not already installed)
npm i -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

When prompted, configure environment variables (same Supabase credentials):

```bash
vercel env add SUPABASE_URL
# Paste your Supabase URL

vercel env add SUPABASE_ANON_KEY
# Paste your anon key

vercel env add SUPABASE_SERVICE_ROLE_KEY
# Paste your service role key
```

### Test API Endpoint

```bash
# Replace with your Vercel URL
curl "https://your-app.vercel.app/api/read?crypto=BTC"
```

Expected response:

```json
{
  "success": true,
  "message": "Retrieved 1 record(s)",
  "data": [
    {
      "symbol": "BTC",
      "price": 98750.00,
      "overall_summary": "Strong Buy",
      ...
    }
  ]
}
```

## You're Done! 🎉

Your crypto scraper is now running on Railway and scraping data every hour.

### What's Happening Now?

1. **Railway scraper** runs every 60 minutes, scraping BTC and ETH and saving to Supabase
2. **Vercel API** serves data from Supabase via `/api/read` endpoint
3. **Supabase** stores all historical technical analysis data

### Architecture Summary

```
Railway (Scraper)  →  Supabase (Database)  ←  Vercel (API)
   Every 60 min          PostgreSQL            On-demand reads
```

## Next Steps

### Monitor Your Scraper

**Railway Dashboard:**
- **Logs**: View real-time scraper output
- **Metrics**: Monitor CPU, memory usage
- **Usage**: Track costs (should be ~$3-5/month)

**Check Logs:**
1. Go to Railway dashboard
2. Click your service
3. Click **Logs** tab
4. Watch for scrape completion messages every hour

### Optimize Costs

**Scrape Less Frequently:**
```bash
# Scrape every 2 hours (50% cost reduction)
SCRAPER_INTERVAL_MINUTES=120

# Scrape every 4 hours (75% cost reduction)
SCRAPER_INTERVAL_MINUTES=240
```

**Scrape More Cryptos:**
```bash
# Add more cryptocurrencies (supported: BTC,ETH,ADA,SOL,DOT,LINK,MATIC,LTC,XRP,DOGE)
SCRAPER_CRYPTOS=BTC,ETH,ADA,SOL

# Or scrape all supported cryptocurrencies
SCRAPER_CRYPTOS=
```

Update variables in Railway dashboard → Variables tab → Update → Railway auto-redeploys

### Set Up Alerts

**Railway Notifications:**
1. Go to Railway Account Settings
2. Enable email notifications for:
   - Deployment failures
   - Service crashes
   - Budget alerts

**Supabase Monitoring:**
1. Supabase dashboard → Settings → Database
2. Monitor table size, query performance

### Add More Cryptocurrencies

To add support for more cryptocurrencies:

1. Check if supported in `src/utils/crypto_config.py`
2. If not listed, add to `SUPPORTED_CRYPTOS` dict
3. Deploy changes to Railway (auto-deploys from GitHub)

Currently configured to scrape: **BTC and ETH** (default)

All supported: BTC, ETH, ADA, SOL, DOT, LINK, MATIC, LTC, XRP, DOGE

## Troubleshooting

### Problem: No data in Supabase

**Solution:**
1. Check Railway logs for errors
2. Verify Supabase credentials in Railway variables
3. Ensure database schema was created
4. Check Supabase RLS policies (should be disabled for service role key)

### Problem: Railway scraper keeps crashing

**Solution:**
1. Check Railway logs for specific error
2. Common issues:
   - Invalid Supabase credentials → Update variables
   - Playwright timeout → Increase timeout in code
   - Memory limit → Increase Railway memory allocation

### Problem: High Railway costs

**Solution:**
1. Check Railway Usage tab for breakdown
2. Reduce scraping frequency: `SCRAPER_INTERVAL_MINUTES=120`
3. Scrape fewer cryptos: `SCRAPER_CRYPTOS=BTC,ETH`
4. Expected cost: $3-5/month on Hobby plan ($5/month includes $5 credits)

### Problem: API returns old data

**Solution:**
1. Check Railway logs - is scraper running?
2. Verify last scraped time in Supabase:
   ```sql
   SELECT symbol, MAX(scraped_at) as last_scraped
   FROM technical_analysis
   GROUP BY symbol;
   ```
3. If scraper is running but not saving, check service role key

## Useful Commands

### Railway CLI

```bash
# View logs
railway logs

# Restart service
railway restart

# Check variables
railway variables

# Open dashboard
railway open
```

### Vercel CLI

```bash
# View logs
vercel logs

# View deployments
vercel ls

# View environment variables
vercel env ls
```

### Supabase SQL Queries

```sql
-- Count records per crypto
SELECT symbol, COUNT(*) as records
FROM technical_analysis
GROUP BY symbol
ORDER BY symbol;

-- Get latest price for each crypto
SELECT DISTINCT ON (symbol)
    symbol, price, price_change_percent, overall_summary, scraped_at
FROM technical_analysis
ORDER BY symbol, scraped_at DESC;

-- Delete old data (older than 30 days)
DELETE FROM technical_analysis
WHERE scraped_at < NOW() - INTERVAL '30 days';
```

## Cost Breakdown

| Service | Plan | Cost | Purpose |
|---------|------|------|---------|
| **Railway** | Hobby | **$5/month** | Scraper service (includes $5 credits) |
| **Vercel** | Hobby | **$0/month** | API service (free tier) |
| **Supabase** | Free/Pro | **$0-25/month** | Database |
| **Total** | - | **$5-30/month** | Complete infrastructure |

Expected Railway usage: $2.90-$4.52/month (fits within $5 included credits)

## Support

- **Railway Docs**: https://docs.railway.com
- **Railway Discord**: https://discord.gg/railway
- **This Project**: See `SCHEDULED_SCRAPING_DEPLOYMENT.md` for detailed guide

---

**That's it!** You now have a production-ready crypto scraper running on Railway. 🚀

The scraper will continuously monitor **Bitcoin and Ethereum** every hour and keep your database updated with the latest technical analysis data. You can easily add more cryptocurrencies by updating the `SCRAPER_CRYPTOS` environment variable in Railway.
