"""
Enhanced tests for legislator_tools.py with improved fixture usage and parametrization
"""

from unittest.mock import patch

import pytest

from tests.test_helpers import assert_api_error_handling, assert_not_found_handling
from wa_leg_mcp.tools.legislator_tools import find_legislator


class TestFindLegislator:
    """Tests for the find_legislator function."""

    @pytest.mark.parametrize(
        ("scenario", "mock_return", "filter_args", "expected_count", "expected_error"),
        [
            (
                "success_no_filter",
                [
                    {"name": "Representative Smith", "agency": "House", "district": "1"},
                    {"name": "Senator Jones", "agency": "Senate", "district": "2"},
                ],
                {},
                2,
                None,
            ),
            (
                "success_with_chamber_filter",
                [
                    {"name": "Representative Smith", "agency": "House", "district": "1"},
                    {"name": "Senator Jones", "agency": "Senate", "district": "2"},
                ],
                {"chamber": "House"},
                1,
                None,
            ),
            (
                "success_with_district_filter",
                [
                    {"name": "Representative Smith", "agency": "House", "district": "1"},
                    {"name": "Senator Jones", "agency": "Senate", "district": "2"},
                ],
                {"district": "1"},
                1,
                None,
            ),
            (
                "success_with_multiple_filters",
                [
                    {"name": "Representative Smith", "agency": "House", "district": "1"},
                    {"name": "Senator Jones", "agency": "Senate", "district": "2"},
                ],
                {"chamber": "House", "district": "1"},
                1,
                None,
            ),
            (
                "no_results_with_filters",
                [
                    {"name": "Representative Smith", "agency": "House", "district": "1"},
                    {"name": "Senator Jones", "agency": "Senate", "district": "2"},
                ],
                {"chamber": "Senate", "district": "1"},
                0,
                None,
            ),
            (
                "not_found",
                None,
                {},
                None,
                "No legislators found",
            ),
            (
                "api_error",
                Exception("API Error"),
                {},
                None,
                "Failed to find legislators",
            ),
        ],
    )
    def test_find_legislator_scenarios(
        self, scenario, mock_return, filter_args, expected_count, expected_error, common_test_data
    ):
        """Test different scenarios for find_legislator using parametrization."""
        # Setup mocks
        with (
            patch("wa_leg_mcp.tools.legislator_tools.get_current_biennium") as mock_get_biennium,
            patch("wa_leg_mcp.tools.legislator_tools.wsl_client") as mock_client,
        ):

            mock_get_biennium.return_value = common_test_data["biennium"]

            # Configure the mock client based on the scenario
            if isinstance(mock_return, Exception):
                mock_client.get_sponsors.side_effect = mock_return
            else:
                mock_client.get_sponsors.return_value = mock_return

            # Call function with filter arguments
            result = find_legislator(**filter_args)

            # Assertions
            if expected_error:
                assert "error" in result
                assert expected_error in result["error"]
            else:
                if expected_count == 0:
                    assert result["count"] == 0
                    assert len(result["legislators"]) == 0
                else:
                    assert result["count"] == expected_count
                    assert len(result["legislators"]) == expected_count
                assert result["biennium"] == common_test_data["biennium"]

    def test_find_legislator_api_error_helper(self):
        """Test API error handling using the helper function."""
        with patch("wa_leg_mcp.tools.legislator_tools.wsl_client") as mock_client:
            assert_api_error_handling(
                find_legislator,
                mock_client.get_sponsors,
                "Failed to find legislators",
            )

    def test_find_legislator_not_found_helper(self):
        """Test not found handling using the helper function."""
        with patch("wa_leg_mcp.tools.legislator_tools.wsl_client") as mock_client:
            assert_not_found_handling(
                find_legislator,
                mock_client.get_sponsors,
                "No legislators found",
            )

    def test_find_legislator_with_explicit_biennium(self):
        """Test find_legislator with explicitly provided biennium."""
        # Setup mocks
        with (
            patch("wa_leg_mcp.tools.legislator_tools.get_current_biennium") as mock_get_biennium,
            patch("wa_leg_mcp.tools.legislator_tools.wsl_client") as mock_client,
        ):

            mock_client.get_sponsors.return_value = [
                {"name": "Representative Smith", "agency": "House", "district": "1"},
            ]
            explicit_biennium = "2021-22"

            # Call function with explicit biennium
            result = find_legislator(biennium=explicit_biennium)

            # Assertions
            mock_client.get_sponsors.assert_called_once_with(explicit_biennium)
            assert result["biennium"] == explicit_biennium
            # mock_get_biennium should not be called when biennium is provided
            mock_get_biennium.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__])
