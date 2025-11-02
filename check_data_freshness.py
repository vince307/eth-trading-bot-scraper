"""
Data Freshness Checker for Technical Analysis Database

This script checks when the technical analysis data was last updated in Supabase.
Useful for ensuring your trading bot has fresh data before making decisions.

Usage:
    python3 check_data_freshness.py

    # Check specific crypto
    python3 check_data_freshness.py BTC

    # Check all cryptos
    python3 check_data_freshness.py --all

    # JSON output
    python3 check_data_freshness.py --json
"""

import sys
import json
from datetime import datetime, timezone, timedelta
from src.database.supabase_client import SupabaseClient


def check_freshness(symbol='BTC', json_output=False):
    """
    Check data freshness for a given cryptocurrency.

    Args:
        symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH')
        json_output: If True, output JSON instead of human-readable text

    Returns:
        dict: Freshness data with age, status, etc.
    """
    try:
        client = SupabaseClient()

        # Query latest data for symbol
        result = client.supabase.table('technical_analysis')\
            .select('*')\
            .eq('symbol', symbol)\
            .order('created_at', desc=True)\
            .limit(1)\
            .execute()

        if not result.data:
            if json_output:
                return {
                    'symbol': symbol,
                    'status': 'no_data',
                    'message': 'No data found in database'
                }
            else:
                print(f"❌ {symbol}: No data found in database")
                return None

        latest = result.data[0]

        # Calculate age
        scraped_at = datetime.fromisoformat(latest['scraped_at'].replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        age = now - scraped_at

        # Determine status
        if age < timedelta(hours=1):
            status = 'fresh'
            emoji = '✅'
        elif age < timedelta(hours=2):
            status = 'acceptable'
            emoji = '⚠️ '
        else:
            status = 'stale'
            emoji = '❌'

        # Format output
        if json_output:
            return {
                'symbol': symbol,
                'status': status,
                'age_minutes': age.total_seconds() / 60,
                'age_hours': age.total_seconds() / 3600,
                'scraped_at': latest['scraped_at'],
                'price': float(latest['price']),
                'indicator_count': len(latest.get('technical_indicators', [])),
                'overall_summary': latest.get('overall_summary', 'N/A')
            }
        else:
            age_str = f"{age.total_seconds() / 60:.1f} minutes" if age < timedelta(hours=1) \
                     else f"{age.total_seconds() / 3600:.1f} hours"

            print(f"{emoji} {symbol}:")
            print(f"   Age: {age_str}")
            print(f"   Scraped: {scraped_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            print(f"   Price: ${float(latest['price']):,.2f}")
            print(f"   Indicators: {len(latest.get('technical_indicators', []))} indicators")
            print(f"   Summary: {latest.get('overall_summary', 'N/A')}")

            return {
                'status': status,
                'age_seconds': age.total_seconds()
            }

    except Exception as e:
        if json_output:
            return {
                'symbol': symbol,
                'status': 'error',
                'error': str(e)
            }
        else:
            print(f"❌ Error checking {symbol}: {e}")
            return None


def check_all_cryptos(json_output=False):
    """Check freshness for all cryptocurrencies in database."""
    from src.utils.crypto_config import get_supported_symbols

    symbols = get_supported_symbols()

    if not json_output:
        print(f"{'='*60}")
        print(f"Data Freshness Check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")

    results = {}
    for symbol in symbols:
        result = check_freshness(symbol, json_output)
        if result:
            results[symbol] = result
        if not json_output:
            print()  # Add spacing between symbols

    if json_output:
        print(json.dumps(results, indent=2))

    return results


def main():
    """Main entry point."""
    # Parse command line arguments
    json_output = '--json' in sys.argv
    check_all = '--all' in sys.argv

    # Remove flags from argv
    args = [arg for arg in sys.argv[1:] if not arg.startswith('--')]

    if check_all:
        check_all_cryptos(json_output)
    elif args:
        symbol = args[0].upper()
        if not json_output:
            print(f"{'='*60}")
            print(f"Data Freshness Check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*60}\n")

        result = check_freshness(symbol, json_output)

        if json_output and result:
            print(json.dumps(result, indent=2))
    else:
        # Default: check BTC
        if not json_output:
            print(f"{'='*60}")
            print(f"Data Freshness Check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*60}\n")

        result = check_freshness('BTC', json_output)

        if json_output and result:
            print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
