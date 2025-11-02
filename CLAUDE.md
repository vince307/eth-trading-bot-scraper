# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python application that fetches cryptocurrency data from **CoinGecko API** (price/market data + OHLC candlesticks) and calculates technical indicators locally using the **ta library**. Data is stored in Supabase. Supports multiple cryptocurrencies (BTC, ETH, ADA, SOL, DOT, LINK, MATIC, LTC, XRP, DOGE). Designed to work alongside `eth-trading-bot-api` (TypeScript) by populating the same database with technical analysis data.

## Development Commands

```bash
# Setup
pip install -r requirements.txt

# Test CoinGecko client
python3 test_coingecko.py

# Test API locally (requires Vercel CLI)
vercel dev

# Deploy to Vercel
vercel --prod
```

## Architecture Overview

### Core Components

**`src/api/coingecko_client.py`** - CoinGecko API client:
- Fetches real-time price, 24h change, market cap, and volume data
- Fetches OHLC candlestick data (up to 365 days for MA200 calculation)
- Works with or without API key (public endpoints available)
- Free Demo plan: 30 calls/minute (more than sufficient)
- Returns price data in ~1 second

**`src/api/indicators_calculator.py`** - Technical indicators calculator:
- Calculates 12+ technical indicators locally using `ta` library
- Processes OHLC data from CoinGecko
- Returns structured data matching database schema
- Fast: <1 second calculation time
- Professional indicator set covering momentum, trend, volatility, volume

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
- Integrates CoinGecko (price + OHLC) and local indicator calculation
- Returns JSON matching TypeScript API format
- Validates crypto parameter against supported cryptocurrencies

### Data Flow

1. **Vercel Function** receives HTTP request
2. **CoinGeckoClient** fetches price/market data (~1 second)
3. **CoinGeckoClient** fetches OHLC candlestick data (~1 second)
4. **IndicatorsCalculator** calculates technical indicators locally (<1 second)
5. **Data merging** combines price data with calculated indicators
6. **SupabaseClient** (optional) inserts complete data to database
7. **Response** returned matching TypeScript API format

### Database Schema Compatibility

Inserts to `technical_analysis` table with:
- `symbol`, `price`, `price_change`, `price_change_percent`
- `overall_summary`, `technical_indicators_summary`, `moving_averages_summary`
- `technical_indicators` (JSONB), `moving_averages` (JSONB), `pivot_points` (JSONB)
- `source_url`, `scraped_at`

## Technical Indicators (12+ indicators)

**Momentum & Trend:**
- RSI (14) - Relative Strength Index
- MACD (12,26,9) - Moving Average Convergence Divergence
- StochRSI - Stochastic RSI oscillator

**Volatility & Breakouts:**
- Bollinger Bands (20,2) - Volatility measurement
- ATR (14) - Average True Range for risk management

**Volume Analysis:**
- OBV - On Balance Volume
- CMF (20) - Chaikin Money Flow

**Institutional Levels:**
- VWAP - Volume Weighted Average Price

**Trend Signals:**
- SuperTrend - Clear buy/sell signals

**Moving Averages:**
- EMA 20 - Short-term trend
- EMA 50 - Medium-term trend
- EMA 200 - Long-term trend (bull/bear divider)

## CoinGecko API Integration

### Overview
CoinGecko provides real-time price and market data plus historical OHLC candlesticks for indicator calculation.

### Endpoints Used
- **`/simple/price`** - Current price, market cap, volume, 24h change
- **`/coins/{id}/ohlc`** - OHLC candlestick data (1, 7, 14, 30, 90, 180, 365 days)

### Free Demo Plan Limits
- **Rate Limit**: 30 calls per minute
- **Daily Usage**: Negligible (2 calls per crypto per fetch)
- **With API Key**: Optional - works without key for public endpoints
- **Fetch Time**: ~2 seconds total per cryptocurrency

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
- 300s max duration for API calls
- 512MB memory

## Key Technical Decisions

### Why CoinGecko + Local Calculation?
- **Fast**: ~2-3 seconds total (vs 4 minutes with TAAPI.IO)
- **Reliable**: Official API, no rate limit issues
- **Cost-effective**: Free tier perfect for frequent updates
- **No external dependencies**: Calculate indicators locally
- **Scalable**: Easy to add more indicators or cryptos
- **Lightweight**: ~5MB deployment (no Playwright/browser needed)

### Why These 12 Indicators?

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

## Integration with eth-trading-bot-api

This Python app **populates the same database** as the TypeScript API:

1. **Python app** → Fetches from CoinGecko → Calculates indicators → Inserts to `technical_analysis` table
2. **TypeScript API** → Reads from `technical_analysis` table → Executes trading logic

Both systems work independently but share the same data source (Supabase).

## Common Development Tasks

### Testing the API client locally
```python
from src.api.coingecko_client import CoinGeckoClient
from src.api.indicators_calculator import IndicatorsCalculator

# Initialize clients
coingecko = CoinGeckoClient()
calculator = IndicatorsCalculator()

# Fetch price data
price_result = coingecko.get_price_data("BTC")
print(price_result['data'])

# Fetch OHLC data
ohlc_result = coingecko.get_ohlc_data("BTC", days=365)
print(f"Fetched {len(ohlc_result['data'])} candles")

# Calculate indicators
indicators = calculator.calculate_indicators(ohlc_result['data'], "BTC")
print(indicators)
```

### Testing database insertion
```python
from src.api.coingecko_client import CoinGeckoClient
from src.api.indicators_calculator import IndicatorsCalculator
from src.database.supabase_client import SupabaseClient

# Fetch and save Bitcoin data
coingecko = CoinGeckoClient()
calculator = IndicatorsCalculator()
db = SupabaseClient(use_service_role=True)

# Get data
price_result = coingecko.get_price_data("BTC")
ohlc_result = coingecko.get_ohlc_data("BTC", days=365)
indicators = calculator.calculate_indicators(ohlc_result['data'], "BTC")

# Merge and save
indicators['price'] = price_result['data']['price']
saved = db.insert_technical_analysis(indicators)
print(f"Saved to database: {saved}")
```

### API Usage Examples
```bash
# Fetch Bitcoin (no save)
curl "https://your-vercel-url.vercel.app/api/scrape?crypto=BTC"

# Fetch Ethereum and save to database
curl "https://your-vercel-url.vercel.app/api/scrape?crypto=ETH&save=true"

# Fetch with different interval
curl "https://your-vercel-url.vercel.app/api/scrape?crypto=BTC&interval=4h"
```

### Adding new cryptocurrencies
Edit `src/utils/crypto_config.py` and add to `SUPPORTED_CRYPTOS`:
```python
"XYZ": CryptoConfig(
    symbol="XYZ",
    name="MyToken",
    coingecko_id="mytoken"
),
```

## Troubleshooting

### CoinGecko rate limit errors (429)
- Free tier: 30 calls/minute
- Each crypto fetch = 2 calls (price + OHLC)
- Max: 15 cryptos per minute on free tier
- Consider upgrading to Pro plan for higher limits

### Database connection errors
- Verify SUPABASE_URL and keys in .env
- Use service role key for write operations
- Check Supabase table permissions/RLS policies

### Missing indicators in response
- Check OHLC data availability (need enough candles for indicators)
- Minimum: 200 candles for MA200
- Some cryptos may have limited history

## Important Notes

- **Fast**: ~2-3 seconds per crypto (vs 4 minutes with TAAPI.IO)
- **Lightweight**: ~5MB deployment (vs 150MB with Playwright)
- **No rate limiting delays**: Immediate response
- **Service role key**: Required for database writes from serverless function
- **Schema compatibility**: No migration needed - JSONB handles indicator structures
- **Free tier**: 30 calls/minute = 15 cryptos/minute
- **Professional indicators**: 12+ indicators covering all trading aspects
- **Local calculation**: No external API dependencies for indicators
