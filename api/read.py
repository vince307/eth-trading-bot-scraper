"""
Vercel serverless function for reading technical analysis data from database
Endpoint: GET /api/read?crypto=BTC&limit=10
"""
import os
import sys
import json
import logging
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database.supabase_client import SupabaseClient
from src.utils.crypto_config import is_supported_crypto, get_supported_symbols

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class handler(BaseHTTPRequestHandler):
    """HTTP request handler for reading data from database."""

    def do_GET(self):
        """Handle GET requests."""
        try:
            # Parse URL and query parameters
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)

            # Extract parameters
            crypto = query_params.get('crypto', [None])[0]
            limit = int(query_params.get('limit', ['1'])[0])

            # Validate crypto parameter
            if crypto and not is_supported_crypto(crypto):
                supported = get_supported_symbols()
                self._send_error_response(
                    400,
                    f"Unsupported cryptocurrency: {crypto}",
                    f"Supported cryptocurrencies: {', '.join(supported)}"
                )
                return

            logger.info(f"Reading data - Crypto: {crypto or 'ALL'}, Limit: {limit}")

            # Connect to database
            db_client = SupabaseClient()

            # Get data
            if crypto:
                data = db_client.get_latest_technical_analysis(symbol=crypto.upper(), limit=limit)
            else:
                data = db_client.get_latest_technical_analysis(limit=limit)

            if data is None:
                self._send_error_response(500, "Database error", "Failed to retrieve data")
                return

            if len(data) == 0:
                self._send_json_response(200, {
                    "success": True,
                    "message": f"No data found for {crypto or 'any cryptocurrency'}",
                    "data": []
                })
                return

            # Format response
            response_data = {
                "success": True,
                "message": f"Retrieved {len(data)} record(s)",
                "data": data,
                "count": len(data)
            }

            self._send_json_response(200, response_data)

        except ValueError as e:
            self._send_error_response(400, "Invalid parameter", str(e))
        except Exception as e:
            logger.error(f"Error processing request: {e}", exc_info=True)
            self._send_error_response(500, "Internal server error", str(e))

    def _send_json_response(self, status_code: int, data: dict):
        """Send JSON response."""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        response_json = json.dumps(data, indent=2, default=str)
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
