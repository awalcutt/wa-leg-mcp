"""
Shared utilities for bill document retrieval.

This module contains shared functionality used by both the MCP resources and tools
for retrieving and processing bill documents from the Washington State Legislature.
"""

import logging
import re
from typing import Any, Dict, Literal, Optional, Union

import httpx

logger = logging.getLogger(__name__)

# Type aliases for clarity
BillFormat = Literal["xml", "htm", "pdf"]
Chamber = Literal["House", "Senate"]


def validate_biennium(biennium: str) -> bool:
    """
    Validate that a biennium string follows the correct format.

    A valid biennium must:
    - Follow the format "YYYY-YY" (e.g., "2025-26")
    - Start with an odd year (legislative sessions begin in odd years)
    - Second year must be first year + 1
    - Not be in the future

    Args:
        biennium: The biennium string to validate in format "YYYY-YY"

    Returns:
        True if the biennium is valid, False otherwise
    """
    if not re.match(r"^\d{4}-\d{2}$", biennium):
        return False

    year1, year2 = biennium.split("-")

    try:
        year1_int = int(year1)
        year2_int = int("20" + year2)  # Assuming 21st century
    except ValueError:
        return False

    # Check that the first year is odd
    if year1_int % 2 != 1:
        return False

    # Check that second year is first year + 1
    if year2_int != year1_int + 1:
        return False

    # Check if it's not in the future
    from datetime import datetime

    current_year = datetime.now().year
    return not year1_int > current_year


def validate_chamber(chamber: str) -> bool:
    """
    Validate that a chamber name is valid for Washington State Legislature.

    Args:
        chamber: The chamber name to validate (case-sensitive)

    Returns:
        True if the chamber name is exactly "House" or "Senate", False otherwise
    """
    return chamber in ["House", "Senate"]


def validate_bill_number(bill_number: Union[int, str]) -> bool:
    """
    Validate that a bill number is in the correct format.

    Args:
        bill_number: The bill number to validate. Can be an integer or string
                    containing only digits. Must be 3-5 digits long.

    Returns:
        True if the bill number is valid, False otherwise
    """
    # Convert to string if integer
    bill_str = str(bill_number)

    # Must be digits only and 3-5 digits long
    return re.match(r"^\d{3,5}$", bill_str) is not None


def get_bill_document_url(
    biennium: str, chamber: Chamber, bill_number: Union[int, str], bill_format: BillFormat = "xml"
) -> str:
    """
    Generate the URL for a Washington State Legislature bill document.

    Args:
        biennium: Legislative biennium in format "YYYY-YY" (e.g., "2025-26")
        chamber: Chamber name - must be exactly "House" or "Senate"
        bill_number: Bill number as integer or string (e.g., 1234 or "1234")
        bill_format: Document format - "xml", "htm", or "pdf" (defaults to "xml")

    Returns:
        The full URL for accessing the bill document
    """
    base_url = f"https://lawfilesext.leg.wa.gov/biennium/{biennium}"

    if bill_format == "xml":
        return f"{base_url}/Xml/Bills/{chamber}%20Bills/{bill_number}.xml"
    elif bill_format == "htm":
        return f"{base_url}/Htm/Bills/{chamber}%20Bills/{bill_number}.htm"
    else:  # pdf
        return f"{base_url}/Pdf/Bills/{chamber}%20Bills/{bill_number}.pdf"


async def fetch_bill_document(
    biennium: str, chamber: Chamber, bill_number: str, bill_format: BillFormat = "xml"
) -> Union[str, Dict[str, Any]]:
    """
    Fetch a bill document from the Washington State Legislature website.

    Args:
        biennium: Legislative biennium in format "YYYY-YY" (e.g., "2025-26")
        chamber: Chamber name - must be exactly "House" or "Senate"
        bill_number: Bill number as string (e.g., "1234")
        bill_format: Document format - "xml", "htm", or "pdf" (defaults to "xml")

    Returns:
        For XML and HTM formats: The actual document content as text
        For PDF format: A dictionary with the URL to access the PDF

    Raises:
        ValueError: If parameters are invalid
        httpx.HTTPError: If document fetch fails
    """
    # Validate parameters
    if not validate_biennium(biennium):
        return {
            "error": f"Invalid biennium format: {biennium}. "
            "Must be YYYY-YY starting with odd year (e.g., 2025-26)"
        }

    if not validate_chamber(chamber):
        return {
            "error": f"Invalid chamber: {chamber}. "
            "Must be exactly 'House' or 'Senate' (case-sensitive)"
        }

    if not validate_bill_number(bill_number):
        return {
            "error": f"Invalid bill number: {bill_number}. "
            "Must be 3-5 digits without prefixes (e.g., 1234 not HB1234)"
        }

    document_url = get_bill_document_url(biennium, chamber, bill_number, bill_format)

    # For PDF, just return the URL
    if bill_format == "pdf":
        return {
            "url": document_url,
            "mime_type": "application/pdf",
            "bill_info": {
                "biennium": biennium,
                "chamber": chamber,
                "bill_number": bill_number,
                "format": bill_format,
            },
            "description": f"PDF URL for {chamber} Bill {bill_number} from the {biennium} biennium",
            "note": "Use the 'url' field to access the PDF document",
        }

    # For XML and HTM, fetch the content
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(document_url, timeout=30.0)
            response.raise_for_status()
            return response.text

    except Exception as e:
        logger.error(f"Failed to fetch bill document: {e}")
        # Return URL as fallback with error
        return {
            "url": document_url,
            "error": f"Could not fetch content: {str(e)}",
            "bill_info": {
                "biennium": biennium,
                "chamber": chamber,
                "bill_number": bill_number,
                "format": bill_format,
            },
            "note": "Document content unavailable, URL provided as fallback",
        }


def determine_chamber_from_bill_id(bill_id: str) -> Optional[Chamber]:
    """
    Determine the chamber (House or Senate) from a bill ID.

    Args:
        bill_id: Bill ID in format like "HB 1234" or "SB 5678"

    Returns:
        "House" for HB, "Senate" for SB, None if can't determine
    """
    if bill_id.startswith("HB") or bill_id.startswith("SHB") or bill_id.startswith("ESHB"):
        return "House"
    elif bill_id.startswith("SB") or bill_id.startswith("SSB") or bill_id.startswith("ESSB"):
        return "Senate"
    return None


def extract_bill_number(bill_id: str) -> Optional[str]:
    """
    Extract the numeric bill number from a bill ID.

    Args:
        bill_id: Bill ID in format like "HB 1234" or "SB 5678"

    Returns:
        The numeric portion as a string, or None if can't extract
    """
    match = re.search(r"(\d{3,5})", bill_id)
    if match:
        return match.group(1)
    return None
