"""
Tests for the WSL Search Client
"""

import unittest
from unittest.mock import MagicMock, patch

from wa_leg_mcp.clients import WSLSearchClient


class TestWSLSearchClient(unittest.TestCase):
    """Test cases for the WSL Search Client"""

    def setUp(self):
        self.client = WSLSearchClient()

    @patch("requests.Session.post")
    def test_search_bills(self, mock_post):
        """Test searching for bills"""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "Success": True,
            "Response": (
                '<div class="searchResultRowClass">'
                '<a id="1566-S" href="javascript:;" class="searchResultDisplayNameClass">1566-S</a>'
                "(2025-26)<br/>"
                "AN ACT Relating to making improvements to transparency and accountability"
                "</div>"
            ),
        }
        mock_post.return_value = mock_response

        # Call the method
        results = self.client.search_bills("intelligence", bienniums=["2025-26"])

        # Verify the results
        assert results is not None
        assert len(results) == 1
        assert results[0]["bill_id"] == "1566-S"
        assert results[0]["bill_number"] == 1566
        assert results[0]["biennium"] == "2025-26"
        assert "transparency and accountability" in results[0]["description"]

    @patch("requests.Session.post")
    def test_search_bills_error(self, mock_post):
        """Test error handling when searching for bills"""
        # Mock response
        mock_post.side_effect = Exception("API Error")

        # Call the method
        results = self.client.search_bills("intelligence")

        # Verify the results
        assert results is None

    @patch("requests.Session.post")
    def test_search_bills_api_failure(self, mock_post):
        """Test handling API failure response"""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"Success": False, "Response": "Error message"}
        mock_post.return_value = mock_response

        # Call the method
        results = self.client.search_bills("intelligence")

        # Verify the results
        assert results is None


if __name__ == "__main__":
    unittest.main()
