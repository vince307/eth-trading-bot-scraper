"""Test script for CoinGecko client"""
from src.api.coingecko_client import CoinGeckoClient
import json

def test_coingecko():
    """Test CoinGecko API client"""

    print("=" * 60)
    print("COINGECKO CLIENT TEST")
    print("=" * 60)
    print()

    # Initialize client
    try:
        client = CoinGeckoClient()
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

    # Test BTC price data
    print("\n2. Fetching BTC price data...")
    try:
        result = client.get_price_data('BTC')

        if result.get('success'):
            data = result['data']
            print(f"✅ BTC price fetch: SUCCESS")
            print("=" * 60)
            print(f"  Price: ${data['price']:,.2f}")
            print(f"  24h Change: ${data['priceChange24h']:+,.2f} ({data['priceChangePercent24h']:+.2f}%)")
            print(f"  Market Cap: ${data['marketCap']:,.0f}")
            print(f"  24h Volume: ${data['volume24h']:,.0f}")
            print(f"  Last Updated: {data['lastUpdated']} (UNIX)")
        else:
            print(f"❌ BTC price fetch: FAILED - {result.get('error')}")
            return
    except Exception as e:
        print(f"❌ BTC price fetch failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # Test ETH price data
    print("\n3. Fetching ETH price data...")
    try:
        result = client.get_price_data('ETH')

        if result.get('success'):
            data = result['data']
            print(f"✅ ETH price fetch: SUCCESS")
            print("=" * 60)
            print(f"  Price: ${data['price']:,.2f}")
            print(f"  24h Change: ${data['priceChange24h']:+,.2f} ({data['priceChangePercent24h']:+.2f}%)")
            print(f"  Market Cap: ${data['marketCap']:,.0f}")
            print(f"  24h Volume: ${data['volume24h']:,.0f}")
            print(f"  Last Updated: {data['lastUpdated']} (UNIX)")

            print("\n" + "=" * 60)
            print("FULL JSON RESPONSE")
            print("=" * 60)
            print(json.dumps(data, indent=2))
        else:
            print(f"❌ ETH price fetch: FAILED - {result.get('error')}")
    except Exception as e:
        print(f"❌ ETH price fetch failed: {e}")
        import traceback
        traceback.print_exc()

    # Test OHLC data
    print("\n4. Fetching BTC OHLC data (1 day)...")
    try:
        result = client.get_ohlc_data('BTC', days=1)

        if result.get('success'):
            data = result['data']
            print(f"✅ BTC OHLC fetch: SUCCESS")
            print("=" * 60)
            print(f"  Total candles: {len(data)}")
            if len(data) > 0:
                print(f"  First candle: {data[0]}")
                print(f"  Last candle: {data[-1]}")
                print(f"\n  Latest candle breakdown:")
                print(f"    Timestamp: {data[-1][0]}")
                print(f"    Open: ${data[-1][1]:,.2f}")
                print(f"    High: ${data[-1][2]:,.2f}")
                print(f"    Low: ${data[-1][3]:,.2f}")
                print(f"    Close: ${data[-1][4]:,.2f}")
        else:
            print(f"❌ BTC OHLC fetch: FAILED - {result.get('error')}")
    except Exception as e:
        print(f"❌ BTC OHLC fetch failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_coingecko()
