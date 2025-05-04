"""
Washington State Legislature MCP Server

Main server implementation that provides tools for accessing Washington State
Legislature data through the Model Context Protocol.
"""

import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from .tools import (
    find_legislator,
    get_bill_documents,
    get_bill_info,
    get_bill_status,
    get_committee_meetings,
    search_bills,
)

# Constants
SERVER_NAME = "Washington State Legislature MCP Server"
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_API_TIMEOUT = 30
DEFAULT_CACHE_TTL = 300

# Load environment variables
load_dotenv()

# Initialize logger
logger = logging.getLogger(__name__)


@dataclass
class ServerConfig:
    """Configuration for the MCP server."""

    api_timeout: int = DEFAULT_API_TIMEOUT
    cache_ttl: int = DEFAULT_CACHE_TTL
    log_level: str = DEFAULT_LOG_LEVEL
    server_name: str = SERVER_NAME

    @classmethod
    def from_env(cls) -> "ServerConfig":
        """Create configuration from environment variables."""
        return cls(
            api_timeout=int(os.getenv("WSL_API_TIMEOUT", str(DEFAULT_API_TIMEOUT))),
            cache_ttl=int(os.getenv("WSL_CACHE_TTL", str(DEFAULT_CACHE_TTL))),
            log_level=os.getenv("LOG_LEVEL", DEFAULT_LOG_LEVEL),
            server_name=os.getenv("SERVER_NAME", SERVER_NAME),
        )


def configure_logging(level: str = DEFAULT_LOG_LEVEL) -> None:
    """Configure logging with the specified level."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def ping() -> Dict[str, Any]:
    """Simple health check to verify the server is running."""
    return {
        "status": "ok",
        "service": SERVER_NAME,
        "timestamp": datetime.now().isoformat(),
    }


def get_default_tools() -> List[Callable]:
    """Get the default set of tools for the server."""
    return [
        get_bill_info,
        search_bills,
        get_committee_meetings,
        find_legislator,
        get_bill_status,
        get_bill_documents,
        ping,
    ]


def create_server(
    config: Optional[ServerConfig] = None, tools: Optional[List[Callable]] = None
) -> FastMCP:
    """
    Create and configure the MCP server instance.

    Args:
        config: Server configuration. If None, uses default configuration.
        tools: List of tools to add to the server. If None, uses default tools.

    Returns:
        Configured FastMCP server instance.
    """
    if config is None:
        config = ServerConfig()

    if tools is None:
        tools = get_default_tools()

    # Create MCP server instance
    mcp = FastMCP(config.server_name)

    # Add all tools to the server
    for tool in tools:
        mcp.add_tool(tool)

    return mcp


class ServerError(Exception):
    """Base exception for server errors."""

    pass


class ServerStartupError(ServerError):
    """Exception raised when the server fails to start."""

    pass


def main() -> None:
    """Main entry point for the MCP server."""
    try:
        # Load configuration
        config = ServerConfig.from_env()

        # Configure logging
        configure_logging(config.log_level)

        logger.info(f"Starting {config.server_name}...")
        logger.debug(f"Configuration: {config}")

        # Create and configure server
        server = create_server(config)

        # Run with stdio transport
        server.run()

    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server failed to start: {str(e)}")
        logger.exception("Detailed error information:")
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
