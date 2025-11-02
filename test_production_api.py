"""Test production API to verify symbol is correctly saved"""
import requests
import json
import time

def test_production_api():
    """Test production API with different cryptos"""

    print("=" * 70)
    print("PRODUCTION API TEST - Symbol Verification")
    print("=" * 70)
    print()

    base_url = "https://eth-trading-bot-scraper.vercel.app/api/scrape"

    # Test different cryptocurrencies
    test_cases = [
        {"crypto": "ETH", "expected_price_range": (3000, 5000)},
        {"crypto": "BTC", "expected_price_range": (100000, 120000)},
        {"crypto": "SOL", "expected_price_range": (100, 300)},
    ]

    for i, test in enumerate(test_cases, 1):
        crypto = test["crypto"]
        expected_range = test["expected_price_range"]

        print(f"\n{i}. Testing {crypto}")
        print("-" * 70)

        # Make API call (without save to avoid polluting database during test)
        url = f"{base_url}?crypto={crypto}&save=false"
        print(f"URL: {url}")
        print()

        try:
            print("⏳ Making API request...")
            start_time = time.time()
            response = requests.get(url, timeout=300)  # 5 minute timeout
            elapsed = time.time() - start_time

            print(f"⏱️  Response time: {elapsed:.1f}s")
            print(f"📊 Status code: {response.status_code}")
            print()

            if response.status_code == 200:
                data = response.json()

                # Check if successful
                if data.get('success'):
                    parsed = data.get('data', {}).get('parsed', {})

                    # Extract key fields
                    symbol = parsed.get('symbol', 'NOT FOUND')
                    price = parsed.get('price', 0)
                    price_change_pct = parsed.get('priceChangePercent', 0)
                    indicators_count = len(parsed.get('technicalIndicators', []))
                    ma_count = len(parsed.get('movingAverages', []))

                    # Verify symbol
                    symbol_match = symbol == crypto
                    price_match = expected_range[0] <= price <= expected_range[1]

                    print("=" * 70)
                    print(f"RESULTS FOR {crypto}")
                    print("=" * 70)
                    print(f"Symbol in response: {symbol}")
                    print(f"  ✅ CORRECT" if symbol_match else f"  ❌ WRONG (expected {crypto})")
                    print()
                    print(f"Price: ${price:,.2f}")
                    if price > 0:
                        print(f"  ✅ IN EXPECTED RANGE ({expected_range[0]:,} - {expected_range[1]:,})" if price_match else f"  ⚠️  OUT OF EXPECTED RANGE")
                    else:
                        print(f"  ❌ PRICE IS ZERO (CoinGecko fetch may have failed)")
                    print()
                    print(f"24h Change: {price_change_pct:+.2f}%")
                    print(f"Indicators: {indicators_count}/12")
                    print(f"Moving Averages: {ma_count}/3")
                    print()

                    # Show what would be saved to database
                    print("📝 Data that WOULD be saved to database:")
                    print(f"   symbol: '{symbol}'")
                    print(f"   price: {price}")
                    print(f"   priceChangePercent: {price_change_pct}")
                    print()

                    if not symbol_match:
                        print("🔍 DEBUGGING INFO:")
                        print(f"   Requested crypto: {crypto}")
                        print(f"   Symbol in response: {symbol}")
                        print(f"   This indicates the API is not correctly passing the symbol!")
                        print()
                        print("   Response structure:")
                        print(f"   {json.dumps(parsed, indent=2)[:500]}...")

                else:
                    print(f"❌ API returned success=false")
                    print(f"Error: {data.get('error', 'Unknown')}")
                    print(f"Details: {data.get('details', 'None')}")

            else:
                print(f"❌ HTTP Error {response.status_code}")
                print(f"Response: {response.text[:500]}")

        except requests.exceptions.Timeout:
            print(f"❌ Request timed out after 300 seconds")
        except Exception as e:
            print(f"❌ Error: {e}")

        # Wait between requests
        if i < len(test_cases):
            print()
            print(f"⏳ Waiting 5 seconds before next test...")
            time.sleep(5)

    print()
    print("=" * 70)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 70)

if __name__ == "__main__":
    test_production_api()
