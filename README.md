# Cryptocurrency Trading Bot - Technical Analysis Scraper

Professional-grade cryptocurrency technical analysis data fetcher using **CoinGecko API** + local indicator calculation. Fetches 12+ professional indicators, real-time prices, and market data, storing them in Supabase. Designed to work alongside [`eth-trading-bot-api`](../eth-trading-bot-api) by populating the same database.

**Status**: ✅ **Production Ready**
**Current Version**: CoinGecko + Local Calculation (November 2025)

---

## 🚀 Key Features

### Data Sources
- ✅ **CoinGecko API**: Real-time price, market cap, 24h volume, change data, and OHLC candlesticks
- ✅ **Local Calculation**: Professional-grade technical indicators calculated using `ta` library
- ✅ **Fast & Reliable**: ~2-3 seconds per crypto (vs 4 minutes with TAAPI.IO)

### Technical Indicators (12+ Professional-Grade)
- **Momentum**: RSI(14), MACD(12,26), StochRSI
- **Trend**: SuperTrend, EMA 20/50/200
- **Volatility**: Bollinger Bands(20,2), ATR(14)
- **Volume**: OBV, CMF(20)
- **Institutional**: VWAP

### Performance & Reliability
- ✅ **Lightning Fast**: ~2-3 seconds per crypto (vs 4 minutes with external APIs)
- ✅ **Fast Cold Starts**: <1 second
- ✅ **Lightweight**: ~5MB deployment (no browser dependencies)
- ✅ **No Rate Limiting**: Immediate responses, no delays
- ✅ **Production Ready**: Complete error handling and logging

### Multi-Cryptocurrency Support
Supports 10 cryptocurrencies: **BTC, ETH, ADA, SOL, DOT, LINK, MATIC, LTC, XRP, DOGE**

---

## 📋 Quick Start

### Prerequisites

- Python 3.12+
- [CoinGecko API key](https://www.coingecko.com/en/api) (optional - works without for public endpoints)
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
   # - COINGECKO_API_KEY (optional - works without for public endpoints)
   # - SUPABASE_URL
   # - SUPABASE_ANON_KEY
   # - SUPABASE_SERVICE_ROLE_KEY
   ```

3. **Test locally:**
   ```bash
   # Test CoinGecko client
   python3 test_coingecko.py

   # Test database connection
   python -c "from src.database.supabase_client import SupabaseClient; client = SupabaseClient(); print(client.test_connection())"

   # Test API locally (requires Vercel CLI)
   vercel dev
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
- `exchange` (optional): Exchange name (for metadata) - default: binance
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

---

## 📊 Response Format

```json
{
  "success": true,
  "message": "Technical analysis data fetched successfully from coingecko+pandas-ta, and saved to database",
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
        // ... 9+ more indicators
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
      "sourceUrl": "https://www.coingecko.com/en/coins/ethereum",
      "scrapedAt": "2025-11-02T15:56:16.106073Z",
      "metadata": {
        "exchange": "binance",
        "interval": "1h",
        "provider": "coingecko+pandas-ta"
      }
    },
    "savedToDatabase": true,
    "source": "coingecko+pandas-ta",
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
   vercel env add COINGECKO_API_KEY production  # Optional
   vercel env add SUPABASE_URL production
   vercel env add SUPABASE_ANON_KEY production
   vercel env add SUPABASE_SERVICE_ROLE_KEY production
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

---

## 📁 Project Structure

```
eth-trading-bot-scraper/
├── api/
│   ├── scrape.py                # Single crypto endpoint
│   └── read.py                  # Read endpoint (for testing)
├── src/
│   ├── api/
│   │   ├── coingecko_client.py  # CoinGecko API client
│   │   └── indicators_calculator.py # Technical indicators calculator
│   ├── database/
│   │   └── supabase_client.py   # Supabase database client
│   └── utils/
│       └── crypto_config.py     # Cryptocurrency configuration
├── test_coingecko.py            # CoinGecko client tests
├── requirements.txt             # Python dependencies
├── vercel.json                  # Vercel configuration
├── .env.example                 # Environment variables template
├── CLAUDE.md                    # Complete technical documentation
└── README.md                    # This file
```

---

## 🔧 How It Works

### Data Flow

```
1. API Request → /api/scrape?crypto=ETH&save=true

2. CoinGecko Client (~1 second)
   ├─ Fetch real-time price
   ├─ Fetch 24h change, market cap, volume
   └─ Fetch OHLC candlestick data (365 days)

3. Indicators Calculator (<1 second)
   ├─ Calculate RSI, MACD, Bollinger Bands
   ├─ Calculate StochRSI, ATR, SuperTrend
   ├─ Calculate OBV, CMF, VWAP
   └─ Calculate EMA 20/50/200

4. Data Merging
   ├─ Combine price data with indicators
   ├─ Calculate summary signals
   └─ Format data matching database schema

5. Save to Supabase (optional)
   └─ Insert to technical_analysis table

6. Return JSON Response (~2-3 seconds total)
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

### CoinGecko Demo Plan (Free)
- **Rate Limit**: 30 calls per minute
- **Usage**: 2 calls per crypto (price + OHLC)
- **Max**: 15 cryptos per minute
- **Fetch Time**: ~1-2 seconds per cryptocurrency

### Local Calculation
- **Processing Time**: <1 second
- **No external dependencies**: All calculated locally
- **No rate limits**: Process as many as you want

### Total Performance
- **Single Crypto**: ~2-3 seconds total
- **10 Cryptos**: ~25-30 seconds total (if sequential)
- **Cold Start**: <1 second
- **Success Rate**: 99%+ (depends on CoinGecko availability)

---

## 📚 Documentation

- **[CLAUDE.md](CLAUDE.md)** - Complete technical documentation for developers

---

## 🔍 Troubleshooting

### CoinGecko API Errors (429)
- Demo plan: 30 calls/minute (2 calls per crypto = 15 cryptos/minute max)
- Works without API key (lower rate limits)
- With API key: Higher rate limits
- Consider upgrading to Pro plan for production use

### Database Connection Errors
- Verify SUPABASE_URL and keys in .env
- Use service role key for write operations
- Check Supabase table permissions/RLS policies

### Missing Indicators
- Check OHLC data availability (need enough candles)
- Minimum: 200 candles for MA200
- Some cryptos may have limited history on CoinGecko

---

## 🆕 Recent Updates (November 2025)

### Current Architecture (CoinGecko + Local Calculation)
- ✅ Fetch OHLC data from CoinGecko
- ✅ Calculate all indicators locally using `ta` library
- ✅ Fast: ~2-3 seconds per crypto (vs 4 minutes with TAAPI.IO)
- ✅ Lightweight: ~5MB deployment
- ✅ No rate limiting delays
- ✅ No external API dependencies for indicators

### Why Local Calculation?
- **60x faster**: 2-3 seconds vs 4 minutes (TAAPI.IO)
- **No delays**: Immediate response (no 18-second rate limiting)
- **Cost-effective**: Only uses CoinGecko (free tier sufficient)
- **Scalable**: Can process multiple cryptos quickly
- **Reliable**: No dependency on multiple external services

---

## 🤝 Integration with eth-trading-bot-api

This Python scraper works alongside the TypeScript trading API:

1. **Python scraper** → Fetches from CoinGecko → Calculates indicators → Inserts to `technical_analysis` table
2. **TypeScript API** → Reads from `technical_analysis` table → Executes trading logic

Both systems work independently but share the same Supabase database.

---

## 📝 License

ISC

---

**Built with ❤️ for the crypto community**

*Disclaimer: This tool is for educational purposes. Always verify data before making trading decisions.*
