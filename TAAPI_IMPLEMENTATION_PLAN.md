# TAAPI.IO Implementation Plan

## Rate Limit Analysis

**TAAPI.IO Free Tier:**
- ✅ 1 request per 15 seconds
- ✅ 4 requests per minute
- ✅ 240 requests per hour
- ✅ 5,760 requests per day

**Source:** https://taapi.io/documentation/rate-limits/

## Optimized Approach for Free Tier

### Indicators Fetched (Per Cryptocurrency)
1. **RSI (14)** - Momentum indicator
2. **MACD** - Trend following
3. **Stochastic** - Overbought/oversold
4. **EMA 20** - Short-term trend
5. **EMA 50** - Medium-term trend
6. **EMA 200** - Long-term trend

**Total: 6 requests per crypto**

### Time Requirements
- **Per crypto:** 6 requests × 15 seconds = **90 seconds (~1.5 minutes)**
- **BTC + ETH:** 12 requests × 15 seconds = **180 seconds (~3 minutes)**

### Why This Works for Trading Bot

Your trading bot likely runs on an **hourly schedule**:
- ✅ Fetch takes 3 minutes
- ✅ Plenty of time within 1-hour window
- ✅ 24 hourly updates = 288 requests/day (well under 5,760 limit)
- ✅ Provides essential indicators for trading decisions

## What We Sacrificed (Compared to Full Suite)

**Removed to save requests:**
- ❌ CCI, ADX, Williams %R, ROC, ATR (non-essential indicators)
- ❌ SMA (Simple Moving Averages) - using EMA only
- ❌ MA5, MA10, MA100 periods - keeping only 20, 50, 200
- ❌ Pivot Points (not available in free tier anyway)

**Kept the essentials:**
- ✅ RSI - Most popular momentum indicator
- ✅ MACD - Standard trend indicator
- ✅ Stochastic - Overbought/oversold signals
- ✅ 3 EMAs - Short, medium, long-term trends

## Alternative: Bulk Endpoint

Could potentially reduce to **1 request per crypto** using bulk endpoint:
- Limit: 20 calculations per request
- Our 6 indicators = 6 calculations (under limit)
- **Time per crypto: 15 seconds instead of 90 seconds**

**Note:** Bulk endpoint may not be available on free tier (got 429 errors earlier).
Worth testing after rate limit resets.

## Production Usage Pattern

For automated trading bot running every hour:

```
Hour 0: Fetch BTC + ETH data (3 minutes)
Hour 1: Fetch BTC + ETH data (3 minutes)
...
Hour 23: Fetch BTC + ETH data (3 minutes)

Total daily requests: 24 hours × 12 requests = 288 requests
Free tier limit: 5,760 requests/day
Usage: 5% of daily quota
```

**Conclusion:** Free tier is perfectly adequate for hourly trading bot!

## If You Need More

### Upgrade to Basic Plan ($8.99/mo)
- 5 requests per 15 seconds
- Same 6 indicators would take: 6 ÷ 5 × 15 = **18 seconds per crypto**
- Could add more indicators or fetch more frequently

### Use Bulk Endpoint (Paid Tiers)
- If bulk works on paid tiers: **15 seconds per crypto**
- Could fetch all indicators in single request

## Implementation Status

✅ TaapiClient created with 15-second rate limiting
✅ Optimized to 6 essential indicators
✅ Ready for testing (waiting for rate limit reset)
⏳ Need to test with real data
⏳ Need to verify database integration
⏳ Need to deploy to Vercel

## Next Steps

1. **Wait 5 minutes** for rate limit to fully reset
2. **Run test:** `python3 test_taapi.py`
3. **Verify data quality** - check if indicators are meaningful
4. **Test database save**
5. **Deploy to Vercel**
6. **Set up hourly cron job**
