"""
Tests for bill_tools.py
"""

import unittest
from unittest.mock import patch

# Import the functions to test
from wa_leg_mcp.tools.bill_tools import (
    get_bill_amendments,
    get_bill_documents,
    get_bill_info,
    get_bill_status,
    get_bills_by_year,
    search_bills,
)


class TestBillTools(unittest.TestCase):
    """Test cases for bill tools."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_bill_number = 1234  # Changed from "HB1234" to 1234
        self.test_biennium = "2023-24"
        self.test_year = "2023"
        self.test_query = "climate change"

        # Sample bill data for testing
        self.mock_bill_data = [
            {
                "biennium": "2025-26",
                "bill_id": "HB 1000",
                "bill_number": "1000",
                "substitute_version": "0",
                "engrossed_version": "0",
                "short_legislation_type": {
                    "short_legislation_type": "B",
                    "long_legislation_type": "Bill",
                },
                "original_agency": "House",
                "active": True,
                "short_description": "Test Bill",
                "long_description": "Test Bill Title",
                "sponsor": "Test Sponsor",
                "introduced_date": "2023-01-01",
                "current_status": {
                    "status": "In Committee",
                    "action_date": "2023-01-15",
                    "history_line": "First reading, referred to Committee.",
                    "amendments_exist": False,
                    "veto": False,
                    "partial_veto": False,
                },
                "legal_title": "AN ACT Relating to test bill",
            }
        ]

        # Sample bills by year data
        self.mock_bills_by_year = [
            {
                "biennium": "2025-26",
                "bill_id": "HB 1000",
                "bill_number": 1000,
                "original_agency": "House",
                "active": True,
            },
            {
                "biennium": "2025-26",
                "bill_id": "SB 5678",
                "bill_number": 5678,
                "original_agency": "Senate",
                "active": False,
                "introduced_date": "2023-02-01",
            },
        ]

        # Sample search results data
        self.mock_search_results = [
            {
                "bill_id": "HB 1234",
                "bill_number": 1234,
                "biennium": "2023-24",
                "description": "Relating to climate change mitigation",
            },
            {
                "bill_id": "SB 5678",
                "bill_number": 5678,
                "biennium": "2023-24",
                "description": "Addressing climate change impacts",
            },
        ]

        # Sample documents data
        self.mock_documents_data = [
            {
                "name": "Bill Text",
                "type": "bill",
                "class": "Original",
                "pdf_url": "http://example.com/bill.pdf",
                "htm_url": "http://example.com/bill.html",
                "description": "Original Bill",
                "bill_id": "HB 1234",
                "biennium": "2023-24",
                "short_friendly_name": "Original Bill",
                "long_friendly_name": "House Bill 1234",
            },
            {
                "name": "Amendment",
                "type": "amendment",
                "class": "House",
                "pdf_url": "http://example.com/amendment.pdf",
                "htm_url": "http://example.com/amendment.html",
                "description": "House Amendment",
                "bill_id": "HB 1234",
                "biennium": "2023-24",
                "short_friendly_name": "Amendment",
                "long_friendly_name": "House Amendment to HB 1234",
            },
        ]

        # Sample amendments data
        self.mock_amendments_data = [
            {
                "bill_number": 1234,
                "name": "1234 AMH COMM H1234.1",
                "bill_id": "HB 1234",
                "sponsor_name": "Committee",
                "description": "Committee Amendment",
                "floor_action": "ADOPTED",
                "floor_action_date": "2023-02-15",
                "htm_url": "http://example.com/amendment.html",
                "pdf_url": "http://example.com/amendment.pdf",
                "agency": "House",
                "type": "Committee",
            },
            {
                "bill_number": 5678,
                "name": "5678 AMH FLOOR H5678.1",
                "bill_id": "HB 5678",
                "sponsor_name": "Representative Smith",
                "description": "Floor Amendment",
                "floor_action": "WITHDRAWN",
                "floor_action_date": "2023-03-01",
                "htm_url": "http://example.com/amendment2.html",
                "pdf_url": "http://example.com/amendment2.pdf",
                "agency": "House",
                "type": "Floor",
            },
        ]

    @patch("wa_leg_mcp.tools.bill_tools.get_current_biennium")
    @patch("wa_leg_mcp.tools.bill_tools.wsl_client")
    def test_get_bill_info_success(self, mock_client, mock_get_biennium):
        """Test successful retrieval of bill information."""
        # Setup mocks
        mock_get_biennium.return_value = self.test_biennium
        mock_client.get_legislation.return_value = self.mock_bill_data

        # Call function
        result = get_bill_info(self.test_bill_number)

        # Assertions
        mock_client.get_legislation.assert_called_once_with(
            self.test_biennium, str(self.test_bill_number)
        )
        assert result["bill_number"] == self.test_bill_number
        assert result["title"] == "Test Bill Title"
        assert result["sponsor"] == "Test Sponsor"
        assert result["status"] == "In Committee"
        assert result["introduced_date"] == "2023-01-01"
        assert result["active"]
        assert result["agency"] == "House"

    @patch("wa_leg_mcp.tools.bill_tools.get_current_biennium")
    @patch("wa_leg_mcp.tools.bill_tools.wsl_client")
    def test_get_bill_info_not_found(self, mock_client, mock_get_biennium):
        """Test bill not found scenario."""
        # Setup mocks
        mock_get_biennium.return_value = self.test_biennium
        mock_client.get_legislation.return_value = None

        # Call function
        result = get_bill_info(self.test_bill_number)

        # Assertions
        assert "error" in result
        assert "not found" in result["error"]

    @patch("wa_leg_mcp.tools.bill_tools.get_current_biennium")
    @patch("wa_leg_mcp.tools.bill_tools.wsl_client")
    def test_get_bill_info_exception(self, mock_client, mock_get_biennium):
        """Test exception handling."""
        # Setup mocks
        mock_get_biennium.return_value = self.test_biennium
        mock_client.get_legislation.side_effect = Exception("API Error")

        # Call function
        result = get_bill_info(self.test_bill_number)

        # Assertions
        assert "error" in result
        assert "Failed to fetch bill information" in result["error"]

    @patch("wa_leg_mcp.tools.bill_tools.get_current_year")
    @patch("wa_leg_mcp.tools.bill_tools.wsl_client")
    def test_get_bills_by_year_success(self, mock_client, mock_get_current_year):
        """Test successful bills by year retrieval."""
        # Setup mocks
        mock_get_current_year.return_value = self.test_year
        mock_client.get_legislation_by_year.return_value = self.mock_bills_by_year

        # Call function
        result = get_bills_by_year()

        # Assertions
        mock_client.get_legislation_by_year.assert_called_once_with(self.test_year)
        assert result["count"] == 2
        assert len(result["bills"]) == 2
        assert result["bills"][0]["bill_id"] == "HB 1000"
        assert result["bills"][1]["bill_id"] == "SB 5678"
        assert result["year"] == self.test_year

    @patch("wa_leg_mcp.tools.bill_tools.get_current_year")
    @patch("wa_leg_mcp.tools.bill_tools.wsl_client")
    def test_get_bills_by_year_with_filters(self, mock_client, mock_get_current_year):
        """Test bills by year retrieval with filters."""
        # Setup mocks
        mock_get_current_year.return_value = self.test_year
        mock_client.get_legislation_by_year.return_value = self.mock_bills_by_year

        # Call function with active_only filter
        result = get_bills_by_year(active_only=True)

        # Assertions
        assert result["count"] == 1
        assert result["bills"][0]["bill_id"] == "HB 1000"

        # Call function with agency filter
        result = get_bills_by_year(agency="Senate")

        # Assertions
        assert result["count"] == 1
        assert result["bills"][0]["bill_id"] == "SB 5678"

    @patch("wa_leg_mcp.tools.bill_tools.get_current_year")
    @patch("wa_leg_mcp.tools.bill_tools.wsl_client")
    def test_get_bills_by_year_not_found(self, mock_client, mock_get_current_year):
        """Test bills by year retrieval with no results."""
        # Setup mocks
        mock_get_current_year.return_value = self.test_year
        mock_client.get_legislation_by_year.return_value = None

        # Call function
        result = get_bills_by_year()

        # Assertions
        assert "error" in result
        assert "No bills found in year" in result["error"]

    @patch("wa_leg_mcp.tools.bill_tools.get_current_biennium")
    @patch("wa_leg_mcp.tools.bill_tools.wsl_client")
    def test_get_bill_status_success(self, mock_client, mock_get_biennium):
        """Test successful retrieval of bill status."""
        # Setup mocks
        mock_get_biennium.return_value = self.test_biennium
        mock_client.get_legislation.return_value = self.mock_bill_data

        # Call function
        result = get_bill_status(self.test_bill_number)

        # Assertions
        mock_client.get_legislation.assert_called_once_with(
            self.test_biennium, str(self.test_bill_number)
        )
        assert result["bill_number"] == self.test_bill_number
        assert result["current_status"] == "In Committee"
        assert result["status_date"] == "2023-01-15"
        assert result["history_line"] == "First reading, referred to Committee."
        assert not result["amendments_exist"]
        assert not result["veto"]

    @patch("wa_leg_mcp.tools.bill_tools.get_current_biennium")
    @patch("wa_leg_mcp.tools.bill_tools.wsl_client")
    def test_get_bill_documents_success(self, mock_client, mock_get_biennium):
        """Test successful retrieval of bill documents."""
        # Setup mocks
        mock_get_biennium.return_value = self.test_biennium
        mock_client.get_documents.return_value = self.mock_documents_data

        # Call function
        result = get_bill_documents(self.test_bill_number)

        # Assertions
        mock_client.get_documents.assert_called_once_with(
            self.test_biennium, str(self.test_bill_number)
        )
        assert result["bill_number"] == self.test_bill_number
        assert result["count"] == 2
        assert len(result["documents"]) == 2
        assert result["documents"][0]["type"] == "bill"
        assert result["documents"][1]["type"] == "amendment"
        assert result["documents"][0]["pdf_url"] == "http://example.com/bill.pdf"
        assert result["documents"][0]["htm_url"] == "http://example.com/bill.html"

    @patch("wa_leg_mcp.tools.bill_tools.get_current_biennium")
    @patch("wa_leg_mcp.tools.bill_tools.wsl_client")
    def test_get_bill_documents_with_filter(self, mock_client, mock_get_biennium):
        """Test retrieval of bill documents with type filter."""
        # Setup mocks
        mock_get_biennium.return_value = self.test_biennium
        mock_client.get_documents.return_value = self.mock_documents_data

        # Call function with document_type filter
        result = get_bill_documents(self.test_bill_number, document_type="amendment")

        # Assertions
        assert result["count"] == 1
        assert result["documents"][0]["type"] == "amendment"

    @patch("wa_leg_mcp.tools.bill_tools.get_current_biennium")
    @patch("wa_leg_mcp.tools.bill_tools.wsl_client")
    def test_get_bill_documents_not_found(self, mock_client, mock_get_biennium):
        """Test bill documents not found scenario."""
        # Setup mocks
        mock_get_biennium.return_value = self.test_biennium
        mock_client.get_documents.return_value = None

        # Call function
        result = get_bill_documents(self.test_bill_number)

        # Assertions
        assert "error" in result
        assert "No documents found" in result["error"]

    @patch("wa_leg_mcp.tools.bill_tools.get_current_biennium")
    @patch("wa_leg_mcp.tools.bill_tools.wsl_client")
    def test_get_bill_documents_exception(self, mock_client, mock_get_biennium):
        """Test exception handling in get_bill_documents."""
        # Setup mocks
        mock_get_biennium.return_value = self.test_biennium
        mock_client.get_documents.side_effect = Exception("API Error")

        # Call function
        result = get_bill_documents(self.test_bill_number)

        # Assertions
        assert "error" in result
        assert "Failed to fetch bill documents" in result["error"]

    @patch("wa_leg_mcp.tools.bill_tools.get_current_biennium")
    @patch("wa_leg_mcp.tools.bill_tools.wsl_client")
    def test_get_bill_status_not_found(self, mock_client, mock_get_biennium):
        """Test bill status not found scenario."""
        # Setup mocks
        mock_get_biennium.return_value = self.test_biennium
        mock_client.get_legislation.return_value = None

        # Call function
        result = get_bill_status(self.test_bill_number)

        # Assertions
        assert "error" in result
        assert "not found" in result["error"]

    @patch("wa_leg_mcp.tools.bill_tools.get_current_biennium")
    @patch("wa_leg_mcp.tools.bill_tools.wsl_client")
    def test_get_bill_status_exception(self, mock_client, mock_get_biennium):
        """Test exception handling in get_bill_status."""
        # Setup mocks
        mock_get_biennium.return_value = self.test_biennium
        mock_client.get_legislation.side_effect = Exception("API Error")

        # Call function
        result = get_bill_status(self.test_bill_number)

        # Assertions
        assert "error" in result
        assert "Failed to fetch bill status" in result["error"]

    @patch("wa_leg_mcp.tools.bill_tools.get_current_year")
    @patch("wa_leg_mcp.tools.bill_tools.wsl_client")
    def test_get_bills_by_year_exception(self, mock_client, mock_get_current_year):
        """Test exception handling in get_bills_by_year."""
        # Setup mocks
        mock_get_current_year.return_value = self.test_year
        mock_client.get_legislation_by_year.side_effect = Exception("API Error")

        # Call function
        result = get_bills_by_year()

        # Assertions
        assert "error" in result
        assert "Failed to retrieve bills" in result["error"]

    @patch("wa_leg_mcp.tools.bill_tools.get_current_biennium")
    @patch("wa_leg_mcp.tools.bill_tools.wsl_client")
    def test_get_bill_info_with_explicit_biennium(self, mock_client, mock_get_biennium):
        """Test get_bill_info with explicitly provided biennium."""
        # Setup mocks
        mock_client.get_legislation.return_value = self.mock_bill_data
        explicit_biennium = "2021-22"

        # Call function with explicit biennium
        result = get_bill_info(self.test_bill_number, biennium=explicit_biennium)

        # Assertions
        mock_client.get_legislation.assert_called_once_with(
            explicit_biennium, str(self.test_bill_number)
        )
        assert result["biennium"] == explicit_biennium
        # mock_get_biennium should not be called when biennium is provided
        mock_get_biennium.assert_not_called()

    @patch("wa_leg_mcp.tools.bill_tools.get_current_biennium")
    @patch("wa_leg_mcp.tools.bill_tools.wsl_client")
    def test_get_bill_amendments_success(self, mock_client, mock_get_biennium):
        """Test successful retrieval of bill amendments."""
        # Setup mocks
        mock_get_biennium.return_value = self.test_biennium
        mock_client.get_amendments.return_value = self.mock_amendments_data

        # Call function
        result = get_bill_amendments(self.test_bill_number)

        # Assertions
        mock_client.get_amendments.assert_called_once_with(self.test_biennium.split("-")[0])
        assert result["bill_number"] == self.test_bill_number
        assert result["count"] == 1
        assert len(result["amendments"]) == 1
        assert result["amendments"][0]["bill_id"] == "HB 1234"
        assert result["amendments"][0]["sponsor_name"] == "Committee"
        assert result["amendments"][0]["floor_action"] == "ADOPTED"

    @patch("wa_leg_mcp.tools.bill_tools.get_current_biennium")
    @patch("wa_leg_mcp.tools.bill_tools.wsl_client")
    def test_get_bill_amendments_not_found(self, mock_client, mock_get_biennium):
        """Test bill amendments not found scenario."""
        # Setup mocks
        mock_get_biennium.return_value = self.test_biennium
        mock_client.get_amendments.return_value = None

        # Call function
        result = get_bill_amendments(self.test_bill_number)

        # Assertions
        assert "error" in result
        assert "Failed to fetch amendments" in result["error"]

    @patch("wa_leg_mcp.tools.bill_tools.get_current_biennium")
    @patch("wa_leg_mcp.tools.bill_tools.wsl_search_client")
    def test_search_bills_success(self, mock_search_client, mock_get_biennium):
        """Test successful bill search with keywords."""
        # Setup mocks
        mock_get_biennium.return_value = self.test_biennium
        mock_search_client.search_bills.return_value = self.mock_search_results

        # Call function
        result = search_bills(query=self.test_query)

        # Assertions
        mock_search_client.search_bills.assert_called_once()
        assert result["query"] == self.test_query
        assert result["count"] == 2
        assert len(result["bills"]) == 2
        assert result["bills"][0]["bill_id"] == "HB 1234"
        assert result["bills"][1]["bill_id"] == "SB 5678"

    @patch("wa_leg_mcp.tools.bill_tools.get_current_biennium")
    @patch("wa_leg_mcp.tools.bill_tools.wsl_search_client")
    def test_search_bills_not_found(self, mock_search_client, mock_get_biennium):
        """Test bill search with no results."""
        # Setup mocks
        mock_get_biennium.return_value = self.test_biennium
        mock_search_client.search_bills.return_value = []

        # Call function
        result = search_bills(query=self.test_query)

        # Assertions
        assert "error" in result
        assert f"No bills found matching query: {self.test_query}" in result["error"]

    @patch("wa_leg_mcp.tools.bill_tools.get_current_biennium")
    @patch("wa_leg_mcp.tools.bill_tools.wsl_search_client")
    def test_search_bills_exception(self, mock_search_client, mock_get_biennium):
        """Test exception handling in search_bills."""
        # Setup mocks
        mock_get_biennium.return_value = self.test_biennium
        mock_search_client.search_bills.side_effect = Exception("API Error")

        # Call function
        result = search_bills(query=self.test_query)

        # Assertions
        assert "error" in result
        assert "Failed to search bills" in result["error"]

    @patch("wa_leg_mcp.tools.bill_tools.get_current_biennium")
    @patch("wa_leg_mcp.tools.bill_tools.wsl_client")
    def test_get_bill_amendments_no_matching_bill(self, mock_client, mock_get_biennium):
        """Test scenario where amendments exist but none match the requested bill number."""
        # Setup mocks
        mock_get_biennium.return_value = self.test_biennium
        # Create amendments data with only bill 5678, not our test bill 1234
        amendments_data = [
            amendment
            for amendment in self.mock_amendments_data
            if amendment.get("bill_number") != self.test_bill_number
        ]
        mock_client.get_amendments.return_value = amendments_data

        # Call function
        result = get_bill_amendments(self.test_bill_number)

        # Assertions
        assert "error" in result
        assert f"No amendments found for bill {self.test_bill_number}" in result["error"]

    @patch("wa_leg_mcp.tools.bill_tools.get_current_biennium")
    @patch("wa_leg_mcp.tools.bill_tools.wsl_client")
    def test_get_bill_amendments_exception(self, mock_client, mock_get_biennium):
        """Test exception handling in get_bill_amendments."""
        # Setup mocks
        mock_get_biennium.return_value = self.test_biennium
        mock_client.get_amendments.side_effect = Exception("API Error")

        # Call function
        result = get_bill_amendments(self.test_bill_number)

        # Assertions
        assert "error" in result
        assert "Failed to fetch bill amendments" in result["error"]


if __name__ == "__main__":
    unittest.main()
