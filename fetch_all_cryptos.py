"""
Fetch Technical Analysis for All Enabled Cryptocurrencies

This script fetches technical analysis data for all cryptocurrencies
defined in the SUPPORTED_CRYPTOS environment variable and saves to database.

Usage:
    # Fetch all enabled cryptos (from env var)
    python3 fetch_all_cryptos.py

    # Fetch specific cryptos (override env var)
    python3 fetch_all_cryptos.py BTC ETH SOL

    # Dry run (don't save to database)
    python3 fetch_all_cryptos.py --dry-run

Environment Variables:
    SUPPORTED_CRYPTOS - Comma-separated list of cryptos (default: BTC,ETH,SOL)
    TAAPI_API_KEY - TAAPI.IO API key
    SUPABASE_* - Supabase credentials
"""

import sys
import time
from datetime import datetime
from src.api.taapi_client import TaapiClient
from src.database.supabase_client import insert_technical_analysis_data
from src.utils.crypto_config import get_enabled_cryptos


def fetch_all_cryptos(cryptos=None, save_to_db=True):
    """
    Fetch technical analysis for multiple cryptocurrencies.

    Args:
        cryptos: List of crypto symbols (default: from env var)
        save_to_db: Whether to save to database (default: True)

    Returns:
        dict: Results with success/failure counts
    """
    # Get cryptos from env var if not provided
    if not cryptos:
        cryptos = get_enabled_cryptos()

    print(f"{'='*60}")
    print(f"Fetching Technical Analysis")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    print(f"Cryptocurrencies: {', '.join(cryptos)}")
    print(f"Total: {len(cryptos)} cryptos")
    print(f"Save to database: {save_to_db}")
    print(f"\nEstimated time: ~{len(cryptos) * 4} minutes")
    print(f"(~4 minutes per crypto with retry mechanism)\n")
    print(f"{'='*60}\n")

    # Initialize client
    client = TaapiClient()

    # Track results
    results = {
        'success': [],
        'failed': [],
        'total_time': 0
    }

    start_time = time.time()

    # Fetch each crypto
    for i, symbol in enumerate(cryptos, 1):
        print(f"\n[{i}/{len(cryptos)}] Fetching {symbol}...")
        print(f"{'─'*60}")

        crypto_start = time.time()

        try:
            # Fetch data
            result = client.get_technical_analysis(symbol=symbol)

            if result['success']:
                data = result['data']['parsed']

                # Display summary
                indicators = data.get('technicalIndicators', [])
                mas = data.get('movingAverages', [])
                price = data.get('price', 0)

                print(f"✅ {symbol} fetch successful")
                print(f"   Price: ${price:,.2f}")
                print(f"   Indicators: {len(indicators)}/12")
                print(f"   Moving Averages: {len(mas)}/3")
                print(f"   Summary: {data.get('summary', {}).get('overall', 'N/A')}")

                # Save to database
                if save_to_db:
                    saved = insert_technical_analysis_data(data, use_service_role=True)
                    if saved:
                        print(f"   ✅ Saved to database")
                        results['success'].append(symbol)
                    else:
                        print(f"   ❌ Failed to save to database")
                        results['failed'].append(symbol)
                else:
                    print(f"   ⚠️  Skipped database save (dry-run mode)")
                    results['success'].append(symbol)

            else:
                print(f"❌ {symbol} fetch failed: {result.get('message', 'Unknown error')}")
                results['failed'].append(symbol)

        except Exception as e:
            print(f"❌ {symbol} fetch error: {e}")
            results['failed'].append(symbol)

        crypto_time = time.time() - crypto_start
        print(f"   Time: {crypto_time:.1f}s")

        # Add delay between cryptos to be respectful to API
        # (Not strictly necessary since TaapiClient already has rate limiting,
        #  but good practice)
        if i < len(cryptos):
            print(f"\n⏳ Waiting 5 seconds before next crypto...")
            time.sleep(5)

    # Calculate total time
    results['total_time'] = time.time() - start_time

    # Print summary
    print(f"\n{'='*60}")
    print(f"FETCH COMPLETE")
    print(f"{'='*60}\n")
    print(f"Success: {len(results['success'])}/{len(cryptos)} cryptos")
    if results['success']:
        print(f"  ✅ {', '.join(results['success'])}")
    if results['failed']:
        print(f"Failed: {len(results['failed'])}/{len(cryptos)} cryptos")
        print(f"  ❌ {', '.join(results['failed'])}")
    print(f"\nTotal time: {results['total_time'] / 60:.1f} minutes")
    print(f"Average per crypto: {results['total_time'] / len(cryptos):.1f} seconds")
    print(f"\n{'='*60}")

    return results


def main():
    """Main entry point."""
    # Parse command line arguments
    dry_run = '--dry-run' in sys.argv
    args = [arg for arg in sys.argv[1:] if not arg.startswith('--')]

    # Get cryptos from command line or env var
    cryptos = [c.upper() for c in args] if args else None

    # Fetch all cryptos
    results = fetch_all_cryptos(cryptos=cryptos, save_to_db=not dry_run)

    # Exit with error code if any failed
    sys.exit(0 if not results['failed'] else 1)


if __name__ == "__main__":
    main()
