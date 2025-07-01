import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv('GOOGLE_PLACES_API_KEY')
PLACES_API_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"

def get_coordinates_for_location(location_name):
    """
    (Simulation) A real implementation would use a geocoding API.
    For this project, we'll use a hardcoded dictionary for simplicity.
    """
    print(f"[Discovery] Getting coordinates for '{location_name}'...")
    locations = {
        "new york, ny": "40.7128,-74.0060",
        "san francisco, ca": "37.7749,-122.4194",
        "london, uk": "51.5072,-0.1276",
    }
    coords = locations.get(location_name.lower())
    if coords:
        print(f"  - Found coordinates: {coords}")
        return coords
    else:
        print(f"  - Could not find coordinates for '{location_name}'. Using default.")
        return "40.7128,-74.0060" # Default to NYC

def find_local_stores(location_name, radius_metters=5000):
    """
    Uses the Google Places API to find local electronics stores.
    """
    if not API_KEY:
        print("[Discovery] ERROR: GOOGLE_PLACES_API_KEY not found in .env file. Skipping local discovery.")
        return []

    coords = get_coordinates_for_location(location_name)
    params = {
        'query': 'electronics store',
        'location': coords,
        'radius': radius_metters,
        'key': API_KEY
    }

    print(f"[Discovery] Aearching for local stores near {location_name}...")
    try:
        response = requests.get(PLACES_API_URL, params=params)
        response.raise_for_status()
        results = response.json().get('results',[])

        stores = []
        # Take the top 5 to not overwhelm the demo
        for place in results[:5]:
            stores.append({
                'name': place['name'],
                'scope': 'local'
            })

        print(f"    - Found {len(stores)} local stores.")
        return stores
    except requests.exceptions.RequestException as e:
        print(f"[Discovery] ERROR: Could not connect to Google Places API. {e}")
        return []
    except Exception as e:
        print(f"[Discovery] ERROR: An error occurred during local discovery. {e}")
        return []

def get_national_stores():
    """Returns a curated list of prominent national stores."""
    print("[Discovery] Getting curated list of national stores...")
    stores = [
        {'name': 'Best Buy', 'scope': 'national', 'mcp': False, 'api': True, 'scraping': True},
        {'name': 'Walmart', 'scope': 'national', 'mcp': False, 'api': True, 'scraping': True},
        {'name': 'Target', 'scope': 'national', 'mcp': False, 'api': False, 'scraping': True},
        {'name': 'Micro Center', 'scope': 'national', 'mcp': False, 'api': False, 'scraping': True},
    ]
    print(f"  - Found {len(stores)} national stores.")
    return stores

def get_international_stores():
    """Returns a curated list of prominent international stores."""
    print("[Discovery] Getting curated list of international stores...")
    stores = [
        {'name': 'Amazon', 'scope': 'international', 'mcp': True, 'api': True, 'scraping': True},
        {'name': 'AliExpress', 'scope': 'international', 'mcp': False, 'api': False, 'scraping': True},
        {'name': 'B&H Photo Video', 'scope': 'international', 'mcp': False, 'api': True, 'scraping': True},
    ]
    print(f"  - Found {len(stores)} international stores.")
    return stores
