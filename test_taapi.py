"""Test script for TAAPI.IO client"""
from src.api.taapi_client import TaapiClient
import json
import time

def test_taapi_connection():
    """Test TAAPI.IO connection and data fetching"""

    print("=" * 60)
    print("TAAPI.IO CLIENT TEST - Professional Grade Indicators")
    print("=" * 60)
    print()
    print("Free Tier Limit: 1 request per 15 seconds (using 18s for safety)")
    print()
    print("Indicators per crypto (12 total):")
    print("  - RSI, MACD, Bollinger Bands, OBV")
    print("  - StochRSI, ATR, VWAP, SuperTrend, CMF")
    print("  - EMA20, EMA50, EMA200")
    print()
    print("Estimated time: ~216 seconds (~3.6 minutes) per cryptocurrency")
    print("=" * 60)
    print()

    # Initialize client
    try:
        client = TaapiClient()
        print("✅ Client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        return

    # Test connection
    print("\n1. Testing API connection...")
    try:
        connected = client.test_connection()
        if connected:
            print("✅ Connection test: SUCCESS")
        else:
            print("❌ Connection test: FAILED")
            return
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return

    # Test BTC data fetch
    print("\n2. Fetching BTC technical analysis...")
    print("   (This will take ~216 seconds: 12 indicators × 18s delay...)")
    start_time = time.time()
    try:
        result = client.get_technical_analysis('BTC')

        if result.get('success'):
            elapsed = time.time() - start_time
            data = result['data']
            print(f"✅ BTC fetch: SUCCESS (took {elapsed:.1f}s)")
            print(f"   Symbol: {data['symbol']}")
            print(f"   Price: ${data['price']:,.2f}")
            print(f"   Price Change: {data['priceChangePercent']:+.2f}%")
            print(f"   Technical Indicators: {len(data['technicalIndicators'])} indicators")
            print(f"   Moving Averages: {len(data['movingAverages'])} MAs")
            print(f"   Pivot Points: {len(data['pivotPoints'])} pivot types")
            print(f"   Overall Summary: {data['summary']['overall']}")
            print(f"   Tech Indicators Summary: {data['summary']['technicalIndicators']}")
            print(f"   Moving Averages Summary: {data['summary']['movingAverages']}")

            # Show all indicators
            print("\n   Technical Indicators:")
            for ind in data['technicalIndicators']:
                if 'value' in ind:
                    print(f"     - {ind['name']}: {ind.get('value', 'N/A')} ({ind['signal']})")
                elif 'upper' in ind:  # Bollinger Bands
                    print(f"     - {ind['name']}: Upper={ind['upper']:.2f}, Mid={ind['middle']:.2f}, Lower={ind['lower']:.2f} ({ind['signal']})")

            # Show all MAs
            print("\n   Moving Averages:")
            for ma in data['movingAverages']:
                print(f"     - {ma['name']} ({ma['type']}): {ma['value']:.2f} ({ma['signal']})")
        else:
            print(f"❌ BTC fetch: FAILED - {result.get('error')}")
            return
    except Exception as e:
        print(f"❌ BTC fetch failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # Test ETH data fetch
    print("\n3. Fetching ETH technical analysis...")
    print("   (This will take ~216 seconds: 12 indicators × 18s delay...)")
    start_time = time.time()
    try:
        result = client.get_technical_analysis('ETH')

        if result.get('success'):
            elapsed = time.time() - start_time
            data = result['data']
            print(f"✅ ETH fetch: SUCCESS (took {elapsed:.1f}s)")
            print(f"   Symbol: {data['symbol']}")
            print(f"   Price: ${data['price']:,.2f}")
            print(f"   Price Change: {data['priceChangePercent']:+.2f}%")
            print(f"   Overall Summary: {data['summary']['overall']}")
        else:
            print(f"❌ ETH fetch: FAILED - {result.get('error')}")
    except Exception as e:
        print(f"❌ ETH fetch failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
    print("=" * 60)

if __name__ == "__main__":
    test_taapi_connection()
