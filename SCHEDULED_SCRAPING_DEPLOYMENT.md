# Scheduled Scraping Deployment Guide

This guide explains how to deploy the scheduled scraping architecture to production.

## Architecture Overview

The scheduled scraping solution consists of two separate services:

1. **Scraper Service** (Railway.app) - Runs scheduled scraping with Playwright
2. **API Service** (Vercel) - Serves data from database (read-only)

```
┌─────────────────┐
│  Railway.app    │
│  Scraper        │
│  (Docker +      │
│   Playwright)   │
└────────┬────────┘
         │
         │ Scrapes hourly
         │ Saves to DB
         ▼
┌─────────────────┐
│   Supabase      │
│   Database      │
│   (PostgreSQL)  │
└────────┬────────┘
         │
         │ Reads data
         ▼
┌─────────────────┐
│   Vercel        │
│   API           │
│   (/api/read)   │
└─────────────────┘
```

## Why This Architecture?

**Problem:** Vercel serverless functions don't support Playwright browsers (large binaries, execution environment limitations)

**Solution:** Separate the scraping (heavy, scheduled) from API (lightweight, on-demand)

**Benefits:**
- ✅ Full Playwright support in Railway
- ✅ Scheduled scraping (hourly, customizable)
- ✅ Fast API responses (reads from database)
- ✅ No Vercel deployment errors
- ✅ Lower API costs (no scraping overhead)

## Prerequisites

1. **Supabase Account** - Database for storing scraped data
2. **Railway.app Account** - For deploying scraper service
3. **Vercel Account** - For deploying API service
4. **GitHub Repository** (optional) - For automated deployments

## Part 1: Setup Supabase Database

### 1.1 Create Supabase Project

1. Go to https://app.supabase.com
2. Create new project
3. Wait for database initialization

### 1.2 Create Database Schema

Run this SQL in Supabase SQL Editor:

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

-- Create index on symbol for faster queries
CREATE INDEX IF NOT EXISTS idx_technical_analysis_symbol ON technical_analysis(symbol);

-- Create index on scraped_at for time-based queries
CREATE INDEX IF NOT EXISTS idx_technical_analysis_scraped_at ON technical_analysis(scraped_at DESC);

-- Create composite index for symbol + scraped_at
CREATE INDEX IF NOT EXISTS idx_technical_analysis_symbol_scraped_at ON technical_analysis(symbol, scraped_at DESC);
```

### 1.3 Get Supabase Credentials

1. Go to Project Settings → API
2. Copy these values:
   - `Project URL` → `SUPABASE_URL`
   - `anon public` key → `SUPABASE_ANON_KEY`
   - `service_role` key → `SUPABASE_SERVICE_ROLE_KEY`

⚠️ **Important:** Keep `service_role` key secret! It bypasses Row Level Security.

## Part 2: Deploy Scraper Service to Railway.app

### 2.1 Create Railway Project

1. Go to https://railway.app
2. Click "New Project"
3. Choose deployment method:
   - **Option A: Deploy from GitHub** (recommended)
     - Connect GitHub repository
     - Railway auto-detects Dockerfile
   - **Option B: Deploy from CLI**
     - Install Railway CLI: `npm i -g @railway/cli`
     - Login: `railway login`
     - Initialize: `railway init`
     - Deploy: `railway up`

### 2.2 Configure Environment Variables

In Railway dashboard → Variables tab, add:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SCRAPER_INTERVAL_MINUTES=60
SCRAPER_CRYPTOS=
```

**Environment Variable Details:**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SUPABASE_URL` | ✅ Yes | - | Supabase project URL |
| `SUPABASE_ANON_KEY` | ✅ Yes | - | Supabase anon key |
| `SUPABASE_SERVICE_ROLE_KEY` | ✅ Yes | - | Supabase service role key (for writes) |
| `SCRAPER_INTERVAL_MINUTES` | ❌ No | `60` | Scraping interval in minutes |
| `SCRAPER_CRYPTOS` | ❌ No | (all) | Comma-separated crypto symbols to scrape |

**Examples:**

```bash
# Scrape all cryptocurrencies every hour (default)
SCRAPER_INTERVAL_MINUTES=60
SCRAPER_CRYPTOS=

# Scrape only BTC and ETH every 30 minutes
SCRAPER_INTERVAL_MINUTES=30
SCRAPER_CRYPTOS=BTC,ETH

# Scrape only Bitcoin every 15 minutes
SCRAPER_INTERVAL_MINUTES=15
SCRAPER_CRYPTOS=BTC
```

### 2.3 Deploy and Monitor

1. Railway will automatically build Docker image
2. Check build logs for errors
3. Monitor scraper logs:
   ```
   Starting scheduled scraper (interval: 60 minutes)
   Running initial scrape...
   Scraping BTC...
   ✓ Successfully saved BTC to database
   ```

### 2.4 Verify Scraper is Working

Check Supabase database:

```sql
-- Check latest scraped data
SELECT symbol, price, scraped_at
FROM technical_analysis
ORDER BY scraped_at DESC
LIMIT 10;

-- Count records per cryptocurrency
SELECT symbol, COUNT(*) as records
FROM technical_analysis
GROUP BY symbol
ORDER BY symbol;
```

## Part 3: Deploy API Service to Vercel

### 3.1 Install Vercel CLI

```bash
npm i -g vercel
```

### 3.2 Configure Environment Variables

Create `.env.production` file:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

Or configure in Vercel dashboard:

1. Go to Vercel project settings
2. Navigate to Environment Variables
3. Add the three Supabase variables

### 3.3 Deploy to Vercel

```bash
# Login to Vercel
vercel login

# Deploy to production
vercel --prod
```

### 3.4 Test API Endpoints

Once deployed, test the read endpoint:

```bash
# Get latest data for all cryptocurrencies
curl https://your-app.vercel.app/api/read

# Get latest data for Bitcoin
curl https://your-app.vercel.app/api/read?crypto=BTC

# Get last 5 Bitcoin records
curl https://your-app.vercel.app/api/read?crypto=BTC&limit=5

# Get last 10 records for all cryptocurrencies
curl https://your-app.vercel.app/api/read?limit=10
```

**Expected Response:**

```json
{
  "success": true,
  "message": "Retrieved 1 record(s)",
  "data": [
    {
      "id": "...",
      "symbol": "BTC",
      "price": 34250.50,
      "price_change": 1250.30,
      "price_change_percent": 3.79,
      "overall_summary": "Strong Buy",
      "technical_indicators": [...],
      "moving_averages": [...],
      "pivot_points": [...],
      "scraped_at": "2025-01-26T10:00:00.000Z"
    }
  ],
  "count": 1
}
```

## Part 4: Local Development & Testing

### 4.1 Local Development Setup

```bash
# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Copy environment file
cp .env.scraper.example .env

# Edit .env with your credentials
nano .env
```

### 4.2 Test Scraper Locally

```bash
# Run one-time scrape (test)
python scraper_cron.py --once

# Run scheduled scraper
python scraper_cron.py
```

### 4.3 Test with Docker Locally

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### 4.4 Test API Locally

```bash
# Install Vercel CLI
npm i -g vercel

# Run dev server
vercel dev

# Test endpoint
curl http://localhost:3000/api/read?crypto=BTC
```

## Part 5: Monitoring & Troubleshooting

### 5.1 Monitor Scraper Service (Railway)

**Check Logs:**
1. Go to Railway dashboard
2. Click on your service
3. View logs in real-time

**What to look for:**
```
✓ Successfully saved BTC to database
✓ Successfully saved ETH to database
Scrape completed: 10 successful, 0 failed
```

**Common Issues:**

| Error | Cause | Fix |
|-------|-------|-----|
| `Connection refused` | Supabase credentials wrong | Check environment variables |
| `Playwright timeout` | Website slow/blocked | Increase timeout in code |
| `No data scraped` | Website structure changed | Update parser patterns |

### 5.2 Monitor API Service (Vercel)

**Check Logs:**
```bash
vercel logs
```

**Test Health:**
```bash
curl https://your-app.vercel.app/api/read
```

### 5.3 Monitor Database (Supabase)

**Check Data Freshness:**
```sql
-- Get latest scrape time per cryptocurrency
SELECT
    symbol,
    MAX(scraped_at) as last_scraped,
    NOW() - MAX(scraped_at) as time_since_last_scrape
FROM technical_analysis
GROUP BY symbol
ORDER BY symbol;
```

**Check Scraping Consistency:**
```sql
-- Count scrapes per hour
SELECT
    symbol,
    DATE_TRUNC('hour', scraped_at) as hour,
    COUNT(*) as scrapes
FROM technical_analysis
WHERE scraped_at > NOW() - INTERVAL '24 hours'
GROUP BY symbol, hour
ORDER BY hour DESC, symbol;
```

## Part 6: Production Best Practices

### 6.1 Database Cleanup

Old data can accumulate. Set up cleanup:

```sql
-- Delete records older than 30 days
DELETE FROM technical_analysis
WHERE scraped_at < NOW() - INTERVAL '30 days';
```

Create scheduled cleanup (Supabase SQL Editor):

```sql
-- Create cleanup function
CREATE OR REPLACE FUNCTION cleanup_old_technical_analysis()
RETURNS void AS $$
BEGIN
    DELETE FROM technical_analysis
    WHERE scraped_at < NOW() - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql;

-- Schedule with pg_cron (if available)
-- Or run manually/via external cron
```

### 6.2 Error Alerting

**Railway:** Set up notifications in Railway dashboard for service failures

**Vercel:** Configure error alerting in Vercel dashboard

**Supabase:** Monitor database health in Supabase dashboard

### 6.3 Scaling Considerations

**Increase Scraping Frequency:**
```bash
# Scrape every 15 minutes instead of 60
SCRAPER_INTERVAL_MINUTES=15
```

**Reduce Cryptocurrencies:**
```bash
# Only scrape most important coins
SCRAPER_CRYPTOS=BTC,ETH,ADA,SOL
```

**Database Performance:**
- Indexes already created on `symbol` and `scraped_at`
- Consider partitioning table if data grows large
- Monitor query performance in Supabase

## Part 7: Cost Estimates

### Railway.app
- **Starter Plan:** $5/month (500 hours execution)
- **Hobby Plan:** $20/month (unlimited hours)
- **Estimate:** ~$5-10/month for 24/7 scraper

### Vercel
- **Hobby Plan:** Free (100GB bandwidth, 100GB-hrs compute)
- **Pro Plan:** $20/month (1TB bandwidth, 1000GB-hrs compute)
- **Estimate:** Free tier sufficient for read-only API

### Supabase
- **Free Plan:** 500MB database, 2GB bandwidth
- **Pro Plan:** $25/month (8GB database, 50GB bandwidth)
- **Estimate:** Free tier sufficient for testing, Pro for production

**Total Estimated Cost:** $5-10/month (minimal usage) to $45-55/month (heavy usage)

## Support & Troubleshooting

### Getting Help

1. **Railway Issues:** https://railway.app/help
2. **Vercel Issues:** https://vercel.com/support
3. **Supabase Issues:** https://supabase.com/docs

### Common Questions

**Q: Can I use a different database instead of Supabase?**
A: Yes, modify `src/database/supabase_client.py` to use PostgreSQL, MongoDB, etc.

**Q: Can I deploy scraper to a different platform?**
A: Yes, any platform that supports Docker (Render, Fly.io, AWS ECS, etc.)

**Q: Can I run scraper on my own server?**
A: Yes, use `docker-compose up -d` on any server with Docker installed

**Q: How do I add more cryptocurrencies?**
A: Edit `src/utils/crypto_config.py` to add new symbols and URLs

**Q: Can I scrape more frequently than every hour?**
A: Yes, set `SCRAPER_INTERVAL_MINUTES=15` (or any value)

---

## Quick Start Checklist

- [ ] Create Supabase project and database schema
- [ ] Get Supabase credentials (URL, anon key, service role key)
- [ ] Create Railway.app project
- [ ] Configure Railway environment variables
- [ ] Deploy scraper to Railway
- [ ] Verify scraper is running (check logs)
- [ ] Check Supabase database for scraped data
- [ ] Create Vercel project
- [ ] Configure Vercel environment variables
- [ ] Deploy API to Vercel
- [ ] Test API endpoint
- [ ] Set up monitoring and alerts
- [ ] Configure database cleanup (optional)

**Estimated Setup Time:** 30-45 minutes

---

## Next Steps

Once deployed, you can:

1. Integrate the API with your trading bot (`eth-trading-bot-api`)
2. Build a dashboard to visualize technical analysis data
3. Add webhooks for real-time alerts
4. Extend to support more cryptocurrencies
5. Add custom technical indicators

Happy trading! 🚀
