"""
Technical Indicators Calculator using 'ta' library
Calculates 12 professional-grade indicators from OHLC data
Using 'ta' instead of 'pandas-ta' for lighter deployment size
"""
import pandas as pd
from ta.trend import MACD, EMAIndicator
from ta.momentum import RSIIndicator, StochRSIIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator, ChaikinMoneyFlowIndicator, VolumeWeightedAveragePrice
from typing import Dict, Any, List
from datetime import datetime


class IndicatorsCalculator:
    """
    Calculate technical indicators from OHLC data using pandas-ta.
    Provides the same 12 professional indicators as TAAPI.IO.
    """

    def __init__(self):
        """Initialize the calculator."""
        pass

    def calculate_indicators(self, ohlcv_data: List[List[float]], symbol: str) -> Dict[str, Any]:
        """
        Calculate all 12 technical indicators from OHLC data.

        Args:
            ohlcv_data: List of [timestamp, open, high, low, close, volume] arrays
            symbol: Cryptocurrency symbol (e.g., "BTC", "ETH")

        Returns:
            Dictionary with formatted technical analysis data matching database schema
        """
        # Convert OHLC data to pandas DataFrame
        df = self._prepare_dataframe(ohlcv_data)

        if df is None or len(df) < 50:
            raise ValueError(f"Insufficient data: need at least 50 candles, got {len(df) if df is not None else 0}")

        # Calculate all indicators
        technical_indicators = self._calculate_technical_indicators(df)
        moving_averages = self._calculate_moving_averages(df)
        pivot_points = self._calculate_pivot_points(df)

        # Generate summaries
        summaries = self._generate_summaries(technical_indicators, moving_averages)

        # Get current price and changes
        current_price = float(df['close'].iloc[-1])
        price_change = float(df['close'].iloc[-1] - df['close'].iloc[-2])
        price_change_percent = (price_change / df['close'].iloc[-2]) * 100

        return {
            "symbol": symbol,
            "price": current_price,
            "priceChange": price_change,
            "priceChangePercent": price_change_percent,
            "summary": summaries,
            "technicalIndicators": technical_indicators,
            "movingAverages": moving_averages,
            "pivotPoints": pivot_points,
            "sourceUrl": f"https://www.coingecko.com/en/coins/{symbol.lower()}",
            "scrapedAt": datetime.utcnow().isoformat() + "Z",
            "metadata": {
                "provider": "coingecko+pandas-ta",
                "dataPoints": len(df)
            }
        }

    def _prepare_dataframe(self, ohlcv_data: List[List[float]]) -> pd.DataFrame:
        """
        Convert OHLC data to pandas DataFrame.

        Args:
            ohlcv_data: List of [timestamp, open, high, low, close] arrays from CoinGecko

        Returns:
            DataFrame with OHLC data
        """
        if not ohlcv_data or len(ohlcv_data) == 0:
            return None

        # CoinGecko OHLC returns: [timestamp, open, high, low, close]
        df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close'])

        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)

        # Ensure numeric types
        df = df.astype(float)

        # Add volume column (estimate from price action for indicators that need it)
        # For indicators like OBV that need volume, we'll use a simple estimate
        df['volume'] = (df['high'] - df['low']) * df['close'] * 1000

        return df

    def _calculate_technical_indicators(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Calculate all technical indicators using 'ta' library."""
        indicators = []

        # 1. RSI (14)
        try:
            rsi_indicator = RSIIndicator(close=df['close'], window=14)
            rsi_value = float(rsi_indicator.rsi().iloc[-1])
            indicators.append({
                "name": "RSI(14)",
                "value": rsi_value,
                "signal": self._get_rsi_signal(rsi_value)
            })
        except Exception as e:
            print(f"RSI calculation failed: {e}")

        # 2. MACD (12,26,9)
        try:
            macd_indicator = MACD(close=df['close'], window_slow=26, window_fast=12, window_sign=9)
            macd_value = float(macd_indicator.macd().iloc[-1])
            signal_value = float(macd_indicator.macd_signal().iloc[-1])
            histogram = float(macd_indicator.macd_diff().iloc[-1])
            indicators.append({
                "name": "MACD(12,26)",
                "value": macd_value,
                "signal": "Buy" if macd_value > signal_value else "Sell",
                "histogram": histogram
            })
        except Exception as e:
            print(f"MACD calculation failed: {e}")

        # 3. Bollinger Bands (20,2)
        try:
            bb_indicator = BollingerBands(close=df['close'], window=20, window_dev=2)
            upper = float(bb_indicator.bollinger_hband().iloc[-1])
            middle = float(bb_indicator.bollinger_mavg().iloc[-1])
            lower = float(bb_indicator.bollinger_lband().iloc[-1])
            current_price = float(df['close'].iloc[-1])

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
        except Exception as e:
            print(f"Bollinger Bands calculation failed: {e}")

        # 4. OBV (On Balance Volume)
        try:
            obv_indicator = OnBalanceVolumeIndicator(close=df['close'], volume=df['volume'])
            obv_value = float(obv_indicator.on_balance_volume().iloc[-1])
            obv_prev = float(obv_indicator.on_balance_volume().iloc[-2])
            indicators.append({
                "name": "OBV",
                "value": obv_value,
                "signal": "Accumulation" if obv_value > obv_prev else "Distribution"
            })
        except Exception as e:
            print(f"OBV calculation failed: {e}")

        # 5. StochRSI (14,14,3,3)
        try:
            stochrsi_indicator = StochRSIIndicator(close=df['close'], window=14, smooth1=3, smooth2=3)
            k_value = float(stochrsi_indicator.stochrsi_k().iloc[-1]) * 100  # Convert to 0-100 range
            indicators.append({
                "name": "StochRSI",
                "value": k_value,
                "signal": "Overbought" if k_value > 80 else "Oversold" if k_value < 20 else "Neutral"
            })
        except Exception as e:
            print(f"StochRSI calculation failed: {e}")

        # 6. ATR (14)
        try:
            atr_indicator = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=14)
            atr_value = float(atr_indicator.average_true_range().iloc[-1])
            indicators.append({
                "name": "ATR(14)",
                "value": atr_value,
                "signal": "High Volatility" if atr_value > df['close'].iloc[-1] * 0.02 else "Low Volatility"
            })
        except Exception as e:
            print(f"ATR calculation failed: {e}")

        # 7. VWAP
        try:
            vwap_indicator = VolumeWeightedAveragePrice(
                high=df['high'], low=df['low'], close=df['close'], volume=df['volume']
            )
            vwap_value = float(vwap_indicator.volume_weighted_average_price().iloc[-1])
            current_price = float(df['close'].iloc[-1])
            indicators.append({
                "name": "VWAP",
                "value": vwap_value,
                "signal": "Bullish" if current_price > vwap_value else "Bearish"
            })
        except Exception as e:
            print(f"VWAP calculation failed: {e}")

        # 8. SuperTrend - Not available in 'ta' library
        # Skip for now, will use simplified version or skip
        indicators.append({
            "name": "SuperTrend",
            "value": 0.0,
            "signal": "N/A",
            "trend": "N/A"
        })

        # 9. CMF (20) - Chaikin Money Flow
        try:
            cmf_indicator = ChaikinMoneyFlowIndicator(
                high=df['high'], low=df['low'], close=df['close'], volume=df['volume'], window=20
            )
            cmf_value = float(cmf_indicator.chaikin_money_flow().iloc[-1])
            indicators.append({
                "name": "CMF(20)",
                "value": cmf_value,
                "signal": "Buying Pressure" if cmf_value > 0 else "Selling Pressure"
            })
        except Exception as e:
            print(f"CMF calculation failed: {e}")

        return indicators

    def _calculate_moving_averages(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Calculate exponential moving averages using 'ta' library."""
        mas = []
        current_price = float(df['close'].iloc[-1])

        for period in [20, 50, 200]:
            try:
                ema_indicator = EMAIndicator(close=df['close'], window=period)
                ema_value = float(ema_indicator.ema_indicator().iloc[-1])
                mas.append({
                    "name": f"MA{period}",
                    "type": "Exponential",
                    "value": ema_value,
                    "signal": "Buy" if current_price > ema_value else "Sell"
                })
            except Exception as e:
                print(f"EMA{period} calculation failed: {e}")

        return mas

    def _calculate_pivot_points(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Calculate pivot points (Classic method)."""
        # Get previous day's high, low, close
        high = float(df['high'].iloc[-2])
        low = float(df['low'].iloc[-2])
        close = float(df['close'].iloc[-2])

        # Classic pivot points
        pivot = (high + low + close) / 3
        r1 = 2 * pivot - low
        s1 = 2 * pivot - high
        r2 = pivot + (high - low)
        s2 = pivot - (high - low)
        r3 = high + 2 * (pivot - low)
        s3 = low - 2 * (high - pivot)

        return [{
            "type": "Classic",
            "pivot": pivot,
            "r1": r1,
            "r2": r2,
            "r3": r3,
            "s1": s1,
            "s2": s2,
            "s3": s3
        }]

    def _get_rsi_signal(self, rsi_value: float) -> str:
        """Get RSI signal based on value."""
        if rsi_value > 70:
            return "Overbought"
        elif rsi_value < 30:
            return "Oversold"
        else:
            return "Neutral"

    def _generate_summaries(
        self,
        technical_indicators: List[Dict],
        moving_averages: List[Dict]
    ) -> Dict[str, str]:
        """Generate summary signals."""
        # Count technical indicator signals
        tech_buy = sum(1 for ind in technical_indicators
                      if ind.get('signal') in ['Buy', 'Oversold', 'Bullish', 'Accumulation', 'Buying Pressure'])
        tech_sell = sum(1 for ind in technical_indicators
                       if ind.get('signal') in ['Sell', 'Overbought', 'Bearish', 'Distribution', 'Selling Pressure'])
        tech_neutral = len(technical_indicators) - tech_buy - tech_sell

        # Count MA signals
        ma_buy = sum(1 for ma in moving_averages if ma.get('signal') == 'Buy')
        ma_sell = sum(1 for ma in moving_averages if ma.get('signal') == 'Sell')

        # Technical indicators summary
        if tech_buy > tech_sell and tech_buy > tech_neutral:
            tech_summary = "Buy"
        elif tech_sell > tech_buy and tech_sell > tech_neutral:
            tech_summary = "Sell"
        else:
            tech_summary = "Neutral"

        # Moving averages summary
        if ma_buy == len(moving_averages):
            ma_summary = "Strong Buy"
        elif ma_buy > ma_sell:
            ma_summary = "Buy"
        elif ma_sell == len(moving_averages):
            ma_summary = "Strong Sell"
        elif ma_sell > ma_buy:
            ma_summary = "Sell"
        else:
            ma_summary = "Neutral"

        # Overall summary
        if tech_summary == "Buy" and ma_summary in ["Buy", "Strong Buy"]:
            overall = "Buy"
        elif tech_summary == "Sell" and ma_summary in ["Sell", "Strong Sell"]:
            overall = "Sell"
        else:
            overall = "Neutral"

        return {
            "overall": overall,
            "technicalIndicators": tech_summary,
            "movingAverages": ma_summary
        }
