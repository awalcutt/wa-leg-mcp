"""
Enhanced tests for bill_tools.py with improved fixture usage and parametrization
"""

from unittest.mock import patch

import pytest

from wa_leg_mcp.tools.bill_tools import (
    get_bill_amendments,
    get_bill_content,
    get_bill_documents,
    get_bill_info,
    get_bill_status,
    get_bills_by_year,
    search_bills,
)


class TestBillInfo:
    """Tests for the get_bill_info function."""

    @pytest.mark.parametrize(
        ("scenario", "mock_return", "expected_result", "expected_error"),
        [
            (
                "success",
                [
                    {
                        "bill_number": "1234",
                        "long_description": "Test Bill Title",
                        "sponsor": "Test Sponsor",
                    }
                ],
                {"bill_number": "1234", "title": "Test Bill Title", "sponsor": "Test Sponsor"},
                None,
            ),
            (
                "not_found",
                None,
                None,
                "Bill 1234 not found",
            ),
            (
                "api_error",
                Exception("API Error"),
                None,
                "Failed to fetch bill information",
            ),
        ],
    )
    def test_get_bill_info_scenarios(
        self, scenario, mock_return, expected_result, expected_error, common_test_data
    ):
        """Test different scenarios for get_bill_info using parametrization."""
        # Setup mocks
        with (
            patch("wa_leg_mcp.tools.bill_tools.get_current_biennium") as mock_get_biennium,
            patch("wa_leg_mcp.tools.bill_tools.wsl_client") as mock_client,
        ):

            mock_get_biennium.return_value = common_test_data["biennium"]

            # Configure the mock client based on the scenario
            if isinstance(mock_return, Exception):
                mock_client.get_legislation.side_effect = mock_return
            else:
                mock_client.get_legislation.return_value = mock_return

            # Call function
            result = get_bill_info(common_test_data["bill_number"])

            # Assertions
            if expected_error:
                assert "error" in result
                assert expected_error in result["error"]
            else:
                for key, value in expected_result.items():
                    assert result[key] == value

    def test_get_bill_info_with_explicit_biennium(self, common_test_data):
        """Test get_bill_info with explicitly provided biennium."""
        # Setup mocks
        with (
            patch("wa_leg_mcp.tools.bill_tools.get_current_biennium") as mock_get_biennium,
            patch("wa_leg_mcp.tools.bill_tools.wsl_client") as mock_client,
        ):

            mock_client.get_legislation.return_value = [
                {
                    "bill_number": "1234",
                    "long_description": "Test Bill Title",
                    "sponsor": "Test Sponsor",
                }
            ]
            explicit_biennium = "2021-22"

            # Call function with explicit biennium
            result = get_bill_info(common_test_data["bill_number"], biennium=explicit_biennium)

            # Assertions
            mock_client.get_legislation.assert_called_once_with(
                explicit_biennium, common_test_data["bill_number"]
            )
            assert result["biennium"] == explicit_biennium
            # mock_get_biennium should not be called when biennium is provided
            mock_get_biennium.assert_not_called()


class TestBillStatus:
    """Tests for the get_bill_status function."""

    @pytest.mark.parametrize(
        ("scenario", "mock_return", "expected_keys", "expected_error"),
        [
            (
                "success",
                [{"current_status": {"status": "In Committee", "action_date": "2023-01-15"}}],
                ["bill_number", "current_status", "status_date", "history_line"],
                None,
            ),
            (
                "not_found",
                None,
                None,
                "Bill 1234 not found",
            ),
            (
                "api_error",
                Exception("API Error"),
                None,
                "Failed to fetch bill status",
            ),
        ],
    )
    def test_get_bill_status_scenarios(
        self, scenario, mock_return, expected_keys, expected_error, common_test_data
    ):
        """Test different scenarios for get_bill_status using parametrization."""
        # Setup mocks
        with (
            patch("wa_leg_mcp.tools.bill_tools.get_current_biennium") as mock_get_biennium,
            patch("wa_leg_mcp.tools.bill_tools.wsl_client") as mock_client,
        ):

            mock_get_biennium.return_value = common_test_data["biennium"]

            # Configure the mock client based on the scenario
            if isinstance(mock_return, Exception):
                mock_client.get_legislation.side_effect = mock_return
            else:
                mock_client.get_legislation.return_value = mock_return

            # Call function
            result = get_bill_status(common_test_data["bill_number"])

            # Assertions
            if expected_error:
                assert "error" in result
                assert expected_error in result["error"]
            else:
                for key in expected_keys:
                    assert key in result


class TestBillsByYear:
    """Tests for the get_bills_by_year function."""

    @pytest.mark.parametrize(
        ("scenario", "mock_return", "filter_args", "expected_count", "expected_error"),
        [
            (
                "success_no_filter",
                [{"bill_id": "HB 1000"}, {"bill_id": "SB 5678"}],
                {},
                2,
                None,
            ),
            (
                "success_with_agency_filter",
                [
                    {"bill_id": "HB 1000", "original_agency": "House"},
                    {"bill_id": "SB 5678", "original_agency": "Senate"},
                ],
                {"agency": "House"},
                1,
                None,
            ),
            (
                "success_with_active_filter",
                [{"bill_id": "HB 1000", "active": True}, {"bill_id": "SB 5678", "active": False}],
                {"active_only": True},
                1,
                None,
            ),
            (
                "not_found",
                None,
                {},
                None,
                "No bills found in year",
            ),
            (
                "api_error",
                Exception("API Error"),
                {},
                None,
                "Failed to retrieve bills",
            ),
        ],
    )
    def test_get_bills_by_year_scenarios(
        self, scenario, mock_return, filter_args, expected_count, expected_error, common_test_data
    ):
        """Test different scenarios for get_bills_by_year using parametrization."""
        # Setup mocks
        with (
            patch("wa_leg_mcp.tools.bill_tools.get_current_year") as mock_get_current_year,
            patch("wa_leg_mcp.tools.bill_tools.wsl_client") as mock_client,
        ):

            mock_get_current_year.return_value = common_test_data["year"]

            # Set up mock to either return a value or raise an exception
            if isinstance(mock_return, Exception):
                mock_client.get_legislation_by_year.side_effect = mock_return
            else:
                mock_client.get_legislation_by_year.return_value = mock_return
            result = get_bills_by_year(**filter_args)

            # Assertions
            if expected_error:
                assert "error" in result
                assert expected_error in result["error"]
            else:
                assert result["count"] == expected_count
                assert len(result["bills"]) == expected_count
                assert result["year"] == common_test_data["year"]


class TestSearchBills:
    """Tests for the search_bills function."""

    @pytest.mark.parametrize(
        ("scenario", "mock_return", "expected_count", "expected_error"),
        [
            (
                "success",
                [{"bill_id": "HB 1234"}, {"bill_id": "SB 5678"}],
                2,
                None,
            ),
            (
                "empty_results",
                [],
                None,
                "No bills found matching query",
            ),
            (
                "api_error",
                Exception("API Error"),
                None,
                "Failed to search bills",
            ),
        ],
    )
    def test_search_bills_scenarios(
        self, scenario, mock_return, expected_count, expected_error, common_test_data
    ):
        """Test different scenarios for search_bills using parametrization."""
        # Setup mocks
        with (
            patch("wa_leg_mcp.tools.bill_tools.get_current_biennium") as mock_get_biennium,
            patch("wa_leg_mcp.tools.bill_tools.wsl_search_client") as mock_search_client,
        ):

            mock_get_biennium.return_value = common_test_data["biennium"]

            # Set up mock to either return a value or raise an exception
            if isinstance(mock_return, Exception):
                mock_search_client.search_bills.side_effect = mock_return
            else:
                mock_search_client.search_bills.return_value = mock_return
            result = search_bills(query=common_test_data["query"])

            # Assertions
            if expected_error:
                assert "error" in result
                assert expected_error in result["error"]
            else:
                assert result["count"] == expected_count
                assert len(result["bills"]) == expected_count
                assert result["query"] == common_test_data["query"]


class TestBillDocuments:
    """Tests for the get_bill_documents function."""

    @pytest.mark.parametrize(
        ("scenario", "mock_return", "filter_args", "expected_count", "expected_error"),
        [
            (
                "success_no_filter",
                [{"type": "bill"}, {"type": "amendment"}],
                {},
                2,
                None,
            ),
            (
                "success_with_type_filter",
                [{"type": "bill"}, {"type": "amendment"}],
                {"document_type": "bill"},
                1,
                None,
            ),
            (
                "not_found",
                None,
                {},
                None,
                "No documents found",
            ),
            (
                "api_error",
                Exception("API Error"),
                {},
                None,
                "Failed to fetch bill documents",
            ),
        ],
    )
    def test_get_bill_documents_scenarios(
        self, scenario, mock_return, filter_args, expected_count, expected_error, common_test_data
    ):
        """Test different scenarios for get_bill_documents using parametrization."""
        # Setup mocks
        with (
            patch("wa_leg_mcp.tools.bill_tools.get_current_biennium") as mock_get_biennium,
            patch("wa_leg_mcp.tools.bill_tools.wsl_client") as mock_client,
        ):

            mock_get_biennium.return_value = common_test_data["biennium"]

            # Set up mock to either return a value or raise an exception
            if isinstance(mock_return, Exception):
                mock_client.get_documents.side_effect = mock_return
            else:
                mock_client.get_documents.return_value = mock_return
            result = get_bill_documents(common_test_data["bill_number"], **filter_args)

            # Assertions
            if expected_error:
                assert "error" in result
                assert expected_error in result["error"]
            else:
                assert result["count"] == expected_count
                assert len(result["documents"]) == expected_count
                assert result["bill_number"] == common_test_data["bill_number"]


class TestBillAmendments:
    """Tests for the get_bill_amendments function."""

    @pytest.mark.parametrize(
        ("scenario", "mock_return", "bill_number", "expected_count", "expected_error"),
        [
            (
                "success",
                [{"bill_number": 1234, "bill_id": "HB 1234"}],
                1234,
                1,
                None,
            ),
            (
                "no_matching_amendments",
                [{"bill_number": 5678, "bill_id": "HB 5678"}],
                1234,
                None,
                "No amendments found for bill",
            ),
            (
                "not_found",
                None,
                1234,
                None,
                "Failed to fetch amendments",
            ),
            (
                "api_error",
                Exception("API Error"),
                1234,
                None,
                "Failed to fetch bill amendments",
            ),
        ],
    )
    def test_get_bill_amendments_scenarios(
        self, scenario, mock_return, bill_number, expected_count, expected_error, common_test_data
    ):
        """Test different scenarios for get_bill_amendments using parametrization."""
        # Setup mocks
        with (
            patch("wa_leg_mcp.tools.bill_tools.get_current_biennium") as mock_get_biennium,
            patch("wa_leg_mcp.tools.bill_tools.wsl_client") as mock_client,
        ):

            mock_get_biennium.return_value = common_test_data["biennium"]

            # Set up mock to either return a value or raise an exception
            if isinstance(mock_return, Exception):
                mock_client.get_amendments.side_effect = mock_return
            else:
                mock_client.get_amendments.return_value = mock_return
            result = get_bill_amendments(bill_number)

            # Assertions
            if expected_error:
                assert "error" in result
                assert expected_error in result["error"]
            elif expected_count:
                # Verify the amendments list exists and has the expected length
                assert "amendments" in result
                assert len(result["amendments"]) == expected_count
                # Verify the count field matches the length of the amendments list
                assert result["count"] == len(result["amendments"])
                assert result["bill_number"] == bill_number


class TestBillContent:
    """Tests for the get_bill_content function."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("bill_format", "expected_content_type"),
        [
            ("xml", "content"),
            ("pdf", "url"),
            ("htm", "content"),
        ],
    )
    async def test_get_bill_content_formats(
        self, bill_format, expected_content_type, common_test_data, async_mock_httpx_client
    ):
        """Test get_bill_content with different formats."""
        # Setup mocks
        with (
            patch("wa_leg_mcp.tools.bill_tools.get_current_biennium") as mock_get_biennium,
            patch("wa_leg_mcp.tools.bill_tools.fetch_bill_document") as mock_fetch_document,
        ):
            mock_get_biennium.return_value = common_test_data["biennium"]

            # Configure mock response based on format
            if bill_format == "pdf":
                mock_fetch_document.return_value = {
                    "url": f"https://example.com/bill.{bill_format}",
                    "mime_type": "application/pdf",
                }
            else:
                mock_fetch_document.return_value = "<bill>Test content</bill>"

            # Call function
            result = await get_bill_content(
                bill_number=common_test_data["bill_number"],
                chamber=common_test_data["chamber"],
                bill_format=bill_format,
            )

            # Assertions
            mock_fetch_document.assert_called_once_with(
                common_test_data["biennium"],
                common_test_data["chamber"],
                common_test_data["bill_number"],
                bill_format,
            )

            if expected_content_type == "content":
                assert "content" in result
                assert result["content"] == "<bill>Test content</bill>"
            else:
                assert "url" in result

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("scenario", "mock_fetch_return", "expected_error"),
        [
            (
                "invalid_format",
                None,
                "Invalid format",
            ),
            (
                "fetch_error",
                {"error": "Failed to fetch"},
                "Failed to fetch",
            ),
            (
                "exception",
                Exception("Test error"),
                "Failed to fetch bill content",
            ),
        ],
    )
    async def test_get_bill_content_error_scenarios(
        self, scenario, mock_fetch_return, expected_error, common_test_data
    ):
        """Test error scenarios for get_bill_content."""
        # Setup mocks
        with (
            patch("wa_leg_mcp.tools.bill_tools.get_current_biennium") as mock_get_biennium,
            patch("wa_leg_mcp.tools.bill_tools.fetch_bill_document") as mock_fetch_document,
        ):
            mock_get_biennium.return_value = common_test_data["biennium"]

            # Configure mock based on scenario
            if scenario == "invalid_format":
                # Don't configure mock_fetch_document as it shouldn't be called
                bill_format = "invalid"
            else:
                bill_format = "xml"
                if isinstance(mock_fetch_return, Exception):
                    mock_fetch_document.side_effect = mock_fetch_return
                else:
                    mock_fetch_document.return_value = mock_fetch_return

            # Call function
            result = await get_bill_content(
                bill_number=common_test_data["bill_number"],
                chamber=common_test_data["chamber"],
                bill_format=bill_format,
            )

            # Assertions
            assert "error" in result
            assert expected_error in result["error"]

    @pytest.mark.asyncio
    async def test_chamber_determination_fails_defaults_to_house(self, common_test_data):
        """Test case where chamber determination fails and defaults to House.

        House is the default chamber because most bills originate there and
        it's a reasonable first attempt when the chamber is unknown.
        """
        # Setup mocks
        with (
            patch("wa_leg_mcp.tools.bill_tools.get_current_biennium") as mock_get_biennium,
            patch("wa_leg_mcp.tools.bill_tools.get_bill_info") as mock_get_bill_info,
            patch(
                "wa_leg_mcp.tools.bill_tools.determine_chamber_from_bill_id"
            ) as mock_determine_chamber,
            patch("wa_leg_mcp.tools.bill_tools.fetch_bill_document") as mock_fetch_document,
        ):
            mock_get_biennium.return_value = common_test_data["biennium"]
            # Return bill info but with no bill_id to determine chamber from
            mock_get_bill_info.return_value = {"bill_number": common_test_data["bill_number"]}
            # Chamber determination returns None
            mock_determine_chamber.return_value = None
            mock_fetch_document.return_value = "<bill>Test content</bill>"

            # Call function without specifying chamber
            result = await get_bill_content(
                bill_number=common_test_data["bill_number"], bill_format="xml"
            )

            # Assertions
            mock_get_bill_info.assert_called_once()
            # Should default to House when chamber determination fails
            mock_fetch_document.assert_called_once_with(
                common_test_data["biennium"], "House", common_test_data["bill_number"], "xml"
            )
            assert result["content"] == "<bill>Test content</bill>"
            assert result["chamber"] == "House"

    @pytest.mark.asyncio
    async def test_house_fails_fallback_to_senate(self, common_test_data):
        """Test case where House bill fetch fails and falls back to Senate."""
        # Setup mocks
        with (
            patch("wa_leg_mcp.tools.bill_tools.get_current_biennium") as mock_get_biennium,
            patch("wa_leg_mcp.tools.bill_tools.get_bill_info") as mock_get_bill_info,
            patch(
                "wa_leg_mcp.tools.bill_tools.determine_chamber_from_bill_id"
            ) as mock_determine_chamber,
            patch("wa_leg_mcp.tools.bill_tools.fetch_bill_document") as mock_fetch_document,
        ):
            mock_get_biennium.return_value = common_test_data["biennium"]
            # Return bill info but with no bill_id that can be used to determine chamber
            mock_get_bill_info.return_value = {"bill_number": common_test_data["bill_number"]}
            # Chamber determination returns None
            mock_determine_chamber.return_value = None

            # First call fails with House, second succeeds with Senate
            mock_fetch_document.side_effect = [
                {"error": "Bill not found in House"},
                "<bill>Test content</bill>",
            ]

            # Call function without specifying chamber
            result = await get_bill_content(
                bill_number=common_test_data["bill_number"], bill_format="xml"
            )

            # Assertions
            assert mock_fetch_document.call_count == 2
            # First call should be with House
            mock_fetch_document.assert_any_call(
                common_test_data["biennium"], "House", common_test_data["bill_number"], "xml"
            )
            # Second call should be with Senate
            mock_fetch_document.assert_any_call(
                common_test_data["biennium"], "Senate", common_test_data["bill_number"], "xml"
            )
            assert result["content"] == "<bill>Test content</bill>"
            assert result["chamber"] == "Senate"


if __name__ == "__main__":
    pytest.main([__file__])
