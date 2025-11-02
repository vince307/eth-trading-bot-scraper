"""
TAAPI.IO API client for fetching cryptocurrency technical analysis data
Alternative to web scraping - uses official TAAPI.IO REST API
"""
import os
import logging
import requests
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()


class TaapiClient:
    """
    Client for TAAPI.IO technical analysis API.
    Fetches pre-calculated technical indicators for cryptocurrencies.

    Includes rate limiting to comply with free tier restrictions:
    - Free tier: 5000 calls/day, but limited to ~10 calls/minute
    - Adds configurable delay between requests
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        rate_limit_delay: float = 18.0
    ):
        """
        Initialize TAAPI.IO client.

        Args:
            api_key: TAAPI.IO API secret key (defaults to TAAPI_API_KEY env var)
            rate_limit_delay: Seconds to wait between API calls (default: 18s for free tier safety)
                             Free tier: 1 request per 15 seconds (using 18s for safety margin)
        """
        self.api_key = api_key or os.getenv("TAAPI_API_KEY")
        if not self.api_key:
            raise ValueError("TAAPI_API_KEY environment variable not set")

        self.base_url = "https://api.taapi.io"
        self.timeout = 30  # seconds
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0

        logger.info(f"TAAPI.IO client initialized (rate limit: {rate_limit_delay}s between requests)")

    def _wait_for_rate_limit(self):
        """
        Enforce rate limiting by waiting if necessary.
        Ensures minimum delay between consecutive API calls.
        """
        if self.rate_limit_delay <= 0:
            return

        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last_request
            logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def get_technical_analysis(
        self,
        symbol: str,
        exchange: str = "binance",
        interval: str = "1h"
    ) -> Dict[str, Any]:
        """
        Get comprehensive technical analysis for a cryptocurrency.
        Returns data in format compatible with our database schema.

        Args:
            symbol: Cryptocurrency symbol (e.g., "BTC", "ETH")
            exchange: Exchange to fetch data from (default: "binance")
            interval: Time interval (e.g., "1h", "4h", "1d")

        Returns:
            Dictionary with parsed technical analysis data matching database schema
        """
        try:
            logger.info(f"Fetching technical analysis for {symbol} from {exchange} ({interval})")

            # Normalize symbol to USDT pair for API
            trading_pair = f"{symbol}/USDT"

            # Fetch all required indicators (individually for free tier)
            bulk_data = self._fetch_indicators_individually(trading_pair, exchange, interval)

            # Get current price
            price_data = self._get_price(trading_pair, exchange)

            # Format data to match our database schema
            formatted_data = self._format_to_schema(
                symbol=symbol,
                bulk_data=bulk_data,
                price_data=price_data,
                exchange=exchange,
                interval=interval
            )

            logger.info(f"Successfully fetched technical analysis for {symbol}")
            return {
                "success": True,
                "data": formatted_data,
                "source": "taapi.io",
                "scrapedAt": datetime.utcnow().isoformat() + "Z"
            }

        except Exception as e:
            logger.error(f"Error fetching technical analysis for {symbol}: {e}")
            return {
                "success": False,
                "error": str(e),
                "symbol": symbol
            }

    def _fetch_indicators_individually(
        self,
        symbol: str,
        exchange: str,
        interval: str
    ) -> Dict[str, Any]:
        """
        Fetch indicators one by one (for free tier compatibility).
        Includes retry mechanism for missing indicators.

        Args:
            symbol: Trading pair (e.g., "BTC/USDT")
            exchange: Exchange name
            interval: Time interval

        Returns:
            Dictionary with all indicator values
        """
        result = {}

        # Professional-grade indicators for crypto trading
        # Based on professional crypto trader analysis
        # Total: 12 indicators (10 indicators + 2 MAs counted separately)
        indicators_config = [
            # Tier 1: Core Momentum & Trend
            ("rsi", {"period": 14}),           # 1. RSI - Momentum essential
            ("macd", {}),                       # 2. MACD - Trend following

            # Tier 1: Volatility & Breakouts
            ("bbands", {"period": 20, "stddev": 2}),  # 3. Bollinger Bands - Volatility/breakouts CRITICAL

            # Tier 1: Volume Analysis
            ("obv", {}),                        # 4. OBV - Volume confirmation CRITICAL

            # Tier 2: Advanced Momentum
            ("stochrsi", {}),                   # 5. StochRSI - Better than regular Stochastic for crypto

            # Tier 2: Risk Management & Volatility
            ("atr", {"period": 14}),           # 6. ATR - Risk management essential

            # Tier 2: Institutional Levels
            ("vwap", {}),                       # 7. VWAP - Institutional benchmark

            # Tier 2: Trend Signals
            ("supertrend", {}),                 # 8. SuperTrend - Clear buy/sell signals

            # Tier 3: Money Flow
            ("cmf", {"period": 20}),           # 9. Chaikin Money Flow - Whale detection
        ]

        # Fetch moving averages (essential periods for crypto)
        # EMA20 = short-term, EMA50 = medium-term, EMA200 = long-term bull/bear divider
        ma_periods = [20, 50, 200]

        # Combine all indicators into single list for retry logic
        all_indicators = list(indicators_config) + [(f"ema", {"period": p}) for p in ma_periods]

        # Initial fetch attempt
        logger.info(f"Starting initial fetch of {len(all_indicators)} indicators for {symbol}")
        for indicator_name, params in all_indicators:
            # Handle EMA naming
            if indicator_name == "ema":
                key = f"ema{params['period']}"
            else:
                key = indicator_name

            try:
                data = self._fetch_single_indicator(
                    indicator_name, symbol, exchange, interval, params
                )
                result[key] = data
                logger.debug(f"✓ Fetched {key}")
            except Exception as e:
                logger.warning(f"✗ Failed to fetch {key}: {e}")
                result[key] = {}

        # Retry mechanism for missing indicators
        max_retries = 5
        retry_delay = 30  # seconds

        for retry_attempt in range(1, max_retries + 1):
            # Check which indicators are missing (empty dict or no data)
            missing_indicators = []

            for indicator_name, params in all_indicators:
                if indicator_name == "ema":
                    key = f"ema{params['period']}"
                else:
                    key = indicator_name

                # Check if indicator data is missing or empty
                if key not in result or not result[key] or result[key] == {}:
                    missing_indicators.append((indicator_name, params, key))

            # If all indicators fetched successfully, break
            if not missing_indicators:
                logger.info(f"✓ All {len(all_indicators)} indicators successfully fetched for {symbol}")
                break

            # Log missing indicators
            missing_names = [key for _, _, key in missing_indicators]
            logger.warning(f"Retry {retry_attempt}/{max_retries}: {len(missing_indicators)} indicators missing: {', '.join(missing_names)}")

            # If this is the last retry, accept what we have
            if retry_attempt == max_retries:
                logger.warning(f"⚠ Max retries reached. Accepting partial data. Missing: {', '.join(missing_names)}")
                break

            # Wait before retrying
            logger.info(f"Waiting {retry_delay} seconds before retry {retry_attempt}...")
            time.sleep(retry_delay)

            # Retry fetching missing indicators
            logger.info(f"Retrying {len(missing_indicators)} missing indicators...")
            for indicator_name, params, key in missing_indicators:
                try:
                    data = self._fetch_single_indicator(
                        indicator_name, symbol, exchange, interval, params
                    )
                    result[key] = data
                    logger.info(f"✓ Retry successful: {key}")
                except Exception as e:
                    logger.warning(f"✗ Retry failed for {key}: {e}")
                    result[key] = {}

        # Final summary
        successful = sum(1 for v in result.values() if v and v != {})
        total = len(all_indicators)
        logger.info(f"Fetch complete for {symbol}: {successful}/{total} indicators ({successful/total*100:.1f}%)")

        return result

    def _fetch_single_indicator(
        self,
        indicator: str,
        symbol: str,
        exchange: str,
        interval: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Fetch a single indicator from TAAPI.IO.
        Includes automatic rate limiting.

        Args:
            indicator: Indicator name (e.g., "rsi", "macd")
            symbol: Trading pair
            exchange: Exchange name
            interval: Time interval
            params: Additional parameters (e.g., {"period": 14})

        Returns:
            Indicator data dictionary
        """
        # Wait for rate limit before making request
        self._wait_for_rate_limit()

        url = f"{self.base_url}/{indicator}"
        query_params = {
            "secret": self.api_key,
            "exchange": exchange,
            "symbol": symbol,
            "interval": interval,
            **params
        }

        response = requests.get(url, params=query_params, timeout=self.timeout)
        response.raise_for_status()

        return response.json()

    def _fetch_bulk_indicators(
        self,
        symbol: str,
        exchange: str,
        interval: str
    ) -> Dict[str, Any]:
        """
        Fetch multiple indicators in a single API call using TAAPI bulk endpoint.
        NOTE: This may not be available on free tier.

        Args:
            symbol: Trading pair (e.g., "BTC/USDT")
            exchange: Exchange name
            interval: Time interval

        Returns:
            Dictionary with all indicator values
        """
        # Define all indicators we need
        indicators = {
            # Technical Indicators
            "rsi": {"indicator": "rsi", "period": 14},
            "macd": {"indicator": "macd"},
            "stoch": {"indicator": "stoch"},
            "stochrsi": {"indicator": "stochrsi"},
            "cci": {"indicator": "cci", "period": 20},
            "adx": {"indicator": "adx", "period": 14},
            "ao": {"indicator": "ao"},
            "mom": {"indicator": "mom", "period": 10},
            "williams": {"indicator": "willr", "period": 14},
            "roc": {"indicator": "roc", "period": 10},
            "bbands": {"indicator": "bbands", "period": 20},
            "atr": {"indicator": "atr", "period": 14},

            # Moving Averages
            "sma5": {"indicator": "sma", "period": 5},
            "sma10": {"indicator": "sma", "period": 10},
            "sma20": {"indicator": "sma", "period": 20},
            "sma50": {"indicator": "sma", "period": 50},
            "sma100": {"indicator": "sma", "period": 100},
            "sma200": {"indicator": "sma", "period": 200},
            "ema5": {"indicator": "ema", "period": 5},
            "ema10": {"indicator": "ema", "period": 10},
            "ema20": {"indicator": "ema", "period": 20},
            "ema50": {"indicator": "ema", "period": 50},
            "ema100": {"indicator": "ema", "period": 100},
            "ema200": {"indicator": "ema", "period": 200},

            # Pivot Points
            "pivot_classic": {"indicator": "pivots", "type": "classic"},
            "pivot_fibonacci": {"indicator": "pivots", "type": "fibonacci"},
            "pivot_camarilla": {"indicator": "pivots", "type": "camarilla"},
            "pivot_woodie": {"indicator": "pivots", "type": "woodie"}
        }

        # Build bulk request payload
        constructs = []
        for key, config in indicators.items():
            construct = {
                "id": key,
                "indicator": config["indicator"],
                "symbol": symbol,
                "exchange": exchange,
                "interval": interval
            }
            # Add optional parameters
            if "period" in config:
                construct["period"] = config["period"]
            if "type" in config:
                construct["type"] = config["type"]

            constructs.append(construct)

        # Make bulk API request
        url = f"{self.base_url}/bulk"
        payload = {
            "secret": self.api_key,
            "construct": constructs
        }

        response = requests.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()

        bulk_response = response.json()

        # Convert list response to dictionary keyed by id
        result = {}
        if isinstance(bulk_response, list):
            for item in bulk_response:
                if "id" in item:
                    result[item["id"]] = item

        return result

    def _get_price(self, symbol: str, exchange: str) -> Dict[str, Any]:
        """
        Get current price data for a cryptocurrency.

        Args:
            symbol: Trading pair (e.g., "BTC/USDT")
            exchange: Exchange name

        Returns:
            Dictionary with price information
        """
        # For free tier, we'll use the RSI endpoint to also get price
        # since it includes price in the response
        self._wait_for_rate_limit()

        url = f"{self.base_url}/rsi"
        params = {
            "secret": self.api_key,
            "exchange": exchange,
            "symbol": symbol,
            "interval": "1h"
        }

        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            # Extract price from candle data if available
            return {
                "value": data.get("close", 0),  # Close price from the candle
                "close": data.get("close", 0)
            }
        except Exception as e:
            logger.warning(f"Could not fetch price, using 0: {e}")
            return {"value": 0, "close": 0}

    def _format_to_schema(
        self,
        symbol: str,
        bulk_data: Dict[str, Any],
        price_data: Dict[str, Any],
        exchange: str,
        interval: str
    ) -> Dict[str, Any]:
        """
        Format TAAPI.IO response data to match our database schema.

        Args:
            symbol: Crypto symbol (BTC, ETH, etc.)
            bulk_data: Bulk indicators response
            price_data: Price data response
            exchange: Exchange name
            interval: Time interval

        Returns:
            Formatted data matching our schema
        """
        # Extract price information
        current_price = price_data.get("value", 0)

        # Calculate price change (TAAPI doesn't provide this directly, so we'll use ROC as approximation)
        roc_data = bulk_data.get("roc", {})
        price_change_percent = roc_data.get("value", 0) if roc_data else 0
        price_change = current_price * (price_change_percent / 100)

        # Format technical indicators
        technical_indicators = self._format_technical_indicators(bulk_data)

        # Format moving averages
        moving_averages = self._format_moving_averages(bulk_data, current_price)

        # Format pivot points
        pivot_points = self._format_pivot_points(bulk_data)

        # Generate summaries based on indicator values
        summaries = self._generate_summaries(technical_indicators, moving_averages)

        return {
            "symbol": symbol,
            "price": float(current_price),
            "priceChange": float(price_change),
            "priceChangePercent": float(price_change_percent),
            "summary": summaries,
            "technicalIndicators": technical_indicators,
            "movingAverages": moving_averages,
            "pivotPoints": pivot_points,
            "sourceUrl": f"https://www.{exchange}.com/trade/{symbol}_USDT",
            "scrapedAt": datetime.utcnow().isoformat() + "Z",
            "metadata": {
                "exchange": exchange,
                "interval": interval,
                "provider": "taapi.io"
            }
        }

    def _format_technical_indicators(self, bulk_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format technical indicators from bulk data."""
        indicators = []

        # 1. RSI (14)
        rsi = bulk_data.get("rsi", {})
        if rsi and "value" in rsi:
            indicators.append({
                "name": "RSI(14)",
                "value": float(rsi["value"]),
                "signal": self._get_rsi_signal(rsi["value"])
            })

        # 2. MACD (12,26,9)
        macd = bulk_data.get("macd", {})
        if macd and "valueMACD" in macd:
            macd_val = float(macd["valueMACD"])
            signal_val = float(macd.get("valueMACDSignal", 0))
            indicators.append({
                "name": "MACD(12,26)",
                "value": macd_val,
                "signal": "Buy" if macd_val > signal_val else "Sell",
                "histogram": float(macd.get("valueMACDHist", 0))
            })

        # 3. Bollinger Bands (20,2)
        bbands = bulk_data.get("bbands", {})
        if bbands and "valueUpperBand" in bbands:
            upper = float(bbands["valueUpperBand"])
            middle = float(bbands["valueMiddleBand"])
            lower = float(bbands["valueLowerBand"])
            # Determine signal based on current price vs bands
            current_price = float(bbands.get("close", middle))
            if current_price >= upper:
                signal = "Overbought"
            elif current_price <= lower:
                signal = "Oversold"
            else:
                signal = "Neutral"

            indicators.append({
                "name": "Bollinger Bands(20,2)",
                "upper": upper,
                "middle": middle,
                "lower": lower,
                "signal": signal
            })

        # 4. OBV (On Balance Volume)
        obv = bulk_data.get("obv", {})
        if obv and "value" in obv:
            indicators.append({
                "name": "OBV",
                "value": float(obv["value"]),
                "signal": "Accumulation" if obv["value"] > 0 else "Distribution"
            })

        # 5. StochRSI
        stochrsi = bulk_data.get("stochrsi", {})
        if stochrsi and "valueK" in stochrsi:
            k_val = float(stochrsi["valueK"])
            indicators.append({
                "name": "StochRSI",
                "value": k_val,
                "signal": self._get_stoch_signal(k_val, stochrsi.get("valueD", 50))
            })

        # 6. ATR (14)
        atr = bulk_data.get("atr", {})
        if atr and "value" in atr:
            atr_val = float(atr["value"])
            indicators.append({
                "name": "ATR(14)",
                "value": atr_val,
                "signal": "High Volatility" if atr_val > 0 else "Low Volatility"
            })

        # 7. VWAP
        vwap = bulk_data.get("vwap", {})
        if vwap and "value" in vwap:
            vwap_val = float(vwap["value"])
            current_price = float(vwap.get("close", 0))
            indicators.append({
                "name": "VWAP",
                "value": vwap_val,
                "signal": "Bullish" if current_price > vwap_val else "Bearish"
            })

        # 8. SuperTrend
        supertrend = bulk_data.get("supertrend", {})
        if supertrend and "value" in supertrend:
            st_val = float(supertrend["value"])
            trend = supertrend.get("trend", 1)
            indicators.append({
                "name": "SuperTrend",
                "value": st_val,
                "signal": "Buy" if trend == 1 else "Sell",
                "trend": "Uptrend" if trend == 1 else "Downtrend"
            })

        # 9. Chaikin Money Flow (20)
        cmf = bulk_data.get("cmf", {})
        if cmf and "value" in cmf:
            cmf_val = float(cmf["value"])
            indicators.append({
                "name": "CMF(20)",
                "value": cmf_val,
                "signal": "Buying Pressure" if cmf_val > 0 else "Selling Pressure"
            })

        return indicators

    def _format_moving_averages(self, bulk_data: Dict[str, Any], current_price: float) -> List[Dict[str, Any]]:
        """Format moving averages from bulk data."""
        mas = []

        # Only include periods we actually fetched (EMA only)
        periods = [20, 50, 200]

        for period in periods:
            # Exponential MA only
            ema_key = f"ema{period}"
            ema = bulk_data.get(ema_key, {})
            if ema and "value" in ema:
                mas.append({
                    "name": f"MA{period}",
                    "type": "Exponential",
                    "value": float(ema["value"]),
                    "signal": "Buy" if current_price > ema["value"] else "Sell"
                })

        return mas

    def _format_pivot_points(self, bulk_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format pivot points from bulk data."""
        # Pivot points not included in free tier, return empty list
        return []

    def _generate_summaries(
        self,
        technical_indicators: List[Dict[str, Any]],
        moving_averages: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """
        Generate summary recommendations based on indicators.

        Args:
            technical_indicators: List of technical indicators
            moving_averages: List of moving averages

        Returns:
            Dictionary with overall, technical, and MA summaries
        """
        # Count buy/sell signals for technical indicators
        tech_buy = sum(1 for ind in technical_indicators if ind.get("signal") == "Buy")
        tech_sell = sum(1 for ind in technical_indicators if ind.get("signal") == "Sell")
        tech_total = len(technical_indicators)

        # Count buy/sell signals for moving averages
        ma_buy = sum(1 for ma in moving_averages if ma.get("signal") == "Buy")
        ma_sell = sum(1 for ma in moving_averages if ma.get("signal") == "Sell")
        ma_total = len(moving_averages)

        # Determine summaries
        tech_summary = self._get_summary_label(tech_buy, tech_sell, tech_total)
        ma_summary = self._get_summary_label(ma_buy, ma_sell, ma_total)

        # Overall summary (weighted average)
        total_buy = tech_buy + ma_buy
        total_sell = tech_sell + ma_sell
        total_signals = tech_total + ma_total

        overall_summary = self._get_summary_label(total_buy, total_sell, total_signals)

        return {
            "overall": overall_summary,
            "technicalIndicators": tech_summary,
            "movingAverages": ma_summary
        }

    def _get_summary_label(self, buy_count: int, sell_count: int, total: int) -> str:
        """Get summary label based on buy/sell counts."""
        if total == 0:
            return "Neutral"

        buy_ratio = buy_count / total
        sell_ratio = sell_count / total

        if buy_ratio >= 0.7:
            return "Strong Buy"
        elif buy_ratio >= 0.5:
            return "Buy"
        elif sell_ratio >= 0.7:
            return "Strong Sell"
        elif sell_ratio >= 0.5:
            return "Sell"
        else:
            return "Neutral"

    def _get_rsi_signal(self, value: float) -> str:
        """Get RSI signal based on value."""
        if value < 30:
            return "Buy"  # Oversold
        elif value > 70:
            return "Sell"  # Overbought
        else:
            return "Neutral"

    def _get_stoch_signal(self, k_value: float, d_value: float) -> str:
        """Get Stochastic signal based on K and D values."""
        if k_value < 20:
            return "Buy"  # Oversold
        elif k_value > 80:
            return "Sell"  # Overbought
        else:
            return "Neutral"

    def _get_cci_signal(self, value: float) -> str:
        """Get CCI signal based on value."""
        if value < -100:
            return "Buy"  # Oversold
        elif value > 100:
            return "Sell"  # Overbought
        else:
            return "Neutral"

    def _get_williams_signal(self, value: float) -> str:
        """Get Williams %R signal based on value."""
        if value < -80:
            return "Buy"  # Oversold
        elif value > -20:
            return "Sell"  # Overbought
        else:
            return "Neutral"

    def test_connection(self) -> bool:
        """
        Test TAAPI.IO API connection.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Simple test: fetch BTC RSI
            self._wait_for_rate_limit()

            url = f"{self.base_url}/rsi"
            params = {
                "secret": self.api_key,
                "exchange": "binance",
                "symbol": "BTC/USDT",
                "interval": "1h"
            }

            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            if "value" in data:
                logger.info("TAAPI.IO connection test successful")
                return True
            else:
                logger.error(f"TAAPI.IO unexpected response: {data}")
                return False

        except Exception as e:
            logger.error(f"TAAPI.IO connection test failed: {e}")
            return False
