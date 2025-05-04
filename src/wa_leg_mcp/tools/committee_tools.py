"""
Committee-related MCP tools for Washington State Legislature data.
"""

import logging
from typing import Any, Dict

from ..clients.wsl_client import WSLClient
from ..utils.formatters import get_current_biennium

logger = logging.getLogger(__name__)

wsl_client = WSLClient()


def get_committee_meetings(start_date: str, end_date: str, committee: str = None) -> Dict[str, Any]:
    """
    Retrieve committee meetings and agendas.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        committee: Filter by specific committee (optional)

    Returns:
        Dict containing list of committee meetings
    """
    try:
        logger.info(f"Fetching committee meetings from {start_date} to {end_date}")

        # Get committee meetings
        meetings_data = wsl_client.get_committee_meetings(start_date, end_date)

        if not meetings_data or len(meetings_data) == 0:
            return {"error": f"No meetings found between {start_date} and {end_date}"}

        # Filter by committee if specified
        filtered_meetings = []

        for meeting in meetings_data:
            # Check if committee matches any of the committees in the meeting
            if committee and not any(
                c.get("name", "").lower() == committee.lower()
                for c in meeting.get("committees", [])
            ):
                continue

            committees_info = [
                {
                    "name": c.get("name", ""),
                    "long_name": c.get("long_name", ""),
                    "agency": c.get("agency", ""),
                    "acronym": c.get("acronym", ""),
                    "id": c.get("id", ""),
                }
                for c in meeting.get("committees", [])
            ]

            filtered_meetings.append(
                {
                    "agenda_id": meeting.get("agenda_id", ""),
                    "agency": meeting.get("agency", ""),
                    "committees": committees_info,
                    "date": meeting.get("date", ""),
                    "room": meeting.get("room", ""),
                    "building": meeting.get("building", ""),
                    "cancelled": meeting.get("cancelled", False),
                    "committee_type": meeting.get("committee_type", ""),
                    "notes": meeting.get("notes", ""),
                    "address": meeting.get("address", ""),
                    "city": meeting.get("city", ""),
                    "state": meeting.get("state", ""),
                }
            )

        return {
            "start_date": start_date,
            "end_date": end_date,
            "count": len(filtered_meetings),
            "meetings": filtered_meetings,
        }

    except Exception as e:
        logger.error(f"Error fetching committee meetings: {str(e)}")
        return {"error": f"Failed to fetch committee meetings: {str(e)}"}


def get_committees(biennium: str = None) -> Dict[str, Any]:
    """
    Retrieve list of committees for a specific biennium.

    Args:
        biennium: Legislative biennium in format "2025-26" (optional, defaults to current)

    Returns:
        Dict containing list of committees
    """
    try:
        if not biennium:
            biennium = get_current_biennium()

        logger.info(f"Fetching committees for biennium {biennium}")

        # Get committees
        committees_data = wsl_client.get_committees(biennium)

        if not committees_data or len(committees_data) == 0:
            return {"error": f"No committees found for biennium {biennium}"}

        formatted_committees = []
        for committee in committees_data:
            formatted_committees.append(
                {
                    "id": committee.get("id", ""),
                    "name": committee.get("name", ""),
                    "long_name": committee.get("long_name", ""),
                    "agency": committee.get("agency", ""),
                    "acronym": committee.get("acronym", ""),
                    "phone": committee.get("phone", ""),
                }
            )

        return {
            "biennium": biennium,
            "count": len(formatted_committees),
            "committees": formatted_committees,
        }

    except Exception as e:
        logger.error(f"Error fetching committees: {str(e)}")
        return {"error": f"Failed to fetch committees: {str(e)}"}
