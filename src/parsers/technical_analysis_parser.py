"""
Technical Analysis Parser - Python port of TypeScript parser
Parses markdown content from investing.com to extract technical indicators,
moving averages, pivot points, and market summaries.
"""
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TechnicalAnalysisParser:
    """Parse technical analysis data from markdown content."""

    @staticmethod
    def parse_markdown(markdown: str, source_url: str) -> Optional[Dict[str, Any]]:
        """
        Parse markdown content to extract technical analysis data.

        Args:
            markdown: Markdown content from scraped page
            source_url: URL of the source page

        Returns:
            Dictionary containing parsed technical analysis data or None if parsing fails
        """
        try:
            data = {
                "symbol": TechnicalAnalysisParser._extract_symbol(markdown),
                "price": TechnicalAnalysisParser._extract_price(markdown),
                "priceChange": TechnicalAnalysisParser._extract_price_change(markdown),
                "priceChangePercent": TechnicalAnalysisParser._extract_price_change_percent(markdown),
                "summary": TechnicalAnalysisParser._extract_summary(markdown),
                "technicalIndicatorsSummary": TechnicalAnalysisParser._extract_technical_indicators_summary(markdown),
                "movingAveragesSummary": TechnicalAnalysisParser._extract_moving_averages_summary(markdown),
                "technicalIndicators": TechnicalAnalysisParser._extract_technical_indicators(markdown),
                "movingAverages": TechnicalAnalysisParser._extract_moving_averages(markdown),
                "pivotPoints": TechnicalAnalysisParser._extract_pivot_points(markdown),
                "scrapedAt": datetime.utcnow().isoformat() + "Z",
                "sourceUrl": source_url
            }
            return data
        except Exception as e:
            logger.error(f"Error parsing technical analysis markdown: {e}")
            return None

    @staticmethod
    def _extract_symbol(markdown: str) -> str:
        """Extract symbol (e.g., ETH, BTC) from markdown."""
        # Look for title patterns
        title_match = re.search(r'# (.*?)(\n|$)', markdown)
        if title_match:
            title = title_match.group(1).lower()
            if 'ethereum' in title or 'eth' in title:
                return 'ETH'
            if 'bitcoin' in title or 'btc' in title:
                return 'BTC'

        # Look for ETH/USD patterns
        symbol_match = re.search(r'(ETH|BTC|ADA|SOL|DOT)/USD', markdown, re.IGNORECASE)
        if symbol_match:
            return symbol_match.group(1).upper()

        return 'UNKNOWN'

    @staticmethod
    def _extract_price(markdown: str) -> float:
        """Extract current price from markdown."""
        price_patterns = [
            # Pattern: price on one line, change on next line
            r'([0-9,]+\.[0-9]+)\s*\n\s*[+\-]([0-9,]+\.[0-9]+)\s*\([+\-]([0-9,]+\.[0-9]+)%\)',
            # Pattern: price with USD
            r'([0-9,]+\.?[0-9]*)\s*USD',
            # Pattern: labeled price
            r'Price[:\s]*\$?([0-9,]+\.?[0-9]*)',
            # Pattern: simple price in 4,xxx.xx format (ETH range)
            r'(4,[0-9]{3}\.[0-9]{2})'
        ]

        for pattern in price_patterns:
            match = re.search(pattern, markdown, re.IGNORECASE)
            if match:
                price_str = match.group(1)
                if price_str:
                    return float(price_str.replace(',', ''))

        return 0.0

    @staticmethod
    def _extract_price_change(markdown: str) -> float:
        """Extract price change from markdown."""
        change_patterns = [
            # Pattern with price: "4,491.64\n+11.46(+0.26%)"
            r'([0-9,]+\.[0-9]+)\s*\n\s*([+\-])([0-9,]+\.[0-9]+)\s*\([+\-]([0-9,]+\.[0-9]+)%\)',
            # Simple change pattern: "+11.46(+0.26%)"
            r'([+\-])([0-9,]+\.?\d*)\s*\([+\-]([0-9,]+\.?\d*)%\)'
        ]

        for pattern in change_patterns:
            match = re.search(pattern, markdown)
            if match:
                groups = match.groups()
                if len(groups) == 4:  # First pattern
                    sign = 1 if groups[1] == '+' else -1
                    return sign * float(groups[2].replace(',', ''))
                elif len(groups) == 3:  # Second pattern
                    sign = 1 if groups[0] == '+' else -1
                    return sign * float(groups[1].replace(',', ''))

        return 0.0

    @staticmethod
    def _extract_price_change_percent(markdown: str) -> float:
        """Extract price change percentage from markdown."""
        change_patterns = [
            # Pattern with price: "4,491.64\n+11.46(+0.26%)"
            r'([0-9,]+\.[0-9]+)\s*\n\s*[+\-]([0-9,]+\.[0-9]+)\s*\(([+\-])([0-9,]+\.[0-9]+)%\)',
            # Simple change pattern: "+11.46(+0.26%)"
            r'[+\-]([0-9,]+\.?\d*)\s*\(([+\-])([0-9,]+\.?\d*)%\)'
        ]

        for pattern in change_patterns:
            match = re.search(pattern, markdown)
            if match:
                groups = match.groups()
                if len(groups) == 4:  # First pattern
                    sign = 1 if groups[2] == '+' else -1
                    return sign * float(groups[3].replace(',', ''))
                elif len(groups) == 3:  # Second pattern
                    sign = 1 if groups[1] == '+' else -1
                    return sign * float(groups[2].replace(',', ''))

        return 0.0

    @staticmethod
    def _extract_summary(markdown: str) -> Dict[str, str]:
        """Extract summary information."""
        summary = {
            "overall": "Neutral",
            "technicalIndicators": "Neutral",
            "movingAverages": "Neutral"
        }

        # Overall summary
        summary_match = re.search(r'## Summary:\s*((?:Strong\s+)?(?:Sell|Buy|Neutral))', markdown, re.IGNORECASE)
        if summary_match:
            summary["overall"] = summary_match.group(1).strip()

        # Technical indicators summary
        tech_match = re.search(r'Technical Indicators[^#]*?Summary:\s*((?:Strong\s+)?(?:Sell|Buy|Neutral))\s*Buy:\s*(\d+)', markdown, re.IGNORECASE | re.DOTALL)
        if tech_match:
            summary["technicalIndicators"] = tech_match.group(1).strip()

        # Moving averages summary
        ma_match = re.search(r'Moving Averages[^#]*?Summary:\s*((?:Strong\s+)?(?:Sell|Buy|Neutral))\s*Buy:\s*(\d+)', markdown, re.IGNORECASE | re.DOTALL)
        if ma_match:
            summary["movingAverages"] = ma_match.group(1).strip()

        return summary

    @staticmethod
    def _extract_technical_indicators(markdown: str) -> List[Dict[str, Any]]:
        """Extract technical indicators like RSI, MACD, STOCH, etc."""
        indicators = []
        lines = markdown.split('\n')

        # Multiple pattern variations to handle different markdown formats
        indicator_patterns = [
            # Standard table format: | Name | Value | Action |
            {"name": "RSI(14)", "patterns": [
                r'\|\s*RSI\(14\)\s*\|\s*([\d.]+)\s*\|\s*(\w+)',
                r'RSI\(14\)\s*(?:\||:)\s*([\d.]+)\s*(?:\||:)\s*(\w+)',
                r'RSI\s*\(14\)\s*(?:\||:)?\s*([\d.]+)\s*(?:\||:)?\s*(\w+)'
            ]},
            {"name": "STOCH(9,6)", "patterns": [
                r'\|\s*STOCH\(9,6\)\s*\|\s*([\d.]+)\s*\|\s*(\w+)',
                r'STOCH\(9,6\)\s*(?:\||:)\s*([\d.]+)\s*(?:\||:)\s*(\w+)'
            ]},
            {"name": "STOCHRSI(14)", "patterns": [
                r'\|\s*STOCHRSI\(14\)\s*\|\s*([\d.]+)\s*\|\s*(\w+)',
                r'STOCHRSI\(14\)\s*(?:\||:)\s*([\d.]+)\s*(?:\||:)\s*(\w+)'
            ]},
            {"name": "MACD(12,26)", "patterns": [
                r'\|\s*MACD\(12,26\)\s*\|\s*([-\d.]+)\s*\|\s*(\w+)',
                r'MACD\(12,26\)\s*(?:\||:)\s*([-\d.]+)\s*(?:\||:)\s*(\w+)'
            ]},
            {"name": "ADX(14)", "patterns": [
                r'\|\s*ADX\(14\)\s*\|\s*([\d.]+)\s*\|\s*(\w+)',
                r'ADX\(14\)\s*(?:\||:)\s*([\d.]+)\s*(?:\||:)\s*(\w+)'
            ]},
            {"name": "Williams %R", "patterns": [
                r'\|\s*Williams\s+%?R\s*\|\s*([-\d.]+)\s*\|\s*(\w+)',
                r'Williams\s+%?R\s*(?:\||:)\s*([-\d.]+)\s*(?:\||:)\s*(\w+)'
            ]},
            {"name": "CCI(14)", "patterns": [
                r'\|\s*CCI\(14\)\s*\|\s*([-\d.]+)\s*\|\s*(\w+)',
                r'CCI\(14\)\s*(?:\||:)\s*([-\d.]+)\s*(?:\||:)\s*(\w+)'
            ]},
            {"name": "ATR(14)", "patterns": [
                r'\|\s*ATR\(14\)\s*\|\s*([\d.]+)\s*\|\s*([\w\s]+)',
                r'ATR\(14\)\s*(?:\||:)\s*([\d.]+)\s*(?:\||:)\s*([\w\s]+)'
            ]},
            {"name": "Ultimate Oscillator", "patterns": [
                r'\|\s*Ultimate\s+Oscillator\s*\|\s*([\d.]+)\s*\|\s*(\w+)',
                r'Ultimate\s+Oscillator\s*(?:\||:)\s*([\d.]+)\s*(?:\||:)\s*(\w+)'
            ]},
            {"name": "ROC", "patterns": [
                r'\|\s*ROC\s*\|\s*([-\d.]+)\s*\|\s*(\w+)',
                r'ROC\s*(?:\||:)\s*([-\d.]+)\s*(?:\||:)\s*(\w+)'
            ]},
            {"name": "Bull/Bear Power(13)", "patterns": [
                r'\|\s*Bull/?Bear\s+Power\(13\)\s*\|\s*([-\d.]+)\s*\|\s*(\w+)',
                r'Bull/?Bear\s+Power\(13\)\s*(?:\||:)\s*([-\d.]+)\s*(?:\||:)\s*(\w+)'
            ]},
            {"name": "Highs/Lows(14)", "patterns": [
                r'\|\s*Highs?/?Lows?\(14\)\s*\|\s*([-\d.]+)\s*\|\s*(\w+)',
                r'Highs?/?Lows?\(14\)\s*(?:\||:)\s*([-\d.]+)\s*(?:\||:)\s*(\w+)'
            ]}
        ]

        for line in lines:
            # Skip lines without any table-like characters
            if not ('|' in line or ':' in line):
                continue

            for indicator in indicator_patterns:
                matched = False
                # Try each pattern variant
                for pattern in indicator.get("patterns", []):
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        try:
                            value_str = match.group(1).strip()
                            # Handle numeric value conversion
                            value = float(value_str.replace(',', ''))
                            action = match.group(2).strip() if match.lastindex >= 2 else "Unknown"

                            indicators.append({
                                "name": indicator["name"],
                                "value": value,
                                "action": action,
                                "rawValue": line.strip()
                            })
                            matched = True
                            break
                        except (ValueError, IndexError) as e:
                            logger.debug(f"Failed to parse indicator {indicator['name']}: {e}")
                            continue

                if matched:
                    break

        # Log if no indicators found (for debugging)
        if len(indicators) == 0:
            logger.warning("No technical indicators extracted from markdown")
            # Save markdown sample for debugging (first 2000 chars)
            logger.debug(f"Markdown sample (first 2000 chars):\n{markdown[:2000]}")

        return indicators

    @staticmethod
    def _extract_moving_averages(markdown: str) -> List[Dict[str, Any]]:
        """Extract moving averages data."""
        moving_averages = []
        lines = markdown.split('\n')

        ma_patterns = [
            {"period": 5, "pattern": r'\|\s*MA5\s*\|\s*([\d.]+)\s*\|\s*(\w+)\s*\|\s*([\d.]+)\s*\|\s*(\w+)\s*\|'},
            {"period": 10, "pattern": r'\|\s*MA10\s*\|\s*([\d.]+)\s*\|\s*(\w+)\s*\|\s*([\d.]+)\s*\|\s*(\w+)\s*\|'},
            {"period": 20, "pattern": r'\|\s*MA20\s*\|\s*([\d.]+)\s*\|\s*(\w+)\s*\|\s*([\d.]+)\s*\|\s*(\w+)\s*\|'},
            {"period": 50, "pattern": r'\|\s*MA50\s*\|\s*([\d.]+)\s*\|\s*(\w+)\s*\|\s*([\d.]+)\s*\|\s*(\w+)\s*\|'},
            {"period": 100, "pattern": r'\|\s*MA100\s*\|\s*([\d.]+)\s*\|\s*(\w+)\s*\|\s*([\d.]+)\s*\|\s*(\w+)\s*\|'},
            {"period": 200, "pattern": r'\|\s*MA200\s*\|\s*([\d.]+)\s*\|\s*(\w+)\s*\|\s*([\d.]+)\s*\|\s*(\w+)\s*\|'}
        ]

        for line in lines:
            if '|' not in line or 'MA' not in line:
                continue

            for ma in ma_patterns:
                match = re.search(ma["pattern"], line, re.IGNORECASE)
                if match:
                    moving_averages.append({
                        "period": ma["period"],
                        "simple": {
                            "value": float(match.group(1)),
                            "action": match.group(2).strip()
                        },
                        "exponential": {
                            "value": float(match.group(3)),
                            "action": match.group(4).strip()
                        }
                    })
                    break

        return moving_averages

    @staticmethod
    def _extract_pivot_points(markdown: str) -> List[Dict[str, Any]]:
        """Extract pivot points data."""
        pivot_points = []

        # Look for pivot points section
        pivot_section_match = re.search(r'## \[Pivot Points\].*?\n([\s\S]*?)(?=##|$)', markdown, re.IGNORECASE)
        if not pivot_section_match:
            return pivot_points

        table_content = pivot_section_match.group(1)

        pivot_patterns = [
            {
                "name": "Classic",
                "pattern": r'Classic\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)'
            },
            {
                "name": "Fibonacci",
                "pattern": r'Fibonacci\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)'
            },
            {
                "name": "Camarilla",
                "pattern": r'Camarilla\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)'
            },
            {
                "name": "Woodie's",
                "pattern": r"Woodie's\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)"
            }
        ]

        for pivot in pivot_patterns:
            match = re.search(pivot["pattern"], table_content, re.IGNORECASE)
            if match:
                pivot_points.append({
                    "name": pivot["name"],
                    "s3": float(match.group(1)),
                    "s2": float(match.group(2)),
                    "s1": float(match.group(3)),
                    "pivot": float(match.group(4)),
                    "r1": float(match.group(5)),
                    "r2": float(match.group(6)),
                    "r3": float(match.group(7))
                })

        return pivot_points

    @staticmethod
    def _extract_technical_indicators_summary(markdown: str) -> Dict[str, Any]:
        """Extract technical indicators summary table data."""
        pattern = r'\|\s*Technical Indicators:\s*\|\s*([^|]+)\s*\|\s*Buy:\s*\((\d+)\)\s*\|\s*Sell:\s*\((\d+)\)\s*\|'
        match = re.search(pattern, markdown, re.IGNORECASE)

        if match:
            return {
                "recommendation": match.group(1).strip(),
                "buyCount": int(match.group(2)),
                "sellCount": int(match.group(3)),
                "neutralCount": 0
            }

        return {
            "recommendation": "Neutral",
            "buyCount": 0,
            "sellCount": 0,
            "neutralCount": 0
        }

    @staticmethod
    def _extract_moving_averages_summary(markdown: str) -> Dict[str, Any]:
        """Extract moving averages summary table data."""
        pattern = r'\|\s*Moving Averages:\s*\|\s*([^|]+)\s*\|\s*Buy:\s*\((\d+)\)\s*\|\s*Sell:\s*\((\d+)\)\s*\|'
        match = re.search(pattern, markdown, re.IGNORECASE)

        if match:
            return {
                "recommendation": match.group(1).strip(),
                "buyCount": int(match.group(2)),
                "sellCount": int(match.group(3)),
                "neutralCount": 0
            }

        return {
            "recommendation": "Neutral",
            "buyCount": 0,
            "sellCount": 0,
            "neutralCount": 0
        }
