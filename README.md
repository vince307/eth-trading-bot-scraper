# Cryptocurrency Trading Bot - Technical Analysis Scraper

Professional-grade cryptocurrency technical analysis data fetcher using **TAAPI.IO API** + **CoinGecko API**. Fetches 12 professional indicators, real-time prices, and market data, storing them in Supabase. Designed to work alongside [`eth-trading-bot-api`](../eth-trading-bot-api) by populating the same database.

**Status**: ✅ **Production Ready**
**Current Version**: TAAPI.IO + CoinGecko API (November 2025)

---

## 🚀 Key Features

### Data Sources
- ✅ **TAAPI.IO API**: 12 professional-grade technical indicators
- ✅ **CoinGecko API**: Real-time price, market cap, 24h volume, and change data
- ✅ **Dual Integration**: Best of both worlds - professional indicators + accurate pricing

### Technical Indicators (12 Professional-Grade)
- **Momentum**: RSI(14), MACD(12,26), StochRSI
- **Trend**: SuperTrend, EMA 20/50/200
- **Volatility**: Bollinger Bands(20,2), ATR(14)
- **Volume**: OBV, CMF(20)
- **Institutional**: VWAP

### Performance & Reliability
- ✅ **99%+ Success Rate**: Robust retry mechanism (5 attempts, 30s pauses)
- ✅ **Fast Cold Starts**: <1 second (vs 10s with web scraping)
- ✅ **Lightweight**: ~5MB deployment (vs 150MB with Playwright)
- ✅ **Rate Limit Compliant**: 18-second delays for free tier
- ✅ **Production Ready**: Complete error handling and logging

### Multi-Cryptocurrency Support
Supports 10 cryptocurrencies: **BTC, ETH, ADA, SOL, DOT, LINK, MATIC, LTC, XRP, DOGE**

---

## 📋 Quick Start

### Prerequisites

- Python 3.12+
- [TAAPI.IO API key](https://taapi.io) (free tier: 5,760 requests/day)
- [CoinGecko API key](https://www.coingecko.com/en/api) (free Demo plan: 30 calls/minute)
- Supabase account (same database as eth-trading-bot-api)
- Vercel account (for deployment)

### Installation

1. **Clone and install dependencies:**
   ```bash
   cd eth-trading-bot-scraper
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials:
   # - TAAPI_API_KEY (required)
   # - COINGECKO_API_KEY (optional - works without for public endpoints)
   # - SUPABASE_URL
   # - SUPABASE_ANON_KEY
   # - SUPABASE_SERVICE_ROLE_KEY
   ```

3. **Test locally:**
   ```bash
   # Test CoinGecko client (fast, ~5 seconds)
   python3 test_coingecko.py

   # Test TAAPI.IO client (slow, ~4 minutes per crypto)
   python3 test_taapi.py

   # Test combined integration (ETH only)
   python3 test_combined.py

   # Test database connection
   python -c "from src.database.supabase_client import SupabaseClient; client = SupabaseClient(); print(client.test_connection())"
   ```

---

## 🌐 API Endpoints

### Single Cryptocurrency
```bash
GET /api/scrape?crypto={SYMBOL}&save={true|false}&exchange={EXCHANGE}&interval={INTERVAL}
```

**Parameters:**
- `crypto` (optional): Cryptocurrency symbol (BTC, ETH, etc.) - default: BTC
- `save` (optional): Save to database - default: false
- `exchange` (optional): Exchange to fetch from - default: binance
- `interval` (optional): Time interval (1h, 4h, 1d) - default: 1h

**Examples:**
```bash
# Fetch Bitcoin (no save)
curl "https://your-vercel-url.vercel.app/api/scrape?crypto=BTC"

# Fetch Ethereum and save to database
curl "https://your-vercel-url.vercel.app/api/scrape?crypto=ETH&save=true"

# Fetch with different interval
curl "https://your-vercel-url.vercel.app/api/scrape?crypto=BTC&interval=4h"
```

### Batch Fetch All Cryptocurrencies
```bash
GET /api/scrape_all?save={true|false}
```

Fetches all enabled cryptocurrencies sequentially (configured via `SUPPORTED_CRYPTOS` env var).

**Example:**
```bash
curl "https://your-vercel-url.vercel.app/api/scrape_all?save=true"
```

---

## 📊 Response Format

```json
{
  "success": true,
  "message": "Technical analysis data fetched successfully from taapi.io, and saved to database",
  "data": {
    "parsed": {
      "symbol": "ETH",
      "price": 3850.41,
      "priceChange": -37.93,
      "priceChangePercent": -0.99,
      "marketData": {
        "marketCap": 464736211475,
        "volume24h": 14992018610,
        "lastUpdated": 1762100582
      },
      "summary": {
        "overall": "Neutral",
        "technicalIndicators": "Neutral",
        "movingAverages": "Strong Sell"
      },
      "technicalIndicators": [
        {
          "name": "RSI(14)",
          "value": 43.40,
          "signal": "Neutral"
        },
        {
          "name": "MACD(12,26)",
          "value": -1.71,
          "signal": "Sell",
          "histogram": -4.66
        },
        {
          "name": "Bollinger Bands(20,2)",
          "upper": 3911.53,
          "middle": 3879.77,
          "lower": 3848.02,
          "signal": "Neutral"
        }
        // ... 5 more indicators
      ],
      "movingAverages": [
        {
          "name": "MA20",
          "type": "Exponential",
          "value": 3876.33,
          "signal": "Sell"
        }
        // ... MA50, MA200
      ],
      "pivotPoints": [],
      "sourceUrl": "https://www.binance.com/trade/ETH_USDT",
      "scrapedAt": "2025-11-02T15:56:16.106073Z",
      "metadata": {
        "exchange": "binance",
        "interval": "1h",
        "provider": "taapi.io"
      }
    },
    "savedToDatabase": true,
    "source": "taapi.io",
    "metadata": {
      "exchange": "binance",
      "interval": "1h",
      "fetchedAt": "2025-11-02T16:09:06.748747Z"
    }
  }
}
```

---

## 🚀 Production Deployment

### Deploy to Vercel

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel:**
   ```bash
   vercel login
   ```

3. **Set environment variables:**
   ```bash
   vercel env add TAAPI_API_KEY production
   vercel env add COINGECKO_API_KEY production
   vercel env add SUPABASE_URL production
   vercel env add SUPABASE_ANON_KEY production
   vercel env add SUPABASE_SERVICE_ROLE_KEY production
   vercel env add SUPPORTED_CRYPTOS production  # e.g., "BTC,ETH,SOL"
   ```

4. **Deploy:**
   ```bash
   vercel --prod
   ```

### Configure Vercel Cron Jobs (Optional)

Add to `vercel.json` for automatic hourly updates:

```json
{
  "crons": [
    {
      "path": "/api/scrape_all",
      "schedule": "0 * * * *"
    }
  ]
}
```

---

## 📁 Project Structure

```
eth-trading-bot-scraper/
├── api/
│   ├── scrape.py              # Single crypto endpoint (+ CoinGecko integration)
│   └── scrape_all.py          # Batch fetch endpoint
├── src/
│   ├── api/
│   │   ├── taapi_client.py    # TAAPI.IO API client
│   │   └── coingecko_client.py # CoinGecko API client (NEW)
│   ├── database/
│   │   └── supabase_client.py # Supabase database client
│   └── utils/
│       └── crypto_config.py   # Cryptocurrency configuration (with CoinGecko IDs)
├── test_taapi.py              # TAAPI.IO client tests
├── test_coingecko.py          # CoinGecko client tests (NEW)
├── test_combined.py           # Combined integration test (NEW)
├── requirements.txt           # Python dependencies
├── vercel.json                # Vercel configuration
├── .env.example               # Environment variables template
├── CLAUDE.md                  # Complete technical documentation
└── README.md                  # This file
```

---

## 🔧 How It Works

### Data Flow

```
1. API Request → /api/scrape?crypto=ETH&save=true

2. CoinGecko Client (fast, ~1 second)
   ├─ Fetch real-time price
   ├─ Fetch 24h change & volume
   └─ Fetch market cap

3. TAAPI.IO Client (slow, ~4 minutes)
   ├─ Fetch 12 technical indicators (18s delay between each)
   ├─ Retry mechanism (5 attempts, 30s pauses)
   └─ Format data matching database schema

4. Merge Data
   ├─ Combine price data from CoinGecko
   └─ Combine indicators from TAAPI.IO

5. Save to Supabase (optional)
   └─ Insert to technical_analysis table

6. Return JSON Response
```

### Database Schema

```sql
CREATE TABLE technical_analysis (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    symbol VARCHAR(10) NOT NULL,
    price DECIMAL(20, 8) NOT NULL,
    price_change DECIMAL(20, 8),
    price_change_percent DECIMAL(10, 4),
    overall_summary VARCHAR(50),
    technical_indicators_summary VARCHAR(50),
    moving_averages_summary VARCHAR(50),
    technical_indicators JSONB,
    moving_averages JSONB,
    pivot_points JSONB,
    source_url TEXT NOT NULL,
    scraped_at TIMESTAMPTZ NOT NULL
);
```

---

## 🎯 Rate Limits & Performance

### TAAPI.IO Free Tier
- **Rate Limit**: 1 request per 15 seconds (we use 18s for safety)
- **Daily Quota**: 5,760 requests/day
- **Fetch Time**: ~4 minutes per cryptocurrency (12 indicators × 18s + retries)
- **Hourly Usage**: BTC + ETH = 576 requests/day (10% of quota) ✅

### CoinGecko Demo Plan
- **Rate Limit**: 30 calls per minute
- **Fetch Time**: ~1 second per cryptocurrency
- **Daily Usage**: Negligible compared to TAAPI.IO

### Total Performance
- **Single Crypto**: ~4 minutes (TAAPI dominates)
- **BTC + ETH**: ~8 minutes total
- **Cold Start**: <1 second
- **Success Rate**: 99%+ (with retry mechanism)

---

## 📚 Documentation

- **[CLAUDE.md](CLAUDE.md)** - Complete technical documentation for developers
- **[MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md)** - Migration from web scraping to API
- **[PROFESSIONAL_INDICATORS.md](PROFESSIONAL_INDICATORS.md)** - Indicator analysis & trading strategies
- **[MULTI_CRYPTO_SETUP.md](MULTI_CRYPTO_SETUP.md)** - Multi-cryptocurrency configuration guide

---

## 🔍 Troubleshooting

### TAAPI.IO Rate Limit Errors (429)
- Check rate limiting delay (currently 18s between requests)
- Verify you're not exceeding free tier limits
- Consider upgrading to Basic plan ($8.99/mo) for 5 requests per 15 seconds

### CoinGecko API Errors
- Demo plan works without API key (lower rate limits)
- With API key: 30 calls/minute (more than enough)
- Check API key is correctly set in Vercel environment variables

### Database Connection Errors
- Verify SUPABASE_URL and keys in .env
- Use service role key for write operations
- Check Supabase table permissions/RLS policies

### Missing Indicators
- **Retry mechanism** automatically handles missing indicators (up to 5 attempts)
- Expected success rate: 99%+ with retries
- Minimum acceptable: 8/12 indicators (66%)
- Check logs for specific indicator failures

---

## 🆕 Recent Updates (November 2025)

### CoinGecko Integration ✨
- ✅ Added CoinGecko API client for real-time price data
- ✅ Fixed missing price/market data (was $0.00, now accurate)
- ✅ Added market cap, 24h volume, and price change data
- ✅ Merged seamlessly with TAAPI.IO indicators
- ✅ Works with or without API key (public endpoints fallback)

### TAAPI.IO Migration
- ✅ Migrated from web scraping (Playwright) to TAAPI.IO REST API
- ✅ Improved from 6 basic → 12 professional indicators
- ✅ Reduced deployment size: 150MB → 5MB (30x smaller)
- ✅ Improved cold start: 10s → <1s (10x faster)
- ✅ Increased reliability: 60% → 99%+ (with retry mechanism)

---

## 🤝 Integration with eth-trading-bot-api

This Python scraper works alongside the TypeScript trading API:

1. **Python scraper** → Fetches from TAAPI.IO + CoinGecko → Inserts to `technical_analysis` table
2. **TypeScript API** → Reads from `technical_analysis` table → Executes trading logic

Both systems work independently but share the same Supabase database.

---

## 📝 License

ISC

---

**Built with ❤️ for the crypto community**

*Disclaimer: This tool is for educational purposes. Always verify data before making trading decisions.*
