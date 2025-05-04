"""
Tests for the WSLClient class in wa_leg_mcp.clients.wsl_client
"""

import os

# Import directly from the module to avoid dependency issues
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from wa_leg_mcp.clients.wsl_client import WSLClient


class TestWSLClient(unittest.TestCase):
    """Test cases for the WSLClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = WSLClient()
        self.test_biennium = "2023-24"
        self.test_bill_number = "1234"
        self.test_year = "2023"
        self.test_begin_date = "2023-01-01"
        self.test_end_date = "2023-12-31"

        # Mock responses with the expected structure
        self.mock_legislation_response = {
            "array_of_legislation": [
                {
                    "biennium": "2025-26",
                    "bill_id": "HB 1000",
                    "bill_number": "1000",
                    "short_description": "Test Bill",
                    "long_description": "Test Bill Description",
                }
            ]
        }

        self.mock_legislation_by_year_response = {
            "array_of_legislation_info": [
                {
                    "biennium": "2025-26",
                    "bill_id": "HB 1000",
                    "bill_number": 1000,
                    "active": True,
                }
            ]
        }

        self.mock_committees_response = {
            "array_of_committee": [
                {
                    "id": "31649",
                    "name": "Agriculture & Natural Resources",
                    "long_name": "House Committee on Agriculture & Natural Resources",
                    "agency": "House",
                    "acronym": "AGNR",
                    "phone": "(360) 786-7339",
                }
            ]
        }

        self.mock_committee_meetings_response = {
            "array_of_committee_meeting": [
                {
                    "agenda_id": 32300,
                    "agency": "Joint",
                    "committees": [
                        {
                            "id": "27992",
                            "name": "Joint Committee on Employment Relations",
                            "agency": "Joint",
                        }
                    ],
                    "room": "Virtual",
                    "date": "2025-01-09",
                }
            ]
        }

        self.mock_sponsors_response = {
            "array_of_member": [
                {
                    "id": "31526",
                    "name": "Peter Abbarno",
                    "long_name": "Representative Abbarno",
                    "agency": "House",
                    "party": "R",
                    "district": "20",
                }
            ]
        }

        self.mock_amendments_response = {
            "array_of_amendment": [
                {
                    "bill_number": 5195,
                    "name": "5195-S AMH THAR H2391.1",
                    "bill_id": "SSB 5195",
                    "sponsor_name": "Tharinger",
                }
            ]
        }

        self.mock_documents_response = {
            "array_of_legislative_document": [
                {
                    "name": "1000",
                    "short_friendly_name": "Original Bill",
                    "biennium": "2025-26",
                    "bill_id": "HB 1000",
                }
            ]
        }

    @patch("wa_leg_mcp.clients.wsl_client.get_legislation")
    def test_get_legislation_success(self, mock_get_legislation):
        """Test successful get_legislation call."""
        mock_get_legislation.return_value = self.mock_legislation_response

        result = self.client.get_legislation(self.test_biennium, self.test_bill_number)

        mock_get_legislation.assert_called_once_with(self.test_biennium, self.test_bill_number)
        assert result == self.mock_legislation_response.get("array_of_legislation")

    @patch("wa_leg_mcp.clients.wsl_client.get_legislation")
    def test_get_legislation_exception(self, mock_get_legislation):
        """Test get_legislation with exception."""
        mock_get_legislation.side_effect = Exception("API error")

        result = self.client.get_legislation(self.test_biennium, self.test_bill_number)

        mock_get_legislation.assert_called_once_with(self.test_biennium, self.test_bill_number)
        assert result is None

    @patch("wa_leg_mcp.clients.wsl_client.get_legislation_by_year")
    def test_get_legislation_by_year_success(self, mock_get_legislation_by_year):
        """Test successful get_legislation_by_year call."""
        mock_get_legislation_by_year.return_value = self.mock_legislation_by_year_response

        result = self.client.get_legislation_by_year(self.test_year)

        mock_get_legislation_by_year.assert_called_once_with(self.test_year)
        assert result == self.mock_legislation_by_year_response.get("array_of_legislation_info")

    @patch("wa_leg_mcp.clients.wsl_client.get_legislation_by_year")
    def test_get_legislation_by_year_exception(self, mock_get_legislation_by_year):
        """Test get_legislation_by_year with exception."""
        mock_get_legislation_by_year.side_effect = Exception("API error")

        result = self.client.get_legislation_by_year(self.test_year)

        mock_get_legislation_by_year.assert_called_once_with(self.test_year)
        assert result is None

    @patch("wa_leg_mcp.clients.wsl_client.get_committees")
    def test_get_committees_success(self, mock_get_committees):
        """Test successful get_committees call."""
        mock_get_committees.return_value = self.mock_committees_response

        result = self.client.get_committees(self.test_biennium)

        mock_get_committees.assert_called_once_with(self.test_biennium)
        assert result == self.mock_committees_response.get("array_of_committee")

    @patch("wa_leg_mcp.clients.wsl_client.get_committees")
    def test_get_committees_exception(self, mock_get_committees):
        """Test get_committees with exception."""
        mock_get_committees.side_effect = Exception("API error")

        result = self.client.get_committees(self.test_biennium)

        mock_get_committees.assert_called_once_with(self.test_biennium)
        assert result is None

    @patch("wa_leg_mcp.clients.wsl_client.get_committee_meetings")
    def test_get_committee_meetings_success(self, mock_get_committee_meetings):
        """Test successful get_committee_meetings call."""
        mock_get_committee_meetings.return_value = self.mock_committee_meetings_response

        result = self.client.get_committee_meetings(self.test_begin_date, self.test_end_date)

        mock_get_committee_meetings.assert_called_once_with(
            self.test_begin_date, self.test_end_date
        )
        assert result == self.mock_committee_meetings_response.get("array_of_committee_meeting")

    @patch("wa_leg_mcp.clients.wsl_client.get_committee_meetings")
    def test_get_committee_meetings_exception(self, mock_get_committee_meetings):
        """Test get_committee_meetings with exception."""
        mock_get_committee_meetings.side_effect = Exception("API error")

        result = self.client.get_committee_meetings(self.test_begin_date, self.test_end_date)

        mock_get_committee_meetings.assert_called_once_with(
            self.test_begin_date, self.test_end_date
        )
        assert result is None

    @patch("wa_leg_mcp.clients.wsl_client.get_sponsors")
    def test_get_sponsors_success(self, mock_get_sponsors):
        """Test successful get_sponsors call."""
        mock_get_sponsors.return_value = self.mock_sponsors_response

        result = self.client.get_sponsors(self.test_biennium)

        mock_get_sponsors.assert_called_once_with(self.test_biennium)
        assert result == self.mock_sponsors_response.get("array_of_member")

    @patch("wa_leg_mcp.clients.wsl_client.get_sponsors")
    def test_get_sponsors_exception(self, mock_get_sponsors):
        """Test get_sponsors with exception."""
        mock_get_sponsors.side_effect = Exception("API error")

        result = self.client.get_sponsors(self.test_biennium)

        mock_get_sponsors.assert_called_once_with(self.test_biennium)
        assert result is None

    @patch("wa_leg_mcp.clients.wsl_client.get_amendments")
    def test_get_amendments_success(self, mock_get_amendments):
        """Test successful get_amendments call."""
        mock_get_amendments.return_value = self.mock_amendments_response

        result = self.client.get_amendments(self.test_year)

        mock_get_amendments.assert_called_once_with(self.test_year)
        assert result == self.mock_amendments_response.get("array_of_amendment")

    @patch("wa_leg_mcp.clients.wsl_client.get_amendments")
    def test_get_amendments_exception(self, mock_get_amendments):
        """Test get_amendments with exception."""
        mock_get_amendments.side_effect = Exception("API error")

        result = self.client.get_amendments(self.test_year)

        mock_get_amendments.assert_called_once_with(self.test_year)
        assert result is None

    @patch("wa_leg_mcp.clients.wsl_client.get_documents")
    def test_get_documents_success(self, mock_get_documents):
        """Test successful get_documents call."""
        mock_get_documents.return_value = self.mock_documents_response

        result = self.client.get_documents(self.test_biennium, self.test_bill_number)

        mock_get_documents.assert_called_once_with(self.test_biennium, self.test_bill_number)
        assert result == self.mock_documents_response.get("array_of_legislative_document")

    @patch("wa_leg_mcp.clients.wsl_client.get_documents")
    def test_get_documents_exception(self, mock_get_documents):
        """Test get_documents with exception."""
        mock_get_documents.side_effect = Exception("API error")

        result = self.client.get_documents(self.test_biennium, self.test_bill_number)

        mock_get_documents.assert_called_once_with(self.test_biennium, self.test_bill_number)
        assert result is None


if __name__ == "__main__":
    unittest.main()
