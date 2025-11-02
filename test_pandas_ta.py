"""
Test script for pandas-ta implementation
Tests CoinGecko OHLC + pandas-ta indicators calculator
"""
import time
from src.api.coingecko_client import CoinGeckoClient
from src.api.indicators_calculator import IndicatorsCalculator


def test_pandas_ta():
    """Test the complete pandas-ta implementation."""
    print("=" * 80)
    print("Testing CoinGecko OHLC + pandas-ta Implementation")
    print("=" * 80)

    # Initialize clients
    coingecko_client = CoinGeckoClient()
    calculator = IndicatorsCalculator()

    # Test with ETH
    crypto = "ETH"
    print(f"\n🔍 Testing {crypto}...\n")

    start_time = time.time()

    # Step 1: Fetch price data
    print("📊 Step 1: Fetching price data from CoinGecko...")
    price_result = coingecko_client.get_price_data(crypto)
    if not price_result.get("success"):
        print(f"❌ Failed to fetch price data: {price_result.get('error')}")
        return

    price_data = price_result.get("data")
    print(f"✅ Price: ${price_data.get('price'):,.2f}")
    print(f"   24h Change: ${price_data.get('priceChange24h'):,.2f} ({price_data.get('priceChangePercent24h'):.2f}%)")
    print(f"   Market Cap: ${price_data.get('marketCap'):,.0f}")
    print(f"   Volume 24h: ${price_data.get('volume24h'):,.0f}")

    # Step 2: Fetch OHLC data
    print("\n📈 Step 2: Fetching OHLC data (90 days)...")
    ohlc_result = coingecko_client.get_ohlc_data(crypto, days=90)
    if not ohlc_result.get("success"):
        print(f"❌ Failed to fetch OHLC data: {ohlc_result.get('error')}")
        return

    ohlc_data = ohlc_result.get("data")
    print(f"✅ Fetched {len(ohlc_data)} candles")

    # Step 3: Calculate indicators
    print("\n🔢 Step 3: Calculating technical indicators with pandas-ta...")
    try:
        indicators_data = calculator.calculate_indicators(ohlc_data, crypto)
        print("✅ Technical indicators calculated successfully")
    except Exception as e:
        print(f"❌ Failed to calculate indicators: {e}")
        import traceback
        traceback.print_exc()
        return

    # Step 4: Display results
    elapsed_time = time.time() - start_time

    print("\n" + "=" * 80)
    print(f"✅ COMPLETE DATA FOR {crypto}")
    print("=" * 80)

    print(f"\n💰 Price Information:")
    print(f"   Price: ${indicators_data.get('price', 0.0):,.2f}")
    print(f"   24h Change: ${indicators_data.get('priceChange', 0.0):,.2f} ({indicators_data.get('priceChangePercent', 0.0):.2f}%)")

    print(f"\n📊 Summary Signals:")
    summary = indicators_data.get("summary", {})
    print(f"   Overall: {summary.get('overall', 'N/A')}")
    print(f"   Technical Indicators: {summary.get('technicalIndicators', 'N/A')}")
    print(f"   Moving Averages: {summary.get('movingAverages', 'N/A')}")

    print(f"\n📈 Technical Indicators ({len(indicators_data.get('technicalIndicators', []))} indicators):")
    for indicator in indicators_data.get("technicalIndicators", []):
        name = indicator.get("name")
        value = indicator.get("value")
        signal = indicator.get("signal")
        if value is not None:
            if isinstance(value, float):
                print(f"   • {name}: {value:.2f} → {signal}")
            else:
                print(f"   • {name}: {value} → {signal}")
        else:
            print(f"   • {name}: {signal}")

    print(f"\n📉 Moving Averages ({len(indicators_data.get('movingAverages', []))} MAs):")
    for ma in indicators_data.get("movingAverages", []):
        name = ma.get("name")
        value = ma.get("value")
        signal = ma.get("signal")
        ma_type = ma.get("type")
        print(f"   • {name} ({ma_type}): ${value:,.2f} → {signal}")

    print(f"\n🎯 Pivot Points:")
    for pivot in indicators_data.get("pivotPoints", []):
        pivot_type = pivot.get("type")
        print(f"   Type: {pivot_type}")
        print(f"   Pivot: ${pivot.get('pivot'):,.2f}")
        print(f"   R1: ${pivot.get('r1'):,.2f}  S1: ${pivot.get('s1'):,.2f}")
        print(f"   R2: ${pivot.get('r2'):,.2f}  S2: ${pivot.get('s2'):,.2f}")
        print(f"   R3: ${pivot.get('r3'):,.2f}  S3: ${pivot.get('s3'):,.2f}")

    print("\n" + "=" * 80)
    print(f"⏱️  Total Time: {elapsed_time:.2f} seconds")
    print("=" * 80)

    # Verify all expected indicators are present
    expected_indicators = [
        "RSI(14)", "MACD(12,26)", "Bollinger Bands(20,2)", "OBV",
        "StochRSI", "ATR(14)", "VWAP", "SuperTrend", "CMF(20)"
    ]

    actual_indicators = [ind.get("name") for ind in indicators_data.get("technicalIndicators", [])]

    print("\n🔍 Indicator Verification:")
    for expected in expected_indicators:
        if expected in actual_indicators:
            print(f"   ✅ {expected}")
        else:
            print(f"   ❌ {expected} - MISSING")

    print(f"\n📊 Total Indicators: {len(actual_indicators)}/12")
    print(f"   Technical: {len(indicators_data.get('technicalIndicators', []))}")
    print(f"   Moving Averages: {len(indicators_data.get('movingAverages', []))}")

    if elapsed_time < 60:
        print(f"\n✅ SUCCESS: Completed in {elapsed_time:.2f}s (well under 60s Vercel timeout)")
    else:
        print(f"\n⚠️  WARNING: Took {elapsed_time:.2f}s (may timeout on Vercel free tier)")


if __name__ == "__main__":
    test_pandas_ta()
