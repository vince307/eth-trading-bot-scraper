"""
Health Check Script for TAAPI.IO Scraper API

This script verifies that the Vercel API endpoint is functioning correctly
by fetching BTC technical analysis and checking the response.

Usage:
    python3 health_check.py

    # Check specific deployment
    python3 health_check.py https://your-deployment.vercel.app

    # Save to log file
    python3 health_check.py >> health_check.log
"""

import requests
import json
import sys
from datetime import datetime


def check_health(base_url=None):
    """
    Check API health by fetching BTC technical analysis.

    Args:
        base_url: Optional base URL (e.g., https://your-deployment.vercel.app)
                 If not provided, uses localhost for local testing

    Returns:
        bool: True if healthy, False otherwise
    """
    # Default to localhost for local testing
    if not base_url:
        base_url = "http://localhost:3000"

    url = f"{base_url}/api/scrape?crypto=BTC"

    print(f"{'='*60}")
    print(f"Health Check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Endpoint: {url}")
    print(f"{'='*60}\n")

    try:
        print("⏳ Fetching BTC technical analysis...")
        print("   (This may take up to 5 minutes due to rate limiting)\n")

        response = requests.get(url, timeout=300)  # 5 minute timeout

        # Check HTTP status
        if response.status_code != 200:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False

        # Parse JSON
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON response: {e}")
            print(f"   Response: {response.text[:200]}")
            return False

        # Check success status
        if not data.get('success'):
            print(f"❌ API returned error")
            print(f"   Message: {data.get('message', 'No message')}")
            return False

        # Check data structure
        parsed = data.get('data', {}).get('parsed', {})

        symbol = parsed.get('symbol', 'UNKNOWN')
        price = parsed.get('price', 0)
        indicators = parsed.get('technicalIndicators', [])
        moving_averages = parsed.get('movingAverages', [])

        # Print results
        print(f"✅ API is healthy!\n")
        print(f"Symbol: {symbol}")
        print(f"Price: ${price:,.2f}")
        print(f"Technical Indicators: {len(indicators)}/12")
        print(f"Moving Averages: {len(moving_averages)}/3")

        if len(indicators) < 8:
            print(f"\n⚠️  Warning: Only {len(indicators)} indicators fetched (expected 12)")
            print(f"   This may indicate API issues or rate limiting")

        # Check if data was saved to database
        saved = data.get('data', {}).get('savedToDatabase', False)
        if saved:
            print(f"\n✅ Data saved to database")
        else:
            print(f"\n⚠️  Data NOT saved to database (save=true not specified)")

        print(f"\n{'='*60}")
        return True

    except requests.Timeout:
        print(f"❌ Request timeout (>5 minutes)")
        print(f"   API may be down or experiencing issues")
        return False

    except requests.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        print(f"   Check if the API is deployed and accessible")
        return False

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    # Get base URL from command line argument
    base_url = sys.argv[1] if len(sys.argv) > 1 else None

    if base_url and not base_url.startswith('http'):
        base_url = f"https://{base_url}"

    # Run health check
    success = check_health(base_url)

    # Exit with appropriate code
    sys.exit(0 if success else 1)
