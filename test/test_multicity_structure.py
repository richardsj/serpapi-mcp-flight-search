#!/usr/bin/env python3
"""
Test to examine SerpAPI multi-city response structure.
Helps understand what data is returned for multi-leg itineraries.
"""

import json
import os
from dotenv import load_dotenv
from serpapi import GoogleSearch

# Load API key from .env
load_dotenv()
api_key = os.getenv("SERP_API_KEY")

if not api_key:
    print("❌ Error: SERP_API_KEY not found in .env file")
    print("Please create a .env file with: SERP_API_KEY=your_key_here")
    exit(1)

# Test multi-city search: Sydney → Singapore → London
flights = [
    {"departure_id": "SYD", "arrival_id": "SIN", "date": "2025-12-01"},
    {"departure_id": "SIN", "arrival_id": "LHR", "date": "2025-12-05"}
]

params = {
    "api_key": api_key,
    "engine": "google_flights",
    "hl": "en",
    "gl": "us",
    "type": "3",  # Multi-city
    "currency": "USD",
    "travel_class": 1,
    "multi_city_json": json.dumps(flights)
}

print("Testing multi-city flight search...")
print(f"Route: {' → '.join([f['departure_id'] for f in flights] + [flights[-1]['arrival_id']])}")
print()

result = GoogleSearch(params).get_dict()

print(f"Response keys: {list(result.keys())}")
print(f"Number of best_flights: {len(result.get('best_flights', []))}")
print()

# Analyze segment structure
print("Analyzing flight segments:")
for i, flight in enumerate(result.get('best_flights', [])[:5], 1):
    segments = flight.get("flights", [])
    print(f"\nFlight #{i}:")
    print(f"  Type: {flight.get('type')}")
    print(f"  Price: ${flight.get('price', 'N/A')}")
    print(f"  Total duration: {flight.get('total_duration', 'N/A')} min")
    print(f"  Number of segments: {len(segments)}")

    for j, segment in enumerate(segments, 1):
        dep = segment.get("departure_airport", {})
        arr = segment.get("arrival_airport", {})
        print(f"    Segment {j}: {dep.get('id')} → {arr.get('id')} on {segment.get('airline')}")

# Show full structure of first complete multi-segment result
print("\n" + "="*60)
print("Full structure of first multi-segment itinerary:")
print("="*60)
for flight in result.get('best_flights', []):
    if len(flight.get("flights", [])) > 1:
        print(json.dumps(flight, indent=2))
        break
else:
    print("No multi-segment itineraries found in results")
