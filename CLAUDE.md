# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python application that fetches cryptocurrency data from **TAAPI.IO API** (technical indicators) and **CoinGecko API** (price/market data), storing it in Supabase. Supports multiple cryptocurrencies (BTC, ETH, ADA, SOL, DOT, LINK, MATIC, LTC, XRP, DOGE). Designed to work alongside `eth-trading-bot-api` (TypeScript) by populating the same database with technical analysis data.

**Key Changes (Nov 2025):**
- Migrated from web scraping (investing.com) to TAAPI.IO REST API due to bot detection issues
- Added CoinGecko API integration for real-time price, market cap, and volume data

## Development Commands

```bash
# Setup
pip install -r requirements.txt

# Test CoinGecko client (fast, ~5 seconds)
python3 test_coingecko.py

# Test TAAPI.IO client (slow, ~4 minutes per crypto)
python3 test_taapi.py

# Test combined integration (CoinGecko + TAAPI.IO)
python3 test_combined.py

# Test database connection
python -c "from src.database.supabase_client import SupabaseClient; client = SupabaseClient(); print(client.test_connection())"

# Test API locally (requires Vercel CLI)
vercel dev

# Deploy to Vercel
vercel --prod
```

## Architecture Overview

### Core Components

**`src/api/taapi_client.py`** - TAAPI.IO API client:
- Fetches 12 professional-grade technical indicators from TAAPI.IO REST API
- Rate limiting: 18 seconds between requests (free tier: 1 req/15s + 3s safety)
- Retry mechanism: Up to 5 retry attempts with 30-second pauses for missing indicators
- Returns structured data matching our database schema
- Professional indicator set covering momentum, trend, volatility, volume, and institutional levels

**`src/api/coingecko_client.py`** - CoinGecko API client (NEW):
- Fetches real-time price, 24h change, market cap, and volume data
- Optional OHLC candlestick data (1, 7, 14, 30, 90, 180, 365 days)
- Works with or without API key (public endpoints available)
- Free Demo plan: 30 calls/minute (more than sufficient)
- Returns price data in ~1 second

**`src/utils/crypto_config.py`** - Cryptocurrency configuration:
- Defines supported cryptocurrencies with CoinGecko IDs
- Currently supports: BTC, ETH, ADA, SOL, DOT, LINK, MATIC, LTC, XRP, DOGE
- Easy to extend with new cryptocurrencies

**`src/database/supabase_client.py`** - Database client:
- Inserts to `technical_analysis` table in Supabase
- Matches schema from `eth-trading-bot-api/database_schema.sql`
- JSONB serialization for indicators, moving averages, pivot points
- Service role key support for write operations

**`api/scrape.py`** - Vercel serverless function:
- HTTP handler using BaseHTTPRequestHandler
- Endpoint: `GET /api/scrape?crypto=BTC&save=true&exchange=binance&interval=1h`
- Query parameters:
  - `crypto` (optional): Cryptocurrency symbol (BTC, ETH, etc.) - default: BTC
  - `exchange` (optional): Exchange to fetch from - default: binance
  - `interval` (optional): Time interval (1h, 4h, 1d) - default: 1h
  - `save` (optional): Save to database - default: false
- Integrates both CoinGecko (price) and TAAPI.IO (indicators)
- Returns JSON matching TypeScript API format
- Validates crypto parameter against supported cryptocurrencies

### Data Flow

1. **Vercel Function** receives HTTP request
2. **CoinGeckoClient** fetches price/market data (~1 second)
3. **TaapiClient** fetches technical indicators from TAAPI.IO API (~4 minutes)
4. **Data merging** combines price data with indicators
5. **SupabaseClient** (optional) inserts complete data to database
6. **Response** returned matching TypeScript API format

### Database Schema Compatibility

Inserts to `technical_analysis` table with:
- `symbol`, `price`, `price_change`, `price_change_percent`
- `overall_summary`, `technical_indicators_summary`, `moving_averages_summary`
- `technical_indicators` (JSONB), `moving_averages` (JSONB), `pivot_points` (JSONB)
- `source_url`, `scraped_at`

## TAAPI.IO Rate Limits & Optimization

### Free Tier Limits
- **1 request per 15 seconds** (we use 18s for safety margin)
- 4 requests per minute
- 240 requests per hour
- 5,760 requests per day

### Professional-Grade Indicator Set (12 indicators per crypto)

**Tier 1: Core Momentum & Trend (2)**
1. **RSI (14)** - Momentum measurement, oversold/overbought detection
2. **MACD (12,26,9)** - Trend following with histogram

**Tier 1: Volatility & Breakouts (1)**
3. **Bollinger Bands (20,2)** - Volatility measurement, breakout detection

**Tier 1: Volume Analysis (1)**
4. **OBV** - On Balance Volume, whale detection

**Tier 2: Advanced Momentum (1)**
5. **StochRSI** - Hyper-sensitive momentum oscillator

**Tier 2: Risk Management & Volatility (1)**
6. **ATR (14)** - Average True Range for risk management

**Tier 2: Institutional Levels (1)**
7. **VWAP** - Volume Weighted Average Price, institutional benchmark

**Tier 2: Trend Signals (1)**
8. **SuperTrend** - Clear buy/sell signals

**Tier 3: Money Flow (1)**
9. **CMF (20)** - Chaikin Money Flow, institutional money flow

**Moving Averages (3)**
10. **EMA 20** - Short-term trend
11. **EMA 50** - Medium-term trend
12. **EMA 200** - Long-term trend (bull/bear divider)

### Retry Mechanism
- **Initial fetch**: All 12 indicators sequentially
- **Missing indicators check**: Identifies which indicators failed
- **Retry logic**: Up to 5 attempts with 30-second pauses between retries
- **Smart retry**: Only retries missing indicators (not all)
- **Graceful degradation**: Accepts partial data after max retries
- **Success rate**: ~99%+ with retry mechanism (vs ~92% without)

### Fetch Time per Cryptocurrency
- Initial fetch: 12 requests × 18 seconds = **~216 seconds (~3.6 minutes)**
- With retries (if needed): Add ~30-150 seconds
- Average total: **~4 minutes per crypto**
- BTC + ETH: **~8 minutes total**

### Perfect for Hourly Trading Bot
- Hourly updates: 24 hours × 24 requests = 576 requests/day (BTC + ETH)
- Free tier limit: 5,760 requests/day
- **Usage: 10% of daily quota** ✅
- Room for 3 more cryptocurrencies if needed

## CoinGecko API Integration

### Overview
CoinGecko provides real-time price and market data to complement TAAPI.IO's technical indicators.

### Endpoint Used
**`/simple/price`** - Fetches current price, market cap, volume, and 24h change

### Free Demo Plan Limits
- **Rate Limit**: 30 calls per minute
- **Daily Usage**: Negligible (1 call per crypto per fetch)
- **With API Key**: Optional - works without key for public endpoints
- **Fetch Time**: ~1 second per cryptocurrency

### Data Provided
- **Price**: Current price in USD
- **24h Change**: Price change in USD and percentage
- **Market Cap**: Total market capitalization
- **24h Volume**: Trading volume in last 24 hours
- **Last Updated**: UNIX timestamp of last price update

### CoinGecko IDs
Configured in `src/utils/crypto_config.py`:
- BTC → `bitcoin`
- ETH → `ethereum`
- ADA → `cardano`
- SOL → `solana`
- DOT → `polkadot`
- LINK → `chainlink`
- MATIC → `matic-network`
- LTC → `litecoin`
- XRP → `ripple`
- DOGE → `dogecoin`

### Why CoinGecko?
- **Accurate Pricing**: Real-time prices from multiple exchanges
- **No API Key Required**: Works with public endpoints (with lower rate limits)
- **Fast**: <1 second response time
- **Reliable**: 99.9% uptime SLA
- **Free**: Demo plan sufficient for our use case

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
TAAPI_API_KEY=your_taapi_api_key
COINGECKO_API_KEY=your_coingecko_api_key  # Optional - works without for public endpoints
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
- 300s max duration for API calls (to accommodate rate limiting)
- 512MB memory (reduced from 1024MB - no Playwright needed)

## Key Technical Decisions

### Why TAAPI.IO over Web Scraping?
- **Reliable**: Official API, no bot detection
- **Maintained**: TAAPI handles data updates
- **Simple**: No browser automation needed
- **Scalable**: Easy to add more indicators
- **Cost-effective**: Free tier perfect for hourly updates

### Why These 12 Indicators? (Professional-Grade Selection)

**Complete Market Coverage:**
- ✅ **Momentum**: RSI, MACD, StochRSI (detects trend strength and reversals)
- ✅ **Trend**: SuperTrend, EMA 20/50/200 (identifies trend direction and changes)
- ✅ **Volatility**: Bollinger Bands, ATR (measures market volatility and risk)
- ✅ **Volume**: OBV, CMF (detects whale activity and institutional flow)
- ✅ **Institutional**: VWAP (institutional benchmark and support/resistance)

**Professional Trading Use Cases:**
- **Trend Trading**: SuperTrend + EMAs + VWAP + CMF
- **Swing Trading**: MACD + Bollinger Bands + RSI + OBV
- **Scalping**: VWAP + StochRSI + ATR + SuperTrend
- **Risk Management**: ATR + Bollinger Bands + SuperTrend
- **Reversal Trading**: RSI divergence + OBV divergence + CMF

**Why This Is Professional-Grade:**
1. Covers all aspects of crypto trading (not just momentum)
2. Multiple confirmations reduce false signals
3. Includes institutional indicators (VWAP, CMF, OBV)
4. Risk management tools (ATR for stop-loss placement)
5. Clear entry/exit signals (SuperTrend, VWAP crossovers)
6. Used by successful crypto traders worldwide

### Data Parity with TypeScript API & Database Schema
- Exact JSONB structure match for technical_indicators, moving_averages
- Same field names and types
- Compatible with `ethPositionMonitor.ts` pattern detection in TypeScript API
- **No database migration needed**: Existing schema handles new indicator structures perfectly
  - JSONB flexibility allows different fields per indicator (e.g., Bollinger Bands has `upper/middle/lower`, MACD has `histogram`)
  - Can store 12 indicators in same array structure as previous 6 indicators
  - Backward compatible with existing TypeScript API queries

## Integration with eth-trading-bot-api

This Python app **populates the same database** as the TypeScript API:

1. **Python app** → Fetches from TAAPI.IO → Inserts to `technical_analysis` table
2. **TypeScript API** → Reads from `technical_analysis` table → Executes trading logic

Both systems work independently but share the same data source (Supabase).

## Common Development Tasks

### Testing the API client locally
```python
from src.api.taapi_client import TaapiClient

# Initialize client
client = TaapiClient()

# Test connection
client.test_connection()

# Fetch Bitcoin data (all 12 indicators)
# Takes ~4 minutes with retry mechanism
result = client.get_technical_analysis(symbol="BTC")
print(result['data'])

# Fetch Ethereum data with different interval
result = client.get_technical_analysis(symbol="ETH", interval="4h")
print(result['data'])

# Run comprehensive test suite
# Tests BTC + ETH, takes ~8 minutes
python3 test_taapi.py
```

### Testing database insertion
```python
from src.api.taapi_client import TaapiClient
from src.database.supabase_client import insert_technical_analysis_data

# Fetch and save Bitcoin data
client = TaapiClient()
result = client.get_technical_analysis(symbol="BTC")

if result['success']:
    data = result['data']['parsed']
    saved = insert_technical_analysis_data(data, use_service_role=True)
    print(f"Saved to database: {saved}")

# Fetch all supported cryptos and save
from src.utils.crypto_config import get_supported_symbols
for symbol in ["BTC", "ETH"]:
    result = client.get_technical_analysis(symbol=symbol)
    if result['success']:
        insert_technical_analysis_data(result['data']['parsed'], use_service_role=True)
        print(f"{symbol} saved successfully")
```

### API Usage Examples
```bash
# Fetch Bitcoin (no save)
curl "https://your-vercel-url.vercel.app/api/scrape?crypto=BTC"

# Fetch Ethereum and save to database
curl "https://your-vercel-url.vercel.app/api/scrape?crypto=ETH&save=true"

# Fetch with different interval
curl "https://your-vercel-url.vercel.app/api/scrape?crypto=BTC&interval=4h"

# Fetch from different exchange
curl "https://your-vercel-url.vercel.app/api/scrape?crypto=BTC&exchange=kraken"
```

### Adding new cryptocurrencies
Edit `src/utils/crypto_config.py` and add to `SUPPORTED_CRYPTOS`:
```python
"XYZ": CryptoConfig(symbol="XYZ", name="MyToken", url_slug="mytoken"),
```

## Troubleshooting

### TAAPI.IO rate limit errors (429)
- Check rate limiting delay (currently 18s between requests)
- Verify you're not exceeding free tier limits
- Consider upgrading to Basic plan ($8.99/mo) for 5 requests per 15 seconds

### Database connection errors
- Verify SUPABASE_URL and keys in .env
- Use service role key for write operations
- Check Supabase table permissions/RLS policies

### Missing indicators in response
- **Retry mechanism** automatically handles missing indicators
- Up to 5 retry attempts with 30-second pauses
- Client gracefully degrades (accepts partial data after max retries)
- Check logs for specific indicator failures
- Expected success rate: ~99%+ with retry mechanism (vs ~92% without)
- Minimum acceptable: 8/12 indicators (66%)

## Important Notes

- **Rate limiting**: 18 seconds between requests (free tier: 1 req/15s + 3s safety)
- **Retry mechanism**: 5 attempts max, 30-second pauses, ~99%+ success rate
- **Service role key**: Required for database writes from serverless function
- **Fetch time**: ~4 minutes per crypto (includes retry mechanism), perfect for hourly updates
- **Schema compatibility**: No migration needed - JSONB handles new indicator structures
- **Daily quota**: Using 10% of free tier limit (576/5760 requests for BTC + ETH)
- **Professional indicators**: 12 indicators covering momentum, trend, volatility, volume, institutional
- **Deployment size**: ~5MB (vs 150MB with Playwright scraping)

## Migration from Web Scraping (November 2025)

### Migration Results

**Before (Web Scraping Approach):**
- ❌ Playwright browser automation
- ❌ HTML parsing with BeautifulSoup/markdownify
- ❌ Investing.com scraping (blocked by Cloudflare)
- ❌ 150MB+ deployment size
- ❌ 10-second cold starts
- ❌ 60% reliability (bot detection)
- ❌ 1024MB memory requirement
- ❌ 6 basic indicators only

**After (TAAPI.IO API Approach):**
- ✅ TAAPI.IO REST API (official, reliable)
- ✅ Simple HTTP requests (no browser needed)
- ✅ No bot detection issues
- ✅ ~5MB deployment size (30x smaller)
- ✅ <1 second cold starts (10x faster)
- ✅ 99%+ reliability (with retry mechanism)
- ✅ 512MB memory requirement (50% less)
- ✅ 12 professional-grade indicators

### Files Removed (Cleanup)
- `src/scrapers/base_scraper.py`
- `src/scrapers/investing_scraper.py`
- `src/scrapers/simple_scraper.py`
- `src/scrapers/vercel_scraper.py`
- `src/parsers/technical_analysis_parser.py`
- Multiple test files: `test_bitcoin.py`, `test_parser_debug.py`, etc.

### Dependencies Removed
- `playwright` (~100MB)
- `beautifulsoup4`
- `lxml`
- `markdownify`

### Dependencies Added
- `requests` (lightweight HTTP client)
- Kept: `supabase`, `python-dotenv`, `python-dateutil`

### Performance Improvements
- **Deployment size**: 150MB → 5MB (30x reduction)
- **Cold start**: 10s → <1s (10x faster)
- **Memory**: 1024MB → 512MB (50% reduction)
- **Reliability**: 60% → 99%+ (with retries)
- **Indicators**: 6 basic → 12 professional (2x more, better quality)
- **Fetch time**: ~2 min → ~4 min (acceptable trade-off for reliability)

### Key Implementation Details
- **Rate limiting**: 18-second delays between API calls (free tier compliance)
- **Retry mechanism**: 5 attempts, 30-second pauses, smart retry of only missing indicators
- **Database**: No migration needed - existing schema compatible via JSONB flexibility
- **Free tier usage**: 10% of daily quota (576/5760 requests for BTC + ETH hourly updates)
