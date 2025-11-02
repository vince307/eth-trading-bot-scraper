"""
Vercel serverless function for fetching cryptocurrency technical analysis
Endpoint: GET /api/scrape?crypto=BTC&save=true&exchange=binance&interval=1h
"""
import os
import sys
import json
import logging
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.api.coingecko_client import CoinGeckoClient
from src.api.indicators_calculator import IndicatorsCalculator
from src.database.supabase_client import SupabaseClient
from src.utils.crypto_config import is_supported_crypto, get_supported_symbols

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class handler(BaseHTTPRequestHandler):
    """HTTP request handler for Vercel serverless function."""

    def do_GET(self):
        """Handle GET requests."""
        try:
            # Parse URL and query parameters
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)

            # Extract parameters
            crypto = query_params.get('crypto', ['BTC'])[0]
            save_to_db = query_params.get('save', ['false'])[0].lower() == 'true'
            exchange = query_params.get('exchange', ['binance'])[0]
            interval = query_params.get('interval', ['1h'])[0]

            # Validate crypto parameter
            if not is_supported_crypto(crypto):
                supported = get_supported_symbols()
                self._send_error_response(
                    400,
                    f"Unsupported cryptocurrency: {crypto}",
                    f"Supported cryptocurrencies: {', '.join(supported)}"
                )
                return

            logger.info(f"Fetching technical analysis - Crypto: {crypto}, Save: {save_to_db}")

            # Initialize clients
            coingecko_client = CoinGeckoClient()
            calculator = IndicatorsCalculator()

            # Step 1: Fetch price data from CoinGecko (fast, ~1 second)
            logger.info("Fetching price data from CoinGecko...")
            price_result = coingecko_client.get_price_data(crypto)

            if not price_result.get("success"):
                self._send_error_response(
                    500,
                    "Failed to fetch price data from CoinGecko",
                    price_result.get('error', 'Unknown error')
                )
                return

            price_data = price_result.get("data")
            logger.info(f"Price data fetched: ${price_data.get('price'):,.2f}")

            # Step 2: Fetch OHLC data from CoinGecko (fast, ~1 second)
            # Using 365 days to get enough candles for MA200 calculation
            logger.info("Fetching OHLC data from CoinGecko...")
            ohlc_result = coingecko_client.get_ohlc_data(crypto, days=365)

            if not ohlc_result.get("success"):
                self._send_error_response(
                    500,
                    "Failed to fetch OHLC data from CoinGecko",
                    ohlc_result.get('error', 'Unknown error')
                )
                return

            ohlc_data = ohlc_result.get("data")
            logger.info(f"OHLC data fetched: {len(ohlc_data)} candles")

            # Step 3: Calculate technical indicators using pandas-ta (fast, <1 second)
            logger.info("Calculating technical indicators...")
            try:
                indicators_data = calculator.calculate_indicators(ohlc_data, crypto)
            except Exception as e:
                self._send_error_response(
                    500,
                    "Failed to calculate technical indicators",
                    str(e)
                )
                return

            # Step 4: Merge price data with calculated indicators
            indicators_data["price"] = price_data.get("price", 0.0)
            indicators_data["priceChange"] = price_data.get("priceChange24h", 0.0)
            indicators_data["priceChangePercent"] = price_data.get("priceChangePercent24h", 0.0)
            indicators_data["marketData"] = {
                "marketCap": price_data.get("marketCap", 0.0),
                "volume24h": price_data.get("volume24h", 0.0),
                "lastUpdated": price_data.get("lastUpdated", 0)
            }
            logger.info("Technical indicators calculated and merged successfully")

            result = {
                "success": True,
                "data": indicators_data,
                "source": "coingecko+pandas-ta",
                "scrapedAt": indicators_data.get("scrapedAt")
            }

            # Save to database if requested
            saved_to_db = False
            if save_to_db and result.get("data"):
                try:
                    db_client = SupabaseClient(use_service_role=True)
                    saved_to_db = db_client.insert_technical_analysis(result["data"])
                    if saved_to_db:
                        logger.info("Data successfully saved to database")
                    else:
                        logger.warning("Failed to save data to database")
                except Exception as e:
                    logger.error(f"Error saving to database: {e}")

            # Prepare response matching TypeScript API format
            response_data = {
                "success": True,
                "message": f"Technical analysis data fetched successfully from {result['source']}{', and saved to database' if saved_to_db else ''}",
                "data": {
                    "parsed": result["data"],
                    "savedToDatabase": saved_to_db,
                    "source": result["source"],
                    "metadata": {
                        "exchange": exchange,
                        "interval": interval,
                        "fetchedAt": result["scrapedAt"]
                    }
                }
            }

            self._send_json_response(200, response_data)

        except Exception as e:
            logger.error(f"Error processing request: {e}", exc_info=True)
            self._send_error_response(500, "Internal server error", str(e))

    def _send_json_response(self, status_code: int, data: dict):
        """Send JSON response."""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        response_json = json.dumps(data, indent=2)
        self.wfile.write(response_json.encode('utf-8'))

    def _send_error_response(self, status_code: int, error: str, details: str = ""):
        """Send error response."""
        error_data = {
            "success": False,
            "error": error,
            "details": details
        }
        self._send_json_response(status_code, error_data)

    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
