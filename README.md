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
- Support for one-way, round-trip, and **multi-city flights**
- Support for all cabin classes (Economy, Premium Economy, Business, First)
- Advanced filtering: stops, layover duration (including multi-day stopovers)
- **Intelligent multi-city search** with iterative departure token chaining
- **Selection strategies**: cheapest, fastest, or balanced route optimization
- **Airline exclusions**: Filter out specific carriers (e.g., avoid Chinese/UAE airlines)
- **Time window filtering**: Restrict searches to specific departure time ranges
- Configurable logging levels via MCP_LOG_LEVEL environment variable
- Defensive error handling to prevent MCP crashes
- Modular, maintainable code structure

## MCP Tools

This package provides the following Model Context Protocol tools:

### `search_flights_tool`
Search for one-way or round-trip flights with advanced filtering options.

**Parameters:**
- `origin`: Departure airport code (e.g., ATL, JFK)
- `destination`: Arrival airport code (e.g., LAX, ORD)
- `outbound_date`: Departure date (YYYY-MM-DD)
- `return_date`: Optional return date for round trips (YYYY-MM-DD)
- `travel_class`: Cabin class (1=Economy [default], 2=Premium Economy, 3=Business, 4=First)
- `stops`: Number of stops (0=Any [default], 1=Nonstop only, 2=1 stop or fewer, 3=2 stops or fewer)
- `layover_duration`: Layover duration range in minutes as "min,max"
  - Example: `"90,330"` for 1.5-5.5 hours
  - Example: `"1440,10080"` for 1-7 days (great for extended stopovers!)

### `search_multi_city_flights_tool`
Search for complex multi-city itineraries using **iterative leg-by-leg search** with intelligent flight selection.

This tool uses Google Flights' progressive selection model: it searches the first leg, automatically selects the best option based on your strategy, then chains to the next leg using departure tokens. This ensures you get complete, bookable multi-city itineraries.

**Parameters:**
- `flights`: JSON string of flight segments. Each segment must have `departure_id`, `arrival_id`, and `date`.
  - Example: `'[{"departure_id":"SYD","arrival_id":"SIN","date":"2025-12-01"},{"departure_id":"SIN","arrival_id":"LHR","date":"2025-12-05"}]'`
  - This searches SYD→SIN on Dec 1, then SIN→LHR on Dec 5 (4-day stopover in Singapore)
- `travel_class`: Cabin class for all segments (1=Economy [default], 2=Premium Economy, 3=Business, 4=First)
- `stops`: Number of stops per segment (0=Any [default], 1=Nonstop only, 2=1 stop or fewer, 3=2 stops or fewer)
- `layover_duration`: Layover duration range in minutes as "min,max" (e.g., "1440,10080" for 1-7 days)
- `exclude_airlines`: Comma-separated airline codes to exclude (e.g., "CA,MU,EY,EK" to avoid Chinese/UAE carriers)
- `outbound_times`: Departure time range as "start,end" in 24h format (e.g., "09,23" for 9am-11pm flights only)
- `selection_strategy`: How to choose flights - "cheapest" [default], "fastest", or "balanced"

**How It Works:**
1. Searches leg 1 and automatically selects the best option (cheapest/fastest/balanced)
2. Uses that flight's departure token to search leg 2 with compatible connections
3. Repeats for all legs, building a complete itinerary
4. Returns all selected legs with total price, duration, and API calls used

**Use Cases:**
- Extended stopovers in multiple cities (e.g., Sydney → Singapore [5 days] → London)
- Complex business trips with multiple destinations
- Avoiding specific airlines or inconvenient departure times
- Finding the fastest or most balanced multi-city routes

### `server_status`
Check if the MCP server is running.

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
