"""
Enhanced tests for committee_tools.py with improved fixture usage and parametrization
"""

from unittest.mock import patch

import pytest

from tests.test_helpers import assert_api_error_handling, assert_not_found_handling
from wa_leg_mcp.tools.committee_tools import get_committee_meetings, get_committees


class TestCommitteeMeetings:
    """Tests for the get_committee_meetings function."""

    @pytest.mark.parametrize(
        ("scenario", "mock_return", "filter_args", "expected_count", "expected_error"),
        [
            (
                "success_no_filter",
                [
                    {"committees": [{"name": "Ways & Means"}]},
                    {"committees": [{"name": "Transportation"}]},
                ],
                {},
                2,
                None,
            ),
            (
                "success_with_committee_filter",
                [
                    {"committees": [{"name": "Ways & Means"}]},
                    {"committees": [{"name": "Transportation"}]},
                ],
                {"committee": "Ways & Means"},
                1,
                None,
            ),
            (
                "not_found",
                None,
                {},
                None,
                "No meetings found",
            ),
            (
                "api_error",
                Exception("API Error"),
                {},
                None,
                "Failed to fetch committee meetings",
            ),
        ],
    )
    def test_get_committee_meetings_scenarios(
        self, scenario, mock_return, filter_args, expected_count, expected_error, common_test_data
    ):
        """Test different scenarios for get_committee_meetings using parametrization."""
        # Setup mocks
        with patch("wa_leg_mcp.tools.committee_tools.wsl_client") as mock_client:
            # Configure the mock client based on the scenario
            if isinstance(mock_return, Exception):
                mock_client.get_committee_meetings.side_effect = mock_return
            else:
                mock_client.get_committee_meetings.return_value = mock_return

            # Call function with filter arguments
            result = get_committee_meetings(
                common_test_data["begin_date"], common_test_data["end_date"], **filter_args
            )

            # Assertions
            if expected_error:
                assert "error" in result
                assert expected_error in result["error"]
            else:
                assert result["count"] == expected_count
                assert len(result["meetings"]) == expected_count
                assert result["start_date"] == common_test_data["begin_date"]
                assert result["end_date"] == common_test_data["end_date"]

    def test_get_committee_meetings_api_error_helper(self, common_test_data):
        """Test API error handling using the helper function."""
        with patch("wa_leg_mcp.tools.committee_tools.wsl_client") as mock_client:
            assert_api_error_handling(
                get_committee_meetings,
                mock_client.get_committee_meetings,
                "Failed to fetch committee meetings",
                start_date=common_test_data["begin_date"],
                end_date=common_test_data["end_date"],
            )

    def test_get_committee_meetings_not_found_helper(self, common_test_data):
        """Test not found handling using the helper function."""
        with patch("wa_leg_mcp.tools.committee_tools.wsl_client") as mock_client:
            assert_not_found_handling(
                get_committee_meetings,
                mock_client.get_committee_meetings,
                "No meetings found",
                start_date=common_test_data["begin_date"],
                end_date=common_test_data["end_date"],
            )


class TestCommittees:
    """Tests for the get_committees function."""

    @pytest.mark.parametrize(
        ("scenario", "mock_return", "expected_count", "expected_error"),
        [
            (
                "success",
                [
                    {"name": "Agriculture & Natural Resources", "agency": "House"},
                    {"name": "Appropriations", "agency": "House"},
                ],
                2,
                None,
            ),
            (
                "not_found",
                None,
                None,
                "No committees found",
            ),
            (
                "api_error",
                Exception("API Error"),
                None,
                "Failed to fetch committees",
            ),
        ],
    )
    def test_get_committees_scenarios(
        self, scenario, mock_return, expected_count, expected_error, common_test_data
    ):
        """Test different scenarios for get_committees using parametrization."""
        # Setup mocks
        with (
            patch("wa_leg_mcp.tools.committee_tools.get_current_biennium") as mock_get_biennium,
            patch("wa_leg_mcp.tools.committee_tools.wsl_client") as mock_client,
        ):

            mock_get_biennium.return_value = common_test_data["biennium"]

            # Configure the mock client based on the scenario
            if isinstance(mock_return, Exception):
                mock_client.get_committees.side_effect = mock_return
            else:
                mock_client.get_committees.return_value = mock_return

            # Call function
            result = get_committees()

            # Assertions
            if expected_error:
                assert "error" in result
                assert expected_error in result["error"]
            else:
                assert result["count"] == expected_count
                assert len(result["committees"]) == expected_count
                assert result["biennium"] == common_test_data["biennium"]

    def test_get_committees_with_explicit_biennium(self, common_test_data):
        """Test get_committees with explicitly provided biennium."""
        # Setup mocks
        with (
            patch("wa_leg_mcp.tools.committee_tools.get_current_biennium") as mock_get_biennium,
            patch("wa_leg_mcp.tools.committee_tools.wsl_client") as mock_client,
        ):

            mock_client.get_committees.return_value = [
                {"name": "Agriculture & Natural Resources", "agency": "House"},
            ]
            explicit_biennium = "2021-22"

            # Call function with explicit biennium
            result = get_committees(biennium=explicit_biennium)

            # Assertions
            mock_client.get_committees.assert_called_once_with(explicit_biennium)
            assert result["biennium"] == explicit_biennium
            # mock_get_biennium should not be called when biennium is provided
            mock_get_biennium.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__])
