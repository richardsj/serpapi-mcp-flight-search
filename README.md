# MCP Flight Search
<a href="https://glama.ai/mcp/servers/@arjunprabhulal/mcp-flight-search">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@arjunprabhulal/mcp-flight-search/badge" />
</a>

A flight search service built with Model Context Protocol (MCP). This service demonstrates how to implement MCP tools for flight search capabilities.

## What is Model Context Protocol?

The Model Context Protocol (MCP) is a standard developed by Anthropic that enables AI models to use tools by defining a structured format for tool descriptions, calls, and responses. This project implements MCP tools that can be used by Claude and other MCP-compatible models.

## Installation

```bash
# Install from PyPI
pip install mcp-flight-search

# Or install from the project directory (development mode)
pip install -e .
```

## Usage

Start the MCP server:

```bash
# Using the command-line entry point
mcp-flight-search --connection_type http

# Or run directly
python main.py --connection_type http
```

You can also specify a custom port:
```bash
python main.py --connection_type http --port 5000
```

## Environment Variables

Set the SerpAPI key as an environment variable:
```bash
export SERP_API_KEY="your-api-key-here"
```

## Features

- MCP-compliant tools for flight search functionality
- Integration with SerpAPI Google Flights
- Support for one-way and round-trip flights
- Support for all cabin classes (Economy, Premium Economy, Business, First)
- Configurable logging levels via MCP_LOG_LEVEL environment variable
- Rich logging with structured output
- Modular, maintainable code structure

## MCP Tools

This package provides the following Model Context Protocol tools:

- `search_flights_tool`: Search for flights between airports with parameters:
  - `origin`: Departure airport code (e.g., ATL, JFK)
  - `destination`: Arrival airport code (e.g., LAX, ORD)
  - `outbound_date`: Departure date (YYYY-MM-DD)
  - `return_date`: Optional return date for round trips (YYYY-MM-DD)
  - `travel_class`: Optional cabin class (1=Economy [default], 2=Premium Economy, 3=Business, 4=First)

- `server_status`: Check if the MCP server is running

## Project Structure

```
mcp-flight-search/
├── mcp_flight_search/
│   ├── __init__.py              # Package initialization and exports
│   ├── config.py                # Configuration variables (API keys)
│   ├── models/
│   │   ├── __init__.py          # Models package init
│   │   └── schemas.py           # Pydantic models (FlightInfo)
│   ├── services/
│   │   ├── __init__.py          # Services package init
│   │   ├── search_service.py    # Main flight search logic
│   │   └── serpapi_client.py    # SerpAPI client wrapper
│   ├── utils/
│   │   ├── __init__.py          # Utils package init
│   │   └── logging.py           # Logging configuration
│   └── server.py                # MCP server setup and tool registration
├── main.py                      # Main entry point
├── pyproject.toml               # Python packaging configuration
├── LICENSE                      # MIT License
└── README.md                    # Project documentation
```

## Author

For more articles on AI/ML and Generative AI, follow me on Medium: https://medium.com/@arjun-prabhulal

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
