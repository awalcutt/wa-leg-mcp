"""
Tests for legislator_tools.py
"""

import unittest
from unittest.mock import patch

# Import the function to test
from wa_leg_mcp.tools.legislator_tools import find_legislator


class TestLegislatorTools(unittest.TestCase):
    """Test cases for legislator tools."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_biennium = "2023-24"

        # Sample legislators data for testing
        self.mock_sponsors_data = [
            {
                "id": "31526",
                "name": "Representative Smith",
                "long_name": "Representative Smith",
                "party": "D",
                "district": "1",
                "agency": "House",
                "email": "smith@example.com",
                "phone": "555-1234",
                "first_name": "Representative",
                "last_name": "Smith",
                "acronym": "SMIT",
            },
            {
                "id": "31527",
                "name": "Senator Jones",
                "long_name": "Senator Jones",
                "party": "R",
                "district": "2",
                "agency": "Senate",
                "email": "jones@example.com",
                "phone": "555-5678",
                "first_name": "Senator",
                "last_name": "Jones",
                "acronym": "JONE",
            },
            {
                "id": "31528",
                "name": "Representative Johnson",
                "long_name": "Representative Johnson",
                "party": "D",
                "district": "1",
                "agency": "House",
                "email": "johnson@example.com",
                "phone": "555-9012",
                "first_name": "Representative",
                "last_name": "Johnson",
                "acronym": "JOHN",
            },
        ]

    @patch("wa_leg_mcp.tools.legislator_tools.get_current_biennium")
    @patch("wa_leg_mcp.tools.legislator_tools.wsl_client")
    def test_find_legislator_success(self, mock_client, mock_get_biennium):
        """Test successful retrieval of legislators."""
        # Setup mocks
        mock_get_biennium.return_value = self.test_biennium
        mock_client.get_sponsors.return_value = self.mock_sponsors_data

        # Call function
        result = find_legislator()

        # Assertions
        mock_client.get_sponsors.assert_called_once_with(self.test_biennium)
        assert result["biennium"] == self.test_biennium
        assert result["count"] == 3
        assert len(result["legislators"]) == 3
        assert result["legislators"][0]["name"] == "Representative Smith"
        assert result["legislators"][1]["name"] == "Senator Jones"
        assert result["legislators"][0]["first_name"] == "Representative"
        assert result["legislators"][0]["last_name"] == "Smith"
        assert result["legislators"][0]["acronym"] == "SMIT"

    @patch("wa_leg_mcp.tools.legislator_tools.get_current_biennium")
    @patch("wa_leg_mcp.tools.legislator_tools.wsl_client")
    def test_find_legislator_with_chamber_filter(self, mock_client, mock_get_biennium):
        """Test legislator search with chamber filter."""
        # Setup mocks
        mock_get_biennium.return_value = self.test_biennium
        mock_client.get_sponsors.return_value = self.mock_sponsors_data

        # Call function with chamber filter
        result = find_legislator(chamber="House")

        # Assertions
        assert result["count"] == 2
        assert len(result["legislators"]) == 2
        assert result["legislators"][0]["name"] == "Representative Smith"
        assert result["legislators"][1]["name"] == "Representative Johnson"

        # Test with different chamber
        result = find_legislator(chamber="Senate")

        # Assertions
        assert result["count"] == 1
        assert len(result["legislators"]) == 1
        assert result["legislators"][0]["name"] == "Senator Jones"

    @patch("wa_leg_mcp.tools.legislator_tools.get_current_biennium")
    @patch("wa_leg_mcp.tools.legislator_tools.wsl_client")
    def test_find_legislator_with_district_filter(self, mock_client, mock_get_biennium):
        """Test legislator search with district filter."""
        # Setup mocks
        mock_get_biennium.return_value = self.test_biennium
        mock_client.get_sponsors.return_value = self.mock_sponsors_data

        # Call function with district filter
        result = find_legislator(district="1")

        # Assertions
        assert result["count"] == 2
        assert len(result["legislators"]) == 2
        assert result["legislators"][0]["name"] == "Representative Smith"
        assert result["legislators"][1]["name"] == "Representative Johnson"

        # Test with different district
        result = find_legislator(district="2")

        # Assertions
        assert result["count"] == 1
        assert len(result["legislators"]) == 1
        assert result["legislators"][0]["name"] == "Senator Jones"

    @patch("wa_leg_mcp.tools.legislator_tools.get_current_biennium")
    @patch("wa_leg_mcp.tools.legislator_tools.wsl_client")
    def test_find_legislator_with_multiple_filters(self, mock_client, mock_get_biennium):
        """Test legislator search with multiple filters."""
        # Setup mocks
        mock_get_biennium.return_value = self.test_biennium
        mock_client.get_sponsors.return_value = self.mock_sponsors_data

        # Call function with multiple filters
        result = find_legislator(chamber="House", district="1")

        # Assertions
        assert result["count"] == 2
        assert len(result["legislators"]) == 2
        assert result["legislators"][0]["name"] == "Representative Smith"
        assert result["legislators"][1]["name"] == "Representative Johnson"

        # Test with different combination
        result = find_legislator(chamber="Senate", district="1")

        # Assertions
        assert result["count"] == 0
        assert len(result["legislators"]) == 0

    @patch("wa_leg_mcp.tools.legislator_tools.get_current_biennium")
    @patch("wa_leg_mcp.tools.legislator_tools.wsl_client")
    def test_find_legislator_not_found(self, mock_client, mock_get_biennium):
        """Test legislator search with no results."""
        # Setup mocks
        mock_get_biennium.return_value = self.test_biennium
        mock_client.get_sponsors.return_value = None

        # Call function
        result = find_legislator()

        # Assertions
        assert "error" in result
        assert "No legislators found" in result["error"]

    @patch("wa_leg_mcp.tools.legislator_tools.get_current_biennium")
    @patch("wa_leg_mcp.tools.legislator_tools.wsl_client")
    def test_find_legislator_exception(self, mock_client, mock_get_biennium):
        """Test exception handling."""
        # Setup mocks
        mock_get_biennium.return_value = self.test_biennium
        mock_client.get_sponsors.side_effect = Exception("API Error")

        # Call function
        result = find_legislator()

        # Assertions
        assert "error" in result
        assert "Failed to find legislators" in result["error"]

    @patch("wa_leg_mcp.tools.legislator_tools.get_current_biennium")
    @patch("wa_leg_mcp.tools.legislator_tools.wsl_client")
    def test_find_legislator_with_explicit_biennium(self, mock_client, mock_get_biennium):
        """Test find_legislator with explicitly provided biennium."""
        # Setup mocks
        mock_client.get_sponsors.return_value = self.mock_sponsors_data
        explicit_biennium = "2021-22"

        # Call function with explicit biennium
        result = find_legislator(biennium=explicit_biennium)

        # Assertions
        mock_client.get_sponsors.assert_called_once_with(explicit_biennium)
        assert result["biennium"] == explicit_biennium
        # mock_get_biennium should not be called when biennium is provided
        mock_get_biennium.assert_not_called()


if __name__ == "__main__":
    unittest.main()
