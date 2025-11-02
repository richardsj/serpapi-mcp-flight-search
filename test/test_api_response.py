#!/usr/bin/env python3
"""
Test to see what the actual SerpAPI response looks like for our multi-city params.
"""

import asyncio
import json
import sys
import os
from dotenv import load_dotenv

sys.path.insert(0, '..')

from mcp_flight_search.services.serpapi_client import run_search

load_dotenv()

async def test_api_response():
    """Test what SerpAPI actually returns for our multi-city request"""

    params = {
        "api_key": os.getenv("SERP_API_KEY"),
        "engine": "google_flights",
        "hl": "en",
        "gl": "us",
        "type": "3",
        "currency": "USD",
        "travel_class": 1,
        "multi_city_json": json.dumps([
            {"departure_id": "LAX", "arrival_id": "JFK", "date": "2025-11-10"},
            {"departure_id": "JFK", "arrival_id": "BOS", "date": "2025-11-12"}
        ]),
        "sort_by": 2,
        "stops": 1
    }

    print("Sending request with params:")
    print(json.dumps({k: v for k, v in params.items() if k != 'api_key'}, indent=2))
    print("\n" + "="*70 + "\n")

    result = await run_search(params)

    print("Response keys:", list(result.keys()))
    print()

    if "error" in result:
        print(f"ERROR: {result['error']}")
        return

    if "best_flights" in result:
        print(f"best_flights count: {len(result['best_flights'])}")
        if result['best_flights']:
            print("\nFirst flight sample:")
            print(json.dumps(result['best_flights'][0], indent=2))
    else:
        print("No 'best_flights' in response")

    if "other_flights" in result:
        print(f"\nother_flights count: {len(result['other_flights'])}")

    # Print all top-level keys and their types
    print("\n" + "="*70)
    print("Full response structure:")
    for key in result.keys():
        value = result[key]
        if isinstance(value, list):
            print(f"  {key}: list with {len(value)} items")
        elif isinstance(value, dict):
            print(f"  {key}: dict with keys: {list(value.keys())}")
        else:
            print(f"  {key}: {type(value).__name__}")

if __name__ == "__main__":
    asyncio.run(test_api_response())
