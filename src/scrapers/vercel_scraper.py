"""
Vercel-optimized scraper that handles Playwright installation issues
Uses Playwright if available, falls back to finding alternative data sources
"""
from typing import Dict, Any, Optional
import logging
import os

logger = logging.getLogger(__name__)


class VercelScraper:
    """
    Scraper optimized for Vercel serverless environment.
    Attempts to use Playwright, handles installation issues gracefully.
    """

    def __init__(self, timeout: int = 60000):
        self.timeout = timeout
        self.playwright_available = False
        self._check_playwright()

    def _check_playwright(self):
        """Check if Playwright is available and properly installed."""
        try:
            from playwright.sync_api import sync_playwright
            self.playwright_available = True
            logger.info("Playwright is available")
        except (ImportError, Exception) as e:
            logger.warning(f"Playwright not available: {e}")
            self.playwright_available = False

    def scrape_crypto_technical_analysis(
        self,
        crypto: Optional[str] = None,
        url: Optional[str] = None,
        cache_bust: bool = False
    ) -> Dict[str, Any]:
        """
        Scrape cryptocurrency technical analysis.
        Tries Playwright first, falls back to HTTP if needed.
        """
        if self.playwright_available:
            return self._scrape_with_playwright(crypto, url, cache_bust)
        else:
            logger.warning("Playwright not available, using fallback method")
            return self._scrape_fallback(crypto, url, cache_bust)

    def _scrape_with_playwright(
        self,
        crypto: Optional[str],
        url: Optional[str],
        cache_bust: bool
    ) -> Dict[str, Any]:
        """Scrape using Playwright (JavaScript execution)."""
        try:
            from src.scrapers.investing_scraper import InvestingScraper

            scraper = InvestingScraper(timeout=self.timeout, headless=True)
            result = scraper.scrape_crypto_technical_analysis(
                crypto=crypto,
                url=url,
                cache_bust=cache_bust
            )

            # Verify we got technical indicators
            if result.get('success') and result.get('parsed'):
                indicators = result['parsed'].get('technicalIndicators', [])
                if len(indicators) > 0:
                    logger.info(f"Successfully scraped with Playwright: {len(indicators)} indicators")
                    return result
                else:
                    logger.warning("Playwright scrape returned no indicators, trying fallback")
                    return self._scrape_fallback(crypto, url, cache_bust)

            return result

        except Exception as e:
            logger.error(f"Playwright scraping failed: {e}")
            logger.info("Falling back to HTTP scraper")
            return self._scrape_fallback(crypto, url, cache_bust)

    def _scrape_fallback(
        self,
        crypto: Optional[str],
        url: Optional[str],
        cache_bust: bool
    ) -> Dict[str, Any]:
        """
        Fallback method using HTTP scraper.
        Note: Will not have technical indicators due to JavaScript requirement.
        """
        from src.scrapers.simple_scraper import SimpleScraper

        logger.warning(
            "Using SimpleScraper fallback - technical indicators may be empty. "
            "For full functionality, ensure Playwright is properly installed."
        )

        scraper = SimpleScraper(timeout=30)
        result = scraper.scrape_crypto_technical_analysis(
            crypto=crypto,
            url=url,
            cache_bust=cache_bust
        )

        # Add warning to result
        if result.get('success') and result.get('parsed'):
            result['warning'] = (
                "Technical indicators unavailable: Playwright required but not installed. "
                "Only pivot points are available."
            )

        return result
