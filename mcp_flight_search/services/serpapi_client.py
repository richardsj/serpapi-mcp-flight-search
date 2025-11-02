"""
SerpAPI client for flight searches.
"""
import asyncio
import json
from typing import Dict, Any
from serpapi import GoogleSearch
from mcp_flight_search.utils.logging import logger
from mcp_flight_search.config import SERP_API_KEY

async def run_search(params: Dict[str, Any]):
    """
    Run SerpAPI search asynchronously.
    
    Args:
        params: Parameters for the SerpAPI search
        
    Returns:
        Search results from SerpAPI
    """
    try:
        logger.debug(f"Sending SerpAPI request with params: {json.dumps(params, indent=2)}")
        result = await asyncio.to_thread(lambda: GoogleSearch(params).get_dict())
        logger.debug(f"SerpAPI response received, keys: {list(result.keys())}")
        return result
    except Exception as e:
        logger.exception(f"SerpAPI search error: {str(e)}")
        return {"error": str(e)}

def prepare_flight_search_params(
    origin: str,
    destination: str,
    outbound_date: str,
    return_date: str = None,
    travel_class: int = 1,
    stops: int = None,
    layover_duration: str = None
) -> Dict[str, Any]:
    """
    Prepare parameters for a flight search.

    Args:
        origin: Departure airport code
        destination: Arrival airport code
        outbound_date: Departure date (YYYY-MM-DD)
        return_date: Return date for round trips (YYYY-MM-DD)
        travel_class: Cabin class (1=Economy, 2=Premium Economy, 3=Business, 4=First)
        stops: Number of stops (0=Any, 1=Nonstop only, 2=1 stop or fewer, 3=2 stops or fewer)
        layover_duration: Layover duration range in minutes as "min,max" (e.g., "90,330" or "1440,10080" for 1-7 days)

    Returns:
        Dictionary of parameters for SerpAPI
    """
    params = {
        "api_key": SERP_API_KEY,
        "engine": "google_flights",
        "hl": "en",
        "gl": "us",
        "departure_id": origin.strip().upper(),
        "arrival_id": destination.strip().upper(),
        "outbound_date": outbound_date,
        "currency": "USD",
        "type": "2",  # One-way trip by default
        "travel_class": travel_class
    }

    # Add return date if provided (making it a round trip)
    if return_date:
        logger.debug("Round trip detected, adding return_date and setting type=1")
        params["return_date"] = return_date
        params["type"] = "1"  # Set to round trip
    else:
        logger.debug("One-way trip detected, type=2")

    # Add optional stops filter
    if stops is not None:
        params["stops"] = stops
        logger.debug(f"Stops filter set to: {stops}")

    # Add optional layover duration filter
    if layover_duration:
        params["layover_duration"] = layover_duration
        logger.debug(f"Layover duration filter set to: {layover_duration}")

    return params


def prepare_multi_city_params(
    flights: list,
    travel_class: int = 1,
    stops: int = None,
    layover_duration: str = None,
    exclude_airlines: str = None,
    outbound_times: str = None,
    sort_by: int = 2,  # Default to price sort
    departure_token: str = None
) -> Dict[str, Any]:
    """
    Prepare parameters for a multi-city flight search.

    Args:
        flights: List of flight segments, each with departure_id, arrival_id, date
                Example: [{"departure_id": "SYD", "arrival_id": "SIN", "date": "2025-12-01"}]
        travel_class: Cabin class (1=Economy, 2=Premium Economy, 3=Business, 4=First)
        stops: Number of stops (0=Any, 1=Nonstop only, 2=1 stop or fewer, 3=2 stops or fewer)
        layover_duration: Layover duration range in minutes as "min,max"
        exclude_airlines: Comma-separated airline codes to exclude (e.g., "CA,MU,EY,EK")
        outbound_times: Departure time range as "start,end" in 24h format (e.g., "09,23" for 9am-11pm)
        sort_by: Sort order (1=Top flights, 2=Price, 3=Departure time, 4=Arrival time, 5=Duration, 6=Emissions)
        departure_token: Token from previous leg to chain multi-city searches

    Returns:
        Dictionary of parameters for SerpAPI
    """
    params = {
        "api_key": SERP_API_KEY,
        "engine": "google_flights",
        "hl": "en",
        "gl": "us",
        "type": "3",  # Multi-city
        "currency": "USD",
        "travel_class": travel_class,
        "multi_city_json": json.dumps(flights),
        "sort_by": sort_by
    }

    if departure_token:
        params["departure_token"] = departure_token
        logger.debug(f"Using departure_token for chained search")

    if stops is not None:
        params["stops"] = stops
        logger.debug(f"Multi-city stops filter: {stops}")

    if layover_duration:
        params["layover_duration"] = layover_duration
        logger.debug(f"Multi-city layover duration: {layover_duration}")

    if exclude_airlines:
        params["exclude_airlines"] = exclude_airlines
        logger.debug(f"Excluding airlines: {exclude_airlines}")

    if outbound_times:
        params["outbound_times"] = outbound_times
        logger.debug(f"Departure time filter: {outbound_times}")

    logger.debug(f"Multi-city search with {len(flights)} segments")

    return params 