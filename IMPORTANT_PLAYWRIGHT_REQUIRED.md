# ⚠️ IMPORTANT: Playwright Required for Technical Indicators

## Issue Identified

The **SimpleScraper** (HTTP-only) **cannot extract technical indicators** from investing.com because the data is loaded dynamically via JavaScript after the initial page load.

### What Works vs What Doesn't:

| Scraper Type | Technical Indicators | Moving Averages | Pivot Points | Use Case |
|--------------|---------------------|-----------------|--------------|----------|
| **SimpleScraper** (HTTP) | ❌ Empty | ❌ Empty | ✅ Works | Testing only |
| **InvestingScraper** (Playwright) | ✅ Works | ✅ Works | ✅ Works | Production |

## Root Cause

Investing.com loads the technical indicators table (`technicalIndicatorsTbl`) using JavaScript **after** the initial HTML is delivered. This means:

1. **SimpleScraper** fetches the raw HTML → No technical indicators data
2. **InvestingScraper** (Playwright) executes JavaScript → Waits for table to load → Gets all data

## Solution

The `api/scrape.py` file has been updated to use **InvestingScraper with Playwright**.

```python
# OLD (doesn't work for technical indicators)
from src.scrapers.simple_scraper import SimpleScraper
scraper = SimpleScraper(timeout=30)

# NEW (works correctly)
from src.scrapers.investing_scraper import InvestingScraper
scraper = InvestingScraper(timeout=60000, headless=True)
```

## Vercel Deployment Considerations

### Playwright in Vercel

Playwright **does work** in Vercel's serverless environment, but:

1. **Bundle Size**: Adds ~100MB to deployment (Chromium browser)
2. **Cold Start**: First request may take 5-10 seconds
3. **Memory**: Requires sufficient memory allocation (1024MB recommended)

### Vercel Configuration

Ensure `vercel.json` is configured properly:

```json
{
  "version": 2,
  "functions": {
    "api/**/*.py": {
      "memory": 1024,
      "maxDuration": 60
    }
  },
  "env": {
    "PLAYWRIGHT_BROWSERS_PATH": "/tmp/.playwright"
  }
}
```

### Deployment Steps

1. Playwright must be in `requirements.txt`:
   ```
   playwright==1.40.0
   ```

2. After deployment, Playwright will automatically install Chromium in `/tmp/.playwright`

3. First request will be slow (~10s) as Playwright initializes

4. Subsequent requests will be faster (~5-8s)

## Testing

### Local Testing

```bash
# Test with Playwright (works)
python -c "from src.scrapers.investing_scraper import scrape_crypto_technical; result = scrape_crypto_technical(crypto='BTC'); print(f'Technical Indicators: {len(result[\"parsed\"][\"technicalIndicators\"])}')"

# Expected output: Technical Indicators: 12
```

### API Testing

```bash
# After deploying to Vercel
curl "https://your-app.vercel.app/api/scrape?crypto=BTC"

# Check the response
# - technicalIndicators should have 12 items
# - movingAverages should have 6 items
# - pivotPoints should have 4 items
```

## Why SimpleScraper Exists

SimpleScraper was created for environments where Playwright cannot run, but it's **not suitable for production** when you need technical indicators data. It's only useful for:

- Quick testing
- Environments that don't support Playwright
- Scraping sites that don't use JavaScript for data loading

## Summary

✅ **Use InvestingScraper (with Playwright)** for production
❌ **Don't use SimpleScraper** - it will return empty technical indicators

The API has been fixed to use InvestingScraper. After redeploying to Vercel, technical indicators will populate correctly.
