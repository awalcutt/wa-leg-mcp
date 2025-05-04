"""
Tests for committee_tools.py
"""

import unittest
from unittest.mock import patch

# Import the functions to test
from wa_leg_mcp.tools.committee_tools import get_committee_meetings, get_committees


class TestCommitteeTools(unittest.TestCase):
    """Test cases for committee tools."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_start_date = "2023-01-01"
        self.test_end_date = "2023-01-31"
        self.test_committee = "Ways & Means"
        self.test_biennium = "2023-24"

        # Sample committee meeting data for testing
        self.mock_meetings_data = [
            {
                "agenda_id": 32300,
                "agency": "Joint",
                "committees": [
                    {
                        "id": "27992",
                        "name": "Ways & Means",
                        "long_name": "Senate Committee on Ways & Means",
                        "agency": "Senate",
                        "acronym": "WM",
                        "phone": None,
                    }
                ],
                "room": "Hearing Room 1",
                "building": "Senate Building",
                "address": ",",
                "city": None,
                "state": "",
                "date": "2023-01-15",
                "cancelled": False,
                "committee_type": "Full Committee",
                "notes": "Committee meeting notes",
            },
            {
                "agenda_id": 32301,
                "agency": "House",
                "committees": [
                    {
                        "id": "27993",
                        "name": "Transportation",
                        "long_name": "House Committee on Transportation",
                        "agency": "House",
                        "acronym": "TR",
                        "phone": None,
                    }
                ],
                "room": "Hearing Room 2",
                "building": "House Building",
                "address": ",",
                "city": None,
                "state": "",
                "date": "2023-01-20",
                "cancelled": False,
                "committee_type": "Full Committee",
                "notes": "Committee meeting notes",
            },
        ]

        # Sample committees data for testing
        self.mock_committees_data = [
            {
                "id": "31649",
                "name": "Agriculture & Natural Resources",
                "long_name": "House Committee on Agriculture & Natural Resources",
                "agency": "House",
                "acronym": "AGNR",
                "phone": "(360) 786-7339",
            },
            {
                "id": "31650",
                "name": "Appropriations",
                "long_name": "House Committee on Appropriations",
                "agency": "House",
                "acronym": "APP",
                "phone": "(360) 786-7340",
            },
        ]

    @patch("wa_leg_mcp.tools.committee_tools.wsl_client")
    def test_get_committee_meetings_success(self, mock_client):
        """Test successful retrieval of committee meetings."""
        # Setup mock
        mock_client.get_committee_meetings.return_value = self.mock_meetings_data

        # Call function
        result = get_committee_meetings(self.test_start_date, self.test_end_date)

        # Assertions
        mock_client.get_committee_meetings.assert_called_once_with(
            self.test_start_date, self.test_end_date
        )
        assert result["start_date"] == self.test_start_date
        assert result["end_date"] == self.test_end_date
        assert result["count"] == 2
        assert len(result["meetings"]) == 2
        assert result["meetings"][0]["committees"][0]["name"] == "Ways & Means"
        assert result["meetings"][1]["committees"][0]["name"] == "Transportation"
        assert result["meetings"][0]["room"] == "Hearing Room 1"
        assert result["meetings"][1]["building"] == "House Building"

    @patch("wa_leg_mcp.tools.committee_tools.wsl_client")
    def test_get_committee_meetings_with_filter(self, mock_client):
        """Test committee meetings with committee filter."""
        # Setup mock
        mock_client.get_committee_meetings.return_value = self.mock_meetings_data

        # Call function with committee filter
        result = get_committee_meetings(
            self.test_start_date, self.test_end_date, committee=self.test_committee
        )

        # Assertions
        assert result["count"] == 1
        assert len(result["meetings"]) == 1
        assert result["meetings"][0]["committees"][0]["name"] == "Ways & Means"

    @patch("wa_leg_mcp.tools.committee_tools.wsl_client")
    def test_get_committee_meetings_not_found(self, mock_client):
        """Test committee meetings with no results."""
        # Setup mock
        mock_client.get_committee_meetings.return_value = None

        # Call function
        result = get_committee_meetings(self.test_start_date, self.test_end_date)

        # Assertions
        assert "error" in result
        assert "No meetings found" in result["error"]

    @patch("wa_leg_mcp.tools.committee_tools.wsl_client")
    def test_get_committee_meetings_exception(self, mock_client):
        """Test exception handling."""
        # Setup mock
        mock_client.get_committee_meetings.side_effect = Exception("API Error")

        # Call function
        result = get_committee_meetings(self.test_start_date, self.test_end_date)

        # Assertions
        assert "error" in result
        assert "Failed to fetch committee meetings" in result["error"]

    @patch("wa_leg_mcp.tools.committee_tools.get_current_biennium")
    @patch("wa_leg_mcp.tools.committee_tools.wsl_client")
    def test_get_committees_success(self, mock_client, mock_get_biennium):
        """Test successful retrieval of committees."""
        # Setup mocks
        mock_get_biennium.return_value = self.test_biennium
        mock_client.get_committees.return_value = self.mock_committees_data

        # Call function
        result = get_committees()

        # Assertions
        mock_client.get_committees.assert_called_once_with(self.test_biennium)
        assert result["biennium"] == self.test_biennium
        assert result["count"] == 2
        assert len(result["committees"]) == 2
        assert result["committees"][0]["name"] == "Agriculture & Natural Resources"
        assert result["committees"][1]["name"] == "Appropriations"
        assert result["committees"][0]["agency"] == "House"
        assert result["committees"][1]["acronym"] == "APP"

    @patch("wa_leg_mcp.tools.committee_tools.get_current_biennium")
    @patch("wa_leg_mcp.tools.committee_tools.wsl_client")
    def test_get_committees_not_found(self, mock_client, mock_get_biennium):
        """Test committees not found scenario."""
        # Setup mocks
        mock_get_biennium.return_value = self.test_biennium
        mock_client.get_committees.return_value = None

        # Call function
        result = get_committees()

        # Assertions
        assert "error" in result
        assert "No committees found" in result["error"]

    @patch("wa_leg_mcp.tools.committee_tools.get_current_biennium")
    @patch("wa_leg_mcp.tools.committee_tools.wsl_client")
    def test_get_committees_exception(self, mock_client, mock_get_biennium):
        """Test exception handling in get_committees."""
        # Setup mocks
        mock_get_biennium.return_value = self.test_biennium
        mock_client.get_committees.side_effect = Exception("API Error")

        # Call function
        result = get_committees()

        # Assertions
        assert "error" in result
        assert "Failed to fetch committees" in result["error"]

    @patch("wa_leg_mcp.tools.committee_tools.get_current_biennium")
    @patch("wa_leg_mcp.tools.committee_tools.wsl_client")
    def test_get_committees_with_explicit_biennium(self, mock_client, mock_get_biennium):
        """Test get_committees with explicitly provided biennium."""
        # Setup mocks
        mock_client.get_committees.return_value = self.mock_committees_data
        explicit_biennium = "2021-22"

        # Call function with explicit biennium
        result = get_committees(biennium=explicit_biennium)

        # Assertions
        mock_client.get_committees.assert_called_once_with(explicit_biennium)
        assert result["biennium"] == explicit_biennium
        # mock_get_biennium should not be called when biennium is provided
        mock_get_biennium.assert_not_called()


if __name__ == "__main__":
    unittest.main()
