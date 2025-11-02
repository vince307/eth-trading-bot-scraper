"""Test script for combined TAAPI + CoinGecko data"""
from src.api.taapi_client import TaapiClient
from src.api.coingecko_client import CoinGeckoClient
import json
import time

def test_combined_eth():
    """Test combined data fetching for ETH"""

    print("=" * 60)
    print("COMBINED TEST - COINGECKO + TAAPI.IO")
    print("Testing with Ethereum (ETH)")
    print("=" * 60)
    print()

    crypto = "ETH"

    # Step 1: Fetch price data from CoinGecko (fast)
    print("STEP 1: Fetching price data from CoinGecko...")
    print("-" * 60)
    try:
        cg_client = CoinGeckoClient()
        price_result = cg_client.get_price_data(crypto)

        if price_result.get('success'):
            price_data = price_result['data']
            print(f"✅ Price data fetched successfully")
            print(f"   Price: ${price_data['price']:,.2f}")
            print(f"   24h Change: ${price_data['priceChange24h']:+,.2f} ({price_data['priceChangePercent24h']:+.2f}%)")
            print(f"   Market Cap: ${price_data['marketCap']:,.0f}")
            print(f"   24h Volume: ${price_data['volume24h']:,.0f}")
        else:
            print(f"❌ Failed to fetch price data: {price_result.get('error')}")
            price_data = None
    except Exception as e:
        print(f"❌ Error fetching price data: {e}")
        price_data = None

    # Step 2: Fetch technical indicators from TAAPI.IO (slow)
    print("\nSTEP 2: Fetching technical indicators from TAAPI.IO...")
    print("-" * 60)
    print("This will take ~4 minutes (12 indicators × 18s delay + retries)")
    print()

    start_time = time.time()
    try:
        taapi_client = TaapiClient()
        result = taapi_client.get_technical_analysis(crypto)

        if result.get('success'):
            elapsed = time.time() - start_time
            ta_data = result['data']
            print(f"✅ Technical analysis fetched successfully (took {elapsed:.1f}s)")
            print(f"   Technical Indicators: {len(ta_data['technicalIndicators'])} indicators")
            print(f"   Moving Averages: {len(ta_data['movingAverages'])} MAs")
            print(f"   Overall Summary: {ta_data['summary']['overall']}")
        else:
            print(f"❌ Failed to fetch technical analysis: {result.get('error')}")
            ta_data = None
    except Exception as e:
        print(f"❌ Error fetching technical analysis: {e}")
        ta_data = None

    # Step 3: Merge the data
    print("\nSTEP 3: Merging CoinGecko price data with TAAPI indicators...")
    print("-" * 60)

    if price_data and ta_data:
        # Merge price data into technical analysis
        ta_data['price'] = price_data['price']
        ta_data['priceChange'] = price_data['priceChange24h']
        ta_data['priceChangePercent'] = price_data['priceChangePercent24h']

        # Add market data
        ta_data['marketData'] = {
            'marketCap': price_data['marketCap'],
            'volume24h': price_data['volume24h'],
            'lastUpdated': price_data['lastUpdated']
        }

        print("✅ Data merged successfully!")
        print()
        print("=" * 60)
        print("FINAL COMBINED DATA")
        print("=" * 60)
        print(f"Symbol: {ta_data['symbol']}")
        print(f"Price: ${ta_data['price']:,.2f}")
        print(f"24h Change: ${ta_data['priceChange']:+,.2f} ({ta_data['priceChangePercent']:+.2f}%)")
        print(f"Market Cap: ${ta_data['marketData']['marketCap']:,.0f}")
        print(f"24h Volume: ${ta_data['marketData']['volume24h']:,.0f}")
        print()
        print(f"Overall Summary: {ta_data['summary']['overall']}")
        print(f"Technical Indicators: {ta_data['summary']['technicalIndicators']}")
        print(f"Moving Averages: {ta_data['summary']['movingAverages']}")
        print()
        print("Technical Indicators:")
        for ind in ta_data['technicalIndicators']:
            if 'value' in ind:
                print(f"  - {ind['name']}: {ind.get('value', 'N/A')} ({ind['signal']})")
            elif 'upper' in ind:
                print(f"  - {ind['name']}: Upper=${ind['upper']:.2f}, Mid=${ind['middle']:.2f}, Lower=${ind['lower']:.2f} ({ind['signal']})")

        print()
        print("Moving Averages:")
        for ma in ta_data['movingAverages']:
            print(f"  - {ma['name']} ({ma['type']}): ${ma['value']:.2f} ({ma['signal']})")

        print()
        print("=" * 60)
        print("FULL JSON (first 100 lines)")
        print("=" * 60)
        json_output = json.dumps(ta_data, indent=2)
        lines = json_output.split('\n')
        print('\n'.join(lines[:100]))
        if len(lines) > 100:
            print(f"... ({len(lines) - 100} more lines)")

    else:
        print("❌ Cannot merge data - missing price data or technical analysis")

    print()
    print("=" * 60)
    print("✅ TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_combined_eth()
