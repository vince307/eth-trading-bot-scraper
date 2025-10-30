"""
Supabase database client for storing technical analysis data
Matches the schema from eth-trading-bot-api database
"""
import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from supabase import create_client, Client
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class SupabaseClient:
    """
    Client for interacting with Supabase database.
    Provides methods to insert technical analysis data.
    """

    def __init__(
        self,
        url: Optional[str] = None,
        key: Optional[str] = None,
        use_service_role: bool = False
    ):
        """
        Initialize Supabase client.

        Args:
            url: Supabase URL (defaults to SUPABASE_URL env var)
            key: Supabase key (defaults to SUPABASE_ANON_KEY or SUPABASE_SERVICE_ROLE_KEY)
            use_service_role: Use service role key instead of anon key
        """
        self.url = url or os.getenv("SUPABASE_URL")
        if not self.url:
            raise ValueError("SUPABASE_URL environment variable not set")

        if key:
            self.key = key
        elif use_service_role:
            self.key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            if not self.key:
                raise ValueError("SUPABASE_SERVICE_ROLE_KEY environment variable not set")
        else:
            self.key = os.getenv("SUPABASE_ANON_KEY")
            if not self.key:
                raise ValueError("SUPABASE_ANON_KEY environment variable not set")

        self.client: Client = create_client(self.url, self.key)
        logger.info("Supabase client initialized")

    def insert_technical_analysis(self, data: Dict[str, Any]) -> bool:
        """
        Insert technical analysis data into the database.

        Args:
            data: Parsed technical analysis data dictionary

        Returns:
            True if successful, False otherwise

        Schema matches:
            - symbol: VARCHAR(10)
            - price: DECIMAL(20, 8)
            - price_change: DECIMAL(20, 8)
            - price_change_percent: DECIMAL(10, 4)
            - overall_summary: VARCHAR(50)
            - technical_indicators_summary: VARCHAR(50)
            - moving_averages_summary: VARCHAR(50)
            - technical_indicators: JSONB
            - moving_averages: JSONB
            - pivot_points: JSONB
            - source_url: TEXT
            - scraped_at: TIMESTAMPTZ
        """
        try:
            # Prepare data for database insertion
            db_data = {
                "symbol": data.get("symbol", "UNKNOWN"),
                "price": float(data.get("price", 0)),
                "price_change": float(data.get("priceChange", 0)),
                "price_change_percent": float(data.get("priceChangePercent", 0)),
                "overall_summary": data.get("summary", {}).get("overall", "Neutral"),
                "technical_indicators_summary": data.get("summary", {}).get("technicalIndicators", "Neutral"),
                "moving_averages_summary": data.get("summary", {}).get("movingAverages", "Neutral"),
                "technical_indicators": json.dumps(data.get("technicalIndicators", [])),
                "moving_averages": json.dumps(data.get("movingAverages", [])),
                "pivot_points": json.dumps(data.get("pivotPoints", [])),
                "source_url": data.get("sourceUrl", ""),
                "scraped_at": data.get("scrapedAt", datetime.utcnow().isoformat() + "Z")
            }

            logger.info(f"Inserting technical analysis data for {db_data['symbol']} at ${db_data['price']}")

            # Insert into Supabase
            response = self.client.table("technical_analysis").insert(db_data).execute()

            if response.data:
                logger.info(f"Successfully inserted technical analysis data - ID: {response.data[0].get('id')}")
                return True
            else:
                logger.error("Failed to insert technical analysis data - no data returned")
                return False

        except Exception as e:
            logger.error(f"Error inserting technical analysis data: {e}")
            return False

    def get_latest_technical_analysis(
        self,
        symbol: Optional[str] = None,
        limit: int = 10
    ) -> Optional[list]:
        """
        Retrieve latest technical analysis records.

        Args:
            symbol: Trading symbol to filter by (if None, retrieves all symbols)
            limit: Maximum number of records to retrieve

        Returns:
            List of technical analysis records or None if error
        """
        try:
            query = self.client.table("technical_analysis").select("*")

            # Filter by symbol if provided
            if symbol:
                query = query.eq("symbol", symbol)

            response = query.order("created_at", desc=True).limit(limit).execute()

            if response.data:
                logger.info(f"Retrieved {len(response.data)} technical analysis records")
                return response.data
            return []

        except Exception as e:
            logger.error(f"Error retrieving technical analysis data: {e}")
            return None

    def get_latest_by_symbols(
        self,
        symbols: list,
        limit_per_symbol: int = 1
    ) -> Optional[Dict[str, list]]:
        """
        Retrieve latest technical analysis records for multiple symbols.

        Args:
            symbols: List of trading symbols (e.g., ["BTC", "ETH", "ADA"])
            limit_per_symbol: Maximum number of records per symbol

        Returns:
            Dictionary mapping symbols to their latest records, or None if error

        Example:
            >>> client.get_latest_by_symbols(["BTC", "ETH"], limit_per_symbol=5)
            {"BTC": [...], "ETH": [...]}
        """
        try:
            results = {}
            for symbol in symbols:
                records = self.get_latest_technical_analysis(symbol=symbol, limit=limit_per_symbol)
                if records:
                    results[symbol] = records

            logger.info(f"Retrieved data for {len(results)} symbols")
            return results

        except Exception as e:
            logger.error(f"Error retrieving multi-symbol technical analysis data: {e}")
            return None

    def test_connection(self) -> bool:
        """
        Test database connection.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Try to query the technical_analysis table
            response = self.client.table("technical_analysis") \
                .select("id") \
                .limit(1) \
                .execute()

            logger.info("Database connection test successful")
            return True

        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False


# Convenience function for standalone usage
def insert_technical_analysis_data(
    data: Dict[str, Any],
    use_service_role: bool = False
) -> bool:
    """
    Convenience function to insert technical analysis data.

    Args:
        data: Parsed technical analysis data
        use_service_role: Use service role key instead of anon key

    Returns:
        True if successful, False otherwise
    """
    client = SupabaseClient(use_service_role=use_service_role)
    return client.insert_technical_analysis(data)
