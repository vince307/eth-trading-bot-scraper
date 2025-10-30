# Crypto Trading Bot Scraper

Python web scraping application that scrapes cryptocurrency technical analysis data from investing.com and stores it in Supabase. Supports **10 cryptocurrencies** including Bitcoin, Ethereum, and more. Designed to work alongside [`eth-trading-bot-api`](../eth-trading-bot-api) by populating the same database.

## Features

- 🪙 **Multi-Cryptocurrency Support**: 10 cryptocurrencies supported (default: BTC & ETH)
- ⏰ **Scheduled Scraping**: Runs on Railway.app with configurable intervals (default: hourly)
- 🎯 **Technical Analysis Scraping**: Extracts 12+ indicators, moving averages, and pivot points
- 💾 **Database Integration**: Inserts to Supabase `technical_analysis` table
- 🔄 **Data Parity**: Matches TypeScript API data structures exactly
- 🎭 **Playwright Automation**: Handles JavaScript-rendered content with full browser support
- 📊 **Comprehensive Parsing**: RSI, MACD, Stochastic, ADX, MA5-MA200, Pivot Points
- 🚀 **Fast API**: Vercel serverless endpoint for instant database reads
- 💰 **Cost Efficient**: ~$5/month on Railway Hobby plan
- 🔧 **Extensible**: Easy to add new cryptocurrencies

## Quick Start

### Prerequisites

- Python 3.12+
- Supabase account (same database as eth-trading-bot-api)
- Railway.app account (for scraper service)
- Vercel account (for API deployment)

### Installation

1. **Clone and install dependencies:**
   ```bash
   cd eth-trading-bot-scraper
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase credentials
   ```

3. **Test locally:**
   ```bash
   # Test scraping Bitcoin (without database)
   python -c "from src.scrapers.investing_scraper import scrape_crypto_technical; print(scrape_crypto_technical(crypto='BTC'))"

   # Test scraping Ethereum
   python -c "from src.scrapers.investing_scraper import scrape_crypto_technical; print(scrape_crypto_technical(crypto='ETH'))"

   # Test database connection
   python -c "from src.database.supabase_client import SupabaseClient; client = SupabaseClient(); print(client.test_connection())"
   ```

### Production Deployment

This project uses a **scheduled scraping architecture** with two separate services:

1. **Scraper Service** (Railway.app) - Runs scheduled scraping with Playwright
2. **API Service** (Vercel) - Serves data from database (read-only)

#### 🚀 Quick Start (10 minutes)

📚 **[RAILWAY_QUICKSTART.md](./RAILWAY_QUICKSTART.md)** - Deploy in 10 minutes with step-by-step guide

📖 **[SCHEDULED_SCRAPING_DEPLOYMENT.md](./SCHEDULED_SCRAPING_DEPLOYMENT.md)** - Complete detailed deployment guide

#### Deploy Scraper to Railway.app

**Option 1: Deploy from GitHub (Recommended)**

1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select your repository
4. Add environment variables (Supabase credentials)
5. Deploy automatically

**Option 2: Deploy from CLI**

```bash
npm i -g @railway/cli
railway login
railway init
railway up
```

**Configure Environment Variables in Railway:**

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SCRAPER_INTERVAL_MINUTES=60
SCRAPER_CRYPTOS=BTC,ETH
```

> **Default:** Scrapes BTC and ETH. Leave `SCRAPER_CRYPTOS` empty to scrape all 10 supported cryptocurrencies.

#### Deploy API to Vercel

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel:**
   ```bash
   vercel login
   ```

3. **Set environment variables in Vercel:**
   ```bash
   vercel env add SUPABASE_URL
   vercel env add SUPABASE_ANON_KEY
   vercel env add SUPABASE_SERVICE_ROLE_KEY
   ```

4. **Deploy:**
   ```bash
   vercel --prod
   ```

## API Endpoints

### Read Endpoint (Recommended)

**Database-only read endpoint** - Fast, no scraping overhead:

```
GET https://your-project.vercel.app/api/read
```

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `crypto` | string | - | Cryptocurrency symbol (BTC, ETH, etc.) - optional, returns all if omitted |
| `limit` | number | `1` | Number of records to return |

#### Example Requests

**Get latest Bitcoin data:**
```bash
curl "https://your-project.vercel.app/api/read?crypto=BTC"
```

**Get last 5 Ethereum records:**
```bash
curl "https://your-project.vercel.app/api/read?crypto=ETH&limit=5"
```

**Get latest data for all cryptocurrencies:**
```bash
curl "https://your-project.vercel.app/api/read?limit=10"
```

### Scrape Endpoint (Legacy)

**Direct scraping endpoint** - Use only for testing/development:

```
GET https://your-project.vercel.app/api/scrape
```

⚠️ **Note:** This endpoint is limited by Vercel's serverless environment. Use the read endpoint in production.

### Response Format

```json
{
  "success": true,
  "message": "Technical analysis data fetched and parsed successfully, and saved to database",
  "data": {
    "raw": {
      "url": "https://www.investing.com/crypto/ethereum/technical",
      "title": "Ethereum Technical Analysis",
      "content": "...",
      "contentLength": 50000,
      "scrapedAt": "2025-10-08T12:00:00.000Z"
    },
    "parsed": {
      "symbol": "BTC",
      "price": 98750.00,
      "priceChange": 1250.50,
      "priceChangePercent": 1.28,
      "summary": {
        "overall": "Strong Buy",
        "technicalIndicators": "Buy",
        "movingAverages": "Neutral"
      },
      "technicalIndicators": [
        {
          "name": "RSI(14)",
          "value": 57.18,
          "action": "Buy",
          "rawValue": "| RSI(14) | 57.18 | Buy |"
        }
      ],
      "movingAverages": [
        {
          "period": 5,
          "simple": { "value": 4488.29, "action": "Buy" },
          "exponential": { "value": 4488.00, "action": "Buy" }
        }
      ],
      "pivotPoints": [
        {
          "name": "Classic",
          "s3": 4475.91,
          "s2": 4480.11,
          "s1": 4488.52,
          "pivot": 4492.72,
          "r1": 4501.13,
          "r2": 4505.33,
          "r3": 4513.74
        }
      ],
      "scrapedAt": "2025-10-08T12:00:00.000Z",
      "sourceUrl": "https://www.investing.com/crypto/ethereum/technical"
    },
    "savedToDatabase": true
  }
}
```

## Project Structure

```
eth-trading-bot-scraper/
├── api/
│   └── scrape.py                    # Vercel serverless function
├── src/
│   ├── scrapers/
│   │   ├── base_scraper.py          # Base scraper with Playwright
│   │   ├── investing_scraper.py     # Investing.com scraper (multi-crypto)
│   │   └── simple_scraper.py        # HTTP scraper (Vercel-compatible)
│   ├── parsers/
│   │   └── technical_analysis_parser.py  # Python port of TS parser
│   ├── database/
│   │   └── supabase_client.py       # Supabase database client
│   └── utils/
│       ├── crypto_config.py         # Cryptocurrency configuration (NEW)
│       └── helpers.py               # Utility functions
├── requirements.txt                 # Python dependencies
├── vercel.json                      # Vercel configuration
├── .env.example                     # Environment variables template
├── package.json                     # NPM scripts for Playwright
├── CLAUDE.md                        # Developer guide
├── MULTI_CRYPTO_UPGRADE.md          # Multi-crypto upgrade documentation
└── README.md                        # This file
```

## How It Works

### 1. Scraping Flow

```
Vercel Function (api/scrape.py)
    ↓
InvestingScraper (src/scrapers/investing_scraper.py)
    ↓ [Playwright browser automation]
investing.com technical page
    ↓ [HTML → Markdown conversion]
TechnicalAnalysisParser (src/parsers/technical_analysis_parser.py)
    ↓ [Regex extraction & parsing]
Structured JSON data
    ↓ [Optional: save to database]
SupabaseClient (src/database/supabase_client.py)
    ↓
Supabase technical_analysis table
```

### 2. Data Extraction

The parser extracts:

**Technical Indicators (12+):**
- RSI(14), STOCH(9,6), STOCHRSI(14)
- MACD(12,26), ADX(14), Williams %R
- CCI(14), ATR(14), Ultimate Oscillator
- ROC, Bull/Bear Power(13), Highs/Lows(14)

**Moving Averages (6 periods):**
- MA5, MA10, MA20, MA50, MA100, MA200
- Both Simple (SMA) and Exponential (EMA)
- Action: Buy, Sell, or Neutral

**Pivot Points (4 types):**
- Classic, Fibonacci, Camarilla, Woodie's
- Support levels: S1, S2, S3
- Resistance levels: R1, R2, R3

**Summary Data:**
- Overall market sentiment
- Technical indicators summary
- Moving averages summary
- Buy/Sell/Neutral counts

### 3. Database Integration

Inserts to Supabase `technical_analysis` table:

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

## Supported Cryptocurrencies

Currently supports **10 cryptocurrencies**:

| Symbol | Name | investing.com URL |
|--------|------|-------------------|
| BTC | Bitcoin | `/crypto/bitcoin/technical` |
| ETH | Ethereum | `/crypto/ethereum/technical` |
| ADA | Cardano | `/crypto/cardano/technical` |
| SOL | Solana | `/crypto/solana/technical` |
| DOT | Polkadot | `/crypto/polkadot/technical` |
| LINK | Chainlink | `/crypto/chainlink/technical` |
| MATIC | Polygon | `/crypto/polygon/technical` |
| LTC | Litecoin | `/crypto/litecoin/technical` |
| XRP | XRP | `/crypto/xrp/technical` |
| DOGE | Dogecoin | `/crypto/dogecoin/technical` |

**Easy to extend**: Add new cryptocurrencies in `src/utils/crypto_config.py`

## Integration with eth-trading-bot-api

This Python scraper works alongside the TypeScript trading API:

1. **Python scraper** scrapes investing.com → Inserts to `technical_analysis` table
2. **TypeScript API** reads from `technical_analysis` table → Executes trading decisions

Both share the same Supabase database but run independently. The database schema supports any cryptocurrency symbol.

## Development

### Running Tests Locally

```bash
# Test Bitcoin scraping (no database)
python -c "from src.scrapers.investing_scraper import scrape_crypto_technical; import json; result = scrape_crypto_technical(crypto='BTC'); print(json.dumps(result['parsed'], indent=2))"

# Test Ethereum scraping
python -c "from src.scrapers.investing_scraper import scrape_crypto_technical; import json; result = scrape_crypto_technical(crypto='ETH'); print(json.dumps(result['parsed'], indent=2))"

# Test database insertion
python -c "from src.scrapers.investing_scraper import scrape_crypto_technical; from src.database.supabase_client import insert_technical_analysis_data; result = scrape_crypto_technical(crypto='BTC'); success = insert_technical_analysis_data(result['parsed'], use_service_role=True); print(f'Saved: {success}')"

# Run configuration tests
python3 test_crypto_config.py

# Run integration tests
python3 test_final.py

# Test Vercel function locally (requires Vercel CLI)
vercel dev
# Then visit: http://localhost:3000/api/scrape?crypto=BTC&save=true
```

### Modifying Parser Logic

To add new indicators or change parsing logic, edit:

**`src/parsers/technical_analysis_parser.py`**

Example - Adding a new indicator:

```python
# In _extract_technical_indicators()
indicator_patterns = [
    # ... existing patterns ...
    {"name": "NewIndicator", "pattern": r'\|\s*NewIndicator\s*\|\s*([\d.]+)\s*\|\s*(\w+)'}
]
```

### Adding New Cryptocurrencies

To add support for a new cryptocurrency, edit `src/utils/crypto_config.py`:

```python
SUPPORTED_CRYPTOS: Dict[str, CryptoConfig] = {
    # ... existing cryptos ...
    "XYZ": CryptoConfig(
        symbol="XYZ",
        name="MyToken",
        url_slug="mytoken"  # From investing.com URL
    ),
}
```

The `url_slug` should match the investing.com URL pattern:
`https://www.investing.com/crypto/{url_slug}/technical`

### Environment Variables

Create `.env` file with:

```bash
# Required
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Optional
DEFAULT_CRYPTO=ETH  # Default cryptocurrency to scrape
SCRAPER_TIMEOUT=30000
```

## Troubleshooting

### Playwright Installation Issues

```bash
# Reinstall Chromium
playwright install --force chromium

# Check Playwright version
playwright --version
```

### Vercel Deployment Issues

```bash
# Check function logs
vercel logs

# Test locally first
vercel dev

# Verify environment variables
vercel env ls
```

### Parsing Errors

If investing.com changes their HTML structure:

1. Check the raw markdown output: `result['markdown']`
2. Update regex patterns in `technical_analysis_parser.py`
3. Compare with TypeScript parser in `eth-trading-bot-api`

### Database Connection Errors

```bash
# Test connection
python -c "from src.database.supabase_client import SupabaseClient; client = SupabaseClient(); print(client.test_connection())"

# Check environment variables
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('SUPABASE_URL'))"
```

## Performance

- **Cold start**: 5-10 seconds (Playwright initialization)
- **Warm start**: 2-3 seconds (browser already running)
- **Scraping time**: 3-5 seconds (waiting for page load)
- **Total request time**: 8-15 seconds (first run), 5-8 seconds (subsequent runs)

## Important: Scheduled Scraping Architecture

⚠️ **This project uses a two-service architecture for production:**

1. **Scraper Service** (Railway.app with Docker + Playwright) - Scrapes data hourly and saves to database
2. **API Service** (Vercel serverless) - Reads from database and serves data

**Why this architecture?**
- Vercel serverless doesn't support Playwright browsers
- Scheduled scraping is more efficient than on-demand scraping
- Database reads are faster and cheaper than scraping on every request

See [SCHEDULED_SCRAPING_DEPLOYMENT.md](./SCHEDULED_SCRAPING_DEPLOYMENT.md) for complete setup guide.

## Limitations

- **Playwright bundle size**: ~100MB (affects Vercel deployment size)
- **Serverless timeout**: Max 60 seconds per request
- **Cold start**: First request may take 5-10 seconds (Playwright initialization)
- **Rate limiting**: Investing.com may block frequent requests
- **Cache**: Use `fresh=true` sparingly to avoid rate limits

## Contributing

When contributing, ensure:

1. Data structures match TypeScript API exactly
2. JSONB format is identical for database compatibility
3. Parser patterns handle all investing.com variations
4. Error handling is comprehensive

## License

ISC

## Recent Updates

### Scheduled Scraping Architecture (2025)
- ✅ Separated scraping service (Railway.app) from API service (Vercel)
- ✅ Docker + Playwright support for reliable scraping
- ✅ Scheduled scraping with configurable intervals
- ✅ New `/api/read` endpoint for fast database reads
- ✅ Complete deployment guide with Railway + Vercel

See [SCHEDULED_SCRAPING_DEPLOYMENT.md](./SCHEDULED_SCRAPING_DEPLOYMENT.md) for deployment guide.

### Multi-Cryptocurrency Support (2025)
- ✅ Added support for 10 cryptocurrencies (BTC, ETH, ADA, SOL, DOT, LINK, MATIC, LTC, XRP, DOGE)
- ✅ New `crypto` parameter for API endpoint
- ✅ Centralized cryptocurrency configuration module
- ✅ Backward compatible with existing ETH-focused code
- ✅ Easy to extend with new cryptocurrencies

See [MULTI_CRYPTO_UPGRADE.md](./MULTI_CRYPTO_UPGRADE.md) for detailed upgrade documentation.

---

**Built with ❤️ for the crypto community**

*Disclaimer: This is a data scraping tool for educational purposes. Use responsibly and respect investing.com's terms of service.*
