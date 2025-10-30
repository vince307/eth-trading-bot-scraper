#!/usr/bin/env python3
"""Test Bitcoin scraping functionality"""

from src.scrapers.simple_scraper import scrape_crypto_technical
import json

print('Testing Bitcoin scraping...')
result = scrape_crypto_technical(crypto='BTC')

if result.get('success'):
    parsed = result['parsed']
    print(f"✓ Success! Symbol: {parsed['symbol']}")
    print(f"  Price: ${parsed['price']}")
    print(f"  Price Change: {parsed['priceChange']} ({parsed['priceChangePercent']}%)")
    print(f"  Overall Summary: {parsed['summary']['overall']}")
    print(f"  Technical Indicators: {len(parsed['technicalIndicators'])} found")
    print(f"  Moving Averages: {len(parsed['movingAverages'])} found")
    print(f"  Pivot Points: {len(parsed['pivotPoints'])} found")
    print("\nSample Technical Indicators:")
    for indicator in parsed['technicalIndicators'][:3]:
        print(f"    {indicator['name']}: {indicator['value']} -> {indicator['action']}")
else:
    print(f"✗ Failed: {result.get('error')}")
