"""
Tests for the WSLClient class in wa_leg_mcp.clients.wsl_client organized by functionality
"""

from unittest.mock import patch

import pytest

from wa_leg_mcp.clients.wsl_client import WSLClient


@pytest.fixture
def client():
    """Create a WSLClient instance for testing."""
    return WSLClient()


@pytest.fixture
def test_params():
    """Test parameters for API calls."""
    return {
        "biennium": "2023-24",
        "bill_number": "1234",
        "year": "2023",
        "begin_date": "2023-01-01",
        "end_date": "2023-12-31",
    }


@pytest.fixture
def mock_responses():
    """Mock responses for API calls."""
    return {
        "legislation": {
            "array_of_legislation": [
                {
                    "biennium": "2025-26",
                    "bill_id": "HB 1000",
                    "bill_number": "1000",
                    "short_description": "Test Bill",
                    "long_description": "Test Bill Description",
                }
            ]
        },
        "legislation_by_year": {
            "array_of_legislation_info": [
                {
                    "biennium": "2025-26",
                    "bill_id": "HB 1000",
                    "bill_number": 1000,
                    "active": True,
                }
            ]
        },
        "committees": {
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
        },
        "committee_meetings": {
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
        },
        "sponsors": {
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
        },
        "amendments": {
            "array_of_amendment": [
                {
                    "bill_number": 5195,
                    "name": "5195-S AMH THAR H2391.1",
                    "bill_id": "SSB 5195",
                    "sponsor_name": "Tharinger",
                }
            ]
        },
        "documents": {
            "array_of_legislative_document": [
                {
                    "name": "1000",
                    "short_friendly_name": "Original Bill",
                    "biennium": "2025-26",
                    "bill_id": "HB 1000",
                }
            ]
        },
    }


class TestLegislationMethods:
    """Tests for legislation-related methods in WSLClient."""

    @patch("wa_leg_mcp.clients.wsl_client.get_legislation")
    def test_get_legislation_success(
        self, mock_get_legislation, client, test_params, mock_responses
    ):
        """Test successful get_legislation call."""
        mock_get_legislation.return_value = mock_responses["legislation"]

        result = client.get_legislation(test_params["biennium"], test_params["bill_number"])

        mock_get_legislation.assert_called_once_with(
            test_params["biennium"], test_params["bill_number"]
        )
        assert result == mock_responses["legislation"].get("array_of_legislation")

    @patch("wa_leg_mcp.clients.wsl_client.get_legislation")
    def test_get_legislation_exception(self, mock_get_legislation, client, test_params):
        """Test get_legislation with exception."""
        mock_get_legislation.side_effect = Exception("API error")

        result = client.get_legislation(test_params["biennium"], test_params["bill_number"])

        mock_get_legislation.assert_called_once_with(
            test_params["biennium"], test_params["bill_number"]
        )
        assert result is None

    @patch("wa_leg_mcp.clients.wsl_client.get_legislation_by_year")
    def test_get_legislation_by_year_success(
        self, mock_get_legislation_by_year, client, test_params, mock_responses
    ):
        """Test successful get_legislation_by_year call."""
        mock_get_legislation_by_year.return_value = mock_responses["legislation_by_year"]

        result = client.get_legislation_by_year(test_params["year"])

        mock_get_legislation_by_year.assert_called_once_with(test_params["year"])
        assert result == mock_responses["legislation_by_year"].get("array_of_legislation_info")

    @patch("wa_leg_mcp.clients.wsl_client.get_legislation_by_year")
    def test_get_legislation_by_year_exception(
        self, mock_get_legislation_by_year, client, test_params
    ):
        """Test get_legislation_by_year with exception."""
        mock_get_legislation_by_year.side_effect = Exception("API error")

        result = client.get_legislation_by_year(test_params["year"])

        mock_get_legislation_by_year.assert_called_once_with(test_params["year"])
        assert result is None


class TestCommitteeMethods:
    """Tests for committee-related methods in WSLClient."""

    @patch("wa_leg_mcp.clients.wsl_client.get_committees")
    def test_get_committees_success(self, mock_get_committees, client, test_params, mock_responses):
        """Test successful get_committees call."""
        mock_get_committees.return_value = mock_responses["committees"]

        result = client.get_committees(test_params["biennium"])

        mock_get_committees.assert_called_once_with(test_params["biennium"])
        assert result == mock_responses["committees"].get("array_of_committee")

    @patch("wa_leg_mcp.clients.wsl_client.get_committees")
    def test_get_committees_exception(self, mock_get_committees, client, test_params):
        """Test get_committees with exception."""
        mock_get_committees.side_effect = Exception("API error")

        result = client.get_committees(test_params["biennium"])

        mock_get_committees.assert_called_once_with(test_params["biennium"])
        assert result is None

    @patch("wa_leg_mcp.clients.wsl_client.get_committee_meetings")
    def test_get_committee_meetings_success(
        self, mock_get_committee_meetings, client, test_params, mock_responses
    ):
        """Test successful get_committee_meetings call."""
        mock_get_committee_meetings.return_value = mock_responses["committee_meetings"]

        result = client.get_committee_meetings(test_params["begin_date"], test_params["end_date"])

        mock_get_committee_meetings.assert_called_once_with(
            test_params["begin_date"], test_params["end_date"]
        )
        assert result == mock_responses["committee_meetings"].get("array_of_committee_meeting")

    @patch("wa_leg_mcp.clients.wsl_client.get_committee_meetings")
    def test_get_committee_meetings_exception(
        self, mock_get_committee_meetings, client, test_params
    ):
        """Test get_committee_meetings with exception."""
        mock_get_committee_meetings.side_effect = Exception("API error")

        result = client.get_committee_meetings(test_params["begin_date"], test_params["end_date"])

        mock_get_committee_meetings.assert_called_once_with(
            test_params["begin_date"], test_params["end_date"]
        )
        assert result is None


class TestLegislatorMethods:
    """Tests for legislator-related methods in WSLClient."""

    @patch("wa_leg_mcp.clients.wsl_client.get_sponsors")
    def test_get_sponsors_success(self, mock_get_sponsors, client, test_params, mock_responses):
        """Test successful get_sponsors call."""
        mock_get_sponsors.return_value = mock_responses["sponsors"]

        result = client.get_sponsors(test_params["biennium"])

        mock_get_sponsors.assert_called_once_with(test_params["biennium"])
        assert result == mock_responses["sponsors"].get("array_of_member")

    @patch("wa_leg_mcp.clients.wsl_client.get_sponsors")
    def test_get_sponsors_exception(self, mock_get_sponsors, client, test_params):
        """Test get_sponsors with exception."""
        mock_get_sponsors.side_effect = Exception("API error")

        result = client.get_sponsors(test_params["biennium"])

        mock_get_sponsors.assert_called_once_with(test_params["biennium"])
        assert result is None


class TestDocumentMethods:
    """Tests for document-related methods in WSLClient."""

    @patch("wa_leg_mcp.clients.wsl_client.get_amendments")
    def test_get_amendments_success(self, mock_get_amendments, client, test_params, mock_responses):
        """Test successful get_amendments call."""
        mock_get_amendments.return_value = mock_responses["amendments"]

        result = client.get_amendments(test_params["year"])

        mock_get_amendments.assert_called_once_with(test_params["year"])
        assert result == mock_responses["amendments"].get("array_of_amendment")

    @patch("wa_leg_mcp.clients.wsl_client.get_amendments")
    def test_get_amendments_exception(self, mock_get_amendments, client, test_params):
        """Test get_amendments with exception."""
        mock_get_amendments.side_effect = Exception("API error")

        result = client.get_amendments(test_params["year"])

        mock_get_amendments.assert_called_once_with(test_params["year"])
        assert result is None

    @patch("wa_leg_mcp.clients.wsl_client.get_documents")
    def test_get_documents_success(self, mock_get_documents, client, test_params, mock_responses):
        """Test successful get_documents call."""
        mock_get_documents.return_value = mock_responses["documents"]

        result = client.get_documents(test_params["biennium"], test_params["bill_number"])

        mock_get_documents.assert_called_once_with(
            test_params["biennium"], test_params["bill_number"]
        )
        assert result == mock_responses["documents"].get("array_of_legislative_document")

    @patch("wa_leg_mcp.clients.wsl_client.get_documents")
    def test_get_documents_exception(self, mock_get_documents, client, test_params):
        """Test get_documents with exception."""
        mock_get_documents.side_effect = Exception("API error")

        result = client.get_documents(test_params["biennium"], test_params["bill_number"])

        mock_get_documents.assert_called_once_with(
            test_params["biennium"], test_params["bill_number"]
        )
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__])
