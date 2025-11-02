"""
CoinGecko API client for fetching cryptocurrency price and market data
Provides real-time price, market cap, volume, and 24h change data
"""
import os
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from src.utils.crypto_config import get_crypto_config

# Load environment variables
load_dotenv()


class CoinGeckoClient:
    """Client for interacting with CoinGecko API."""

    def __init__(self):
        """Initialize the CoinGecko client."""
        self.api_key = os.getenv('COINGECKO_API_KEY')
        self.base_url = "https://api.coingecko.com/api/v3"

        # API key is optional for Demo plan endpoints
        # If not provided, will use public endpoints (with lower rate limits)
        if not self.api_key:
            print("Warning: COINGECKO_API_KEY not found. Using public API (lower rate limits).")

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make a request to the CoinGecko API.

        Args:
            endpoint: API endpoint path (e.g., "/simple/price")
            params: Query parameters

        Returns:
            API response as dictionary

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        url = f"{self.base_url}{endpoint}"

        # Add API key to headers if available
        headers = {
            "Accept": "application/json"
        }

        if self.api_key:
            headers["x-cg-demo-api-key"] = self.api_key

        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        return response.json()

    def test_connection(self) -> bool:
        """
        Test connection to CoinGecko API.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Test with a simple ping endpoint
            headers = {"Accept": "application/json"}
            if self.api_key:
                headers["x-cg-demo-api-key"] = self.api_key

            response = requests.get(
                f"{self.base_url}/ping",
                headers=headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False

    def get_price_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get current price and market data for a cryptocurrency.

        Args:
            symbol: Cryptocurrency symbol (e.g., "BTC", "ETH")

        Returns:
            Dictionary containing:
            {
                'success': bool,
                'data': {
                    'price': float,
                    'priceChange24h': float,
                    'priceChangePercent24h': float,
                    'marketCap': float,
                    'volume24h': float,
                    'lastUpdated': int (UNIX timestamp)
                },
                'error': str (if failed)
            }
        """
        try:
            # Get crypto config to find CoinGecko ID
            config = get_crypto_config(symbol)
            if not config:
                return {
                    'success': False,
                    'error': f'Unsupported cryptocurrency: {symbol}'
                }

            # Call CoinGecko /simple/price endpoint
            params = {
                'ids': config.coingecko_id,
                'vs_currencies': 'usd',
                'include_market_cap': 'true',
                'include_24hr_vol': 'true',
                'include_24hr_change': 'true',
                'include_last_updated_at': 'true'
            }

            response = self._make_request('/simple/price', params)

            # Extract data from response
            coin_data = response.get(config.coingecko_id, {})

            if not coin_data:
                return {
                    'success': False,
                    'error': f'No data returned for {symbol}'
                }

            # Parse and format data
            price = coin_data.get('usd', 0.0)
            price_change_percent = coin_data.get('usd_24h_change', 0.0)
            market_cap = coin_data.get('usd_market_cap', 0.0)
            volume_24h = coin_data.get('usd_24h_vol', 0.0)
            last_updated = coin_data.get('last_updated_at', 0)

            # Calculate price change in USD
            price_change = (price * price_change_percent) / 100 if price else 0.0

            return {
                'success': True,
                'data': {
                    'price': price,
                    'priceChange24h': price_change,
                    'priceChangePercent24h': price_change_percent,
                    'marketCap': market_cap,
                    'volume24h': volume_24h,
                    'lastUpdated': last_updated,
                    'source': 'coingecko'
                }
            }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'API request failed: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }

    def get_ohlc_data(self, symbol: str, days: int = 365) -> Dict[str, Any]:
        """
        Get OHLC (Open, High, Low, Close) candlestick data.

        Args:
            symbol: Cryptocurrency symbol (e.g., "BTC", "ETH")
            days: Number of days of data (1, 7, 14, 30, 90, 180, 365)

        Returns:
            Dictionary containing:
            {
                'success': bool,
                'data': [
                    [timestamp, open, high, low, close],
                    ...
                ],
                'error': str (if failed)
            }
        """
        try:
            # Get crypto config to find CoinGecko ID
            config = get_crypto_config(symbol)
            if not config:
                return {
                    'success': False,
                    'error': f'Unsupported cryptocurrency: {symbol}'
                }

            # Validate days parameter
            valid_days = [1, 7, 14, 30, 90, 180, 365]
            if days not in valid_days:
                return {
                    'success': False,
                    'error': f'Invalid days parameter. Must be one of: {valid_days}'
                }

            # Call CoinGecko OHLC endpoint
            endpoint = f'/coins/{config.coingecko_id}/ohlc'
            params = {
                'vs_currency': 'usd',
                'days': str(days)
            }

            response = self._make_request(endpoint, params)

            return {
                'success': True,
                'data': response
            }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'API request failed: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }


def get_price_data(symbol: str) -> Dict[str, Any]:
    """
    Convenience function to get price data without instantiating client.

    Args:
        symbol: Cryptocurrency symbol (e.g., "BTC", "ETH")

    Returns:
        Price data dictionary
    """
    client = CoinGeckoClient()
    return client.get_price_data(symbol)


def get_ohlc_data(symbol: str, days: int = 365) -> Dict[str, Any]:
    """
    Convenience function to get OHLC data without instantiating client.

    Args:
        symbol: Cryptocurrency symbol (e.g., "BTC", "ETH")
        days: Number of days of data (default: 365 to get enough candles for MA200)

    Returns:
        OHLC data dictionary
    """
    client = CoinGeckoClient()
    return client.get_ohlc_data(symbol, days)


def get_complete_data(symbol: str) -> Dict[str, Any]:
    """
    Convenience function to get both price and OHLC data.

    Args:
        symbol: Cryptocurrency symbol (e.g., "BTC", "ETH")

    Returns:
        Dictionary with price_data and ohlc_data
    """
    client = CoinGeckoClient()
    price_result = client.get_price_data(symbol)
    ohlc_result = client.get_ohlc_data(symbol, days=365)

    return {
        'success': price_result.get('success') and ohlc_result.get('success'),
        'price_data': price_result.get('data') if price_result.get('success') else None,
        'ohlc_data': ohlc_result.get('data') if ohlc_result.get('success') else None,
        'error': price_result.get('error') or ohlc_result.get('error')
    }
