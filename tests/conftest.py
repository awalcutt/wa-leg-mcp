"""
Common fixtures for pytest tests.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture
def mock_httpx_client():
    """
    Create a mock for httpx.AsyncClient.

    This fixture mocks the httpx.AsyncClient for synchronous tests and provides
    a standard response with bill content.
    """
    with patch("httpx.AsyncClient") as mock:
        client_instance = AsyncMock()
        mock.return_value.__aenter__.return_value = client_instance

        # Setup the response
        response = MagicMock()
        response.text = "<bill>Test Bill Content</bill>"
        response.raise_for_status = MagicMock()

        client_instance.get.return_value = response
        yield client_instance


@pytest.fixture
async def async_mock_httpx_client():
    """
    Create an async mock for httpx.AsyncClient.

    This fixture is designed to be used with async tests and provides
    the same functionality as mock_httpx_client but in an async context.
    """
    with patch("httpx.AsyncClient") as mock:
        client_instance = AsyncMock()
        mock.return_value.__aenter__.return_value = client_instance

        # Setup the response
        response = AsyncMock()
        response.text = "<bill>Test Bill Content</bill>"
        response.raise_for_status = AsyncMock()

        client_instance.get.return_value = response
        yield client_instance


@pytest.fixture
def common_test_data():
    """
    Common test data used across multiple test files.

    This fixture provides standard test values for bienniums, years, bill numbers,
    and other commonly used test parameters.
    """
    return {
        "biennium": "2023-24",
        "year": "2023",
        "bill_number": "1234",
        "chamber": "House",
        "begin_date": "2023-01-01",
        "end_date": "2023-12-31",
        "query": "climate change",
        "district": "1",
    }


@pytest.fixture
def mock_bill_data():
    """
    Mock bill data for testing bill-related functions.

    This fixture provides a standardized bill object with common fields
    that can be used across different test files.
    """
    return {
        "biennium": "2023-24",
        "bill_id": "HB 1234",
        "bill_number": "1234",
        "substitute_version": "0",
        "engrossed_version": "0",
        "short_legislation_type": {
            "short_legislation_type": "B",
            "long_legislation_type": "Bill",
        },
        "original_agency": "House",
        "active": True,
        "short_description": "Test Bill",
        "long_description": "Test Bill Title",
        "sponsor": "Test Sponsor",
        "introduced_date": "2023-01-01",
        "current_status": {
            "status": "In Committee",
            "action_date": "2023-01-15",
            "history_line": "First reading, referred to Committee.",
            "amendments_exist": False,
            "veto": False,
            "partial_veto": False,
        },
        "legal_title": "AN ACT Relating to test bill",
    }


@pytest.fixture
def mock_wsl_client():
    """
    Mock WSLClient for testing functions that use the client.

    This fixture provides a mock WSLClient with common methods stubbed out.
    """
    with patch("wa_leg_mcp.clients.wsl_client.WSLClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_wsl_search_client():
    """
    Mock WSLSearchClient for testing functions that use the search client.

    This fixture provides a mock WSLSearchClient with common methods stubbed out.
    """
    with patch("wa_leg_mcp.clients.wsl_search_client.WSLSearchClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_datetime(timestamp="2023-01-01T00:00:00"):
    """
    Mock datetime for testing time-dependent functions.

    This fixture provides a mock datetime with a fixed timestamp for consistent testing.

    Args:
        timestamp: ISO format timestamp to use for the mock datetime
    """
    with patch("datetime.datetime") as mock_dt:
        mock_now = MagicMock()
        mock_now.year = int(timestamp.split("-")[0])
        mock_now.isoformat.return_value = timestamp
        mock_dt.now.return_value = mock_now
        yield mock_dt


@pytest.fixture
def parametrized_test_case():
    """
    Factory fixture for creating parametrized test cases.

    This fixture returns a function that helps create standardized test cases
    for parametrized tests.
    """

    def _create_test_case(input_value, expected_output, description=None):
        """
        Create a standardized test case for parametrized tests.

        Args:
            input_value: The input value for the test
            expected_output: The expected output value
            description: Optional description of the test case

        Returns:
            A tuple of (input_value, expected_output, description)
        """
        return (input_value, expected_output, description)

    return _create_test_case
