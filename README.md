# Washington State Legislature MCP Server

A Model Context Protocol (MCP) server that provides AI assistants with access to Washington State Legislature data, enabling civic engagement through conversational interfaces.

## Overview

This MCP server connects AI assistants to the Washington State Legislative Web Services (WSLWS), providing tools for:
- Bill tracking and information retrieval
- Committee meeting schedules and agendas
- Legislator lookup and sponsor information
- Bill status and history tracking
- Legislative document access

## Features

### Core Tools
- `getBillInfo` - Retrieve detailed information about specific bills
- `searchBills` - Search for bills using keywords and optional filtering
- `getBillsByYear` - Retrieve all bills from a specific year with filtering options
- `getCommitteeMeetings` - Get committee meeting schedules and agendas
- `findLegislator` - Find legislators by district or lookup sponsors
- `getBillStatus` - Get current status and history of a bill
- `getBillDocuments` - Retrieve bill document metadata with links
- `getBillContent` - Retrieve the actual content of a bill in AI-friendly format

### MCP Resources
- `bill://xml/{biennium}/{chamber}/{bill_number}` - Access bill documents in structured XML format
- `bill://htm/{biennium}/{chamber}/{bill_number}` - Access bill documents in HTML format
- `bill://pdf/{biennium}/{chamber}/{bill_number}` - Get URLs for bill PDF documents
- `bill://document/{format}/{biennium}/{chamber}/{bill_number}` - Generic format for accessing bill documents


## Installation

### Prerequisites
- Python 3.10+
- pip package manager

### Development Installation
```bash
pip install -e ".[dev]"
```

### Production Installation
```bash
pip install .
```

## Quick Start

### Local Development
```bash
# Test with MCP Inspector
mcp dev src/wa_leg_mcp/server.py

# Run with stdio transport
python src/wa_leg_mcp/server.py
```

### Remote Deployment
For cloud deployment on AWS Lambda, you can use the `mcp-remote` adapter to enable Claude Desktop connectivity:
```json
{
  "mcpServers": {
    "wa-leg": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://your-api-gateway-url/sse"
      ]
    }
  }
}
```

### Basic Configuration
Create a `.env` file:
```env
WSL_API_TIMEOUT=30
WSL_CACHE_TTL=300
LOG_LEVEL=INFO
SERVER_NAME="Washington State Legislature MCP Server"
```

## Repository Structure

```
wa-leg-mcp/
├── src/
│   ├── wa_leg_mcp/
│   │   ├── __init__.py
│   │   ├── server.py           # Main MCP server implementation
│   │   ├── tools/              # Tool implementations
│   │   │   ├── __init__.py
│   │   │   ├── bill_tools.py
│   │   │   ├── committee_tools.py
│   │   │   └── legislator_tools.py
│   │   ├── resources/          # MCP resource implementations
│   │   │   ├── __init__.py
│   │   │   └── bill_resources.py # Bill document resources
│   │   ├── clients/            # API clients
│   │   │   ├── __init__.py
│   │   │   └── wsl_client.py   # WA State Legislature API client
│   │   └── utils/              # Utility functions
│   │       ├── __init__.py
│   │       └── formatters.py
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── test_bill_tools.py
│   ├── test_bill_resources.py  # Tests for bill resources
│   ├── test_committee_tools.py
│   ├── test_legislator_tools.py
│   ├── test_server.py
│   ├── test_utils_formatters.py
│   └── test_wsl_client.py
├── pyproject.toml              # Project configuration and dependencies
├── Makefile                    # Development workflow commands
├── README.md
└── LICENSE
```

## Development

### Setting Up Development Environment

1. Clone the repository:
```bash
git clone https://github.com/awalcutt/wa-leg-mcp.git
cd wa-leg-mcp
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

4. Run tests:
```bash
make test
```

### Adding New Tools

1. Create a new file in `src/wa_leg_mcp/tools/`
2. Implement tool using the MCP decorator:
```python
from mcp.server.fastmcp import Tool

@Tool("toolName", description="Tool description")
def tool_function(param1: str, param2: str = None):
    # Implementation
    return {"result": data}
```

3. Register tool in server.py by adding it to the `get_default_tools()` function
4. Add tests in `tests/`

## Deployment Options

### Local Deployment
- Run directly with Python
- Use with MCP Inspector for development

### Cloud Deployment
- AWS Lambda with API Gateway (supports remote connections via `mcp-remote` adapter)
- Google Cloud Functions
- Azure Functions

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `WSL_API_TIMEOUT` | API request timeout (seconds) | 30 |
| `WSL_CACHE_TTL` | Cache time-to-live (seconds) | 300 |
| `LOG_LEVEL` | Logging level | INFO |
| `SERVER_NAME` | Custom server name | Washington State Legislature MCP Server |

## Usage Examples

### With Claude Desktop
Add to Claude Desktop configuration:
```json
{
  "mcpServers": {
    "wa-leg": {
      "command": "python",
      "args": ["path/to/src/wa_leg_mcp/server.py"],
      "env": {
        "WSL_CACHE_TTL": "600"
      }
    }
  }
}
```

### With Other AI Clients
```python
# Example client integration
from mcp.client import ClientSession
import asyncio

async def connect_to_legislature_mcp():
    async with ClientSession(server_command=["python", "src/wa_leg_mcp/server.py"]) as session:
        # List available tools
        tools = await session.list_tools()
        
        # Call a tool
        result = await session.call_tool("getBillInfo", {
            "bill_number": "HB1234",
            "biennium": "2025-26"
        })
        
        print(result)
        
        # Access a resource
        bill_xml = await session.read_resource(
            "bill://xml/2025-26/House/1234"
        )
        
        print(f"Bill XML content length: {len(bill_xml)}")

asyncio.run(connect_to_legislature_mcp())
```

## API Documentation

### Tools

#### getBillInfo
Retrieves detailed information about a specific bill using the GetLegislation API.

Parameters:
- `bill_number` (string, required): Bill number (e.g., "HB1234", "SB5678")
- `biennium` (string, required): Legislative biennium in format "2025-26"

Returns: Bill details including description, sponsor, status, fiscal notes, and companions

#### searchBills
Searches for bills using keywords and optional filtering via the WSL Search API.

Parameters:
- `query` (string, required): Search query text (e.g., "climate change", "transportation")
- `bienniums` (array, optional): List of bienniums to search (format: "YYYY-YY"), defaults to current
- `agency` (string, optional): Filter by originating agency ("House", "Senate", or "Both")
- `max_results` (integer, optional): Maximum number of total results to return (max 100)

Returns: List of bills matching the search criteria

#### getBillsByYear
Retrieves all bills from a specific year with optional filtering using the GetLegislationByYear API.

Parameters:
- `year` (string, optional): Year in format "YYYY" (e.g., "2025"), defaults to current
- `agency` (string, optional): Filter by originating agency ("House" or "Senate")
- `active_only` (boolean, optional): If True, only return active bills

Returns: List of bills matching the criteria

#### getCommitteeMeetings
Retrieves committee meetings and agendas using the GetCommitteeMeetings API.

Parameters:
- `start_date` (string, required): Start date in YYYY-MM-DD format
- `end_date` (string, required): End date in YYYY-MM-DD format
- `committee` (string, optional): Filter by specific committee

Returns: List of committee meetings with dates, times, locations, and agenda items

#### findLegislator
Finds legislators using the GetSponsors API.

Parameters:
- `biennium` (string, required): Legislative biennium in format "2025-26"
- `chamber` (string, optional): "house" or "senate"

Returns: List of legislators with ID, name, party, and contact information

#### getBillStatus
Gets current status and history using the GetCurrentStatus API.

Parameters:
- `bill_number` (string, required): Bill number (e.g., "HB1234")
- `biennium` (string, required): Legislative biennium in format "2025-26"

Returns: Current status, history, action dates, and status descriptions

#### getBillDocuments
Retrieves bill documents metadata (functionality based on Document service endpoints).

Parameters:
- `bill_number` (string, required): Bill number
- `biennium` (string, required): Legislative biennium in format "2025-26"
- `document_type` (string, optional): "bill", "amendment", "report"

Returns: Document metadata with links to HTML and PDF versions

#### getBillContent
Retrieves the actual content of a bill in an AI-friendly format.

Parameters:
- `bill_number` (integer, required): Bill number as an integer (e.g., 1234 for HB1234)
- `biennium` (string, optional): Legislative biennium in format "2025-26" (defaults to current)
- `chamber` (string, optional): Chamber name - "House" or "Senate" (optional if bill_number is unique across chambers)
- `bill_format` (string, optional): Document format - "xml" (default), "htm", or "pdf"

Returns: For XML and HTM formats: Dict containing the document content and metadata. For PDF format: Dict containing the URL to access the PDF and metadata.

### Resources

#### Bill Document Resources
The MCP server provides direct access to bill documents through URI templates:

##### bill://xml/{biennium}/{chamber}/{bill_number}
Access bill documents in structured XML format (recommended for AI processing).

Parameters:
- `biennium` (string): Legislative biennium in format "YYYY-YY" (e.g., "2025-26")
- `chamber` (string): Chamber name - must be exactly "House" or "Senate"
- `bill_number` (string): Bill number as numeric string (e.g., "1234")

Returns: XML content of the bill document

##### bill://htm/{biennium}/{chamber}/{bill_number}
Access bill documents in HTML format with hyperlinks to referenced laws.

Parameters:
- `biennium` (string): Legislative biennium in format "YYYY-YY"
- `chamber` (string): "House" or "Senate"
- `bill_number` (string): Bill number

Returns: HTML content of the bill document

##### bill://pdf/{biennium}/{chamber}/{bill_number}
Get URLs for bill PDF documents (content not fetched).

Parameters:
- `biennium` (string): Legislative biennium in format "YYYY-YY"
- `chamber` (string): "House" or "Senate"
- `bill_number` (string): Bill number

Returns: Dictionary with URL to access the PDF document

##### bill://document/{format}/{biennium}/{chamber}/{bill_number}
Generic format for accessing bill documents in any supported format.

Parameters:
- `format` (string): Document format - "xml", "htm", or "pdf"
- `biennium` (string): Legislative biennium in format "YYYY-YY"
- `chamber` (string): "House" or "Senate"
- `bill_number` (string): Bill number

Returns: Document content or URL based on format

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
