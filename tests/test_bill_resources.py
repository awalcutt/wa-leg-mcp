"""
Tests for bill_resources.py
"""

import unittest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from wa_leg_mcp.resources.bill_resources import (
    get_bill_document_templates,
    get_bill_document_url,
    read_bill_document,
)
from wa_leg_mcp.utils.bill_document_utils import (
    validate_biennium,
    validate_bill_number,
    validate_chamber,
)


class TestBillResourcesValidation(unittest.TestCase):
    """Test cases for validation functions in bill_resources.py."""

    def test_validate_biennium_valid(self):
        """Test validation of valid biennium strings."""
        # Valid biennium strings
        assert validate_biennium("2023-24")
        assert validate_biennium("2025-26")

        # Test with current year (if it's an odd year)
        current_year = datetime.now().year
        if current_year % 2 == 1:
            assert validate_biennium(f"{current_year}-{str(current_year + 1)[2:]}")

    def test_validate_biennium_invalid(self):
        """Test validation of invalid biennium strings."""
        # Invalid format
        assert not validate_biennium("2023")
        assert not validate_biennium("2023-2024")
        assert not validate_biennium("23-24")

        # Even year start
        assert not validate_biennium("2024-25")

        # Non-consecutive years
        assert not validate_biennium("2023-25")

        # Future biennium (assuming test is run before 2099)
        assert not validate_biennium("2099-00")

        # Invalid format that causes ValueError in int conversion
        assert not validate_biennium("20xx-yy")

    def test_validate_chamber_valid(self):
        """Test validation of valid chamber names."""
        assert validate_chamber("House")
        assert validate_chamber("Senate")

    def test_validate_chamber_invalid(self):
        """Test validation of invalid chamber names."""
        assert not validate_chamber("house")  # Case-sensitive
        assert not validate_chamber("senate")  # Case-sensitive
        assert not validate_chamber("H")
        assert not validate_chamber("S")
        assert not validate_chamber("")
        assert not validate_chamber("Other")

    def test_validate_bill_number_valid(self):
        """Test validation of valid bill numbers."""
        # Integer inputs
        assert validate_bill_number(123)
        assert validate_bill_number(1234)
        assert validate_bill_number(12345)

        # String inputs
        assert validate_bill_number("123")
        assert validate_bill_number("1234")
        assert validate_bill_number("12345")

    def test_validate_bill_number_invalid(self):
        """Test validation of invalid bill numbers."""
        # Too short
        assert not validate_bill_number(12)
        assert not validate_bill_number("12")

        # Too long
        assert not validate_bill_number(123456)
        assert not validate_bill_number("123456")

        # Non-numeric
        assert not validate_bill_number("HB1234")
        assert not validate_bill_number("1234A")
        assert not validate_bill_number("Bill1234")


class TestBillDocumentUrl(unittest.TestCase):
    """Test cases for get_bill_document_url function."""

    def test_get_bill_document_url_xml(self):
        """Test URL generation for XML format."""
        url = get_bill_document_url("2025-26", "House", 1234, "xml")
        expected = (
            "https://lawfilesext.leg.wa.gov/biennium/2025-26/Xml/Bills/House%20Bills/1234.xml"
        )
        assert url == expected

    def test_get_bill_document_url_htm(self):
        """Test URL generation for HTML format."""
        url = get_bill_document_url("2025-26", "Senate", 5678, "htm")
        expected = (
            "https://lawfilesext.leg.wa.gov/biennium/2025-26/Htm/Bills/Senate%20Bills/5678.htm"
        )
        assert url == expected

    def test_get_bill_document_url_pdf(self):
        """Test URL generation for PDF format."""
        url = get_bill_document_url("2025-26", "Senate", 5002, "pdf")
        expected = (
            "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Bills/5002.pdf"
        )
        assert url == expected

    def test_get_bill_document_url_string_bill_number(self):
        """Test URL generation with string bill number."""
        url = get_bill_document_url("2025-26", "House", "1234", "xml")
        expected = (
            "https://lawfilesext.leg.wa.gov/biennium/2025-26/Xml/Bills/House%20Bills/1234.xml"
        )
        assert url == expected


class TestBillDocumentTemplates(unittest.TestCase):
    """Test cases for get_bill_document_templates function."""

    def test_get_bill_document_templates(self):
        """Test creation of bill document templates."""
        templates = get_bill_document_templates()

        # Check that we have the expected number of templates
        assert len(templates) == 4

        # Check that each template has the expected URI pattern
        uri_templates = [template.uri_template for template in templates]
        assert "bill://document/{format}/{biennium}/{chamber}/{bill_number}" in uri_templates
        assert "bill://xml/{biennium}/{chamber}/{bill_number}" in uri_templates
        assert "bill://htm/{biennium}/{chamber}/{bill_number}" in uri_templates
        assert "bill://pdf/{biennium}/{chamber}/{bill_number}" in uri_templates

        # Check that each template has a name and description
        for template in templates:
            assert template.name is not None
            assert template.description is not None
            assert len(template.name) > 0
            assert len(template.description) > 0

    @patch("wa_leg_mcp.resources.bill_resources.get_bill_document_url")
    def test_template_handler_functions(self, mock_get_url):
        """Test the handler functions inside get_bill_document_templates."""
        # Setup the mock to return a predictable URL
        mock_get_url.return_value = "https://example.com/test.url"

        # Get the templates
        templates = get_bill_document_templates()

        # We'll test the template handlers by mocking the get_bill_document_url function
        # and verifying it's called with the correct parameters

        # Test the main document template
        mock_get_url.reset_mock()
        doc_template = next(t for t in templates if "document" in t.uri_template)
        # We need to call the function directly to test it
        handle_bill_document = doc_template.fn
        handle_bill_document(
            bill_format="xml", biennium="2025-26", chamber="House", bill_number="1234"
        )
        mock_get_url.assert_called_with("2025-26", "House", "1234", "xml")

        # Test the XML template
        mock_get_url.reset_mock()
        xml_template = next(
            t
            for t in templates
            if t.uri_template == "bill://xml/{biennium}/{chamber}/{bill_number}"
        )
        handle_xml_bill = xml_template.fn
        handle_xml_bill(biennium="2025-26", chamber="House", bill_number="1234")
        mock_get_url.assert_called_with("2025-26", "House", "1234", "xml")

        # Test the HTML template
        mock_get_url.reset_mock()
        htm_template = next(
            t
            for t in templates
            if t.uri_template == "bill://htm/{biennium}/{chamber}/{bill_number}"
        )
        handle_html_bill = htm_template.fn
        handle_html_bill(biennium="2025-26", chamber="House", bill_number="1234")
        mock_get_url.assert_called_with("2025-26", "House", "1234", "htm")

        # Test the PDF template
        mock_get_url.reset_mock()
        pdf_template = next(
            t
            for t in templates
            if t.uri_template == "bill://pdf/{biennium}/{chamber}/{bill_number}"
        )
        handle_pdf_bill = pdf_template.fn
        handle_pdf_bill(biennium="2025-26", chamber="House", bill_number="1234")
        mock_get_url.assert_called_with("2025-26", "House", "1234", "pdf")


@pytest.mark.asyncio
class TestReadBillDocument:
    """Test cases for read_bill_document function."""

    @pytest.fixture
    def mock_httpx_client(self):
        """Create a mock for httpx.AsyncClient."""
        with patch("httpx.AsyncClient") as mock:
            client_instance = AsyncMock()
            mock.return_value.__aenter__.return_value = client_instance

            # Setup the response
            response = MagicMock()
            response.text = "<bill>Test Bill Content</bill>"
            response.raise_for_status = MagicMock()

            client_instance.get.return_value = response
            yield client_instance

    @pytest.mark.asyncio
    async def test_read_bill_document_xml(self, mock_httpx_client):
        """Test reading an XML bill document."""
        with patch("wa_leg_mcp.resources.bill_resources.fetch_bill_document") as mock_fetch:
            mock_fetch.return_value = "<bill>Test Bill Content</bill>"

            result = await read_bill_document(
                uri="bill://xml/2025-26/House/1234",
                biennium="2025-26",
                chamber="House",
                bill_number="1234",
                bill_format="xml",
            )

            # Check that fetch_bill_document was called with the right parameters
            mock_fetch.assert_called_once_with("2025-26", "House", "1234", "xml")

            # Check that the result is the response text
            assert result == "<bill>Test Bill Content</bill>"

    @pytest.mark.asyncio
    async def test_read_bill_document_pdf(self):
        """Test reading a PDF bill document (returns URL only)."""
        with patch("wa_leg_mcp.resources.bill_resources.fetch_bill_document") as mock_fetch:
            mock_fetch.return_value = {
                "url": "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Bills/5678.pdf",
                "mime_type": "application/pdf",
                "bill_info": {
                    "biennium": "2025-26",
                    "chamber": "Senate",
                    "bill_number": "5678",
                    "format": "pdf",
                },
            }

            result = await read_bill_document(
                uri="bill://pdf/2025-26/Senate/5678",
                biennium="2025-26",
                chamber="Senate",
                bill_number="5678",
                bill_format="pdf",
            )

            # For PDF, we should get a dictionary with the URL
            assert isinstance(result, dict)
            assert "url" in result
            assert (
                result["url"]
                == "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Bills/5678.pdf"
            )
            assert result["mime_type"] == "application/pdf"
            assert "bill_info" in result

    @pytest.mark.asyncio
    async def test_read_bill_document_format_from_uri(self):
        """Test extracting format from URI when not explicitly provided."""
        with patch("wa_leg_mcp.resources.bill_resources.fetch_bill_document") as mock_fetch:
            mock_fetch.return_value = "<bill>Test Bill Content</bill>"

            # Test XML format extraction
            await read_bill_document(
                uri="bill://xml/2025-26/House/1234",
                biennium="2025-26",
                chamber="House",
                bill_number="1234",
            )
            mock_fetch.assert_called_with("2025-26", "House", "1234", "xml")
            mock_fetch.reset_mock()

            # Test HTM format extraction
            await read_bill_document(
                uri="bill://htm/2025-26/House/1234",
                biennium="2025-26",
                chamber="House",
                bill_number="1234",
            )
            mock_fetch.assert_called_with("2025-26", "House", "1234", "htm")
            mock_fetch.reset_mock()

            # Test PDF format extraction
            await read_bill_document(
                uri="bill://pdf/2025-26/House/1234",
                biennium="2025-26",
                chamber="House",
                bill_number="1234",
            )
            mock_fetch.assert_called_with("2025-26", "House", "1234", "pdf")
            mock_fetch.reset_mock()

            # Test document format extraction
            await read_bill_document(
                uri="bill://document/xml/2025-26/House/1234",
                biennium="2025-26",
                chamber="House",
                bill_number="1234",
            )
            mock_fetch.assert_called_with("2025-26", "House", "1234", "xml")
            mock_fetch.reset_mock()

            # Test default to XML when format not in URI
            await read_bill_document(
                uri="bill://other/2025-26/House/1234",
                biennium="2025-26",
                chamber="House",
                bill_number="1234",
            )
            mock_fetch.assert_called_with("2025-26", "House", "1234", "xml")

    @pytest.mark.asyncio
    async def test_read_bill_document_validation_error(self):
        """Test handling of validation errors."""
        with patch("wa_leg_mcp.resources.bill_resources.fetch_bill_document") as mock_fetch:
            mock_fetch.return_value = {"error": "Invalid biennium format"}

            result = await read_bill_document(
                uri="bill://xml/invalid/House/1234",
                biennium="invalid",
                chamber="House",
                bill_number="1234",
            )

            assert "error" in result
            assert result["error"] == "Invalid biennium format"

    @pytest.mark.asyncio
    async def test_read_bill_document_http_error(self):
        """Test handling of HTTP errors."""
        with patch("wa_leg_mcp.resources.bill_resources.fetch_bill_document") as mock_fetch:
            mock_fetch.return_value = {
                "error": "Could not fetch content",
                "url": "https://example.com/error",
            }

            result = await read_bill_document(
                uri="bill://xml/2025-26/House/1234",
                biennium="2025-26",
                chamber="House",
                bill_number="1234",
            )

            assert "error" in result
            assert "Could not fetch content" in result["error"]
            assert "url" in result


if __name__ == "__main__":
    unittest.main()
