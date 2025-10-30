"""Utility helper functions"""
import os
from datetime import datetime
from typing import Optional


def get_env_var(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """
    Get environment variable with optional default value.

    Args:
        key: Environment variable name
        default: Default value if not found
        required: Raise error if not found and no default

    Returns:
        Environment variable value or default

    Raises:
        ValueError: If required=True and variable not found
    """
    value = os.getenv(key, default)
    if required and value is None:
        raise ValueError(f"Required environment variable '{key}' not found")
    return value


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """
    Format datetime as ISO 8601 string.

    Args:
        dt: Datetime object (defaults to now)

    Returns:
        ISO 8601 formatted timestamp string
    """
    if dt is None:
        dt = datetime.utcnow()
    return dt.isoformat() + "Z"


def extract_numeric_value(text: str) -> Optional[float]:
    """
    Extract numeric value from text string.

    Args:
        text: String containing numeric value

    Returns:
        Extracted float value or None
    """
    import re

    # Remove commas and whitespace
    text = text.replace(",", "").strip()

    # Try to find numeric value
    match = re.search(r'[-+]?\d*\.?\d+', text)
    if match:
        try:
            return float(match.group())
        except ValueError:
            return None
    return None
