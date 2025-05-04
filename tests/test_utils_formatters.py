"""
Tests for formatters.py in utils
"""

import unittest
from unittest.mock import patch

from wa_leg_mcp.utils.formatters import get_current_biennium, get_current_year


class TestFormatters(unittest.TestCase):
    """Test cases for formatter utilities."""

    @patch("wa_leg_mcp.utils.formatters.datetime")
    def test_get_current_biennium_odd_year(self, mock_datetime):
        """Test get_current_biennium in an odd-numbered year."""
        # Setup mock for an odd year (2023)
        mock_now = mock_datetime.now.return_value
        mock_now.year = 2023

        # Call function
        result = get_current_biennium()

        # Assertions
        assert result == "2023-24"

    @patch("wa_leg_mcp.utils.formatters.datetime")
    def test_get_current_biennium_even_year(self, mock_datetime):
        """Test get_current_biennium in an even-numbered year."""
        # Setup mock for an even year (2024)
        mock_now = mock_datetime.now.return_value
        mock_now.year = 2024

        # Call function
        result = get_current_biennium()

        # Assertions
        assert result == "2023-24"

    @patch("wa_leg_mcp.utils.formatters.datetime")
    def test_get_current_biennium_decade_transition(self, mock_datetime):
        """Test get_current_biennium during a decade transition."""
        # Setup mock for end of decade (2029)
        mock_now = mock_datetime.now.return_value
        mock_now.year = 2029

        # Call function
        result = get_current_biennium()

        # Assertions
        assert result == "2029-30"

        # Setup mock for start of decade (2030)
        mock_now.year = 2030

        # Call function
        result = get_current_biennium()

        # Assertions
        assert result == "2029-30"

    @patch("wa_leg_mcp.utils.formatters.datetime")
    def test_get_current_year(self, mock_datetime):
        """Test get_current_year function."""
        # Setup mock for year 2023
        mock_now = mock_datetime.now.return_value
        mock_now.year = 2023

        # Call function
        result = get_current_year()

        # Assertions
        assert result == "2023"

        # Setup mock for year 2030
        mock_now.year = 2030

        # Call function
        result = get_current_year()

        # Assertions
        assert result == "2030"


if __name__ == "__main__":
    unittest.main()
