"""
Flight search service implementation.
"""
from typing import List, Dict, Optional, Any
from mcp_flight_search.utils.logging import logger
from mcp_flight_search.services.serpapi_client import run_search, prepare_flight_search_params, prepare_multi_city_params

async def search_flights(
    origin: str,
    destination: str,
    outbound_date: str,
    return_date: Optional[str] = None,
    travel_class: int = 1,
    stops: Optional[int] = None,
    layover_duration: Optional[str] = None
) -> List[Dict[str, str]]:
    """
    Search for flights using SerpAPI Google Flights.

    Args:
        origin: Departure airport code (e.g., ATL, JFK)
        destination: Arrival airport code (e.g., LAX, ORD)
        outbound_date: Departure date (YYYY-MM-DD)
        return_date: Return date for round trips (YYYY-MM-DD)
        travel_class: Cabin class (1=Economy, 2=Premium Economy, 3=Business, 4=First)
        stops: Number of stops (0=Any, 1=Nonstop only, 2=1 stop or fewer, 3=2 stops or fewer)
        layover_duration: Layover duration range "min,max" in minutes (e.g., "1440,10080" for 1-7 days)

    Returns:
        A list of available flights with details, or error dict
    """
    try:
        logger.info(f"Searching flights: {origin} to {destination}, dates: {outbound_date} - {return_date}, class: {travel_class}, stops: {stops}, layover: {layover_duration}")
        logger.debug(f"Function called with: origin={origin}, destination={destination}, outbound_date={outbound_date}, return_date={return_date}, travel_class={travel_class}, stops={stops}, layover_duration={layover_duration}")

        # Prepare search parameters
        params = prepare_flight_search_params(origin, destination, outbound_date, return_date, travel_class, stops, layover_duration)

        # Execute search
        logger.debug("Executing SerpAPI search...")
        search_results = await run_search(params)

        # Check for errors
        if "error" in search_results:
            logger.error(f"Flight search error: {search_results['error']}")
            return {"error": search_results["error"]}

        # Process flight results
        return format_flight_results(search_results)

    except Exception as e:
        logger.exception(f"Unexpected error in search_flights: {str(e)}")
        return {"error": f"Flight search failed: {str(e)}"}

def format_flight_results(search_results: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Format raw flight search results into a standardized format.

    Args:
        search_results: Raw search results from SerpAPI

    Returns:
        Formatted list of flight information
    """
    try:
        # Check both best_flights and other_flights (filters may push results to other_flights)
        best_flights = search_results.get("best_flights", [])
        if not best_flights:
            best_flights = search_results.get("other_flights", [])

        logger.debug(f"Search complete. Found {len(best_flights)} flights")

        if not best_flights:
            logger.warning("No flights found in search results")
            return []

        # Format flight data
        formatted_flights = []
        for i, flight in enumerate(best_flights):
            try:
                logger.debug(f"Processing flight {i+1} of {len(best_flights)}")
                if not flight.get("flights") or len(flight["flights"]) == 0:
                    logger.debug(f"Skipping flight {i+1} as it has no flight segments")
                    continue

                # Get first leg details
                first_leg = flight["flights"][0]
                logger.debug(f"Flight {i+1} has airline: {first_leg.get('airline', 'Unknown')}, price: {flight.get('price', 'N/A')}")

                # Process departure airport
                dep_airport = first_leg.get("departure_airport", {})
                if isinstance(dep_airport, dict):
                    dep_name = dep_airport.get("name", "Unknown")
                    dep_id = dep_airport.get("id", "???")
                    dep_time = dep_airport.get("time", "N/A")
                    departure_info = f"{dep_name} ({dep_id}) at {dep_time}"
                else:
                    departure_info = first_leg.get("departure_time", "Unknown")

                # Process arrival airport
                arr_airport = first_leg.get("arrival_airport", {})
                if isinstance(arr_airport, dict):
                    arr_name = arr_airport.get("name", "Unknown")
                    arr_id = arr_airport.get("id", "???")
                    arr_time = arr_airport.get("time", "N/A")
                    arrival_info = f"{arr_name} ({arr_id}) at {arr_time}"
                else:
                    arrival_info = first_leg.get("arrival_time", "Unknown")

                # Add formatted flight to results
                formatted_flights.append({
                    "airline": first_leg.get("airline", "Unknown Airline"),
                    "price": str(flight.get("price", "N/A")),
                    "duration": f"{flight.get('total_duration', 'N/A')} min",
                    "stops": "Nonstop" if len(flight["flights"]) == 1 else f"{len(flight['flights']) - 1} stop(s)",
                    "departure": departure_info,
                    "arrival": arrival_info,
                    "travel_class": first_leg.get("travel_class", "Economy"),
                    "airline_logo": first_leg.get("airline_logo", "")
                })
            except Exception as e:
                logger.warning(f"Skipping malformed flight {i+1}: {str(e)}")
                continue

        logger.info(f"Returning {len(formatted_flights)} formatted flights")
        return formatted_flights

    except Exception as e:
        logger.exception(f"Error formatting flight results: {str(e)}")
        return []


async def search_multi_city_flights(
    flights: str,
    travel_class: int = 1,
    stops: Optional[int] = None,
    layover_duration: Optional[str] = None,
    exclude_airlines: Optional[str] = None,
    outbound_times: Optional[str] = None,
    selection_strategy: str = "cheapest"
) -> Dict[str, Any]:
    """
    Search for multi-city flights using iterative leg-by-leg search with departure tokens.

    This implements Google Flights' progressive selection model: search first leg, select best option,
    use its departure_token to search next leg, repeat. Returns complete itineraries.

    TODO: Make this interactive instead of one-shot automatic selection. Current limitation is that
    we automatically pick the "best" option per leg, which may not be globally optimal. Should return
    options at each stage and let the LLM/user choose interactively to be smarter about the overall
    itinerary (e.g., spending more on leg 1 might unlock cheaper options on leg 2).

    Args:
        flights: JSON string of flight segments, each with departure_id, arrival_id, date
                Example: '[{"departure_id":"SYD","arrival_id":"SIN","date":"2025-12-01"},{"departure_id":"SIN","arrival_id":"LHR","date":"2025-12-05"}]'
        travel_class: Cabin class (1=Economy, 2=Premium Economy, 3=Business, 4=First)
        stops: Number of stops (0=Any, 1=Nonstop only, 2=1 stop or fewer, 3=2 stops or fewer)
        layover_duration: Layover duration range "min,max" in minutes (e.g., "1440,10080" for 1-7 days)
        exclude_airlines: Comma-separated airline codes to exclude (e.g., "CA,MU,EY,EK" for Chinese/UAE airlines)
        outbound_times: Departure time range "start,end" in 24h format (e.g., "09,23" for 9am-11pm)
        selection_strategy: How to choose from options ("cheapest", "fastest", "balanced")

    Returns:
        Dict with 'legs' (array of selected flights per leg), 'total_price', 'total_duration', or 'error'
    """
    try:
        import json

        # Parse the flights JSON string
        flights_list = json.loads(flights)
        num_legs = len(flights_list)

        logger.info(f"Starting iterative multi-city search: {num_legs} legs, strategy: {selection_strategy}")
        logger.debug(f"Segments: {flights_list}")

        selected_legs = []
        total_price = 0
        total_duration = 0
        current_token = None
        api_calls = 0
        MAX_API_CALLS = 10  # Safety limit

        # Iterate through each leg
        for leg_index, leg_info in enumerate(flights_list):
            if api_calls >= MAX_API_CALLS:
                return {"error": f"Safety limit reached: {MAX_API_CALLS} API calls"}

            logger.info(f"Searching leg {leg_index + 1}/{num_legs}: {leg_info['departure_id']} → {leg_info['arrival_id']}")

            # Prepare search for this leg
            params = prepare_multi_city_params(
                flights_list,
                travel_class=travel_class,
                stops=stops,
                layover_duration=layover_duration,
                exclude_airlines=exclude_airlines,
                outbound_times=outbound_times,
                departure_token=current_token
            )

            # Execute search
            search_results = await run_search(params)
            api_calls += 1

            # Check for errors
            if "error" in search_results:
                return {"error": f"Leg {leg_index + 1} search failed: {search_results['error']}"}

            # Get available flights for this leg (check both best_flights and other_flights)
            available_flights = search_results.get("best_flights", [])
            if not available_flights:
                available_flights = search_results.get("other_flights", [])

            if not available_flights:
                return {"error": f"No flights found for leg {leg_index + 1} ({leg_info['departure_id']}→{leg_info['arrival_id']})"}

            logger.debug(f"Leg {leg_index + 1}: found {len(available_flights)} options")

            # Select best option based on strategy
            selected_flight = _select_flight_by_strategy(available_flights, selection_strategy)

            if not selected_flight:
                return {"error": f"Could not select flight for leg {leg_index + 1}"}

            # Extract key info from selected flight
            leg_data = _extract_leg_data(selected_flight, leg_index + 1)
            selected_legs.append(leg_data)

            # Accumulate totals
            if selected_flight.get("price") and isinstance(selected_flight["price"], (int, float)):
                total_price += selected_flight["price"]
            total_duration += selected_flight.get("total_duration", 0)

            # Get departure token for next leg (if not last leg)
            if leg_index < num_legs - 1:
                current_token = selected_flight.get("departure_token")
                if not current_token:
                    logger.warning(f"No departure_token for leg {leg_index + 1}, multi-city chain may break")

        logger.info(f"Multi-city search complete: {len(selected_legs)} legs, total ${total_price}, {total_duration} min, {api_calls} API calls")

        return {
            "legs": selected_legs,
            "total_price": total_price if total_price > 0 else "N/A",
            "total_duration_minutes": total_duration,
            "api_calls_used": api_calls,
            "selection_strategy": selection_strategy
        }

    except json.JSONDecodeError as e:
        logger.exception(f"Invalid JSON in flights parameter: {str(e)}")
        return {"error": f"Invalid flights JSON: {str(e)}"}
    except Exception as e:
        logger.exception(f"Unexpected error in search_multi_city_flights: {str(e)}")
        return {"error": f"Multi-city flight search failed: {str(e)}"}


def _select_flight_by_strategy(available_flights: List[Dict], strategy: str) -> Optional[Dict]:
    """
    Select the best flight from available options based on strategy.

    Args:
        available_flights: List of flight options from SerpAPI
        strategy: Selection strategy ("cheapest", "fastest", "balanced")

    Returns:
        Selected flight dict, or None if no valid selection
    """
    if not available_flights:
        return None

    # Filter out flights without prices (N/A)
    priced_flights = [f for f in available_flights if f.get("price") and isinstance(f.get("price"), (int, float))]

    # If all flights lack pricing, take first available
    if not priced_flights:
        logger.warning("No priced flights available, selecting first option")
        return available_flights[0]

    if strategy == "cheapest":
        # Sort by price (ascending)
        return min(priced_flights, key=lambda f: f.get("price", float('inf')))

    elif strategy == "fastest":
        # Sort by duration (ascending)
        return min(priced_flights, key=lambda f: f.get("total_duration", float('inf')))

    elif strategy == "balanced":
        # Balanced: minimize (normalized_price + normalized_duration)
        # Normalize each metric to 0-1 range
        prices = [f.get("price", 0) for f in priced_flights if f.get("price")]
        durations = [f.get("total_duration", 0) for f in priced_flights if f.get("total_duration")]

        if not prices or not durations:
            return priced_flights[0]

        min_price, max_price = min(prices), max(prices)
        min_dur, max_dur = min(durations), max(durations)

        def score(flight):
            p = flight.get("price", max_price)
            d = flight.get("total_duration", max_dur)
            norm_price = (p - min_price) / (max_price - min_price) if max_price > min_price else 0
            norm_dur = (d - min_dur) / (max_dur - min_dur) if max_dur > min_dur else 0
            return norm_price + norm_dur

        return min(priced_flights, key=score)

    else:
        logger.warning(f"Unknown strategy '{strategy}', defaulting to cheapest")
        return min(priced_flights, key=lambda f: f.get("price", float('inf')))


def _extract_leg_data(flight: Dict, leg_number: int) -> Dict:
    """
    Extract key information from a selected flight for this leg.

    Args:
        flight: Flight dict from SerpAPI
        leg_number: Which leg this is (1-indexed)

    Returns:
        Dict with formatted leg information
    """
    segments = flight.get("flights", [])

    if not segments:
        return {
            "leg": leg_number,
            "error": "No flight segments data"
        }

    # Get first and last segments for overall route
    first_segment = segments[0]
    last_segment = segments[-1]

    dep_airport = first_segment.get("departure_airport", {})
    arr_airport = last_segment.get("arrival_airport", {})

    return {
        "leg": leg_number,
        "departure": f"{dep_airport.get('name', 'Unknown')} ({dep_airport.get('id', '???')})",
        "departure_time": dep_airport.get("time", "N/A"),
        "arrival": f"{arr_airport.get('name', 'Unknown')} ({arr_airport.get('id', '???')})",
        "arrival_time": arr_airport.get("time", "N/A"),
        "airline": first_segment.get("airline", "Unknown"),
        "price": flight.get("price", "N/A"),
        "duration_minutes": flight.get("total_duration", "N/A"),
        "stops": len(segments) - 1,
        "travel_class": first_segment.get("travel_class", "Economy"),
        "segments": len(segments)
    } 