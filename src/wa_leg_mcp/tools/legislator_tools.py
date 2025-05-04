"""
Legislator-related MCP tools for Washington State Legislature data.
"""

import logging
from typing import Any, Dict

from ..clients.wsl_client import WSLClient
from ..utils.formatters import get_current_biennium

logger = logging.getLogger(__name__)

wsl_client = WSLClient()


def find_legislator(
    biennium: str = None, chamber: str = None, district: str = None
) -> Dict[str, Any]:
    """
    Find legislators (sponsors) for a specific biennium, optionally filtered by
    chamber and/or district.

    Args:
        biennium: Legislative biennium in format "2025-26" (optional, defaults to current)
        chamber: Filter by chamber ("house" or "senate") (optional)
        district: Filter by legislative district number (optional)

    Returns:
        Dict containing list of legislators matching the criteria
    """
    try:
        if not biennium:
            biennium = get_current_biennium()

        logger.info(f"Finding legislators for biennium {biennium}")

        # Get sponsors data
        sponsors_data = wsl_client.get_sponsors(biennium)

        if not sponsors_data or len(sponsors_data) == 0:
            return {"error": f"No legislators found for biennium {biennium}"}

        # Filter by chamber and/or district if specified
        filtered_legislators = []

        for sponsor in sponsors_data:
            # Filter by chamber if provided
            if chamber and sponsor.get("agency", "").lower() != chamber.lower():
                continue

            # Filter by district if provided
            if district and str(sponsor.get("district", "")) != str(district):
                continue

            filtered_legislators.append(
                {
                    "id": sponsor.get("id", ""),
                    "name": sponsor.get("name", ""),
                    "long_name": sponsor.get("long_name", ""),
                    "party": sponsor.get("party", ""),
                    "district": sponsor.get("district", ""),
                    "chamber": sponsor.get("agency", ""),
                    "email": sponsor.get("email", ""),
                    "phone": sponsor.get("phone", ""),
                    "first_name": sponsor.get("first_name", ""),
                    "last_name": sponsor.get("last_name", ""),
                    "acronym": sponsor.get("acronym", ""),
                }
            )

        return {
            "biennium": biennium,
            "count": len(filtered_legislators),
            "legislators": filtered_legislators,
        }

    except Exception as e:
        logger.error(f"Error finding legislators: {str(e)}")
        return {"error": f"Failed to find legislators: {str(e)}"}
