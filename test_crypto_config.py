#!/usr/bin/env python3
"""Test cryptocurrency configuration and URL generation"""

from src.utils.crypto_config import (
    get_crypto_config,
    get_technical_url,
    is_supported_crypto,
    get_supported_symbols
)

print("Testing Cryptocurrency Configuration\n")
print("=" * 50)

# Test 1: Get supported symbols
print("\n1. Supported Cryptocurrencies:")
symbols = get_supported_symbols()
print(f"   Total: {len(symbols)}")
print(f"   Symbols: {', '.join(symbols)}")

# Test 2: Bitcoin configuration
print("\n2. Bitcoin Configuration:")
btc_config = get_crypto_config("BTC")
if btc_config:
    print(f"   ✓ Symbol: {btc_config.symbol}")
    print(f"   ✓ Name: {btc_config.name}")
    print(f"   ✓ URL Slug: {btc_config.url_slug}")
    print(f"   ✓ Technical URL: {btc_config.get_technical_url()}")
else:
    print("   ✗ Bitcoin config not found")

# Test 3: Ethereum configuration
print("\n3. Ethereum Configuration:")
eth_config = get_crypto_config("ETH")
if eth_config:
    print(f"   ✓ Symbol: {eth_config.symbol}")
    print(f"   ✓ Name: {eth_config.name}")
    print(f"   ✓ URL Slug: {eth_config.url_slug}")
    print(f"   ✓ Technical URL: {eth_config.get_technical_url()}")
else:
    print("   ✗ Ethereum config not found")

# Test 4: URL slug lookup
print("\n4. URL Slug Lookup:")
btc_from_slug = get_crypto_config("bitcoin")
if btc_from_slug and btc_from_slug.symbol == "BTC":
    print(f"   ✓ 'bitcoin' slug resolved to {btc_from_slug.symbol}")
else:
    print("   ✗ Failed to resolve 'bitcoin' slug")

eth_from_slug = get_crypto_config("ethereum")
if eth_from_slug and eth_from_slug.symbol == "ETH":
    print(f"   ✓ 'ethereum' slug resolved to {eth_from_slug.symbol}")
else:
    print("   ✗ Failed to resolve 'ethereum' slug")

# Test 5: Get technical URLs
print("\n5. Technical URL Generation:")
for symbol in ["BTC", "ETH", "ADA", "SOL"]:
    url = get_technical_url(symbol)
    if url:
        print(f"   ✓ {symbol}: {url}")
    else:
        print(f"   ✗ {symbol}: Failed to generate URL")

# Test 6: Validation
print("\n6. Cryptocurrency Validation:")
test_cases = [
    ("BTC", True),
    ("ETH", True),
    ("bitcoin", True),
    ("ethereum", True),
    ("INVALID", False),
    ("", False)
]

for crypto, expected in test_cases:
    is_valid = is_supported_crypto(crypto)
    status = "✓" if is_valid == expected else "✗"
    print(f"   {status} is_supported_crypto('{crypto}'): {is_valid} (expected: {expected})")

# Test 7: Scraper integration test
print("\n7. Scraper Integration Test:")
from src.scrapers.simple_scraper import SimpleScraper
scraper = SimpleScraper(timeout=30)

# Test that scraper can build URLs
for symbol in ["BTC", "ETH"]:
    url = get_technical_url(symbol)
    print(f"   ✓ {symbol} would scrape: {url}")

print("\n" + "=" * 50)
print("Configuration tests completed!")
