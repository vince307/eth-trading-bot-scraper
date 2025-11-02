"""
Cryptocurrency configuration and URL mapping
Defines supported cryptocurrencies for technical analysis scraping
"""
from typing import Dict, Optional, List
from dataclasses import dataclass
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class CryptoConfig:
    """Configuration for a cryptocurrency."""
    symbol: str  # Trading symbol (e.g., BTC, ETH)
    name: str  # Full name (e.g., Bitcoin, Ethereum)
    url_slug: str  # URL path component for investing.com (deprecated)
    coingecko_id: str  # CoinGecko API coin ID

    def get_technical_url(self) -> str:
        """Get the technical analysis URL for this cryptocurrency."""
        return f"https://www.investing.com/crypto/{self.url_slug}/technical"


# Supported cryptocurrencies
SUPPORTED_CRYPTOS: Dict[str, CryptoConfig] = {
    "BTC": CryptoConfig(symbol="BTC", name="Bitcoin", url_slug="bitcoin", coingecko_id="bitcoin"),
    "ETH": CryptoConfig(symbol="ETH", name="Ethereum", url_slug="ethereum", coingecko_id="ethereum"),
    "ADA": CryptoConfig(symbol="ADA", name="Cardano", url_slug="cardano", coingecko_id="cardano"),
    "SOL": CryptoConfig(symbol="SOL", name="Solana", url_slug="solana", coingecko_id="solana"),
    "DOT": CryptoConfig(symbol="DOT", name="Polkadot", url_slug="polkadot", coingecko_id="polkadot"),
    "LINK": CryptoConfig(symbol="LINK", name="Chainlink", url_slug="chainlink", coingecko_id="chainlink"),
    "MATIC": CryptoConfig(symbol="MATIC", name="Polygon", url_slug="polygon", coingecko_id="matic-network"),
    "LTC": CryptoConfig(symbol="LTC", name="Litecoin", url_slug="litecoin", coingecko_id="litecoin"),
    "XRP": CryptoConfig(symbol="XRP", name="XRP", url_slug="xrp", coingecko_id="ripple"),
    "DOGE": CryptoConfig(symbol="DOGE", name="Dogecoin", url_slug="dogecoin", coingecko_id="dogecoin"),
}

# Allow lookup by URL slug as well
SLUG_TO_SYMBOL: Dict[str, str] = {
    config.url_slug: symbol for symbol, config in SUPPORTED_CRYPTOS.items()
}


def get_crypto_config(identifier: str) -> Optional[CryptoConfig]:
    """
    Get cryptocurrency configuration by symbol or URL slug.

    Args:
        identifier: Symbol (BTC, ETH) or URL slug (bitcoin, ethereum)

    Returns:
        CryptoConfig if found, None otherwise

    Examples:
        >>> get_crypto_config("BTC")
        CryptoConfig(symbol='BTC', name='Bitcoin', url_slug='bitcoin')
        >>> get_crypto_config("bitcoin")
        CryptoConfig(symbol='BTC', name='Bitcoin', url_slug='bitcoin')
    """
    # Try as symbol first (case-insensitive)
    identifier_upper = identifier.upper()
    if identifier_upper in SUPPORTED_CRYPTOS:
        return SUPPORTED_CRYPTOS[identifier_upper]

    # Try as URL slug (case-insensitive)
    identifier_lower = identifier.lower()
    if identifier_lower in SLUG_TO_SYMBOL:
        symbol = SLUG_TO_SYMBOL[identifier_lower]
        return SUPPORTED_CRYPTOS[symbol]

    return None


def is_supported_crypto(identifier: str) -> bool:
    """
    Check if a cryptocurrency is supported.

    Args:
        identifier: Symbol or URL slug

    Returns:
        True if supported, False otherwise
    """
    return get_crypto_config(identifier) is not None


def get_supported_symbols() -> List[str]:
    """
    Get list of supported cryptocurrency symbols.

    Returns:
        List of symbols (e.g., ['BTC', 'ETH', ...])
    """
    return list(SUPPORTED_CRYPTOS.keys())


def get_enabled_cryptos() -> List[str]:
    """
    Get list of enabled cryptocurrencies from environment variable.

    Reads from SUPPORTED_CRYPTOS environment variable (comma-separated).
    Falls back to BTC,ETH,SOL if not set.

    Returns:
        List of enabled crypto symbols (e.g., ['BTC', 'ETH', 'SOL'])

    Examples:
        # With SUPPORTED_CRYPTOS=BTC,ETH,SOL
        >>> get_enabled_cryptos()
        ['BTC', 'ETH', 'SOL']

        # Without environment variable (default)
        >>> get_enabled_cryptos()
        ['BTC', 'ETH', 'SOL']
    """
    # Get from environment variable
    env_cryptos = os.getenv('SUPPORTED_CRYPTOS', 'BTC,ETH,SOL')

    # Parse comma-separated list
    cryptos = [c.strip().upper() for c in env_cryptos.split(',') if c.strip()]

    # Validate all are supported
    valid_cryptos = []
    for crypto in cryptos:
        if crypto in SUPPORTED_CRYPTOS:
            valid_cryptos.append(crypto)
        else:
            print(f"Warning: {crypto} is not a supported cryptocurrency, skipping")

    # Fallback to BTC,ETH,SOL if none are valid
    if not valid_cryptos:
        print("Warning: No valid cryptocurrencies found, using default: BTC,ETH,SOL")
        return ['BTC', 'ETH', 'SOL']

    return valid_cryptos


def get_technical_url(identifier: str) -> Optional[str]:
    """
    Get technical analysis URL for a cryptocurrency.

    Args:
        identifier: Symbol or URL slug

    Returns:
        URL string if found, None otherwise

    Examples:
        >>> get_technical_url("BTC")
        'https://www.investing.com/crypto/bitcoin/technical'
        >>> get_technical_url("ethereum")
        'https://www.investing.com/crypto/ethereum/technical'
    """
    config = get_crypto_config(identifier)
    return config.get_technical_url() if config else None
