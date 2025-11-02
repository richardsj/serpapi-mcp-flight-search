"""
Model Context Protocol (MCP) Flight Search Server implementation.

This module sets up an MCP-compliant server and registers flight search tools
that follow Anthropic's Model Context Protocol specification. These tools can be
accessed by Claude and other MCP-compatible AI models.
"""
from mcp.server.fastmcp import FastMCP
import argparse
from mcp_flight_search.utils.logging import logger
from mcp_flight_search.services.search_service import search_flights
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
    async def search_flights_tool(origin: str, destination: str, outbound_date: str, return_date: str = None, travel_class: int = 1):
        """
        Search for flights using SerpAPI Google Flights.

        This MCP tool allows AI models to search for flight information by specifying
        departure and arrival airports and travel dates.

        Args:
            origin: Departure airport code (e.g., ATL, JFK)
            destination: Arrival airport code (e.g., LAX, ORD)
            outbound_date: Departure date (YYYY-MM-DD)
            return_date: Return date for round trips (YYYY-MM-DD)
            travel_class: Cabin class (1=Economy, 2=Premium Economy, 3=Business, 4=First, default=1)

        Returns:
            A list of available flights with details
        """
        return await search_flights(origin, destination, outbound_date, return_date, travel_class)

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