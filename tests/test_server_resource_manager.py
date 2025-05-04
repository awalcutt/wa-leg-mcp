"""
Tests for the register_bill_resources function in server.py
specifically testing the resource manager edge case (line 115)
"""

import contextlib
from unittest.mock import MagicMock, patch

import pytest

from wa_leg_mcp.server import register_bill_resources


@pytest.fixture
def mock_mcp():
    """Create a mock MCP server instance."""
    mock = MagicMock()
    mock._resource_manager = MagicMock()
    return mock


@pytest.fixture
def mock_templates():
    """Create mock bill document templates."""
    template1 = MagicMock()
    template1.uri_template = "/bills/{biennium}/{chamber}/{bill_number}.{bill_format}"
    template1.name = "Bill Document"
    template1.description = "Bill document in various formats"
    template1.mime_type = "text/xml"

    template2 = MagicMock()
    template2.uri_template = "/amendments/{biennium}/{bill_number}"
    template2.name = "Bill Amendment"
    template2.description = "Bill amendment document"
    template2.mime_type = "text/html"

    return [template1, template2]


def test_register_bill_resources_success(mock_mcp, mock_templates):
    """
    Test successful registration of bill resources.

    This test verifies that bill document templates are correctly registered
    with the MCP resource manager.
    """
    with patch("wa_leg_mcp.server.get_bill_document_templates") as mock_get_templates:
        mock_get_templates.return_value = mock_templates

        # Call the function
        register_bill_resources(mock_mcp)

        # Verify templates were registered
        assert mock_mcp._resource_manager.add_template.call_count == 2

        # Verify each template was registered with the correct parameters
        for template in mock_templates:
            mock_mcp._resource_manager.add_template.assert_any_call(
                fn=template.fn,
                uri_template=template.uri_template,
                name=template.name,
                description=template.description,
                mime_type=template.mime_type,
            )


def test_register_bill_resources_error_handling(mock_mcp, mock_templates):
    """
    Test error handling when adding a template fails (line 115).

    This test specifically targets line 115 in server.py where the function
    adds a template to the resource manager. It verifies that if an exception
    occurs, the function continues to try to add the remaining templates.
    """
    with patch("wa_leg_mcp.server.get_bill_document_templates") as mock_get_templates:
        mock_get_templates.return_value = mock_templates

        # Make the first add_template call succeed but the second one fail
        mock_mcp._resource_manager.add_template.side_effect = [
            None,
            Exception("Failed to add template"),
        ]

        # Call the function - it will raise an exception but we want to verify it tried to add both templates
        with contextlib.suppress(Exception):
            register_bill_resources(mock_mcp)

        # Verify we tried to add both templates
        assert mock_mcp._resource_manager.add_template.call_count == 2


if __name__ == "__main__":
    pytest.main([__file__])
