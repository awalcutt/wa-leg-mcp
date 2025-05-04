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
from typing import Any, Dict, List, Optional, Union

from mcp.server.fastmcp.resources import (
    ResourceTemplate,
)

from ..utils.bill_document_utils import (
    BillFormat,
    Chamber,
    fetch_bill_document,
    get_bill_document_url,
)

logger = logging.getLogger(__name__)


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
            import re

            match = re.match(r"bill://document/([^/]+)/", uri)
            if match:
                bill_format = match.group(1)
        else:
            bill_format = "xml"  # Default to XML

    # Use the shared fetch_bill_document function
    return await fetch_bill_document(biennium, chamber, bill_number, bill_format)
