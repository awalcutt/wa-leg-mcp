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
- `searchBills` - Search for bills by status, date range, or type
- `getCommitteeMeetings` - Get committee meeting schedules and agendas
- `findLegislator` - Find legislators by district or lookup sponsors
- `getBillStatus` - Get current status and history of a bill
- `getBillDocuments` - Retrieve bill text and amendments



## Installation

### Prerequisites
- Python 3.9+
- pip or uv package manager

### Using pip
```bash
pip install -r requirements.txt
```

### Using uv (recommended)
```bash
uv pip install -r requirements.txt
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
│   │   ├── clients/            # API clients
│   │   │   ├── __init__.py
│   │   │   ├── wsl_client.py   # WA State Legislature API client
│   │   │   └── geocoding_client.py
│   │   ├── cache/              # Caching layer
│   │   │   ├── __init__.py
│   │   │   └── cache_manager.py
│   │   └── utils/              # Utility functions
│   │       ├── __init__.py
│   │       └── formatters.py
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_tools/
│   └── test_clients/
├── docker/                     # Docker configurations
│   ├── Dockerfile
│   └── docker-compose.yml
├── requirements.txt
├── pyproject.toml
├── README.md
├── LICENSE
└── .env.example
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
pip install -r requirements-dev.txt
```

4. Run tests:
```bash
pytest
```

### Adding New Tools

1. Create a new file in `src/wa_leg_mcp/tools/`
2. Implement tool using the MCP decorator:
```python
from mcp.server import Tool

@Tool("toolName", description="Tool description")
def tool_function(param1: str, param2: str = None):
    # Implementation
    return {"result": data}
```

3. Register tool in server.py
4. Add tests in `tests/test_tools/`

## Deployment Options

### Local Deployment
- Run directly with Python
- Use with MCP Inspector for development
- Docker container for isolated environment

### Cloud Deployment
- AWS Lambda with API Gateway (supports remote connections via `mcp-remote` adapter)
- Google Cloud Functions
- Azure Functions
- Docker-based deployments (ECS, Cloud Run, etc.)

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `WSL_API_TIMEOUT` | API request timeout (seconds) | 30 |
| `WSL_CACHE_TTL` | Cache time-to-live (seconds) | 300 |
| `LOG_LEVEL` | Logging level | INFO |

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
Searches for bills based on various criteria using the GetLegislationByYear and related APIs.

Parameters:
- `biennium` (string, required): Legislative biennium in format "2025-26"
- `status` (string, optional): Filter by status ("passed_house", "passed_senate", "signed")
- `introduced_since` (string, optional): Date in YYYY-MM-DD format

Returns: List of bills matching criteria

#### getCommitteeMeetings
Retrieves committee meetings and agendas using the GetCommitteeMeetings API.

Parameters:
- `start_date` (string, required): Start date in YYYY-MM-DD format
- `end_date` (string, required): End date in YYYY-MM-DD format
- `committee` (string, optional): Filter by specific committee

Returns: List of committee meetings with dates, times, locations, and agenda items

#### findLegislator
Finds legislators using the GetSponsors API (note: district lookup requires additional geocoding).

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
Retrieves bill documents (functionality based on Document service endpoints).

Parameters:
- `bill_number` (string, required): Bill number
- `biennium` (string, required): Legislative biennium in format "2025-26"
- `document_type` (string, optional): "bill", "amendment", "report"

Returns: Document metadata with links to HTML and PDF versions

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
