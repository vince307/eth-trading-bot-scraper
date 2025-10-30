#!/usr/bin/env python3
"""Debug test for technical indicators parsing"""

from src.scrapers.simple_scraper import SimpleScraper
import json

print("Testing Technical Indicators Parsing...\n")
print("=" * 60)

# Try to scrape and see what we get
scraper = SimpleScraper(timeout=60)

print("\n1. Attempting to scrape Bitcoin technical page...")
result = scraper.scrape_url("https://www.investing.com/crypto/bitcoin/technical")

if result.get('success'):
    print("✓ Scrape successful")
    print(f"  Content length: {result['contentLength']} characters")

    parsed = result.get('parsed')
    if parsed:
        print(f"\n2. Parsed Data:")
        print(f"  Symbol: {parsed.get('symbol')}")
        print(f"  Price: {parsed.get('price')}")
        print(f"  Technical Indicators Count: {len(parsed.get('technicalIndicators', []))}")
        print(f"  Moving Averages Count: {len(parsed.get('movingAverages', []))}")
        print(f"  Pivot Points Count: {len(parsed.get('pivotPoints', []))}")

        if len(parsed.get('technicalIndicators', [])) == 0:
            print("\n⚠ WARNING: Technical indicators are empty!")
            print("\n3. Checking markdown content for technical indicators table...")

            # Save markdown to file for inspection
            with open('debug_markdown.txt', 'w') as f:
                f.write(result['markdown'])
            print("  Saved markdown to debug_markdown.txt")

            # Look for table patterns
            markdown = result['markdown']
            if 'RSI' in markdown:
                print("  ✓ Found 'RSI' in markdown")
            else:
                print("  ✗ 'RSI' NOT found in markdown")

            if 'MACD' in markdown:
                print("  ✓ Found 'MACD' in markdown")
            else:
                print("  ✗ 'MACD' NOT found in markdown")

            if 'technicalIndicatorsTbl' in markdown or 'technical' in markdown.lower():
                print("  ✓ Found technical indicators references")

            # Check for table markers
            table_count = markdown.count('|')
            print(f"  Table markers ('|') found: {table_count}")

            # Show a sample of the markdown around RSI if it exists
            if 'RSI' in markdown:
                idx = markdown.find('RSI')
                sample = markdown[max(0, idx-200):min(len(markdown), idx+200)]
                print(f"\n  Sample around RSI:\n  {sample[:400]}")
        else:
            print("\n✓ Technical indicators parsed successfully!")
            print(f"\nFirst 3 indicators:")
            for ind in parsed['technicalIndicators'][:3]:
                print(f"  - {ind['name']}: {ind['value']} → {ind['action']}")
    else:
        print("✗ No parsed data returned")
        print(f"  Result: {json.dumps(result, indent=2)}")
else:
    print(f"✗ Scrape failed: {result.get('error')}")
    print(f"  Full result: {json.dumps(result, indent=2)}")

print("\n" + "=" * 60)
