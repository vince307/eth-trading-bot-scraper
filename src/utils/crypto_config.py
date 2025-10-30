"""
Cryptocurrency configuration and URL mapping
Defines supported cryptocurrencies for technical analysis scraping
"""
from typing import Dict, Optional, List
from dataclasses import dataclass


@dataclass
class CryptoConfig:
    """Configuration for a cryptocurrency."""
    symbol: str  # Trading symbol (e.g., BTC, ETH)
    name: str  # Full name (e.g., Bitcoin, Ethereum)
    url_slug: str  # URL path component for investing.com

    def get_technical_url(self) -> str:
        """Get the technical analysis URL for this cryptocurrency."""
        return f"https://www.investing.com/crypto/{self.url_slug}/technical"


# Supported cryptocurrencies
SUPPORTED_CRYPTOS: Dict[str, CryptoConfig] = {
    "BTC": CryptoConfig(symbol="BTC", name="Bitcoin", url_slug="bitcoin"),
    "ETH": CryptoConfig(symbol="ETH", name="Ethereum", url_slug="ethereum"),
    "ADA": CryptoConfig(symbol="ADA", name="Cardano", url_slug="cardano"),
    "SOL": CryptoConfig(symbol="SOL", name="Solana", url_slug="solana"),
    "DOT": CryptoConfig(symbol="DOT", name="Polkadot", url_slug="polkadot"),
    "LINK": CryptoConfig(symbol="LINK", name="Chainlink", url_slug="chainlink"),
    "MATIC": CryptoConfig(symbol="MATIC", name="Polygon", url_slug="polygon"),
    "LTC": CryptoConfig(symbol="LTC", name="Litecoin", url_slug="litecoin"),
    "XRP": CryptoConfig(symbol="XRP", name="XRP", url_slug="xrp"),
    "DOGE": CryptoConfig(symbol="DOGE", name="Dogecoin", url_slug="dogecoin"),
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
