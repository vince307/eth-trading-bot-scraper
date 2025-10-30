#!/usr/bin/env python3
"""Test parser with sample markdown data"""

from src.parsers.technical_analysis_parser import TechnicalAnalysisParser

# Sample markdown that should contain technical indicators
sample_markdown = """
# Bitcoin Technical Analysis

BTC/USD 98,750.00

## Technical Indicators

| Name | Value | Action |
|------|-------|--------|
| RSI(14) | 57.18 | Buy |
| STOCH(9,6) | 71.23 | Buy |
| STOCHRSI(14) | 45.12 | Neutral |
| MACD(12,26) | 123.45 | Buy |
| ADX(14) | 25.67 | Buy |
| Williams %R | -35.21 | Buy |
| CCI(14) | 89.34 | Buy |
| ATR(14) | 1234.56 | Less Volatility |
| Ultimate Oscillator | 52.34 | Buy |
| ROC | 2.45 | Buy |
| Bull/Bear Power(13) | 234.56 | Buy |
| Highs/Lows(14) | -0.0045 | Neutral |

## Moving Averages

| Period | Simple MA | Action | Exponential MA | Action |
|--------|-----------|--------|----------------|--------|
| MA5 | 98500.00 | Buy | 98600.00 | Buy |
| MA10 | 97800.00 | Buy | 98100.00 | Buy |
| MA20 | 96500.00 | Buy | 97200.00 | Buy |

## Summary: Strong Buy
"""

print("Testing parser with sample markdown...")
print("=" * 60)

result = TechnicalAnalysisParser.parse_markdown(sample_markdown, "https://test.com")

if result:
    print(f"\n✓ Parser returned data")
    print(f"  Symbol: {result['symbol']}")
    print(f"  Price: {result['price']}")

    tech_indicators = result.get('technicalIndicators', [])
    print(f"\n  Technical Indicators: {len(tech_indicators)}")
    if tech_indicators:
        for ind in tech_indicators[:5]:
            print(f"    - {ind['name']}: {ind['value']} → {ind['action']}")
    else:
        print("    ⚠ No technical indicators extracted!")

    moving_avgs = result.get('movingAverages', [])
    print(f"\n  Moving Averages: {len(moving_avgs)}")
    if moving_avgs:
        for ma in moving_avgs[:3]:
            print(f"    - MA{ma['period']}: {ma['simple']['value']} → {ma['simple']['action']}")
    else:
        print("    ⚠ No moving averages extracted!")
else:
    print("✗ Parser returned None")

print("\n" + "=" * 60)

# Now let's test what patterns actually match
print("\nDirect pattern matching test:")
print("=" * 60)

import re

test_line = "| RSI(14) | 57.18 | Buy |"
pattern = r'\|\s*RSI\(14\)\s*\|\s*([\d.]+)\s*\|\s*(\w+)'

match = re.search(pattern, test_line, re.IGNORECASE)
if match:
    print(f"✓ Pattern matched: {match.group(1)} → {match.group(2)}")
else:
    print(f"✗ Pattern did NOT match")
    print(f"  Test line: '{test_line}'")
    print(f"  Pattern: '{pattern}'")

print("\n" + "=" * 60)
