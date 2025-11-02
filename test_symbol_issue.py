"""Test script to verify symbol is correctly set in responses"""
from src.api.taapi_client import TaapiClient
import json

def test_symbols():
    """Test that different symbols return correct symbol in data"""

    print("=" * 60)
    print("SYMBOL VERIFICATION TEST")
    print("=" * 60)
    print()

    client = TaapiClient()

    # Test quick fetch for BTC (just RSI to see symbol)
    print("Testing BTC symbol...")
    print("-" * 60)

    try:
        # Manually call _fetch_indicator_with_retry to get just one indicator (faster)
        symbol_pair = "BTC/USDT"
        response = client._fetch_indicator_with_retry("rsi", symbol_pair, "binance", "1h", {"period": 14})

        if response:
            print(f"✅ BTC API call successful")
            print(f"   Response keys: {list(response.keys())}")
            print(f"   Symbol in response: {response.get('symbol', 'NOT FOUND')}")
            print(f"   Full response: {json.dumps(response, indent=2)}")
        else:
            print("❌ BTC API call failed")

    except Exception as e:
        print(f"❌ Error: {e}")

    print()
    print("Testing ETH symbol...")
    print("-" * 60)

    try:
        # Test ETH
        symbol_pair = "ETH/USDT"
        response = client._fetch_indicator_with_retry("rsi", symbol_pair, "binance", "1h", {"period": 14})

        if response:
            print(f"✅ ETH API call successful")
            print(f"   Response keys: {list(response.keys())}")
            print(f"   Symbol in response: {response.get('symbol', 'NOT FOUND')}")
            print(f"   Full response: {json.dumps(response, indent=2)}")
        else:
            print("❌ ETH API call failed")

    except Exception as e:
        print(f"❌ Error: {e}")

    print()
    print("=" * 60)
    print("Now testing full get_technical_analysis...")
    print("=" * 60)
    print()

    # Test full analysis for ETH (shorter test)
    print("Calling get_technical_analysis('ETH')...")
    print("This will take ~4 minutes...")
    print()

    result = client.get_technical_analysis("ETH")

    if result.get('success'):
        data = result['data']
        print(f"✅ ETH full analysis successful")
        print()
        print(f"Symbol in result['data']: {data.get('symbol', 'NOT FOUND')}")
        print(f"Price: ${data.get('price', 0):,.2f}")
        print()
        print("First few keys of data:")
        for key in list(data.keys())[:10]:
            value = data[key]
            if isinstance(value, (int, float, str)):
                print(f"  {key}: {value}")
            elif isinstance(value, dict):
                print(f"  {key}: {{...}} (dict with {len(value)} keys)")
            elif isinstance(value, list):
                print(f"  {key}: [...] (list with {len(value)} items)")
    else:
        print(f"❌ Failed: {result.get('error')}")

    print()
    print("=" * 60)
    print("✅ TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_symbols()
