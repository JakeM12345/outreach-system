"""
places_scraper.py
Fetches business leads using the Google Places API and saves them to leads.csv
"""

import os
import csv
import time
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
BASE_URL = "https://maps.googleapis.com/maps/api/place"


def search_places(query: str, location: str, radius: int = 5000) -> list[dict]:
    """
    Search for businesses using the Places Text Search API.

    Args:
        query:    e.g. "coffee shops"
        location: e.g. "Los Angeles, CA"  (geocoded automatically)
        radius:   search radius in metres (default 5 km)

    Returns:
        List of raw place result dicts.
    """
    results = []
    url = f"{BASE_URL}/textsearch/json"
    params = {
        "query": f"{query} in {location}",
        "radius": radius,
        "key": API_KEY,
    }

    while True:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if data.get("status") not in ("OK", "ZERO_RESULTS"):
            print(f"[WARNING] Places API returned status: {data.get('status')}")
            break

        results.extend(data.get("results", []))
        next_page = data.get("next_page_token")
        if not next_page:
            break

        # Google requires a short delay before using next_page_token
        time.sleep(2)
        params = {"pagetoken": next_page, "key": API_KEY}

    return results


def get_place_details(place_id: str) -> dict:
    """
    Fetch detailed info (website, formatted phone) for a single place.
    """
    url = f"{BASE_URL}/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,formatted_address,formatted_phone_number,website,rating,user_ratings_total",
        "key": API_KEY,
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json().get("result", {})


def scrape_leads(query: str, location: str, output_file: str = "leads.csv") -> int:
    """
    Full pipeline: search → enrich → save to CSV.

    Returns:
        Number of leads saved.
    """
    print(f"[+] Searching for '{query}' in '{location}' ...")
    places = search_places(query, location)
    print(f"    Found {len(places)} raw results. Enriching details ...")

    fieldnames = ["name", "address", "phone", "website", "rating", "total_ratings", "place_id"]

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i, place in enumerate(places, 1):
            place_id = place.get("place_id", "")
            details = get_place_details(place_id) if place_id else {}

            row = {
                "name":          details.get("name") or place.get("name", ""),
                "address":       details.get("formatted_address") or place.get("formatted_address", ""),
                "phone":         details.get("formatted_phone_number", ""),
                "website":       details.get("website", ""),
                "rating":        details.get("rating", ""),
                "total_ratings": details.get("user_ratings_total", ""),
                "place_id":      place_id,
            }
            writer.writerow(row)
            print(f"    [{i}/{len(places)}] {row['name']}")

            # Be polite to the API
            time.sleep(0.3)

    print(f"\n[✓] Saved {len(places)} leads to '{output_file}'")
    return len(places)


if __name__ == "__main__":
    scrape_leads(
        query="digital marketing agencies",
        location="Los Angeles, CA",
        output_file="leads.csv",
    )
