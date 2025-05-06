"""
Washington State Legislature MCP Server

A Model Context Protocol server that provides AI assistants with access to
Washington State Legislature data, enabling civic engagement through
conversational interfaces.
"""

from .__version__ import __version__
from .server import create_server, main

__all__ = ["create_server", "main", "__version__"]
