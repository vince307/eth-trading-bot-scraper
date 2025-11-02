"""Script to check database for symbol issues"""
from src.database.supabase_client import SupabaseClient
import json
from datetime import datetime, timedelta

def check_database():
    """Check database for recent entries and symbol distribution"""

    print("=" * 60)
    print("DATABASE CHECK - Technical Analysis Table")
    print("=" * 60)
    print()

    # Initialize client
    try:
        client = SupabaseClient(use_service_role=True)
        print("✅ Database client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        return

    # Test connection
    print("\n1. Testing database connection...")
    if not client.test_connection():
        print("❌ Database connection failed")
        return
    print("✅ Database connection successful")

    # Get latest records for all symbols
    print("\n2. Fetching latest records for each symbol...")
    symbols = ["BTC", "ETH", "SOL", "ADA", "DOT", "LINK", "MATIC", "LTC", "XRP", "DOGE"]

    print("-" * 60)
    print(f"{'Symbol':<10} {'Count':<10} {'Latest Price':<15} {'Last Updated':<25}")
    print("-" * 60)

    total_count = 0
    for symbol in symbols:
        records = client.get_latest_technical_analysis(symbol=symbol, limit=1)
        if records and len(records) > 0:
            count_records = client.client.table("technical_analysis").select("id", count="exact").eq("symbol", symbol).execute()
            count = count_records.count if hasattr(count_records, 'count') else 0
            total_count += count

            latest = records[0]
            price = latest.get('price', 0)
            created_at = latest.get('created_at', 'N/A')
            print(f"{symbol:<10} {count:<10} ${price:<14,.2f} {created_at:<25}")
        else:
            print(f"{symbol:<10} {'0':<10} {'N/A':<15} {'N/A':<25}")

    print("-" * 60)
    print(f"Total records in database: {total_count}")
    print()

    # Get last 24 hours of data
    print("\n3. Recent entries (last 24 hours)...")
    print("-" * 60)

    try:
        # Get all records from last 24 hours
        yesterday = (datetime.utcnow() - timedelta(hours=24)).isoformat() + "Z"
        response = client.client.table("technical_analysis") \
            .select("*") \
            .gte("created_at", yesterday) \
            .order("created_at", desc=True) \
            .execute()

        if response.data:
            print(f"Found {len(response.data)} records in last 24 hours")
            print()
            print(f"{'ID':<10} {'Symbol':<10} {'Price':<15} {'Created At':<30}")
            print("-" * 60)
            for record in response.data[:20]:  # Show first 20
                print(f"{record['id']:<10} {record['symbol']:<10} ${record['price']:<14,.2f} {record['created_at']:<30}")

            # Count by symbol in last 24 hours
            print()
            print("\nSymbol distribution (last 24 hours):")
            print("-" * 60)
            symbol_counts = {}
            for record in response.data:
                sym = record['symbol']
                symbol_counts[sym] = symbol_counts.get(sym, 0) + 1

            for sym, count in sorted(symbol_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"  {sym}: {count} records")

        else:
            print("No records found in last 24 hours")

    except Exception as e:
        print(f"❌ Error fetching recent records: {e}")

    # Check if BTC symbol has non-BTC data
    print("\n4. Checking for symbol mismatches...")
    print("-" * 60)

    try:
        # Get BTC records
        btc_records = client.get_latest_technical_analysis(symbol="BTC", limit=10)
        if btc_records:
            print(f"Latest 10 BTC records:")
            print()
            for i, record in enumerate(btc_records, 1):
                price = record.get('price', 0)
                created = record.get('created_at', 'N/A')
                source = record.get('source_url', 'N/A')

                # Check if price looks like ETH (around $3-4k) or other crypto
                symbol_guess = "BTC"
                if 3000 < price < 5000:
                    symbol_guess = "ETH? (price suggests)"
                elif 100 < price < 200:
                    symbol_guess = "SOL? (price suggests)"
                elif 0 < price < 10:
                    symbol_guess = "ADA/DOT/LINK? (price suggests)"

                print(f"  {i}. Price: ${price:>12,.2f}  Created: {created}  Guess: {symbol_guess}")
                if "ETH" in source or "eth" in source.lower():
                    print(f"      ⚠️  WARNING: Source URL contains 'ETH': {source}")

        # Get ETH records
        print()
        eth_records = client.get_latest_technical_analysis(symbol="ETH", limit=10)
        if eth_records:
            print(f"Latest 10 ETH records:")
            print()
            for i, record in enumerate(eth_records, 1):
                price = record.get('price', 0)
                created = record.get('created_at', 'N/A')
                print(f"  {i}. Price: ${price:>12,.2f}  Created: {created}")
        else:
            print("⚠️  No ETH records found (all data might be under BTC symbol!)")

    except Exception as e:
        print(f"❌ Error checking for mismatches: {e}")

    print()
    print("=" * 60)
    print("✅ DATABASE CHECK COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    check_database()
