"""
Tests for bill_document_utils.py
"""

import unittest
from unittest.mock import AsyncMock, patch

import pytest

from wa_leg_mcp.utils.bill_document_utils import (
    determine_chamber_from_bill_id,
    extract_bill_number,
    fetch_bill_document,
    get_bill_document_url,
    validate_biennium,
    validate_bill_number,
    validate_chamber,
)


class TestBillDocumentUtils(unittest.TestCase):
    """Test cases for bill document utilities."""

    def test_validate_biennium(self):
        """Test biennium validation."""
        # Valid bienniums
        assert validate_biennium("2023-24")
        assert validate_biennium("2025-26")

        # Invalid bienniums
        assert not validate_biennium("2024-25")  # Starts with even year
        assert not validate_biennium("2023-25")  # Years not consecutive
        assert not validate_biennium("202-24")  # Wrong format
        assert not validate_biennium("2023-2")  # Wrong format
        assert not validate_biennium("2023/24")  # Wrong format
        assert not validate_biennium("abcd-ef")  # Non-numeric

    def test_validate_chamber(self):
        """Test chamber validation."""
        # Valid chambers
        assert validate_chamber("House")
        assert validate_chamber("Senate")

        # Invalid chambers
        assert not validate_chamber("house")  # Case sensitive
        assert not validate_chamber("senate")  # Case sensitive
        assert not validate_chamber("H")  # Abbreviation
        assert not validate_chamber("S")  # Abbreviation
        assert not validate_chamber("Other")  # Invalid value

    def test_validate_bill_number(self):
        """Test bill number validation."""
        # Valid bill numbers
        assert validate_bill_number(1234)  # Integer
        assert validate_bill_number("1234")  # String
        assert validate_bill_number("123")  # 3 digits
        assert validate_bill_number("12345")  # 5 digits

        # Invalid bill numbers
        assert not validate_bill_number("HB1234")  # Contains prefix
        assert not validate_bill_number("12")  # Too short
        assert not validate_bill_number("123456")  # Too long
        assert not validate_bill_number("123a")  # Contains non-digits

    def test_get_bill_document_url(self):
        """Test URL generation for bill documents."""
        # Test XML format (default)
        url = get_bill_document_url("2023-24", "House", "1234")
        assert (
            url
            == "https://lawfilesext.leg.wa.gov/biennium/2023-24/Xml/Bills/House%20Bills/1234.xml"
        )

        # Test HTML format
        url = get_bill_document_url("2023-24", "Senate", "5678", "htm")
        assert (
            url
            == "https://lawfilesext.leg.wa.gov/biennium/2023-24/Htm/Bills/Senate%20Bills/5678.htm"
        )

        # Test PDF format
        url = get_bill_document_url("2025-26", "House", 1000, "pdf")
        assert (
            url
            == "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/House%20Bills/1000.pdf"
        )

    def test_determine_chamber_from_bill_id(self):
        """Test determining chamber from bill ID."""
        # House bills
        assert determine_chamber_from_bill_id("HB 1234") == "House"
        assert determine_chamber_from_bill_id("SHB 1234") == "House"
        assert determine_chamber_from_bill_id("ESHB 1234") == "House"

        # Senate bills
        assert determine_chamber_from_bill_id("SB 5678") == "Senate"
        assert determine_chamber_from_bill_id("SSB 5678") == "Senate"
        assert determine_chamber_from_bill_id("ESSB 5678") == "Senate"

        # Invalid or ambiguous bill IDs
        assert determine_chamber_from_bill_id("1234") is None
        assert determine_chamber_from_bill_id("Bill 1234") is None

    def test_extract_bill_number(self):
        """Test extracting bill number from bill ID."""
        # Valid bill IDs
        assert extract_bill_number("HB 1234") == "1234"
        assert extract_bill_number("SB 5678") == "5678"
        assert extract_bill_number("SHB 1234") == "1234"
        assert extract_bill_number("ESSB 5678") == "5678"
        assert extract_bill_number("Bill 1234") == "1234"

        # Invalid bill IDs
        assert extract_bill_number("HB") is None
        assert extract_bill_number("Senate Bill") is None
        assert extract_bill_number("HB12") is None  # Too short


@pytest.fixture
def mock_httpx_client():
    """Create a mock for httpx.AsyncClient."""
    with patch("wa_leg_mcp.utils.bill_document_utils.httpx.AsyncClient") as mock:
        client_instance = AsyncMock()
        mock.return_value.__aenter__.return_value = client_instance

        # Setup the response - use AsyncMock for the entire response object
        response = AsyncMock()
        response.text = "<bill>Test Bill Content</bill>"

        client_instance.get.return_value = response
        yield client_instance


@pytest.mark.asyncio
async def test_fetch_bill_document_xml(mock_httpx_client):
    """Test fetching XML bill document."""
    # Call function
    result = await fetch_bill_document("2023-24", "House", "1234", "xml")

    # Assertions
    assert result == "<bill>Test Bill Content</bill>"
    mock_httpx_client.get.assert_called_once()
    url_called = mock_httpx_client.get.call_args[0][0]
    assert "2023-24" in url_called
    assert "House" in url_called
    assert "1234.xml" in url_called


@pytest.mark.asyncio
async def test_fetch_bill_document_pdf():
    """Test fetching PDF bill document (returns URL only)."""
    # Call function
    result = await fetch_bill_document("2023-24", "House", "1234", "pdf")

    # Assertions
    assert isinstance(result, dict)
    assert "url" in result
    assert result["mime_type"] == "application/pdf"
    assert "bill_info" in result
    assert result["bill_info"]["biennium"] == "2023-24"
    assert result["bill_info"]["chamber"] == "House"
    assert result["bill_info"]["bill_number"] == "1234"


@pytest.mark.asyncio
async def test_fetch_bill_document_invalid_params():
    """Test fetching with invalid parameters."""
    # Invalid biennium
    result = await fetch_bill_document("2024-25", "House", "1234")
    assert "error" in result
    assert "Invalid biennium format" in result["error"]

    # Invalid chamber
    result = await fetch_bill_document("2023-24", "house", "1234")
    assert "error" in result
    assert "Invalid chamber" in result["error"]

    # Invalid bill number
    result = await fetch_bill_document("2023-24", "House", "HB1234")
    assert "error" in result
    assert "Invalid bill number" in result["error"]


@pytest.mark.asyncio
async def test_fetch_bill_document_http_error():
    """Test handling HTTP errors when fetching documents."""
    # Setup mock to raise exception
    with patch("wa_leg_mcp.utils.bill_document_utils.httpx.AsyncClient") as mock_client:
        mock_client_instance = AsyncMock()
        mock_client_instance.get.side_effect = Exception("Connection error")
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        # Call function
        result = await fetch_bill_document("2023-24", "House", "1234", "xml")

        # Assertions
        assert "error" in result
        assert "Could not fetch content" in result["error"]
        assert "url" in result  # Should provide URL as fallback


if __name__ == "__main__":
    unittest.main()
