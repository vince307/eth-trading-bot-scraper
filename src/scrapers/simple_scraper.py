"""
Simple HTTP scraper without Playwright - Vercel compatible
Uses requests + BeautifulSoup for static HTML scraping
"""
from typing import Dict, Any, Optional
from datetime import datetime
import logging

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

from ..parsers.technical_analysis_parser import TechnicalAnalysisParser
from ..utils.crypto_config import get_crypto_config, get_technical_url

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleScraper:
    """
    Simple HTTP-based scraper without browser automation.
    Compatible with serverless environments like Vercel.
    Supports multiple cryptocurrencies (BTC, ETH, ADA, SOL, etc.)
    """

    def __init__(self, timeout: int = 30):
        """
        Initialize simple scraper.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.default_crypto = "ETH"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"'
        }

    def scrape_url(self, url: str) -> Dict[str, Any]:
        """
        Scrape URL using HTTP requests.

        Args:
            url: URL to scrape

        Returns:
            Dictionary containing scraped data
        """
        try:
            logger.info(f"Scraping URL: {url}")

            # Add referer for subsequent requests
            headers = self.headers.copy()
            if 'investing.com' in url:
                headers['Referer'] = 'https://www.investing.com/'

            # Make HTTP request with session
            response = self.session.get(url, headers=headers, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()

            html_content = response.text
            logger.info(f"Successfully fetched {len(html_content)} bytes")

            # Parse with BeautifulSoup
            soup = BeautifulSoup(html_content, 'lxml')

            # Get title
            title_tag = soup.find('title')
            title = title_tag.text if title_tag else "Unknown"

            # Convert to markdown
            markdown_content = md(html_content, heading_style="ATX")

            logger.info(f"Successfully parsed HTML - Title: {title}")

            # Parse technical analysis
            parsed_data = TechnicalAnalysisParser.parse_markdown(markdown_content, url)

            return {
                "url": url,
                "title": title,
                "html": html_content,
                "markdown": markdown_content,
                "contentLength": len(markdown_content),
                "scrapedAt": datetime.utcnow().isoformat() + "Z",
                "parsed": parsed_data,
                "success": True
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            return {
                "url": url,
                "success": False,
                "error": f"Request failed: {str(e)}",
                "scrapedAt": datetime.utcnow().isoformat() + "Z"
            }
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return {
                "url": url,
                "success": False,
                "error": str(e),
                "scrapedAt": datetime.utcnow().isoformat() + "Z"
            }

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

        return self.scrape_url(target_url)

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


# Convenience functions
def scrape_crypto_technical(
    crypto: str = "ETH",
    url: Optional[str] = None,
    timeout: int = 30,
    cache_bust: bool = False
) -> Dict[str, Any]:
    """
    Convenience function to scrape cryptocurrency technical analysis.

    Args:
        crypto: Cryptocurrency symbol (BTC, ETH, etc.) or URL slug (bitcoin, ethereum)
        url: Direct URL to scrape (overrides crypto parameter)
        timeout: Request timeout in seconds
        cache_bust: Add timestamp to URL to bypass caching

    Returns:
        Dictionary containing scraped and parsed data

    Examples:
        >>> scrape_crypto_technical(crypto="BTC")
        >>> scrape_crypto_technical(crypto="bitcoin")
        >>> scrape_crypto_technical(url="https://www.investing.com/crypto/bitcoin/technical")
    """
    scraper = SimpleScraper(timeout=timeout)
    return scraper.scrape_crypto_technical_analysis(crypto=crypto, url=url, cache_bust=cache_bust)


def scrape_eth_technical(
    url: str = None,
    timeout: int = 30,
    cache_bust: bool = False
) -> Dict[str, Any]:
    """
    Convenience function to scrape ETH technical analysis.

    DEPRECATED: Use scrape_crypto_technical(crypto="ETH") instead.
    Kept for backward compatibility.

    Args:
        url: URL to scrape (defaults to ETH technical page)
        timeout: Request timeout in seconds
        cache_bust: Add timestamp to URL to bypass caching

    Returns:
        Dictionary containing scraped and parsed data
    """
    return scrape_crypto_technical(crypto="ETH", url=url, timeout=timeout, cache_bust=cache_bust)


def scrape_bitcoin_technical(
    url: str = None,
    timeout: int = 30,
    cache_bust: bool = False
) -> Dict[str, Any]:
    """
    Convenience function to scrape Bitcoin technical analysis.

    Args:
        url: URL to scrape (defaults to Bitcoin technical page)
        timeout: Request timeout in seconds
        cache_bust: Add timestamp to URL to bypass caching

    Returns:
        Dictionary containing scraped and parsed data
    """
    return scrape_crypto_technical(crypto="BTC", url=url, timeout=timeout, cache_bust=cache_bust)
