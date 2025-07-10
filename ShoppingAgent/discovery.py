import requests
import os
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv('GOOGLE_PLACES_API_KEY')
PLACES_API_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"

# Helper function to clean names for domain guessing
def _clean_shop_name_for_domain(name):
    """Cleans a shop name to guess its domain name."""
    name = name.lower()

    # Remove common corporate suffixes
    name = re.sub(r'\b(inc|llc|ltd|co|corp)\b', '', name)
    # Remove special characters
    name = re.sub(r'[^\w\s-]', '', name)
    # Replace spaces and multiple dashes with a single dash
    name = re.sub(r'[\s-]+', '-', name)
    # Remove leading/trailing dashes
    name = name.strip('-')
    return name

# Helper function to check if an endpoint exists
def _check_endpoint(url):
    """
    Performs a lightweight HEAD request to check if a server exists at the URL.
    Returns True if it gets any response, even an error like 401/403.
    """
    try:
        # Use a short timeout to not hang the discovery process
        response = requests.head(url, timeout=3, allow_redirects=True)
        # Any status code below 500 (Server Error) suggests the endpoint exists,
        # even if it's 401 (Unauthorized) or 403 (Forbidden), which is common for APIs.
        if response.status_code < 500:
            print(f"    ✓ Found endpoint: {url} (Status: {response.status_code})")
            return True
    except requests.exceptions.RequestException:
        # This catches timeouts, connection errors, etc.
        print(f"    ✗ No endpoint found at: {url}")
        pass
    return False

# The main verification function
def verify_communication_methods(shop_name):
    """
    Verifies MCP and API capabilities by checking for common subdomains.
    """
    print(f"    - Verifying communication methods for '{shop_name}'...")
    cleaned_name = _clean_shop_name_for_domain(shop_name)

    # We will assume a .com TLD for this project, which is a reasonable simplification.
    domain = f"{cleaned_name}.com"

    # Check for API subdomain
    api_url = f"https://api.{domain}"
    api_enabled = _check_endpoint(api_url)

    # Check for MCP subdomain
    mcp_url = f"https://mcp.{domain}"
    mcp_enabled = _check_endpoint(mcp_url)

    return {
        'api_enabled': api_enabled,
        'api_url': api_url,
        'mcp_enabled': mcp_enabled,
        'mcp_url': mcp_url if mcp_enabled else None
    }

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
        return "5.06889, -75.51738" # Default to MZLS

def find_local_stores(location_name, radius_metters=50000):
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

    print(f"[Discovery] Searching for local stores near {location_name}...")
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
        {'name': 'Panamericana', 'scope': 'national'},
        {'name': 'Exito', 'scope': 'national'},
        {'name': 'Ktronix', 'scope': 'national'},
    ]
    print(f"  - Found {len(stores)} national stores.")
    return stores

def get_international_stores():
    """Returns a curated list of prominent international stores."""
    print("[Discovery] Getting curated list of international stores...")
    stores = [
        {'name': 'Amazon', 'scope': 'international'},
        {'name': 'AliExpress', 'scope': 'international'},
        {'name': 'ebay', 'scope': 'international'}
    ]
    print(f"  - Found {len(stores)} international stores.")
    return stores
