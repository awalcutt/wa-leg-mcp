"""
Washington State Legislature MCP Server

A Model Context Protocol server that provides AI assistants with access to
Washington State Legislature data, enabling civic engagement through
conversational interfaces.
"""

__version__ = "0.1.0"
__author__ = "Alex Adacutt"

# Package-level imports
from .server import create_server, main

__all__ = ["create_server", "main"]
