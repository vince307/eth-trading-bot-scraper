"""
Investing.com scraper for cryptocurrency technical analysis
Scrapes technical indicators, moving averages, and pivot points
"""
from typing import Dict, Any, Optional
import logging

from bs4 import BeautifulSoup
from .base_scraper import BaseScraper
from ..parsers.technical_analysis_parser import TechnicalAnalysisParser
from ..utils.crypto_config import get_crypto_config, get_technical_url

logger = logging.getLogger(__name__)


class InvestingScraper(BaseScraper):
    """
    Scraper for investing.com technical analysis pages.
    Extracts technical indicators, moving averages, and pivot points.
    Supports multiple cryptocurrencies (BTC, ETH, ADA, SOL, etc.)
    """

    def __init__(self, timeout: int = 60000, headless: bool = True):
        """
        Initialize investing.com scraper.

        Args:
            timeout: Page load timeout in milliseconds (default: 60000)
            headless: Run browser in headless mode
        """
        super().__init__(timeout=timeout, headless=headless)
        # Default to ETH for backward compatibility
        self.default_crypto = "ETH"

    def scrape_crypto_technical_analysis(
        self,
        crypto: Optional[str] = None,
        url: Optional[str] = None,
        cache_bust: bool = False
    ) -> Dict[str, Any]:
        """
        Scrape cryptocurrency technical analysis from investing.com.

        Args:
            crypto: Cryptocurrency symbol (BTC, ETH, etc.) or URL slug (bitcoin, ethereum)
            url: Direct URL to scrape (overrides crypto parameter)
            cache_bust: Add timestamp to URL to bypass caching

        Returns:
            Dictionary containing scraped and parsed technical analysis data

        Examples:
            >>> scraper.scrape_crypto_technical_analysis(crypto="BTC")
            >>> scraper.scrape_crypto_technical_analysis(crypto="bitcoin")
            >>> scraper.scrape_crypto_technical_analysis(url="https://www.investing.com/crypto/bitcoin/technical")
        """
        # Determine target URL
        if url:
            target_url = url
            crypto_identifier = crypto or "UNKNOWN"
        else:
            crypto_identifier = crypto or self.default_crypto
            target_url = get_technical_url(crypto_identifier)

            if not target_url:
                logger.error(f"Unsupported cryptocurrency: {crypto_identifier}")
                return {
                    "success": False,
                    "error": f"Unsupported cryptocurrency: {crypto_identifier}",
                    "crypto": crypto_identifier
                }

        # Add cache busting if requested
        if cache_bust:
            separator = "&" if "?" in target_url else "?"
            import time
            target_url = f"{target_url}{separator}t={int(time.time() * 1000)}"

        logger.info(f"Scraping {crypto_identifier} technical analysis from: {target_url}")

        # Use base scraper to fetch content
        # Try to wait for technical indicators table, but don't fail if it times out
        result = self.scrape_url(
            target_url,
            wait_for_selector=None  # Don't wait for specific selector, just load the page
        )

        if not result.get("success"):
            logger.error(f"Failed to scrape {target_url}: {result.get('error')}")
            return result

        # Log if we got the content
        logger.info(f"Page loaded, content length: {result.get('contentLength', 0)} chars")

        # Parse the markdown content
        parsed_data = TechnicalAnalysisParser.parse_markdown(
            result["markdown"],
            target_url
        )

        if parsed_data is None:
            logger.error("Failed to parse technical analysis data")
            return {
                "success": False,
                "error": "Failed to parse technical analysis data",
                "url": target_url
            }

        logger.info(
            f"Successfully scraped and parsed technical analysis - "
            f"Symbol: {parsed_data['symbol']}, Price: {parsed_data['price']}"
        )

        return {
            "success": True,
            "url": target_url,
            "title": result["title"],
            "markdown": result["markdown"],
            "html": result["html"],
            "contentLength": result["contentLength"],
            "scrapedAt": result["scrapedAt"],
            "parsed": parsed_data
        }

    def scrape_eth_technical_analysis(
        self,
        url: str = None,
        cache_bust: bool = False
    ) -> Dict[str, Any]:
        """
        Scrape ETH technical analysis from investing.com.

        DEPRECATED: Use scrape_crypto_technical_analysis(crypto="ETH") instead.
        Kept for backward compatibility.

        Args:
            url: URL to scrape (defaults to ETH technical page)
            cache_bust: Add timestamp to URL to bypass caching

        Returns:
            Dictionary containing scraped and parsed technical analysis data
        """
        return self.scrape_crypto_technical_analysis(
            crypto="ETH",
            url=url,
            cache_bust=cache_bust
        )

    def parse_content(self, soup: BeautifulSoup, markdown: str) -> Dict[str, Any]:
        """
        Parse content from BeautifulSoup object.
        This method is called by the base scraper.

        Args:
            soup: BeautifulSoup object
            markdown: Markdown content

        Returns:
            Parsed technical analysis data
        """
        # Parse using the TechnicalAnalysisParser
        # URL will be set during scraping
        return TechnicalAnalysisParser.parse_markdown(markdown, "") or {}


# Convenience functions for standalone usage
def scrape_crypto_technical(
    crypto: str = "ETH",
    url: Optional[str] = None,
    timeout: int = 60000,
    cache_bust: bool = False,
    headless: bool = True
) -> Dict[str, Any]:
    """
    Convenience function to scrape cryptocurrency technical analysis.

    Args:
        crypto: Cryptocurrency symbol (BTC, ETH, etc.) or URL slug (bitcoin, ethereum)
        url: Direct URL to scrape (overrides crypto parameter)
        timeout: Page load timeout in milliseconds
        cache_bust: Add timestamp to URL to bypass caching
        headless: Run browser in headless mode

    Returns:
        Dictionary containing scraped and parsed data

    Examples:
        >>> scrape_crypto_technical(crypto="BTC")
        >>> scrape_crypto_technical(crypto="bitcoin")
        >>> scrape_crypto_technical(url="https://www.investing.com/crypto/bitcoin/technical")
    """
    scraper = InvestingScraper(timeout=timeout, headless=headless)
    return scraper.scrape_crypto_technical_analysis(crypto=crypto, url=url, cache_bust=cache_bust)


def scrape_eth_technical(
    url: str = None,
    timeout: int = 30000,
    cache_bust: bool = False,
    headless: bool = True
) -> Dict[str, Any]:
    """
    Convenience function to scrape ETH technical analysis.

    DEPRECATED: Use scrape_crypto_technical(crypto="ETH") instead.
    Kept for backward compatibility.

    Args:
        url: URL to scrape (defaults to ETH technical page)
        timeout: Page load timeout in milliseconds
        cache_bust: Add timestamp to URL to bypass caching
        headless: Run browser in headless mode

    Returns:
        Dictionary containing scraped and parsed data
    """
    return scrape_crypto_technical(crypto="ETH", url=url, timeout=timeout, cache_bust=cache_bust, headless=headless)


def scrape_bitcoin_technical(
    url: str = None,
    timeout: int = 30000,
    cache_bust: bool = False,
    headless: bool = True
) -> Dict[str, Any]:
    """
    Convenience function to scrape Bitcoin technical analysis.

    Args:
        url: URL to scrape (defaults to Bitcoin technical page)
        timeout: Page load timeout in milliseconds
        cache_bust: Add timestamp to URL to bypass caching
        headless: Run browser in headless mode

    Returns:
        Dictionary containing scraped and parsed data
    """
    return scrape_crypto_technical(crypto="BTC", url=url, timeout=timeout, cache_bust=cache_bust, headless=headless)
