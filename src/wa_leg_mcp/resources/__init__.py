"""
Washington State Legislature MCP Resources

This module contains all the MCP resource implementations for accessing
Washington State Legislature documents and data via URI templates.
"""

from .bill_resources import (
    BillFormat,
    Chamber,
    get_bill_document_templates,
    get_bill_document_url,
    read_bill_document,
)

__all__ = [
    "get_bill_document_url",
    "get_bill_document_templates",
    "read_bill_document",
    "BillFormat",
    "Chamber",
]
