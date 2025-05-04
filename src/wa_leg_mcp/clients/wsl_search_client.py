"""
Washington State Legislature Search API Client

A client for interacting with the search.leg.wa.gov Search API to find bills
and other legislative documents.
"""

import html
import json
import logging
import re
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Constants
SEARCH_API_URL = "https://search.leg.wa.gov/SearchTermHandler.ashx"


class WSLSearchClient:
    """
    Client for interacting with the Washington State Legislature Search API.

    This client provides methods to search for bills and other legislative documents
    using the search.leg.wa.gov Search API.
    """

    def __init__(self, session: Optional[requests.Session] = None):
        """
        Initialize the WSL Search Client.

        Args:
            session: Optional requests session to use for API calls
        """
        self.session = session or requests.Session()

    def search_bills(
        self,
        query: str,
        bienniums: Optional[List[str]] = None,
        max_docs: int = 1000,
        proximity: int = 5,
        sort_by: str = "Rank",
        agency: str = "Both",
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Search for bills using the WSL Search API.

        Args:
            query: The search query text
            bienniums: List of bienniums to search (format: "YYYY-YY"). Defaults to current biennium.
            max_docs: Maximum number of documents to return (max 1000)
            proximity: Search proximity value
            sort_by: Sort method ("Rank" or "Name")
            agency: Agency filter ("House", "Senate", or "Both")

        Returns:
            List of bill search results or None if the request failed
        """
        # Default to current biennium if none provided
        if not bienniums:
            bienniums = [
                "2025-26"
            ]  # This should be dynamically determined in a production environment

        # Validate parameters
        if max_docs > 1000:
            max_docs = 1000
        if sort_by not in ["Rank", "Name"]:
            sort_by = "Rank"
        if agency not in ["House", "Senate", "Both"]:
            agency = "Both"

        # Build search parameters
        search_params = {
            "Query": query,
            "DocLike": "",
            "ResultsPerPage": str(max_docs),  # Set results_per_page to same as max_docs
            "MaxDocs": str(max_docs),
            "Proximity": str(proximity),
            "SortBy": sort_by,
            "Agency": agency,
            "Bienniums": bienniums,
            "Years": [],
            "LawDocs": [],
            "BienniumDocs": ["Bill"],
            "YearlyDocs": [],
            "WebDocs": [],
            "Zones": [],
            "Page": 0,  # Always use page 0
        }

        try:
            # Convert the search parameters to a JSON string
            json_data = json.dumps(search_params)

            # Make the API request with the JSON string as form data
            # The API expects application/x-www-form-urlencoded content type
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            response = self.session.post(
                f"{SEARCH_API_URL}?MethodName=Search", data=json_data, headers=headers
            )

            response.raise_for_status()

            # Parse the response
            response_data = response.json()

            if not response_data.get("Success"):
                logger.error(f"Search API returned error: {response_data}")
                return None

            # Parse the HTML response
            return self._parse_search_results(response_data.get("Response", ""))

        except Exception as e:
            logger.error(f"Failed to search bills with query '{query}': {e}")
            return None

    def _parse_search_results(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Parse the HTML search results into structured data.

        Args:
            html_content: HTML content from the search response

        Returns:
            List of parsed bill search results
        """
        results = []

        # Unescape HTML entities
        html_content = html.unescape(html_content)

        # Parse with BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")

        # Find all search result rows
        result_rows = soup.find_all("div", class_="searchResultRowClass")

        for row in result_rows:
            try:
                # Extract bill identifier
                bill_link = row.find("a", class_="searchResultDisplayNameClass")
                if not bill_link:
                    continue

                bill_id = bill_link.text.strip()

                # Extract bill number (numeric part)
                bill_number_match = re.search(r"(\d+)", bill_id)
                bill_number = int(bill_number_match.group(1)) if bill_number_match else None

                # Extract biennium
                biennium_text = row.get_text()
                biennium_match = re.search(r"\((\d{4}-\d{2})\)", biennium_text)
                biennium = biennium_match.group(1) if biennium_match else None

                # Extract description
                description_text = row.get_text()
                description_match = re.search(r"\)\s*(.*?)$", description_text)
                description = description_match.group(1).strip() if description_match else None

                results.append(
                    {
                        "bill_id": bill_id,
                        "bill_number": bill_number,
                        "biennium": biennium,
                        "description": description,
                    }
                )

            except Exception as e:
                logger.error(f"Error parsing search result row: {e}")
                continue

        return results
