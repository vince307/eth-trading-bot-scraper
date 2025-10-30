#!/usr/bin/env python3
"""
Scheduled cryptocurrency scraper
Runs on a schedule to scrape technical analysis data and save to Supabase
"""
import schedule
import time
import logging
from datetime import datetime
from typing import List

from src.scrapers.investing_scraper import scrape_crypto_technical
from src.database.supabase_client import SupabaseClient
from src.utils.crypto_config import get_supported_symbols

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scraper_cron.log')
    ]
)
logger = logging.getLogger(__name__)


class CryptoScraperScheduler:
    """Scheduled cryptocurrency scraper"""

    def __init__(self, cryptos: List[str] = None):
        """
        Initialize scraper scheduler.

        Args:
            cryptos: List of cryptocurrency symbols to scrape.
                    If None, scrapes all supported cryptocurrencies.
        """
        self.cryptos = cryptos or get_supported_symbols()
        self.db_client = SupabaseClient(use_service_role=True)
        logger.info(f"Initialized scraper for {len(self.cryptos)} cryptocurrencies: {', '.join(self.cryptos)}")

    def scrape_single_crypto(self, crypto: str) -> bool:
        """
        Scrape a single cryptocurrency and save to database.

        Args:
            crypto: Cryptocurrency symbol (e.g., 'BTC', 'ETH')

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Scraping {crypto}...")

            # Scrape with Playwright
            result = scrape_crypto_technical(
                crypto=crypto,
                cache_bust=True,  # Always get fresh data
                headless=True
            )

            if not result.get('success'):
                logger.error(f"Failed to scrape {crypto}: {result.get('error')}")
                return False

            parsed_data = result.get('parsed')
            if not parsed_data:
                logger.error(f"No parsed data for {crypto}")
                return False

            # Check if we got technical indicators
            indicators_count = len(parsed_data.get('technicalIndicators', []))
            ma_count = len(parsed_data.get('movingAverages', []))
            pivot_count = len(parsed_data.get('pivotPoints', []))

            logger.info(
                f"{crypto} scraped: {indicators_count} indicators, "
                f"{ma_count} moving averages, {pivot_count} pivot points"
            )

            # Save to database
            success = self.db_client.insert_technical_analysis(parsed_data)

            if success:
                logger.info(f"✓ Successfully saved {crypto} to database")
                return True
            else:
                logger.error(f"✗ Failed to save {crypto} to database")
                return False

        except Exception as e:
            logger.error(f"✗ Error scraping {crypto}: {e}", exc_info=True)
            return False

    def scrape_all_cryptos(self):
        """Scrape all configured cryptocurrencies"""
        logger.info("=" * 60)
        logger.info(f"Starting scheduled scrape at {datetime.now()}")
        logger.info("=" * 60)

        successful = 0
        failed = 0

        for crypto in self.cryptos:
            if self.scrape_single_crypto(crypto):
                successful += 1
            else:
                failed += 1

            # Small delay between requests to avoid rate limiting
            time.sleep(3)

        logger.info("=" * 60)
        logger.info(f"Scrape completed: {successful} successful, {failed} failed")
        logger.info("=" * 60)

    def run_once(self):
        """Run scraper once (useful for testing)"""
        logger.info("Running one-time scrape...")
        self.scrape_all_cryptos()

    def run_scheduled(self, interval_minutes: int = 60):
        """
        Run scraper on a schedule.

        Args:
            interval_minutes: Interval between scrapes in minutes (default: 60)
        """
        logger.info(f"Starting scheduled scraper (interval: {interval_minutes} minutes)")

        # Schedule the job
        schedule.every(interval_minutes).minutes.do(self.scrape_all_cryptos)

        # Run immediately on startup
        logger.info("Running initial scrape...")
        self.scrape_all_cryptos()

        # Keep running
        logger.info("Scheduler running. Press Ctrl+C to stop.")
        try:
            while True:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")


def main():
    """Main entry point"""
    import os
    import sys

    # Get configuration from environment variables
    interval = int(os.getenv('SCRAPER_INTERVAL_MINUTES', '60'))

    # Get specific cryptos from environment, or use all
    cryptos_env = os.getenv('SCRAPER_CRYPTOS')
    cryptos = cryptos_env.split(',') if cryptos_env else None

    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--once':
            # Run once and exit
            scheduler = CryptoScraperScheduler(cryptos=cryptos)
            scheduler.run_once()
            return
        elif sys.argv[1] == '--help':
            print("""
Crypto Scraper Scheduler

Usage:
  python scraper_cron.py              # Run on schedule (default: hourly)
  python scraper_cron.py --once       # Run once and exit
  python scraper_cron.py --help       # Show this help

Environment Variables:
  SCRAPER_INTERVAL_MINUTES  # Scraping interval (default: 60)
  SCRAPER_CRYPTOS          # Comma-separated list of cryptos (default: all)

  Example: SCRAPER_CRYPTOS=BTC,ETH,ADA python scraper_cron.py
            """)
            return

    # Run scheduled scraper
    scheduler = CryptoScraperScheduler(cryptos=cryptos)
    scheduler.run_scheduled(interval_minutes=interval)


if __name__ == '__main__':
    main()
