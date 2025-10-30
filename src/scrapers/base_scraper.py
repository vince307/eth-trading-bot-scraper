"""Base scraper class with common functionality"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from playwright.sync_api import sync_playwright, Browser, Page
from bs4 import BeautifulSoup
from markdownify import markdownify as md

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """
    Abstract base class for web scrapers.
    Provides common functionality for browser automation and HTML parsing.
    """

    def __init__(
        self,
        timeout: int = 30000,
        user_agent: Optional[str] = None,
        headless: bool = True
    ):
        """
        Initialize base scraper.

        Args:
            timeout: Page load timeout in milliseconds
            user_agent: Custom user agent string
            headless: Run browser in headless mode
        """
        self.timeout = timeout
        self.user_agent = user_agent or self._get_default_user_agent()
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    def _get_default_user_agent(self) -> str:
        """Get default user agent string."""
        return (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

    def _init_browser(self) -> None:
        """Initialize Playwright browser."""
        if self.browser is None:
            playwright = sync_playwright().start()
            self.browser = playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )
            logger.info("Browser initialized")

    def _close_browser(self) -> None:
        """Close Playwright browser."""
        if self.browser:
            self.browser.close()
            self.browser = None
            logger.info("Browser closed")

    def scrape_url(self, url: str, wait_for_selector: Optional[str] = None) -> Dict[str, Any]:
        """
        Scrape URL and return structured data.

        Args:
            url: URL to scrape
            wait_for_selector: Optional CSS selector to wait for

        Returns:
            Dictionary containing scraped data
        """
        try:
            self._init_browser()

            # Create new page with context
            context = self.browser.new_context(
                user_agent=self.user_agent,
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
                timezone_id='America/New_York',
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Cache-Control': 'max-age=0'
                }
            )

            # Add script to remove webdriver property
            context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)

            self.page = context.new_page()
            self.page.set_default_timeout(self.timeout)

            logger.info(f"Navigating to {url}")
            self.page.goto(url, wait_until="domcontentloaded")

            # Wait for specific selector if provided
            if wait_for_selector:
                self.page.wait_for_selector(wait_for_selector, timeout=self.timeout)

            # Additional wait for dynamic content
            self.page.wait_for_timeout(2000)

            # Get page content
            html_content = self.page.content()
            title = self.page.title()

            logger.info(f"Successfully scraped {url} - Title: {title}")

            # Convert HTML to markdown
            markdown_content = md(html_content, heading_style="ATX")

            # Parse with BeautifulSoup for additional processing
            soup = BeautifulSoup(html_content, "lxml")

            # Call subclass-specific parsing
            parsed_data = self.parse_content(soup, markdown_content)

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

        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return {
                "url": url,
                "success": False,
                "error": str(e),
                "scrapedAt": datetime.utcnow().isoformat() + "Z"
            }

        finally:
            if self.page:
                self.page.close()
                self.page = None
            self._close_browser()

    @abstractmethod
    def parse_content(self, soup: BeautifulSoup, markdown: str) -> Dict[str, Any]:
        """
        Parse scraped content - must be implemented by subclasses.

        Args:
            soup: BeautifulSoup object of HTML content
            markdown: Markdown conversion of HTML

        Returns:
            Parsed data dictionary
        """
        pass
