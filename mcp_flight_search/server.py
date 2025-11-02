"""
Model Context Protocol (MCP) Flight Search Server implementation.

This module sets up an MCP-compliant server and registers flight search tools
that follow Anthropic's Model Context Protocol specification. These tools can be
accessed by Claude and other MCP-compatible AI models.
"""
from mcp.server.fastmcp import FastMCP
import argparse
from mcp_flight_search.utils.logging import logger
from mcp_flight_search.services.search_service import search_flights, search_multi_city_flights
from mcp_flight_search.config import DEFAULT_PORT, DEFAULT_CONNECTION_TYPE

def create_mcp_server(port=DEFAULT_PORT):
    """
    Create and configure the Model Context Protocol server.
    
    Args:
        port: Port number to run the server on
        
    Returns:
        Configured MCP server instance
    """
    mcp = FastMCP("FlightSearchService", port=port)
    
    # Register MCP-compliant tools
    register_tools(mcp)
    
    return mcp

def register_tools(mcp):
    """
    Register all tools with the MCP server following the Model Context Protocol specification.
    
    Each tool is decorated with @mcp.tool() to make it available via the MCP interface.
    
    Args:
        mcp: The MCP server instance
    """
    @mcp.tool()
    async def search_flights_tool(
        origin: str,
        destination: str,
        outbound_date: str,
        return_date: str = None,
        travel_class: int = 1,
        stops: int = None,
        layover_duration: str = None
    ):
        """
        Search for one-way or round-trip flights using SerpAPI Google Flights.

        This MCP tool allows AI models to search for flight information by specifying
        departure and arrival airports, travel dates, and optional filters.

        Args:
            origin: Departure airport code (e.g., ATL, JFK)
            destination: Arrival airport code (e.g., LAX, ORD)
            outbound_date: Departure date (YYYY-MM-DD)
            return_date: Optional return date for round trips (YYYY-MM-DD)
            travel_class: Cabin class (1=Economy [default], 2=Premium Economy, 3=Business, 4=First)
            stops: Number of stops (0=Any [default], 1=Nonstop only, 2=1 stop or fewer, 3=2 stops or fewer)
            layover_duration: Layover duration range in minutes as "min,max" (e.g., "90,330" for 1.5-5.5 hours, "1440,10080" for 1-7 days)

        Returns:
            A list of available flights with details
        """
        return await search_flights(origin, destination, outbound_date, return_date, travel_class, stops, layover_duration)

    @mcp.tool()
    async def search_multi_city_flights_tool(
        flights: str,
        travel_class: int = 1,
        stops: int = None,
        layover_duration: str = None,
        exclude_airlines: str = None,
        outbound_times: str = None,
        selection_strategy: str = "cheapest"
    ):
        """
        Search for multi-city flights using iterative leg-by-leg search with intelligent selection.

        This tool searches each leg sequentially, automatically selecting the best option based on your
        strategy, then chaining to the next leg. Returns complete multi-city itineraries.

        Args:
            flights: JSON string of flight segments. Each segment must have departure_id, arrival_id, and date.
                    Example: '[{"departure_id":"SYD","arrival_id":"SIN","date":"2025-12-01"},{"departure_id":"SIN","arrival_id":"LHR","date":"2025-12-05"}]'
            travel_class: Cabin class (1=Economy [default], 2=Premium Economy, 3=Business, 4=First)
            stops: Number of stops per segment (0=Any [default], 1=Nonstop only, 2=1 stop or fewer, 3=2 stops or fewer)
            layover_duration: Layover duration range in minutes as "min,max" (e.g., "1440,10080" for 1-7 days)
            exclude_airlines: Comma-separated airline codes to exclude (e.g., "CA,MU,EY,EK" to avoid Chinese/UAE carriers)
            outbound_times: Departure time range as "start,end" in 24h format (e.g., "09,23" for 9am-11pm flights only)
            selection_strategy: How to choose flights ("cheapest" [default], "fastest", "balanced")

        Returns:
            Dict with 'legs' (selected flight for each leg), 'total_price', 'total_duration_minutes', 'api_calls_used', or 'error'
        """
        return await search_multi_city_flights(flights, travel_class, stops, layover_duration, exclude_airlines, outbound_times, selection_strategy)

    @mcp.tool()
    def server_status():
        """
        Check if the Model Context Protocol server is running.
        
        This MCP tool provides a simple way to verify the server is operational.
        
        Returns:
            A status message indicating the server is online
        """
        return {"status": "online", "message": "MCP Flight Search server is running"}
    
    logger.debug("Model Context Protocol tools registered")

def main():
    """
    Main entry point for the Model Context Protocol Flight Search Server.
    """
    # Initialize argument parser
    parser = argparse.ArgumentParser(description="Model Context Protocol Flight Search Service")
    parser.add_argument("--connection_type", type=str, default=DEFAULT_CONNECTION_TYPE, 
                        choices=["http", "stdio"], help="Connection type (http or stdio)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, 
                        help=f"Port to run the server on (default: {DEFAULT_PORT})")
    args = parser.parse_args()
    
    # Initialize MCP server
    mcp = create_mcp_server(port=args.port)
    
    # Determine server type
    server_type = "sse" if args.connection_type == "http" else "stdio"
    
    # Start the server
    logger.info(f"🚀 Starting Model Context Protocol Flight Search Service on port {args.port} with {args.connection_type} connection")
    mcp.run(server_type)

if __name__ == "__main__":
    main() 