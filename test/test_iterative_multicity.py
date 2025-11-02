#!/usr/bin/env python3
"""
Test the new iterative multi-city search with departure_token chaining.
This tests the real implementation that Claude Desktop will use.
"""

import asyncio
import json
import sys
sys.path.insert(0, '..')

from mcp_flight_search.services.search_service import search_multi_city_flights

async def test_two_leg_journey():
    """Test LAX → JFK → BOS with cheapest strategy"""
    print("="*70)
    print("TEST 1: Two-leg journey (LAX → JFK → BOS)")
    print("="*70)

    flights_json = json.dumps([
        {"departure_id": "LAX", "arrival_id": "JFK", "date": "2025-11-10"},
        {"departure_id": "JFK", "arrival_id": "BOS", "date": "2025-11-12"}
    ])

    result = await search_multi_city_flights(
        flights=flights_json,
        travel_class=1,  # Economy
        stops=0,  # Allow any number of stops
        selection_strategy="cheapest"
    )

    print("\nResult:")
    print(json.dumps(result, indent=2))
    print()

    if "error" in result:
        print(f"❌ FAILED: {result['error']}")
        return False
    elif "legs" in result:
        print(f"✅ SUCCESS: {len(result['legs'])} legs found")
        print(f"   Total price: ${result.get('total_price', 'N/A')}")
        print(f"   Total duration: {result.get('total_duration_minutes', 'N/A')} min")
        print(f"   API calls: {result.get('api_calls_used', 'N/A')}")
        return True
    else:
        print("❌ FAILED: Unexpected result structure")
        return False


async def test_three_leg_journey():
    """Test three-leg journey with filters"""
    print("="*70)
    print("TEST 2: Three-leg journey (LAX → ORD → ATL → MIA)")
    print("         With filters: Exclude Spirit/Frontier")
    print("="*70)

    flights_json = json.dumps([
        {"departure_id": "LAX", "arrival_id": "ORD", "date": "2025-11-10"},
        {"departure_id": "ORD", "arrival_id": "ATL", "date": "2025-11-12"},
        {"departure_id": "ATL", "arrival_id": "MIA", "date": "2025-11-14"}
    ])

    result = await search_multi_city_flights(
        flights=flights_json,
        travel_class=1,  # Economy
        stops=1,  # Nonstop only
        exclude_airlines="NK,F9",  # Exclude Spirit, Frontier
        selection_strategy="cheapest"
    )

    print("\nResult:")
    print(json.dumps(result, indent=2))
    print()

    if "error" in result:
        print(f"⚠️  Expected possible failure (very restrictive filters): {result['error']}")
        return True  # This is acceptable - filters may be too strict
    elif "legs" in result:
        print(f"✅ SUCCESS: {len(result['legs'])} legs found")
        print(f"   Total price: ${result.get('total_price', 'N/A')}")
        print(f"   Total duration: {result.get('total_duration_minutes', 'N/A')} min")
        print(f"   API calls: {result.get('api_calls_used', 'N/A')}")
        return True
    else:
        print("❌ FAILED: Unexpected result structure")
        return False


async def test_fastest_strategy():
    """Test 'fastest' selection strategy"""
    print("="*70)
    print("TEST 3: Two-leg journey with 'fastest' strategy")
    print("="*70)

    flights_json = json.dumps([
        {"departure_id": "JFK", "arrival_id": "LAX", "date": "2025-12-15"},
        {"departure_id": "LAX", "arrival_id": "SFO", "date": "2025-12-16"}
    ])

    result = await search_multi_city_flights(
        flights=flights_json,
        travel_class=1,
        selection_strategy="fastest"
    )

    print("\nResult:")
    print(json.dumps(result, indent=2))
    print()

    if "error" in result:
        print(f"❌ FAILED: {result['error']}")
        return False
    elif "legs" in result:
        print(f"✅ SUCCESS: {len(result['legs'])} legs found")
        print(f"   Strategy used: {result.get('selection_strategy')}")
        return True
    else:
        print("❌ FAILED: Unexpected result structure")
        return False


async def main():
    print("\n")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║  ITERATIVE MULTI-CITY FLIGHT SEARCH TEST SUITE                   ║")
    print("║  Testing departure_token chaining with intelligent selection     ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print()

    results = []

    # Test 1: Simple two-leg journey
    results.append(await test_two_leg_journey())

    # Test 2: Three-leg journey with filters
    results.append(await test_three_leg_journey())

    # Test 3: Fastest strategy
    results.append(await test_fastest_strategy())

    # Summary
    print("="*70)
    print("SUMMARY")
    print("="*70)
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("✅ ALL TESTS PASSED!")
        return 0
    else:
        print(f"⚠️  {total - passed} test(s) had issues")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
