"""Test script for TAAPI.IO client - ETH only"""
from src.api.taapi_client import TaapiClient
import json
import time

def test_eth():
    """Test ETH data fetching"""

    print("=" * 60)
    print("TAAPI.IO CLIENT TEST - ETH Only")
    print("=" * 60)
    print()
    print("Fetching 12 professional indicators for Ethereum...")
    print("Estimated time: ~216 seconds (~3.6 minutes)")
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

    # Test ETH data fetch
    print("\n2. Fetching ETH technical analysis...")
    print("   (This will take ~216 seconds: 12 indicators × 18s delay...)")
    start_time = time.time()
    try:
        result = client.get_technical_analysis('ETH')

        if result.get('success'):
            elapsed = time.time() - start_time
            data = result['data']
            print(f"\n✅ ETH fetch: SUCCESS (took {elapsed:.1f}s)")
            print("=" * 60)
            print(f"Symbol: {data['symbol']}")
            print(f"Price: ${data['price']:,.2f}")
            print(f"Price Change: {data['priceChangePercent']:+.2f}%")
            print(f"Technical Indicators: {len(data['technicalIndicators'])} indicators")
            print(f"Moving Averages: {len(data['movingAverages'])} MAs")
            print(f"Pivot Points: {len(data['pivotPoints'])} pivot types")
            print()
            print(f"Overall Summary: {data['summary']['overall']}")
            print(f"Tech Indicators Summary: {data['summary']['technicalIndicators']}")
            print(f"Moving Averages Summary: {data['summary']['movingAverages']}")

            # Show all indicators
            print("\n" + "=" * 60)
            print("TECHNICAL INDICATORS")
            print("=" * 60)
            for ind in data['technicalIndicators']:
                if 'value' in ind:
                    print(f"  {ind['name']}: {ind.get('value', 'N/A')} ({ind['signal']})")
                elif 'upper' in ind:  # Bollinger Bands
                    print(f"  {ind['name']}: Upper={ind['upper']:.2f}, Mid={ind['middle']:.2f}, Lower={ind['lower']:.2f} ({ind['signal']})")
                elif 'macd' in ind:  # MACD
                    print(f"  {ind['name']}: MACD={ind.get('macd', 'N/A')}, Signal={ind.get('macdSignal', 'N/A')}, Histogram={ind.get('histogram', 'N/A')} ({ind['signal']})")

            # Show all MAs
            print("\n" + "=" * 60)
            print("MOVING AVERAGES")
            print("=" * 60)
            for ma in data['movingAverages']:
                print(f"  {ma['name']} ({ma['type']}): {ma['value']:.2f} ({ma['signal']})")

            # Show pivot points
            print("\n" + "=" * 60)
            print("PIVOT POINTS")
            print("=" * 60)
            for pivot in data['pivotPoints']:
                print(f"  {pivot['type']}: {pivot['value']:.2f}")

            # Show full JSON (pretty)
            print("\n" + "=" * 60)
            print("FULL JSON RESPONSE (parsed)")
            print("=" * 60)
            print(json.dumps(data, indent=2))

        else:
            print(f"❌ ETH fetch: FAILED - {result.get('error')}")
            return
    except Exception as e:
        print(f"❌ ETH fetch failed: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n" + "=" * 60)
    print("✅ TEST COMPLETED SUCCESSFULLY")
    print("=" * 60)

if __name__ == "__main__":
    test_eth()
