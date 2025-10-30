# AI Coding Agent Instructions

## Project Overview
ETH trading bot scraper component that extracts technical analysis data from investing.com and stores it in Supabase. Works in conjunction with a separate TypeScript API (`eth-trading-bot-api`) by sharing the same database schema.

## Key Architecture Points
- **Vercel Serverless Function** (`api/scrape.py`) handles HTTP requests with query params `save` and `fresh`
- **Layered Architecture**:
  ```
  InvestingScraper (Playwright) → TechnicalAnalysisParser (Regex) → SupabaseClient (Database)
  ```
- **Data Flow**: HTML → Markdown → Structured JSON → Supabase JSONB
- **Database Schema**: Matches TypeScript API exactly for seamless integration

## Critical Developer Workflows

### Environment Setup
```bash
# Required order of operations:
pip install -r requirements.txt
playwright install chromium  # Must run after pip install
```

### Local Testing Pattern
```python
# 1. Test scraping in isolation
from src.scrapers.investing_scraper import scrape_eth_technical
result = scrape_eth_technical()

# 2. Test database separately
from src.database.supabase_client import insert_technical_analysis_data
success = insert_technical_analysis_data(result['parsed'], use_service_role=True)
```

## Project-Specific Conventions

### Parser Pattern (Technical Analysis)
See `src/parsers/technical_analysis_parser.py`:
```python
# Format for adding new indicators:
indicator_patterns = [
    {
        "name": "RSI(14)",
        "pattern": r'\|\s*RSI\(14\)\s*\|\s*([\d.]+)\s*\|\s*(\w+)'
    }
]
```

### Database Integration Pattern
- Always use service role key for writes from serverless functions
- JSONB structures must exactly match TypeScript API format
- Use `scrapedAt` timestamp for all data points

## Key Integration Points

### 1. Database Schema Contract 
Must preserve this structure for TypeScript API compatibility:
```sql
technical_analysis (
    technical_indicators JSONB,  # Array of {name, value, action}
    moving_averages JSONB,      # Array of {period, simple, exponential}
    pivot_points JSONB          # Array of {name, s1, s2, s3, r1, r2, r3}
)
```

### 2. Investing.com Integration
- Uses Playwright for JavaScript-rendered content
- Cache busting via URL timestamp when `fresh=true`
- Rate limiting concerns - use sparingly

## Common Pitfalls
- Don't modify JSONB structure without updating TypeScript API
- Cold starts take 5-10s due to Playwright initialization
- Always test database writes with service role key
- Regex patterns may need updates if investing.com changes layout

## Reference Files
- `/src/parsers/technical_analysis_parser.py` - Core parsing logic
- `/src/scrapers/investing_scraper.py` - Scraping implementation
- `/src/database/supabase_client.py` - Database integration
- `/api/scrape.py` - HTTP API endpoint