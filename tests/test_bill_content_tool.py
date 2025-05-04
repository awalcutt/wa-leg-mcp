"""
Tests for the get_bill_content tool in bill_tools.py
"""

from unittest.mock import patch

import pytest

from wa_leg_mcp.tools.bill_tools import get_bill_content


@pytest.fixture
def test_data():
    """Set up test fixtures."""
    return {
        "bill_number": 1234,
        "biennium": "2023-24",
        "chamber": "House",
        "sample_xml": "<bill><billNumber>1234</billNumber><title>Test Bill</title></bill>",
        "mock_bill_info": {
            "bill_number": 1234,
            "bill_id": "HB 1234",
            "biennium": "2023-24",
            "title": "Test Bill",
            "sponsor": "Test Sponsor",
        },
    }


@pytest.mark.asyncio
async def test_get_bill_content_xml_success(test_data):
    """Test successful retrieval of bill content in XML format."""
    # Setup mocks
    with (
        patch("wa_leg_mcp.tools.bill_tools.get_current_biennium") as mock_get_biennium,
        patch("wa_leg_mcp.tools.bill_tools.fetch_bill_document") as mock_fetch_document,
    ):

        mock_get_biennium.return_value = test_data["biennium"]
        mock_fetch_document.return_value = test_data["sample_xml"]

        # Call function
        result = await get_bill_content(
            bill_number=test_data["bill_number"], chamber=test_data["chamber"], bill_format="xml"
        )

        # Assertions
        mock_fetch_document.assert_called_once_with(
            test_data["biennium"], test_data["chamber"], str(test_data["bill_number"]), "xml"
        )
        assert result["content"] == test_data["sample_xml"]
        assert result["format"] == "xml"
        assert result["bill_number"] == test_data["bill_number"]
        assert result["chamber"] == test_data["chamber"]
        assert "pdf_url" in result
        assert "html_url" in result


@pytest.mark.asyncio
async def test_get_bill_content_pdf(test_data):
    """Test retrieval of bill content in PDF format (returns URL)."""
    # Setup mocks
    with (
        patch("wa_leg_mcp.tools.bill_tools.get_current_biennium") as mock_get_biennium,
        patch("wa_leg_mcp.tools.bill_tools.fetch_bill_document") as mock_fetch_document,
    ):

        mock_get_biennium.return_value = test_data["biennium"]
        mock_fetch_document.return_value = {
            "url": f"https://lawfilesext.leg.wa.gov/biennium/{test_data['biennium']}/Pdf/Bills/{test_data['chamber']}%20Bills/{test_data['bill_number']}.pdf",
            "mime_type": "application/pdf",
            "bill_info": {
                "biennium": test_data["biennium"],
                "chamber": test_data["chamber"],
                "bill_number": str(test_data["bill_number"]),
                "format": "pdf",
            },
        }

        # Call function
        result = await get_bill_content(
            bill_number=test_data["bill_number"], chamber=test_data["chamber"], bill_format="pdf"
        )

        # Assertions
        mock_fetch_document.assert_called_once_with(
            test_data["biennium"], test_data["chamber"], str(test_data["bill_number"]), "pdf"
        )
        assert "url" in result
        assert result["mime_type"] == "application/pdf"


@pytest.mark.asyncio
async def test_get_bill_content_auto_chamber(test_data):
    """Test automatic chamber detection when not provided."""
    # Setup mocks
    with (
        patch("wa_leg_mcp.tools.bill_tools.get_current_biennium") as mock_get_biennium,
        patch("wa_leg_mcp.tools.bill_tools.get_bill_info") as mock_get_bill_info,
        patch("wa_leg_mcp.tools.bill_tools.fetch_bill_document") as mock_fetch_document,
    ):

        mock_get_biennium.return_value = test_data["biennium"]
        mock_get_bill_info.return_value = test_data["mock_bill_info"]
        mock_fetch_document.return_value = test_data["sample_xml"]

        # Call function without specifying chamber
        result = await get_bill_content(bill_number=test_data["bill_number"], bill_format="xml")

        # Assertions
        mock_get_bill_info.assert_called_once()
        mock_fetch_document.assert_called_once_with(
            test_data["biennium"], "House", str(test_data["bill_number"]), "xml"
        )
        assert result["content"] == test_data["sample_xml"]
        assert result["chamber"] == "House"


@pytest.mark.asyncio
async def test_get_bill_content_fallback_chamber(test_data):
    """Test fallback to Senate when House fails."""
    # Setup mocks
    with (
        patch("wa_leg_mcp.tools.bill_tools.get_current_biennium") as mock_get_biennium,
        patch("wa_leg_mcp.tools.bill_tools.get_bill_info") as mock_get_bill_info,
        patch("wa_leg_mcp.tools.bill_tools.fetch_bill_document") as mock_fetch_document,
    ):

        mock_get_biennium.return_value = test_data["biennium"]
        mock_get_bill_info.return_value = {"error": "Bill not found"}

        # First call fails with House, second succeeds with Senate
        mock_fetch_document.side_effect = [
            {"error": "Bill not found in House"},
            test_data["sample_xml"],
        ]

        # Call function without specifying chamber
        result = await get_bill_content(bill_number=test_data["bill_number"], bill_format="xml")

        # Assertions
        assert mock_fetch_document.call_count == 2
        assert result["content"] == test_data["sample_xml"]
        assert result["chamber"] == "Senate"


@pytest.mark.asyncio
async def test_get_bill_content_invalid_format(test_data):
    """Test handling of invalid format."""
    # Setup mocks
    with (
        patch("wa_leg_mcp.tools.bill_tools.get_current_biennium") as mock_get_biennium,
        patch("wa_leg_mcp.tools.bill_tools.fetch_bill_document") as mock_fetch_document,
    ):

        mock_get_biennium.return_value = test_data["biennium"]

        # Call function with invalid format
        result = await get_bill_content(
            bill_number=test_data["bill_number"],
            chamber=test_data["chamber"],
            bill_format="invalid",
        )

        # Assertions
        mock_fetch_document.assert_not_called()
        assert "error" in result
        assert "Invalid format" in result["error"]


@pytest.mark.asyncio
async def test_get_bill_content_both_chambers_fail(test_data):
    """Test when both House and Senate attempts fail."""
    # Setup mocks
    with (
        patch("wa_leg_mcp.tools.bill_tools.get_current_biennium") as mock_get_biennium,
        patch("wa_leg_mcp.tools.bill_tools.get_bill_info") as mock_get_bill_info,
        patch("wa_leg_mcp.tools.bill_tools.fetch_bill_document") as mock_fetch_document,
    ):

        mock_get_biennium.return_value = test_data["biennium"]
        mock_get_bill_info.return_value = {"error": "Bill not found"}

        # Both House and Senate attempts fail
        mock_fetch_document.side_effect = [
            {"error": "Bill not found in House"},
            {"error": "Bill not found in Senate"},
        ]

        # Call function without specifying chamber
        result = await get_bill_content(bill_number=test_data["bill_number"], bill_format="xml")

        # Assertions
        assert mock_fetch_document.call_count == 2
        assert "error" in result
        assert result == {"error": "Bill not found in Senate"}


@pytest.mark.asyncio
async def test_get_bill_content_exception(test_data):
    """Test exception handling."""
    # Setup mocks
    with (
        patch("wa_leg_mcp.tools.bill_tools.get_current_biennium") as mock_get_biennium,
        patch("wa_leg_mcp.tools.bill_tools.fetch_bill_document") as mock_fetch_document,
    ):

        mock_get_biennium.return_value = test_data["biennium"]
        mock_fetch_document.side_effect = Exception("Test error")

        # Call function
        result = await get_bill_content(
            bill_number=test_data["bill_number"], chamber=test_data["chamber"], bill_format="xml"
        )

        # Assertions
        assert "error" in result
        assert "Failed to fetch bill content" in result["error"]
