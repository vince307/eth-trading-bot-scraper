# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python web scraping application that scrapes cryptocurrency technical analysis data from investing.com and stores it in Supabase. Supports multiple cryptocurrencies (BTC, ETH, ADA, SOL, DOT, LINK, MATIC, LTC, XRP, DOGE). Designed to work alongside `eth-trading-bot-api` (TypeScript) by populating the same database with technical analysis data.

## Development Commands

```bash
# Setup
pip install -r requirements.txt
playwright install chromium

# Run locally (test ETH scraper)
python -c "from src.scrapers.investing_scraper import scrape_crypto_technical; print(scrape_crypto_technical(crypto='ETH'))"

# Run locally (test Bitcoin scraper)
python -c "from src.scrapers.investing_scraper import scrape_crypto_technical; print(scrape_crypto_technical(crypto='BTC'))"

# Test database connection
python -c "from src.database.supabase_client import SupabaseClient; client = SupabaseClient(); print(client.test_connection())"

# Run Vercel dev server (requires Vercel CLI)
vercel dev

# Deploy to Vercel
vercel --prod
```

## Architecture Overview

### Core Components

**`src/scrapers/base_scraper.py`** - Abstract base class for web scraping:
- Playwright browser automation
- HTML to Markdown conversion (using markdownify)
- Error handling and logging
- Extensible `parse_content()` method for subclasses

**`src/scrapers/investing_scraper.py`** - Investing.com scraper (multi-crypto support):
- Scrapes technical analysis for any supported cryptocurrency
- Accepts `crypto` parameter (BTC, ETH, etc.) or URL slug (bitcoin, ethereum)
- Waits for technical indicators table to load
- Cache busting support via URL timestamps
- Returns structured data with raw HTML, markdown, and parsed content
- Backward compatible with legacy `scrape_eth_technical()` function

**`src/scrapers/simple_scraper.py`** - HTTP-based scraper (Vercel compatible):
- Simple HTTP scraper without Playwright (faster, smaller)
- Multi-crypto support matching InvestingScraper
- Used by Vercel serverless function

**`src/utils/crypto_config.py`** - Cryptocurrency configuration:
- Defines supported cryptocurrencies with URL mappings
- Currently supports: BTC, ETH, ADA, SOL, DOT, LINK, MATIC, LTC, XRP, DOGE
- Easy to extend with new cryptocurrencies
- URL builder: symbol → `https://www.investing.com/crypto/{slug}/technical`

**`src/parsers/technical_analysis_parser.py`** - Python port of TypeScript parser:
- Extracts symbol, price, price change, and percentage
- Parses 12+ technical indicators (RSI, MACD, Stochastic, etc.)
- Extracts moving averages (MA5-MA200 with simple/exponential)
- Parses pivot points (Classic, Fibonacci, Camarilla, Woodie's)
- Extracts summary recommendations

**`src/database/supabase_client.py`** - Database client:
- Inserts to `technical_analysis` table in Supabase
- Matches schema from `eth-trading-bot-api/database_schema.sql`
- JSONB serialization for indicators, moving averages, pivot points
- Service role key support for write operations

**`api/scrape.py`** - Vercel serverless function:
- HTTP handler using BaseHTTPRequestHandler
- Endpoint: `GET /api/scrape?crypto=BTC&save=true&fresh=true`
- Query parameters:
  - `crypto` (optional): Cryptocurrency symbol (BTC, ETH, etc.) or URL slug (bitcoin, ethereum)
  - `url` (optional): Direct URL to scrape (overrides crypto parameter)
  - `save` (optional): Save to database (default: false)
  - `fresh` (optional): Cache busting (default: false)
- Returns JSON matching TypeScript API format
- Validates crypto parameter against supported cryptocurrencies

### Data Flow

1. **Vercel Function** receives HTTP request
2. **InvestingScraper** scrapes investing.com using Playwright
3. **TechnicalAnalysisParser** parses markdown to extract structured data
4. **SupabaseClient** (optional) inserts data to database
5. **Response** returned matching TypeScript API format

### Database Schema Compatibility

Inserts to `technical_analysis` table with:
- `symbol`, `price`, `price_change`, `price_change_percent`
- `overall_summary`, `technical_indicators_summary`, `moving_averages_summary`
- `technical_indicators` (JSONB), `moving_averages` (JSONB), `pivot_points` (JSONB)
- `source_url`, `scraped_at`

## Deployment to Vercel

### Prerequisites
1. Vercel account
2. Vercel CLI: `npm i -g vercel`
3. Environment variables configured in Vercel dashboard

### Environment Variables
Required in Vercel project settings:
```bash
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

### Deployment Steps
```bash
# Login to Vercel
vercel login

# Deploy (first time)
vercel

# Deploy to production
vercel --prod
```

### Vercel Configuration

**`vercel.json`**:
- Python 3.12 runtime
- 60s max duration for scraping
- Playwright browsers path set to `/tmp/.playwright`

**Important**: Playwright Chromium works in Vercel's serverless environment but adds ~100MB to deployment size. Function cold starts may take 5-10 seconds.

## Key Technical Decisions

### Why Playwright over Selenium/Puppeteer?
- **Serverless compatible**: Works in Vercel's environment
- **Python native**: No Node.js bridge required
- **Better for dynamic content**: investing.com uses JavaScript-rendered tables

### Data Parity with TypeScript API
- Exact JSONB structure match for technical_indicators, moving_averages, pivot_points
- Same field names and types
- Compatible with `ethPositionMonitor.ts` pattern detection in TypeScript API

### Parser Implementation
- Regex-based extraction from markdown (not HTML parsing)
- Matches TypeScript parser logic exactly
- Table row parsing for indicators and moving averages
- Section-based extraction for pivot points

## Integration with eth-trading-bot-api

This Python scraper **populates the same database** as the TypeScript API:

1. **Python scraper** → Scrapes investing.com → Inserts to `technical_analysis` table
2. **TypeScript API** → Reads from `technical_analysis` table → Executes trading logic

Both systems work independently but share the same data source (Supabase).

## Common Development Tasks

### Testing the scraper locally
```python
from src.scrapers.investing_scraper import scrape_crypto_technical

# Scrape Bitcoin
result = scrape_crypto_technical(crypto="BTC")
print(result['parsed'])

# Scrape Ethereum
result = scrape_crypto_technical(crypto="ETH")
print(result['parsed'])

# Scrape with cache busting
result = scrape_crypto_technical(crypto="BTC", cache_bust=True)

# Scrape using URL slug
result = scrape_crypto_technical(crypto="bitcoin")

# Legacy function (still works)
from src.scrapers.investing_scraper import scrape_eth_technical
result = scrape_eth_technical()
```

### Testing database insertion
```python
from src.scrapers.investing_scraper import scrape_crypto_technical
from src.database.supabase_client import insert_technical_analysis_data

# Scrape Bitcoin and save
result = scrape_crypto_technical(crypto="BTC")
if result['success']:
    success = insert_technical_analysis_data(result['parsed'], use_service_role=True)
    print(f"Saved to database: {success}")

# Scrape multiple cryptocurrencies
from src.utils.crypto_config import get_supported_symbols
for symbol in get_supported_symbols():
    result = scrape_crypto_technical(crypto=symbol)
    if result['success']:
        insert_technical_analysis_data(result['parsed'], use_service_role=True)
```

### API Usage Examples
```bash
# Scrape Bitcoin
curl "https://your-vercel-url.vercel.app/api/scrape?crypto=BTC"

# Scrape Ethereum and save to database
curl "https://your-vercel-url.vercel.app/api/scrape?crypto=ETH&save=true"

# Scrape with cache busting
curl "https://your-vercel-url.vercel.app/api/scrape?crypto=BTC&fresh=true"

# Scrape using URL slug
curl "https://your-vercel-url.vercel.app/api/scrape?crypto=bitcoin"

# Direct URL (overrides crypto parameter)
curl "https://your-vercel-url.vercel.app/api/scrape?url=https://www.investing.com/crypto/cardano/technical"
```

### Adding new cryptocurrencies
Edit `src/utils/crypto_config.py` and add to `SUPPORTED_CRYPTOS`:
```python
"XYZ": CryptoConfig(symbol="XYZ", name="MyToken", url_slug="mytoken"),
```

### Modifying parser patterns
Edit `src/parsers/technical_analysis_parser.py`:
- Update regex patterns in `_extract_*` methods
- Add new indicator patterns to `indicator_patterns` list
- Add new moving average periods to `ma_patterns` list

## Troubleshooting

### Playwright installation issues
```bash
# Install Chromium manually
playwright install chromium

# Check installation
playwright install --help
```

### Vercel deployment issues
- Check function logs: `vercel logs`
- Increase timeout in `vercel.json` if scraping takes >60s
- Verify environment variables are set in Vercel dashboard

### Database connection errors
- Verify SUPABASE_URL and keys in .env
- Use service role key for write operations
- Check Supabase table permissions/RLS policies

### Parsing errors
- Check markdown format from investing.com (may change)
- Add logging to parser methods
- Compare with TypeScript parser output

## Important Notes

- **Playwright bundle size**: ~100MB, affects Vercel cold start times
- **Service role key**: Required for database writes from serverless function
- **Rate limiting**: investing.com may rate-limit requests; use cache busting sparingly
- **Schema compatibility**: Keep JSONB structures identical to TypeScript API
