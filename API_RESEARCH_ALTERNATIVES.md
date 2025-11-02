# Technical Analysis API Research & Alternatives

**Date:** 2025-10-30
**Status:** Investing.com scraping blocked - researching alternatives

## Current Situation

Our Playwright scraper successfully loads investing.com pages but the site detects automation and serves a minimal page without technical analysis data.

**What works:**
- ✅ Symbol detection
- ✅ Price data (though values seem cached/incorrect)
- ✅ 4 Pivot points
- ✅ Page loading and basic scraping

**What's blocked:**
- ❌ Technical indicators (RSI, MACD, Stochastic, etc.) - 0 indicators extracted
- ❌ Moving averages - 0 extracted
- ❌ Complete technical analysis data

**Evidence from logs:**
```
Found 9 element(s) with selector: table
Selector 'table.technicalIndicatorsTbl' not found
Markdown preview shows only navigation menu and language selection
```

The site is serving a different version of the page to automated browsers.

---

## 🔍 Research Summary: Best Technical Analysis Data Sources (2025)

Based on comprehensive research, here are the top options ranked by reliability, data comprehensiveness, and similarity to what we've been trying to get from investing.com:

---

### **🏆 #1 RECOMMENDATION: TAAPI.IO**

**Why it's the best match:**
- ✅ **208+ technical indicators** (RSI, MACD, Stochastic, ADX, etc.)
- ✅ **All the exact indicators** we were trying to scrape from investing.com
- ✅ **Moving averages** (SMA, EMA, WMA)
- ✅ **5,000+ cryptocurrencies** supported
- ✅ **Real-time data** from major exchanges (Binance, ByBit, etc.)
- ✅ **REST API** - easy to integrate with Python scraper
- ✅ **Reliable** - purpose-built for automated trading systems

**Pricing:**
- **Free Tier:** 5 crypto pairs only (BTC & ETH would work perfectly!)
- **Basic Plan:** $8.99/month - More pairs, higher rate limits
- **Pro Plans:** Scale up as needed
- **7-day free trial** for paid plans

**Perfect for your use case because:**
- You only need BTC and ETH (fits free tier!)
- Drop-in replacement for investing.com scraper
- Same data format you were parsing
- No scraping = no blocking

**API Example:**
```python
# Get RSI for BTC
GET https://api.taapi.io/rsi?secret=YOUR_API_KEY&exchange=binance&symbol=BTC/USDT&interval=1h

# Response:
{
  "value": 57.18
}

# Get MACD for ETH
GET https://api.taapi.io/macd?secret=YOUR_API_KEY&exchange=binance&symbol=ETH/USDT&interval=1h

# Get multiple indicators at once (bulk endpoint)
POST https://api.taapi.io/bulk
```

**Documentation:** https://taapi.io/

**Supported Indicators:**
- RSI, MACD, Stochastic, StochRSI
- Moving Averages (SMA, EMA, WMA, VWMA)
- Bollinger Bands, ATR, ADX
- CCI, Williams %R, ROC
- Pivot Points (Classic, Fibonacci, Camarilla, Woodie's)
- 200+ more indicators

---

### **#2 ALTERNATIVE: TA-Lib + Free Price Data**

**Why it's good:**
- ✅ **Completely free** - no API costs
- ✅ **200+ indicators** built-in
- ✅ **Calculate your own** RSI, MACD, moving averages, etc.
- ✅ **BSD License** - use in commercial projects
- ✅ **Python library** - integrates with your code
- ✅ **Full control** over calculations

**How it works:**
1. Get OHLCV price data from free API (CoinGecko, Binance public API)
2. Calculate indicators locally using TA-Lib
3. Save to your Supabase database

**Implementation Example:**
```python
import talib
import pandas as pd
from binance.client import Client  # Free, no API key needed for public data

# Get OHLCV data from Binance
client = Client()
klines = client.get_klines(symbol='BTCUSDT', interval='1h', limit=100)
df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', ...])

# Calculate indicators
df['RSI_14'] = talib.RSI(df['close'], timeperiod=14)
df['MACD'], df['MACD_signal'], df['MACD_hist'] = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)
df['SMA_20'] = talib.SMA(df['close'], timeperiod=20)
df['EMA_50'] = talib.EMA(df['close'], timeperiod=50)

# Save to database
```

**Downsides:**
- ❌ More code to write
- ❌ Need to fetch and store historical price data
- ❌ Need to manage data pipeline
- ❌ More complex than simple API call
- ❌ Need to understand indicator calculations

**Best for:**
- If you want zero ongoing costs
- If you need custom indicator calculations
- If you're comfortable with more code complexity
- If you want educational value (learn how indicators work)

**Installation:**
```bash
pip install TA-Lib
pip install python-binance
```

**Resources:**
- TA-Lib Python: https://ta-lib.github.io/ta-lib-python/
- GitHub: https://github.com/TA-Lib/ta-lib-python
- Tutorial: https://tradermade.com/tutorials/calculate-technical-indicators-in-python-with-ta-lib

---

### **#3 TRADINGVIEW (via unofficial scraper)**

**Why it's interesting:**
- ✅ **Most comprehensive** charting platform
- ✅ **Real-time data** with authentication
- ✅ **3000+ fields** available
- ✅ **Industry standard** for technical analysis

**How it works:**
- Use `tradingview-screener` Python package
- Accesses TradingView's official API
- Can retrieve OHLC, indicators, fundamental metrics

**Downsides:**
- ❌ **No official API** for technical indicators
- ❌ Requires authentication/cookies for real-time data
- ❌ Rate limiting and potential account flags
- ❌ Against TOS (same problem as investing.com)
- ❌ 15-minute delay without paid account ($15/month)
- ❌ CAPTCHA issues with frequent API access

**Verdict:** Not recommended - same scraping issues you're facing now with investing.com

**Package:** https://pypi.org/project/tradingview-screener/

---

### **#4 CryptoCompare API**

**Why it's okay:**
- ✅ **Free tier** available
- ✅ **Institutional-grade** infrastructure (40,000 calls/sec capacity)
- ✅ **Market data** (prices, volumes, market cap)
- ✅ **316 exchanges** covered
- ✅ **7,287 assets** supported
- ✅ **338,335 trading pairs**

**What it provides:**
- Real-time prices
- Historical OHLCV data
- Trading volumes
- Market capitalization
- Exchange data

**Downsides:**
- ❌ **No pre-calculated indicators** (RSI, MACD) in API
- ❌ Would need to calculate yourself (combine with TA-Lib)
- ❌ Focus on market data, not technical analysis

**Verdict:** Good for price data source, but need to add TA-Lib for indicators (same as Option #2)

**API:** https://www.cryptocompare.com/

---

### **#5 Other Options Considered**

**Quantify Crypto:**
- Bullish/bearish signals
- Technical indicators optimized for crypto
- Pricing unclear from research
- Less established than TAAPI.IO

**EODHD Technical Indicators API:**
- Supports MA, RSI, MACD
- Works with stocks, forex, and crypto
- Pricing starts at $19.99/month
- More expensive than TAAPI.IO for same features

**Alpha Vantage:**
- Popular for stocks
- Limited crypto support
- Free tier very restrictive (5 API calls per minute)
- Not ideal for crypto-focused trading

---

## 📊 Side-by-Side Comparison

| Feature | TAAPI.IO | TA-Lib + Binance | TradingView | Investing.com (current) | CryptoCompare |
|---------|----------|------------------|-------------|------------------------|---------------|
| **Cost** | $0-9/mo | $0 | $0-15/mo | $0 | $0 |
| **Technical Indicators** | 208+ | 200+ | All | ❌ Blocked | ❌ No (need TA-Lib) |
| **Moving Averages** | ✅ All types | ✅ All types | ✅ | ❌ Blocked | ❌ No (need TA-Lib) |
| **Pivot Points** | ✅ 4 types | ✅ Can calculate | ✅ | ✅ 4 points | ❌ No |
| **Real-time Data** | ✅ Yes | ✅ Yes | Delayed 15min | ✅ Yes | ✅ Yes |
| **Reliability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ (blocked) | ⭐⭐⭐⭐ |
| **Easy Integration** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐ (blocked) | ⭐⭐⭐⭐ |
| **BTC + ETH Free** | ✅ Yes (5 pairs) | ✅ Yes | ❌ No | ✅ Partial | ✅ Yes |
| **API Quality** | REST API | Library | Unofficial | Scraping | REST API |
| **Rate Limits** | Generous | None (local) | Strict | N/A | 100k calls/mo free |
| **Maintenance** | Low | Medium | High | High | Low |
| **Setup Time** | 10-15 min | 30-60 min | 15-30 min | N/A | 15-30 min |

---

## 🎯 Final Recommendation

**Go with TAAPI.IO for the following reasons:**

### Why TAAPI.IO is the best choice:

1. **Perfect fit for your requirements:**
   - You only need BTC & ETH (free tier covers 5 pairs!)
   - Gets you EXACT data you wanted from investing.com
   - No scraping = no blocking issues

2. **Easy migration:**
   - Minimal code changes from current scraper
   - Similar JSON structure to what you were parsing
   - Drop-in replacement for investing.com calls

3. **Reliable & maintained:**
   - Purpose-built for automated trading systems
   - 208+ indicators (more than investing.com)
   - Real-time data from major exchanges

4. **Cost effective:**
   - FREE for BTC + ETH use case
   - Can upgrade to $8.99/mo if you add more pairs later
   - No infrastructure costs (unlike TA-Lib option)

5. **Time to implement:**
   - 10-15 minutes to integrate
   - Well-documented API
   - Simple REST calls

### When to choose alternatives:

**Choose TA-Lib + Binance if:**
- You want zero ongoing costs (truly free)
- You need custom indicator calculations
- You want to learn how indicators work
- You have time to build data pipeline

**Choose CryptoCompare if:**
- You only need price data
- You're willing to use TA-Lib for indicators
- You need very high rate limits

---

## 📋 Implementation Plan (TAAPI.IO)

### Phase 1: Setup (5 minutes)
1. Sign up at https://taapi.io
2. Get free API key
3. Test API with curl/Postman

### Phase 2: Code Changes (10 minutes)
1. Create new `src/api/taapi_client.py`
2. Replace scraper calls with TAAPI API calls
3. Map TAAPI JSON response to existing database schema
4. Keep existing database structure (no schema changes needed)

### Phase 3: Testing (5 minutes)
1. Test BTC data fetching
2. Test ETH data fetching
3. Verify data saves to Supabase correctly
4. Compare with expected format

### Phase 4: Deploy (5 minutes)
1. Add TAAPI_API_KEY to Railway environment variables
2. Deploy to Railway
3. Monitor logs
4. Verify hourly scraping works

**Total estimated time:** 25-30 minutes

---

## 📝 Code Structure Preview

```python
# src/api/taapi_client.py
import requests
from typing import Dict, Any

class TaapiClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.taapi.io"

    def get_technical_analysis(self, symbol: str, exchange: str = "binance") -> Dict[str, Any]:
        """
        Get comprehensive technical analysis for a cryptocurrency.
        Returns data in format compatible with our database schema.
        """
        # Fetch RSI
        rsi = self._get_indicator("rsi", symbol, exchange)

        # Fetch MACD
        macd = self._get_indicator("macd", symbol, exchange)

        # Fetch Moving Averages
        sma_20 = self._get_indicator("sma", symbol, exchange, period=20)
        ema_50 = self._get_indicator("ema", symbol, exchange, period=50)

        # Fetch Pivot Points
        pivots = self._get_indicator("pivots", symbol, exchange)

        # Format to match our database schema
        return {
            "symbol": symbol,
            "price": self._get_price(symbol, exchange),
            "technicalIndicators": [
                {"name": "RSI(14)", "value": rsi, ...},
                {"name": "MACD(12,26)", "value": macd, ...},
            ],
            "movingAverages": [...],
            "pivotPoints": [...]
        }
```

---

## 🔗 Resources

### TAAPI.IO
- **Website:** https://taapi.io/
- **Documentation:** https://taapi.io/indicators/
- **Pricing:** https://taapi.io/product-category/subscription/
- **API Docs:** Available after signup

### TA-Lib
- **Website:** https://ta-lib.org/
- **Python Wrapper:** https://ta-lib.github.io/ta-lib-python/
- **GitHub:** https://github.com/TA-Lib/ta-lib-python
- **Tutorial:** https://tradermade.com/tutorials/calculate-technical-indicators-in-python-with-ta-lib
- **Crypto Example:** https://arbazhussain.medium.com/cryptocurrency-technical-analysis-using-python-and-ta-lib-2a1c6e35e4d9

### Binance API (for TA-Lib option)
- **Python Client:** https://github.com/sammchardy/python-binance
- **Public API:** No authentication needed for market data

### TradingView
- **Screener Package:** https://pypi.org/project/tradingview-screener/

### CryptoCompare
- **Website:** https://www.cryptocompare.com/
- **API Docs:** https://min-api.cryptocompare.com/

---

## 📌 Next Steps (Tomorrow)

1. **Decision:** Choose between TAAPI.IO or TA-Lib approach
2. **If TAAPI.IO:**
   - Sign up for free account
   - Get API key
   - Test API endpoints
   - Implement `TaapiClient` class
   - Replace scraper calls
   - Deploy and test

3. **If TA-Lib:**
   - Choose price data source (Binance recommended)
   - Install TA-Lib
   - Implement data fetching pipeline
   - Implement indicator calculations
   - Deploy and test

4. **Cleanup:**
   - Remove Playwright dependencies (if using API)
   - Update documentation
   - Remove unused scraper code

---

## 💡 Additional Considerations

### Data Freshness
- **TAAPI.IO:** Real-time from exchanges
- **TA-Lib + Binance:** Real-time, you control update frequency
- **Investing.com (current):** Blocked, unreliable

### Maintenance Burden
- **TAAPI.IO:** Very low - just API calls
- **TA-Lib + Binance:** Medium - manage data pipeline
- **Scraping:** High - constant cat-and-mouse with anti-bot measures

### Scalability
- **TAAPI.IO:** Easily add more pairs (upgrade plan)
- **TA-Lib + Binance:** Fully scalable, just compute resources
- **Scraping:** Not scalable (gets blocked faster with more requests)

### Reliability
- **TAAPI.IO:** ⭐⭐⭐⭐⭐ Professional service
- **TA-Lib + Binance:** ⭐⭐⭐⭐ Depends on your implementation
- **Scraping:** ⭐⭐ Constantly breaking

---

**Status:** Ready for implementation tomorrow
**Recommendation:** TAAPI.IO for fastest, most reliable solution
**Alternative:** TA-Lib + Binance for zero-cost solution with more work
