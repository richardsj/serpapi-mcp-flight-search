#!/usr/bin/env python3
"""
Test what parameters are actually being sent to SerpAPI for multi-city searches.
"""

import json
import sys
sys.path.insert(0, '..')

from mcp_flight_search.services.serpapi_client import prepare_multi_city_params

# Simulate what Claude sent (no stops or layover_duration)
flights_list = [
    {"departure_id": "SYD", "arrival_id": "SIN", "date": "2025-12-01"},
    {"departure_id": "SIN", "arrival_id": "LHR", "date": "2025-12-05"}
]

print("Testing parameters sent for multi-city search...")
print("\nSimulating Claude's request with NO optional filters:")
params = prepare_multi_city_params(flights_list, travel_class=1, stops=None, layover_duration=None)

print("\nParameters being sent to SerpAPI:")
print(json.dumps({k: v for k, v in params.items() if k != 'api_key'}, indent=2))

print("\n\nNow testing with optional filters:")
params_with_filters = prepare_multi_city_params(
    flights_list,
    travel_class=3,
    stops=1,
    layover_duration="1440,10080"
)

print("\nParameters with filters:")
print(json.dumps({k: v for k, v in params_with_filters.items() if k != 'api_key'}, indent=2))
