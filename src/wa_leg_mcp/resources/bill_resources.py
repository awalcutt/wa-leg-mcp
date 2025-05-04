"""
MCP Resources for Washington State Legislature bill documents.

This module provides Model Context Protocol (MCP) resources for accessing Washington State
Legislature bill documents in various formats (XML, HTML, and PDF). These resources use
URI templates following RFC 6570 to enable dynamic access to bills from any biennium,
chamber, and bill number combination.

The resources follow the FastMCP SDK patterns and are designed to be easily
discoverable by AI assistants like Claude.
"""

import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union

import httpx
from mcp.server.fastmcp.resources import (
    ResourceTemplate,
)

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

    Examples:
        >>> validate_biennium("2025-26")
        True
        >>> validate_biennium("2024-25")  # Starts with even year
        False
        >>> validate_biennium("2025-27")  # Years not consecutive
        False
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
    current_year = datetime.now().year
    return not year1_int > current_year


def validate_chamber(chamber: str) -> bool:
    """
    Validate that a chamber name is valid for Washington State Legislature.

    Args:
        chamber: The chamber name to validate (case-sensitive)

    Returns:
        True if the chamber name is exactly "House" or "Senate", False otherwise

    Note:
        Chamber names are case-sensitive and must be exactly "House" or "Senate".
        Do not use abbreviations like "H" or "S".
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

    Examples:
        >>> validate_bill_number(1234)  # Integer
        True
        >>> validate_bill_number("1234")  # String of digits
        True
        >>> validate_bill_number("HB1234")  # Contains non-digits
        False
        >>> validate_bill_number(12)  # Too short
        False

    Note:
        Bill numbers should NOT include prefixes like "HB" or "SB". Just the numeric
        portion is required (e.g., "1234" not "HB1234").
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

    Examples:
        >>> get_bill_document_url("2025-26", "House", 1234, "xml")
        'https://lawfilesext.leg.wa.gov/biennium/2025-26/Xml/Bills/House%20Bills/1234.xml'

        >>> get_bill_document_url("2025-26", "Senate", 5002, "pdf")
        'https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Bills/5002.pdf'

    Note:
        URLs use URL-encoded spaces (%20) between chamber name and "Bills"
    """
    base_url = f"https://lawfilesext.leg.wa.gov/biennium/{biennium}"

    if bill_format == "xml":
        return f"{base_url}/Xml/Bills/{chamber}%20Bills/{bill_number}.xml"
    elif bill_format == "htm":
        return f"{base_url}/Htm/Bills/{chamber}%20Bills/{bill_number}.htm"
    else:  # pdf
        return f"{base_url}/Pdf/Bills/{chamber}%20Bills/{bill_number}.pdf"


def get_bill_document_templates() -> List[ResourceTemplate]:
    """
    Create the resource templates for Washington State Legislature bill documents.

    These templates define the URI patterns that AI assistants can use to request
    bill documents. Multiple templates are provided for convenience and clarity.

    Returns:
        List of ResourceTemplate objects defining available URI patterns

    Available URI Templates:
        1. Generic format template:
           bill://document/{bill_format}/{biennium}/{chamber}/{bill_number}
           - bill_format: "xml", "htm", or "pdf"
           - biennium: Legislative period like "2025-26"
           - chamber: "House" or "Senate"
           - bill_number: Numeric bill identifier (e.g., "1234")

        2. XML-specific template (recommended):
           bill://xml/{biennium}/{chamber}/{bill_number}
           - Best for AI processing due to structured data

        3. HTML-specific template:
           bill://htm/{biennium}/{chamber}/{bill_number}
           - Human-readable with hyperlinks to referenced laws

        4. PDF URL template:
           bill://pdf/{biennium}/{chamber}/{bill_number}
           - Returns URL only (does not fetch content)

    Examples:
        To get the XML for House Bill 1234 from 2025-26:
        bill://xml/2025-26/House/1234

        To get the HTML version:
        bill://htm/2025-26/House/1234

    Note:
        XML format is recommended for AI consumption as it contains structured
        semantic markup for bill sections, amendments, and metadata.
    """
    templates = []

    # Main template for all formats
    def handle_bill_document(
        bill_format: BillFormat, biennium: str, chamber: Chamber, bill_number: str
    ) -> str:
        """Fetch bill document based on format."""
        url = get_bill_document_url(biennium, chamber, bill_number, bill_format)
        # Note: In actual use, this would be called asynchronously
        # For template creation, we just return the URL
        return url

    templates.append(
        ResourceTemplate.from_function(
            fn=handle_bill_document,
            uri_template="bill://document/{format}/{biennium}/{chamber}/{bill_number}",
            name="Washington State Legislature Bill Documents",
            description=(
                "Access Washington State Legislature bills in XML, HTM, or PDF format. "
                "Parameters: format=xml|htm|pdf, biennium=YYYY-YY (e.g. 2025-26), "
                "chamber=House|Senate, bill_number=numeric (e.g. 1234)"
            ),
            mime_type="application/xml",  # Default mime type
        )
    )

    # XML-specific template
    def handle_xml_bill(biennium: str, chamber: Chamber, bill_number: str) -> str:
        """Fetch XML bill document."""
        return get_bill_document_url(biennium, chamber, bill_number, "xml")

    templates.append(
        ResourceTemplate.from_function(
            fn=handle_xml_bill,
            uri_template="bill://xml/{biennium}/{chamber}/{bill_number}",
            name="Washington State Legislature Bill XML",
            description=(
                "Access bill documents in structured XML format (recommended for AI). "
                "Parameters: biennium=YYYY-YY, chamber=House|Senate, bill_number=numeric"
            ),
            mime_type="application/xml",
        )
    )

    # HTML-specific template
    def handle_html_bill(biennium: str, chamber: Chamber, bill_number: str) -> str:
        """Fetch HTML bill document."""
        return get_bill_document_url(biennium, chamber, bill_number, "htm")

    templates.append(
        ResourceTemplate.from_function(
            fn=handle_html_bill,
            uri_template="bill://htm/{biennium}/{chamber}/{bill_number}",
            name="Washington State Legislature Bill HTML",
            description=(
                "Access bill documents in HTML format with hyperlinks. "
                "Parameters: biennium=YYYY-YY, chamber=House|Senate, bill_number=numeric"
            ),
            mime_type="text/html",
        )
    )

    # PDF URL template
    def handle_pdf_bill(biennium: str, chamber: Chamber, bill_number: str) -> str:
        """Get PDF bill document URL."""
        return get_bill_document_url(biennium, chamber, bill_number, "pdf")

    templates.append(
        ResourceTemplate.from_function(
            fn=handle_pdf_bill,
            uri_template="bill://pdf/{biennium}/{chamber}/{bill_number}",
            name="Washington State Legislature Bill PDF URLs",
            description=(
                "Get URLs for bill PDF documents (content not fetched). "
                "Parameters: biennium=YYYY-YY, chamber=House|Senate, bill_number=numeric"
            ),
            mime_type="application/pdf",
        )
    )

    return templates


async def read_bill_document(
    uri: str,
    biennium: str,
    chamber: Chamber,
    bill_number: str,
    bill_format: Optional[BillFormat] = None,
) -> Union[str, Dict[str, Any]]:
    """
    Read a Washington State Legislature bill document resource.

    This function handles the actual fetching of bill documents based on the
    provided parameters. It's called by the resource templates when they match
    a URI pattern.

    Args:
        uri: The original resource URI
        biennium: Legislative biennium (e.g., "2025-26")
        chamber: "House" or "Senate"
        bill_number: Bill number (numeric)
        bill_format: Optional format override ("xml", "htm", or "pdf")

    Returns:
        For XML and HTM formats: The actual document content as text
        For PDF format: A dictionary with the URL to access the PDF

    Raises:
        ValueError: If parameters are invalid
        httpx.HTTPError: If document fetch fails
    """
    # Extract format from URI if not provided
    if bill_format is None:
        if uri.startswith("bill://xml/"):
            bill_format = "xml"
        elif uri.startswith("bill://htm/"):
            bill_format = "htm"
        elif uri.startswith("bill://pdf/"):
            bill_format = "pdf"
        elif uri.startswith("bill://document/"):
            # Extract format from first path component
            match = re.match(r"bill://document/([^/]+)/", uri)
            if match:
                bill_format = match.group(1)
        else:
            bill_format = "xml"  # Default to XML

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
