"""
Bill-related MCP tools for Washington State Legislature data.
"""

import logging
from typing import Any, Dict, Optional

from ..clients.wsl_client import WSLClient
from ..utils.formatters import get_current_biennium, get_current_year

logger = logging.getLogger(__name__)

wsl_client = WSLClient()


def get_bill_info(bill_number: int, biennium: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve detailed information about a specific bill.

    Args:
        bill_number: Bill number as an integer (e.g., 1234 for HB1234, 5678 for SB5678)
        biennium: Legislative biennium in format "YYYY-YY" (e.g., "2025-26") (optional, defaults to current)

    Returns:
        Dict containing bill details including description, sponsor, status, etc.
    """
    try:
        if not biennium:
            biennium = get_current_biennium()

        logger.info(f"Fetching bill info for {bill_number} in biennium {biennium}")

        # Get bill information
        bills_data = wsl_client.get_legislation(biennium, str(bill_number))

        if not bills_data or len(bills_data) == 0:
            return {"error": f"Bill {bill_number} not found in biennium {biennium}"}

        # Use the first bill in the list
        bill_data = bills_data[0]

        # Extract relevant information based on the example response format
        result = {
            "bill_number": bill_number,
            "biennium": biennium,
            "title": bill_data.get("long_description", ""),
            "short_description": bill_data.get("short_description", ""),
            "sponsor": bill_data.get("sponsor", ""),
            "status": (
                bill_data.get("current_status", {}).get("status", "")
                if bill_data.get("current_status")
                else ""
            ),
            "introduced_date": bill_data.get("introduced_date", ""),
            "companions": bill_data.get("companions", []),
            "legal_title": bill_data.get("legal_title", ""),
            "active": bill_data.get("active", False),
            "agency": bill_data.get("original_agency", ""),
        }

        return result

    except Exception as e:
        logger.error(f"Error fetching bill info: {str(e)}")
        return {"error": f"Failed to fetch bill information: {str(e)}"}


def search_bills(year: Optional[str] = None, agency: Optional[str] = None, active_only: bool = False) -> Dict[str, Any]:
    """
    Search for bills in a specific year with optional filtering.

    This function retrieves all legislation for a year and allows filtering by agency
    (House or Senate) and active status.

    Args:
        year: Year in format "YYYY" (e.g., "2025") (optional, defaults to current)
        agency: Filter by originating agency ("House" or "Senate") (optional)
        active_only: If True, only return active bills

    Returns:
        Dict containing list of bills matching the criteria
    """
    try:
        if not year:
            year = get_current_year()

        logger.info(f"Searching bills in year {year}")

        # Get all bills for the year
        bills_data = wsl_client.get_legislation_by_year(year)

        if not bills_data or len(bills_data) == 0:
            return {"error": f"No bills found in year {year}"}

        # Filter bills based on criteria
        filtered_bills = []

        for bill in bills_data:
            # Filter by agency if provided
            if agency and bill.get("original_agency", "").lower() != agency.lower():
                continue

            # Filter by active status if requested
            if active_only and not bill.get("active", False):
                continue

            # Extract relevant bill information
            filtered_bills.append(
                {
                    "bill_id": bill.get("bill_id", ""),
                    "bill_number": bill.get("bill_number", ""),
                    "agency": bill.get("original_agency", ""),
                    "active": bill.get("active", False),
                    "biennium": bill.get("biennium", ""),
                    "short_legislation_type": bill.get("short_legislation_type", {}),
                    "substitute_version": bill.get("substitute_version", "0"),
                    "engrossed_version": bill.get("engrossed_version", "0"),
                }
            )

        return {
            "year": year,
            "count": len(filtered_bills),
            "bills": filtered_bills,
        }

    except Exception as e:
        logger.error(f"Error searching bills: {str(e)}")
        return {"error": f"Failed to search bills: {str(e)}"}


def get_bill_status(bill_number: int, biennium: Optional[str] = None) -> Dict[str, Any]:
    """
    Get the current status and history of a specific bill.

    Args:
        bill_number: Bill number as an integer (e.g., 1234 for HB1234, 5678 for SB5678)
        biennium: Legislative biennium in format "YYYY-YY" (e.g., "2025-26") (optional, defaults to current)

    Returns:
        Dict containing current status and history
    """
    try:
        if not biennium:
            biennium = get_current_biennium()

        logger.info(f"Fetching status for {bill_number} in biennium {biennium}")

        # Get bill information
        bills_data = wsl_client.get_legislation(biennium, str(bill_number))

        if not bills_data or len(bills_data) == 0:
            return {"error": f"Bill {bill_number} not found in biennium {biennium}"}

        # Use the first bill in the list
        bill_data = bills_data[0]
        current_status = bill_data.get("current_status", {})

        # Extract status information
        result = {
            "bill_number": bill_number,
            "biennium": biennium,
            "current_status": current_status.get("status", ""),
            "status_date": current_status.get("action_date", ""),
            "history_line": current_status.get("history_line", ""),
            "amendments_exist": current_status.get("amendments_exist", False),
            "veto": current_status.get("veto", False),
            "partial_veto": current_status.get("partial_veto", False),
        }

        return result

    except Exception as e:
        logger.error(f"Error fetching bill status: {str(e)}")
        return {"error": f"Failed to fetch bill status: {str(e)}"}


def get_bill_documents(
    bill_number: int, biennium: Optional[str] = None, document_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retrieve bill documents including bill text and amendments.

    Args:
        bill_number: Bill number as an integer (e.g., 1234 for HB1234, 5678 for SB5678)
        biennium: Legislative biennium in format "YYYY-YY" (e.g., "2025-26") (optional, defaults to current)
        document_type: Filter by type - "bill", "amendment", "report" (optional)

    Returns:
        Dict containing document metadata with links to HTML and PDF versions
    """
    try:
        if not biennium:
            biennium = get_current_biennium()

        logger.info(f"Fetching documents for {bill_number} in biennium {biennium}")

        # Get document information
        documents_data = wsl_client.get_documents(biennium, str(bill_number))

        if not documents_data or len(documents_data) == 0:
            return {"error": f"No documents found for bill {bill_number} in biennium {biennium}"}

        # Filter documents based on type if specified
        filtered_documents = []

        for doc in documents_data:
            # Filter by document type if provided
            if document_type and doc.get("type", "").lower() != document_type.lower():
                continue

            filtered_documents.append(
                {
                    "name": doc.get("name", ""),
                    "type": doc.get("type", ""),
                    "class": doc.get("class", ""),
                    "pdf_url": doc.get("pdf_url", ""),
                    "htm_url": doc.get("htm_url", ""),
                    "description": doc.get("description", ""),
                    "bill_id": doc.get("bill_id", ""),
                    "biennium": doc.get("biennium", ""),
                    "short_friendly_name": doc.get("short_friendly_name", ""),
                    "long_friendly_name": doc.get("long_friendly_name", ""),
                }
            )

        return {
            "bill_number": bill_number,
            "biennium": biennium,
            "count": len(filtered_documents),
            "documents": filtered_documents,
        }

    except Exception as e:
        logger.error(f"Error fetching bill documents: {str(e)}")
        return {"error": f"Failed to fetch bill documents: {str(e)}"}


def get_bill_amendments(bill_number: int, year: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve amendments for a specific bill.

    Args:
        bill_number: Bill number as an integer (e.g., 1234 for HB1234, 5678 for SB5678)
        year: Year in format "YYYY" (e.g., "2025") (optional, defaults to current year)

    Returns:
        Dict containing amendment metadata with links to HTML and PDF versions
    """
    try:
        if not year:
            biennium = get_current_biennium()
            year = biennium.split("-")[0]

        logger.info(f"Fetching amendments for {bill_number} in year {year}")

        # Get amendment information
        amendments_data = wsl_client.get_amendments(year)

        if not amendments_data:
            return {"error": f"Failed to fetch amendments for year {year}"}

        # Filter amendments for the specific bill
        bill_amendments = [
            amendment for amendment in amendments_data if amendment.get("bill_number") == bill_number
        ]

        if not bill_amendments:
            return {"error": f"No amendments found for bill {bill_number} in year {year}"}

        # Extract relevant amendment information
        formatted_amendments = []
        for amendment in bill_amendments:
            formatted_amendments.append(
                {
                    "name": amendment.get("name", ""),
                    "bill_id": amendment.get("bill_id", ""),
                    "type": amendment.get("type", ""),
                    "sponsor_name": amendment.get("sponsor_name", ""),
                    "description": amendment.get("description", ""),
                    "floor_action": amendment.get("floor_action", ""),
                    "floor_action_date": amendment.get("floor_action_date", ""),
                    "htm_url": amendment.get("htm_url", ""),
                    "pdf_url": amendment.get("pdf_url", ""),
                    "agency": amendment.get("agency", ""),
                }
            )

        return {
            "bill_number": bill_number,
            "year": year,
            "count": len(formatted_amendments),
            "amendments": formatted_amendments,
        }

    except Exception as e:
        logger.error(f"Error fetching bill amendments: {str(e)}")
        return {"error": f"Failed to fetch bill amendments: {str(e)}"}