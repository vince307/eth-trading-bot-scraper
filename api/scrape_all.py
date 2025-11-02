"""
Vercel Serverless Function - Fetch All Enabled Cryptocurrencies Synchronously

This endpoint fetches technical analysis for all enabled cryptocurrencies
one by one in sequential order (BTC → ETH → SOL) and saves to database.

Endpoint: GET /api/scrape_all
Query Parameters:
    - save (optional): Save to database (default: true)

Example:
    https://your-url.vercel.app/api/scrape_all
    https://your-url.vercel.app/api/scrape_all?save=false

Note: This can take 12+ minutes for 3 cryptos (BTC, ETH, SOL)
"""

from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import sys
import os
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.api.taapi_client import TaapiClient
from src.database.supabase_client import insert_technical_analysis_data
from src.utils.crypto_config import get_enabled_cryptos


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests to fetch all enabled cryptocurrencies."""
        try:
            # Parse query parameters
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)

            # Get save parameter (default: true)
            save_to_db = query_params.get('save', ['true'])[0].lower() != 'false'

            # Get enabled cryptocurrencies from env var
            cryptos = get_enabled_cryptos()

            # Log start
            start_time = time.time()
            print(f"{'='*60}")
            print(f"Fetching All Cryptocurrencies (Synchronous)")
            print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*60}")
            print(f"Cryptocurrencies: {', '.join(cryptos)}")
            print(f"Total: {len(cryptos)} cryptos")
            print(f"Save to database: {save_to_db}")
            print(f"Estimated time: ~{len(cryptos) * 4} minutes")
            print(f"{'='*60}\n")

            # Initialize TAAPI client
            taapi_client = TaapiClient()

            # Results tracking
            results = {
                'success': True,
                'message': f'Fetched {len(cryptos)} cryptocurrencies synchronously',
                'data': {
                    'cryptos': [],
                    'summary': {
                        'total': len(cryptos),
                        'successful': 0,
                        'failed': 0,
                        'total_time_seconds': 0
                    }
                }
            }

            # Fetch each cryptocurrency sequentially
            for i, symbol in enumerate(cryptos, 1):
                print(f"\n[{i}/{len(cryptos)}] Fetching {symbol}...")
                print(f"{'─'*60}")

                crypto_start = time.time()
                crypto_result = {
                    'symbol': symbol,
                    'success': False,
                    'error': None,
                    'data': None,
                    'saved_to_database': False,
                    'fetch_time_seconds': 0
                }

                try:
                    # Fetch technical analysis
                    result = taapi_client.get_technical_analysis(symbol=symbol)

                    if result['success']:
                        data = result['data']

                        # Extract summary info
                        indicators = data.get('technicalIndicators', [])
                        mas = data.get('movingAverages', [])
                        price = data.get('price', 0)
                        summary = data.get('summary', {}).get('overall', 'N/A')

                        print(f"✅ {symbol} fetch successful")
                        print(f"   Price: ${price:,.2f}")
                        print(f"   Indicators: {len(indicators)}/12")
                        print(f"   Moving Averages: {len(mas)}/3")
                        print(f"   Summary: {summary}")

                        crypto_result['success'] = True
                        crypto_result['data'] = {
                            'symbol': symbol,
                            'price': price,
                            'indicator_count': len(indicators),
                            'ma_count': len(mas),
                            'summary': summary
                        }

                        # Save to database if requested
                        if save_to_db:
                            saved = insert_technical_analysis_data(data, use_service_role=True)
                            crypto_result['saved_to_database'] = saved

                            if saved:
                                print(f"   ✅ Saved to database")
                                results['data']['summary']['successful'] += 1
                            else:
                                print(f"   ❌ Failed to save to database")
                                crypto_result['error'] = 'Database save failed'
                                results['data']['summary']['failed'] += 1
                        else:
                            print(f"   ⚠️  Skipped database save (save=false)")
                            results['data']['summary']['successful'] += 1

                    else:
                        error_msg = result.get('message', 'Unknown error')
                        print(f"❌ {symbol} fetch failed: {error_msg}")
                        crypto_result['error'] = error_msg
                        results['data']['summary']['failed'] += 1

                except Exception as e:
                    error_msg = str(e)
                    print(f"❌ {symbol} fetch error: {error_msg}")
                    crypto_result['error'] = error_msg
                    results['data']['summary']['failed'] += 1

                # Record fetch time
                crypto_result['fetch_time_seconds'] = time.time() - crypto_start
                print(f"   Time: {crypto_result['fetch_time_seconds']:.1f}s")

                # Add to results
                results['data']['cryptos'].append(crypto_result)

                # Wait before next crypto (except after last one)
                if i < len(cryptos):
                    wait_time = 5
                    print(f"\n⏳ Waiting {wait_time} seconds before next crypto...")
                    time.sleep(wait_time)

            # Calculate total time
            total_time = time.time() - start_time
            results['data']['summary']['total_time_seconds'] = total_time

            # Print final summary
            print(f"\n{'='*60}")
            print(f"FETCH COMPLETE")
            print(f"{'='*60}")
            print(f"Success: {results['data']['summary']['successful']}/{len(cryptos)} cryptos")
            print(f"Failed: {results['data']['summary']['failed']}/{len(cryptos)} cryptos")
            print(f"Total time: {total_time / 60:.1f} minutes")
            print(f"Average per crypto: {total_time / len(cryptos):.1f} seconds")
            print(f"{'='*60}\n")

            # Update success status
            results['success'] = results['data']['summary']['failed'] == 0

            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(results, indent=2).encode())

        except Exception as e:
            # Error response
            error_response = {
                'success': False,
                'message': f'Error fetching cryptocurrencies: {str(e)}',
                'error': str(e)
            }

            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_response, indent=2).encode())
