"""
Formatting utilities for Washington State Legislature data.
"""

from datetime import datetime


def get_current_biennium() -> str:
    """
    Calculate the current legislative biennium.

    In Washington State, the biennium is a two-year legislative cycle
    that begins in odd-numbered years.

    Returns:
        str: Current biennium in format "YYYY-YY" (e.g., "2025-26")
    """
    current_year = datetime.now().year
    if current_year % 2 == 0:
        # Even years are the second year of a biennium
        return f"{current_year - 1}-{str(current_year)[2:]}"
    else:
        # Odd years are the first year of a biennium
        return f"{current_year}-{str(current_year + 1)[2:]}"


def get_current_year() -> str:
    """
    Get the current year as a string.

    Returns:
        str: Current year in format "YYYY" (e.g., "2025")
    """
    return str(datetime.now().year)
