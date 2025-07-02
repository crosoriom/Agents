import requests
import json
from bs4 import BeautifulSoup
from requests.api import request

def scrape_and_summarize_website_text(url: str) -> str:
    """
    Fetches the content of a URL and returns a clean, summarized text version.
    This tool is for accessing websites that do not have an API.
    NOTE: This tool cannot reliably process sites that heavily rely on complex JavaScript.
    """
    print(f"    > Attempting to scrap and summarize URL: {url}")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        # Use BeautifulSoup to parse HTML and extract clean text
        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove script and style elements
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()

        # Get text and clean it up
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = '\n'.join(chunk for chunk in chunks if chunk)

        # Limit the output to avoid overwhelming the LLM context
        max_lenght = 8000
        print(f"    ✓ Scraped successfully. Returning summary of {len(clean_text)} chars.")
        return json.dumps({'url': url, 'content': clean_text[:max_lenght]})

    except requests.exceptions.RequestException as e:
        print(f"    ✗ Scraping failed with error: {e}")
        return json.dumps({"error": f"HTTP request to {url} failed with error: {e}"})

def make_http_get_requests(url: str, params: dict, headers: dict):
    """
    Makes a generic HTTP GET request to a specified URL.
    This is a powerful tool that allows the AI to interact with any web API.
    The AI is responsible for constructing the correct URL, parameters, and headers.
    
    Args:
        url (str): The URL to send the GET request to.
        params (dict, optional): A dictionary of query parameters.
        headers (dict, optional): A dictionary of HTTP headers.

    Returns:
        str: The text content of the response, or an error message.
    """
    try:
        response  = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status() # Raise an exception for bad status codes
        # We return the response as a JSON formatted string
        return json.dumps(response.json())
    except requests.exceptions.RequestException as e:
        return f"Error: HTTP request failed with error: {e}"
    except json.JSONDecodeError:
        return "Error: Failed to decode the response as JSON. The content may not be valid JSON."

def fetch_products_via_mcp(shop_name: str, query: str):
    """
    A simulated implementation for fetching products via a futuristic MCP.
    Use this for shops that explicitly support the Model Context Protocol.
    """
    if shop_name.lower() == "amazon":
        # Simulate a successful MCP response
        mcp_response = [
            {'name': 'MCP Product: High-End Headphones', 'price': 349.99, 'quality_features': ['Excellent noise cancellation', '20-hour battery life'], 'stock': 50},
            {'name': 'MCP Product: Mid-Range Earbuds', 'price': 129.99, 'quality_features': ['Good sound', 'Water resistant'], 'stock': 150}
        ]
        return json.dumps(mcp_response)
    
    return json.dumps({"error": f"MCP is not enabled or supported for {shop_name}."})
