"""
Tests for bill_document_utils.py organized by functionality
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

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


class TestValidation:
    """Tests for validation functions."""

    def test_validate_biennium_valid_formats(self):
        """Test validation of valid biennium formats."""
        # Mock the datetime to return a fixed year
        with patch("datetime.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 1, 1)

            # Valid current biennium
            assert validate_biennium("2023-24") is True

            # Valid past biennium
            assert validate_biennium("2021-22") is True

            # Verify that datetime.now() was called for each biennium validation
            assert mock_datetime.now.call_count == 2

    def test_validate_biennium_future(self):
        """Test validation rejects future bienniums."""
        # Mock the datetime to return a fixed year
        with patch("datetime.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 1, 1)

            # Future biennium should be rejected
            assert validate_biennium("2025-26") is False

            # Mock was called
            mock_datetime.now.assert_called_once()

    def test_validate_biennium_invalid_formats(self):
        """Test validation of invalid biennium formats."""
        # These invalid formats should be rejected by regex validation before reaching the datetime check, improving performance
        assert validate_biennium("2024-25") is False  # Starts with even year
        assert validate_biennium("2023-25") is False  # Years not consecutive
        assert validate_biennium("202-24") is False  # Wrong format
        assert validate_biennium("2023-2") is False  # Wrong format
        assert validate_biennium("2023/24") is False  # Wrong format
        assert validate_biennium("abcd-ef") is False  # Non-numeric

    @pytest.mark.parametrize(
        ("chamber", "expected"),
        [
            ("House", True),  # Valid chamber
            ("Senate", True),  # Valid chamber
            ("house", False),  # Case sensitive
            ("senate", False),  # Case sensitive
            ("H", False),  # Abbreviation
            ("S", False),  # Abbreviation
            ("Other", False),  # Invalid value
        ],
    )
    def test_validate_chamber(self, chamber, expected):
        """Test chamber validation."""
        assert validate_chamber(chamber) == expected

    @pytest.mark.parametrize(
        ("bill_number", "expected"),
        [
            (1234, True),  # Integer
            ("1234", True),  # String
            ("123", True),  # 3 digits
            ("12345", True),  # 5 digits
            ("HB1234", False),  # Contains prefix
            ("12", False),  # Too short
            ("123456", False),  # Too long
            ("123a", False),  # Contains non-digits
        ],
    )
    def test_validate_bill_number(self, bill_number, expected):
        """Test bill number validation."""
        assert validate_bill_number(bill_number) == expected


class TestUrlGeneration:
    """Tests for URL generation functions."""

    @pytest.mark.parametrize(
        ("biennium", "chamber", "bill_number", "bill_format", "expected"),
        [
            (
                "2023-24",
                "House",
                "1234",
                "xml",
                "https://lawfilesext.leg.wa.gov/biennium/2023-24/Xml/Bills/House%20Bills/1234.xml",
            ),
            (
                "2023-24",
                "Senate",
                "5678",
                "htm",
                "https://lawfilesext.leg.wa.gov/biennium/2023-24/Htm/Bills/Senate%20Bills/5678.htm",
            ),
            (
                "2025-26",
                "House",
                1000,
                "pdf",
                "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/House%20Bills/1000.pdf",
            ),
        ],
    )
    def test_get_bill_document_url(self, biennium, chamber, bill_number, bill_format, expected):
        """Test URL generation for bill documents."""
        url = get_bill_document_url(biennium, chamber, bill_number, bill_format)
        assert url == expected


class TestBillIdParsing:
    """Tests for bill ID parsing functions."""

    @pytest.mark.parametrize(
        ("bill_id", "expected"),
        [
            ("HB 1234", "House"),  # House bill
            ("SHB 1234", "House"),  # Substitute House bill
            ("ESHB 1234", "House"),  # Engrossed Substitute House bill
            ("SB 5678", "Senate"),  # Senate bill
            ("SSB 5678", "Senate"),  # Substitute Senate bill
            ("ESSB 5678", "Senate"),  # Engrossed Substitute Senate bill
            ("1234", None),  # Invalid/ambiguous bill ID
            ("Bill 1234", None),  # Invalid/ambiguous bill ID
        ],
    )
    def test_determine_chamber_from_bill_id(self, bill_id, expected):
        """Test determining chamber from bill ID."""
        assert determine_chamber_from_bill_id(bill_id) == expected

    @pytest.mark.parametrize(
        ("bill_id", "expected"),
        [
            ("HB 1234", "1234"),  # House bill
            ("SB 5678", "5678"),  # Senate bill
            ("SHB 1234", "1234"),  # Substitute House bill
            ("ESSB 5678", "5678"),  # Engrossed Substitute Senate bill
            ("Bill 1234", "1234"),  # Generic bill format
            ("HB", None),  # Invalid bill ID
            ("Senate Bill", None),  # Invalid bill ID
            ("HB12", None),  # Too short
        ],
    )
    def test_extract_bill_number(self, bill_id, expected):
        """Test extracting bill number from bill ID."""
        assert extract_bill_number(bill_id) == expected


class TestFetchBillDocument:
    """Tests for fetch_bill_document function."""

    @pytest.fixture
    def mock_httpx_client(self):
        """Create a mock for httpx.AsyncClient."""
        with patch("wa_leg_mcp.utils.bill_document_utils.httpx.AsyncClient") as mock:
            client_instance = AsyncMock()
            mock.return_value.__aenter__.return_value = client_instance

            # Setup the response - use a regular Mock for the response object
            # since raise_for_status() is not awaitable in the real httpx
            response = Mock()
            response.text = "<bill>Test Bill Content</bill>"
            # Make sure raise_for_status doesn't have __await__ attribute
            response.raise_for_status = Mock()

            client_instance.get.return_value = response
            yield client_instance

    @pytest.mark.asyncio
    async def test_fetch_bill_document_xml(self, mock_httpx_client):
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
    async def test_fetch_bill_document_pdf(self):
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
    @pytest.mark.parametrize(
        ("biennium", "chamber", "bill_number", "error_text"),
        [
            ("2024-25", "House", "1234", "Invalid biennium format"),
            ("2023-24", "house", "1234", "Invalid chamber"),
            ("2023-24", "House", "HB1234", "Invalid bill number"),
        ],
    )
    async def test_fetch_bill_document_invalid_params(
        self, biennium, chamber, bill_number, error_text
    ):
        """Test fetching with invalid parameters."""
        result = await fetch_bill_document(biennium, chamber, bill_number)
        assert "error" in result
        assert error_text in result["error"]

    @pytest.mark.asyncio
    async def test_fetch_bill_document_http_error(self):
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
    pytest.main([__file__])
