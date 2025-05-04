"""
Unit tests for the Washington State Legislature MCP Server organized by functionality
"""

import importlib
import logging
import os
import sys
from contextlib import contextmanager
from unittest.mock import MagicMock, call, patch

import pytest

# Constants
MOCK_TIMESTAMP = "2024-01-01T00:00:00"
SERVER_NAME = "Washington State Legislature MCP Server"
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_TIMEOUT = 30
DEFAULT_CACHE_TTL = 300
CUSTOM_TIMEOUT = 60
CUSTOM_CACHE_TTL = 600


class MockTool:
    """Mock implementation of MCP Tool decorator"""

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, func):
        func._tool_name = self.args[0] if self.args else None
        func._tool_description = self.kwargs.get("description", "")
        return func


class MockFastMCP:
    """Mock implementation of FastMCP server"""

    def __init__(self, name):
        self.name = name
        self.tools = []

    def add_tool(self, tool):
        self.tools.append(tool)

    def run(self):
        pass


class TestBase:
    """Base class for test cases with common functionality"""

    @contextmanager
    def patch_datetime(self, timestamp=MOCK_TIMESTAMP):
        """Context manager for mocking datetime"""
        with patch("wa_leg_mcp.server.datetime") as mock_datetime:
            mock_datetime.now.return_value.isoformat.return_value = timestamp
            yield mock_datetime

    @contextmanager
    def patch_environment(self, **env_vars):
        """Context manager for mocking environment variables"""
        with patch.dict(os.environ, env_vars, clear=True):
            yield

    def reload_module(self, module_name="wa_leg_mcp.server"):
        """Reload a module to test import-time behavior"""
        module = importlib.import_module(module_name)
        importlib.reload(module)
        return module


def setup_mcp_mocks():
    """Set up MCP module mocks"""
    mock_mcp = MagicMock()
    mock_server = MagicMock()
    mock_server.FastMCP = MockFastMCP
    mock_server.Tool = MockTool

    sys.modules["mcp"] = mock_mcp
    sys.modules["mcp.server"] = mock_server
    sys.modules["wa_leg_mcp.tools"] = MagicMock()

    return mock_mcp


# Setup mocks before importing the module under test to ensure module-level code uses our mocks
mock_mcp = setup_mcp_mocks()

# Import the module under test
from wa_leg_mcp.server import (
    ServerConfig,
    configure_logging,
    create_server,
    logger,
    main,
    ping,
)


@pytest.fixture
def mock_environment():
    """Set up mock environment variables"""
    env_vars = {
        "LOG_LEVEL": "DEBUG",
        "WSL_API_TIMEOUT": str(CUSTOM_TIMEOUT),
        "WSL_CACHE_TTL": str(CUSTOM_CACHE_TTL),
    }
    with patch.dict(os.environ, env_vars):
        yield


@pytest.fixture
def mock_tools():
    """Mock all tool functions"""
    tools = [
        "get_bill_info",
        "search_bills",
        "get_bills_by_year",
        "get_bill_status",
        "get_bill_documents",
        "get_bill_content",
        "get_committee_meetings",
        "find_legislator",
    ]

    mocks = {}
    patches = []

    for tool in tools:
        patcher = patch(f"wa_leg_mcp.server.{tool}")
        mock = patcher.start()
        patches.append(patcher)
        mocks[tool] = mock

    yield mocks

    for patcher in patches:
        patcher.stop()


class TestPingTool(TestBase):
    """Test cases for the ping health check tool"""

    def test_ping_returns_correct_structure(self):
        """Test that ping returns the expected data structure"""
        with self.patch_datetime(MOCK_TIMESTAMP):
            result = ping()

            assert result["status"] == "ok"
            assert result["service"] == SERVER_NAME
            assert result["timestamp"] == MOCK_TIMESTAMP

    def test_ping_calls_datetime_correctly(self):
        """Test that ping calls datetime.now().isoformat()"""
        with self.patch_datetime() as mock_datetime:
            ping()

            mock_datetime.now.assert_called_once()
            mock_datetime.now.return_value.isoformat.assert_called_once()


class TestCreateServer(TestBase):
    """Test cases for the create_server function"""

    def test_create_server_adds_all_tools(self, mock_tools):
        """Test that create_server adds all required tools"""
        with patch("wa_leg_mcp.server.FastMCP") as mock_fastmcp_class:
            mock_server_instance = MagicMock()
            mock_fastmcp_class.return_value = mock_server_instance

            server = create_server()

            # Verify server creation
            mock_fastmcp_class.assert_called_once_with(SERVER_NAME)
            assert server == mock_server_instance

            # Verify all tools were added
            assert mock_server_instance.add_tool.call_count == 9

            # Verify the expected calls were made
            expected_calls = [
                call(mock_tools["get_bill_info"]),
                call(mock_tools["search_bills"]),
                call(mock_tools["get_bills_by_year"]),
                call(mock_tools["get_committee_meetings"]),
                call(mock_tools["find_legislator"]),
                call(mock_tools["get_bill_status"]),
                call(mock_tools["get_bill_documents"]),
                call(mock_tools["get_bill_content"]),
                call(ping),
            ]

            mock_server_instance.add_tool.assert_has_calls(expected_calls, any_order=True)

    def test_create_server_with_custom_config(self):
        """Test create_server with custom configuration"""
        custom_config = ServerConfig(server_name="Custom Server")

        with patch("wa_leg_mcp.server.FastMCP") as mock_fastmcp_class:
            mock_server_instance = MagicMock()
            mock_fastmcp_class.return_value = mock_server_instance

            server = create_server(config=custom_config)

            # Verify server creation with custom name
            mock_fastmcp_class.assert_called_once_with("Custom Server")
            assert server == mock_server_instance


class TestMain(TestBase):
    """Test cases for the main function"""

    @pytest.fixture
    def mock_main_dependencies(self):
        """Mock dependencies for main function tests"""
        with (
            patch("wa_leg_mcp.server.ServerConfig.from_env") as mock_from_env,
            patch("wa_leg_mcp.server.configure_logging") as mock_configure_logging,
            patch("wa_leg_mcp.server.create_server") as mock_create_server,
            patch.object(logger, "info") as mock_log_info,
            patch.object(logger, "debug") as mock_log_debug,
            patch.object(logger, "error") as mock_log_error,
            patch.object(logger, "exception") as mock_log_exception,
            patch("sys.exit") as mock_exit,
        ):

            # Setup default mock returns
            mock_config = ServerConfig()
            mock_from_env.return_value = mock_config

            yield {
                "from_env": mock_from_env,
                "configure_logging": mock_configure_logging,
                "create_server": mock_create_server,
                "log_info": mock_log_info,
                "log_debug": mock_log_debug,
                "log_error": mock_log_error,
                "log_exception": mock_log_exception,
                "exit": mock_exit,
                "config": mock_config,
            }

    def test_main_success(self, mock_main_dependencies):
        """Test successful server startup"""
        mocks = mock_main_dependencies
        mock_server = MagicMock()
        mocks["create_server"].return_value = mock_server

        main()

        # Verify configuration is loaded
        mocks["from_env"].assert_called_once()

        # Verify logging is configured
        mocks["configure_logging"].assert_called_once_with(mocks["config"].log_level)

        # Verify server creation and startup
        mocks["log_info"].assert_called_with(f"Starting {SERVER_NAME}...")
        mocks["create_server"].assert_called_once_with(mocks["config"])

    def test_main_exception_handling(self, mock_main_dependencies):
        """Test exception handling in main function"""
        mocks = mock_main_dependencies
        test_error = "Test error"
        mocks["create_server"].side_effect = Exception(test_error)

        main()

        mocks["log_error"].assert_called_with(f"Server failed to start: {test_error}")
        mocks["log_exception"].assert_called_once_with("Detailed error information:")
        mocks["exit"].assert_called_once_with(1)

    def test_main_keyboard_interrupt(self, mock_main_dependencies):
        """Test graceful shutdown on KeyboardInterrupt"""
        mocks = mock_main_dependencies
        mocks["create_server"].side_effect = KeyboardInterrupt()

        main()

        mocks["log_info"].assert_called_with("Server shutdown requested")
        mocks["exit"].assert_called_once_with(0)


class TestConfiguration(TestBase):
    """Test cases for configuration and environment variables"""

    def test_default_configuration(self):
        """Test default configuration values"""
        config = ServerConfig()
        assert config.api_timeout == DEFAULT_TIMEOUT
        assert config.cache_ttl == DEFAULT_CACHE_TTL
        assert config.log_level == DEFAULT_LOG_LEVEL
        assert config.server_name == SERVER_NAME

    def test_configuration_from_env(self):
        """Test configuration from environment variables"""
        with self.patch_environment(
            WSL_API_TIMEOUT=str(CUSTOM_TIMEOUT),
            WSL_CACHE_TTL=str(CUSTOM_CACHE_TTL),
            LOG_LEVEL="DEBUG",
            SERVER_NAME="Test Server",
        ):
            config = ServerConfig.from_env()
            assert config.api_timeout == CUSTOM_TIMEOUT
            assert config.cache_ttl == CUSTOM_CACHE_TTL
            assert config.log_level == "DEBUG"
            assert config.server_name == "Test Server"


class TestLogging(TestBase):
    """Test cases for logging configuration"""

    def test_configure_logging_default(self):
        """Test logging configuration with default level"""
        with patch("logging.basicConfig") as mock_basic_config:
            configure_logging()

            mock_basic_config.assert_called_once()
            call_args = mock_basic_config.call_args

            config = call_args[1]
            assert config["level"] == logging.INFO
            assert "format" in config

            # Verify format components
            format_string = config["format"]
            expected_components = [
                "%(asctime)s",
                "%(name)s",
                "%(levelname)s",
                "%(message)s",
            ]
            for component in expected_components:
                assert component in format_string

    def test_configure_logging_custom_level(self):
        """Test logging configuration with custom level"""
        with patch("logging.basicConfig") as mock_basic_config:
            configure_logging("DEBUG")

            mock_basic_config.assert_called_once()
            call_args = mock_basic_config.call_args

            config = call_args[1]
            assert config["level"] == logging.DEBUG

    def test_configure_logging_case_insensitive(self):
        """Test logging configuration handles case insensitivity"""
        with patch("logging.basicConfig") as mock_basic_config:
            configure_logging("debug")

            mock_basic_config.assert_called_once()
            call_args = mock_basic_config.call_args

            config = call_args[1]
            assert config["level"] == logging.DEBUG


class TestMainEntryPoint(TestBase):
    """Test cases for the main entry point"""

    def test_main_can_be_called(self):
        """Test that main function can be called without errors"""
        with (
            patch("wa_leg_mcp.server.ServerConfig.from_env"),
            patch("wa_leg_mcp.server.configure_logging"),
            patch("wa_leg_mcp.server.create_server"),
        ):
            main()
            # If we get here without exceptions (like ImportError or AttributeError from missing dependencies), the test passes


if __name__ == "__main__":
    pytest.main([__file__])
