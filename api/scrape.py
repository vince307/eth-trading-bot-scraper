"""
Vercel serverless function for scraping cryptocurrency technical analysis
Endpoint: GET /api/scrape?crypto=BTC&url=...&save=true&fresh=true
"""
import os
import sys
import json
import logging
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.scrapers.vercel_scraper import VercelScraper
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
            crypto = query_params.get('crypto', [None])[0]
            url = query_params.get('url', [None])[0]
            save_to_db = query_params.get('save', ['false'])[0].lower() == 'true'
            cache_bust = query_params.get('fresh', ['false'])[0].lower() == 'true'

            # Validate crypto parameter if provided
            if crypto and not url:
                if not is_supported_crypto(crypto):
                    supported = get_supported_symbols()
                    self._send_error_response(
                        400,
                        f"Unsupported cryptocurrency: {crypto}",
                        f"Supported cryptocurrencies: {', '.join(supported)}"
                    )
                    return

            logger.info(f"Processing scrape request - Crypto: {crypto}, URL: {url}, Save: {save_to_db}, Fresh: {cache_bust}")

            # Initialize Vercel-optimized scraper
            # Tries Playwright first, falls back to HTTP if not available
            scraper = VercelScraper(timeout=60000)

            # Scrape the page
            result = scraper.scrape_crypto_technical_analysis(
                crypto=crypto,
                url=url,
                cache_bust=cache_bust
            )

            if not result.get("success"):
                self._send_error_response(
                    500,
                    "Failed to scrape data",
                    result.get("error", "Unknown error")
                )
                return

            # Save to database if requested
            saved_to_db = False
            if save_to_db and result.get("parsed"):
                try:
                    db_client = SupabaseClient(use_service_role=True)
                    saved_to_db = db_client.insert_technical_analysis(result["parsed"])
                    if saved_to_db:
                        logger.info("Data successfully saved to database")
                    else:
                        logger.warning("Failed to save data to database")
                except Exception as e:
                    logger.error(f"Error saving to database: {e}")

            # Prepare response matching TypeScript API format
            response_data = {
                "success": True,
                "message": f"Technical analysis data fetched and parsed successfully{', and saved to database' if saved_to_db else ''}",
                "data": {
                    "raw": {
                        "url": result["url"],
                        "title": result["title"],
                        "content": result["markdown"],
                        "html": result.get("html", ""),
                        "contentLength": result["contentLength"],
                        "scrapedAt": result["scrapedAt"]
                    },
                    "parsed": result["parsed"],
                    "savedToDatabase": saved_to_db
                }
            }

            # Add warning if present (from fallback scraper)
            if "warning" in result:
                response_data["warning"] = result["warning"]

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
