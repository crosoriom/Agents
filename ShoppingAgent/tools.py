import requests
import json
import time
from bs4 import BeautifulSoup
from knowledge_base import KnowledgeBase

class ToolBox:
    def __init__(self, kb: KnowledgeBase):
        print("[ToolBox] Initialized with shared Knowledge Base.")
        self.kb = kb

    def _execute_and_time(self, func, *args, **kwargs):
        """A helper to time the execution of a function."""
        start_time = time.monotonic()
        try:
            result = func(*args, **kwargs)
            success = "error" not in result
        except Exception as e:
            result = {"error": str(e)}
            success = False
        end_time = time.monotonic()
        latency = end_time - start_time
        # Return a dictionary that includes the result, success status, and latency
        return {"result": result, "success": success, "latency": latency}

    def get_shop_details_from_kb(self) -> str:
        """Retrieves the full list of shops and their capabilities from the knowledge base."""
        print("    > Querying Knowledge Base for all shop details...")
        all_shops = self.kb.get_all_shops()
        return json.dumps(all_shops)

    def update_shop_performance_in_kb(self, shop_name: str, method: str, latency: float, success: bool) -> str:
        """
        Updates the performance metrics (latency, success rate) for a shop in the Knowledge Base.
        'method' must be one of ['mcp', 'api', 'scraping'].
        """
        print(f"    > Updating KB for '{shop_name}'...")
        if method not in ['mcp', 'api', 'scraping']:
            return json.dumps({"error": "Invalid method. Must be 'mcp', 'api', or 'scraping'."})
        self.kb.update_shop_performance(shop_name, method, latency, success)
        return json.dumps({"status": "success", "message": f"KB updated for {shop_name}."})

    def make_http_get_request(self, url: str, params: dict, headers: dict) -> str:
        """Makes a generic HTTP GET request and reports its performance."""
        def request_logic():
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        
        performance_data = self._execute_and_time(request_logic)
        return json.dumps(performance_data)

    def fetch_products_via_mcp(self, url: str, query: str) -> str:
        """Attempts to fetch products from an MCP URL and reports its performance."""
        def request_logic():
            response = requests.post(url, json={"query": query}, timeout=4)
            response.raise_for_status()
            return response.json()

        performance_data = self._execute_and_time(request_logic)
        return json.dumps(performance_data)

    def scrape_and_summarize_website_text(self, url: str) -> str:
        """Scrapes a website and reports its performance."""
        def request_logic():
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)...'}
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            for el in soup(["script", "style"]): el.decompose()
            text = '\n'.join(chunk for chunk in (phrase.strip() for line in (line.strip() for line in soup.get_text().splitlines()) for phrase in line.split("  ")) if chunk)
            return {'url': url, 'content': text[:8000]}

        performance_data = self._execute_and_time(request_logic)
        return json.dumps(performance_data)

    def get_tool_functions(self) -> dict:
        """Returns the dictionary of all tools available to the LLM."""
        return {
            "get_shop_details_from_kb": self.get_shop_details_from_kb,
            "update_shop_performance_in_kb": self.update_shop_performance_in_kb, # Expose the new tool
            "make_http_get_request": self.make_http_get_request,
            "fetch_products_via_mcp": self.fetch_products_via_mcp,
            "scrape_and_summarize_website_text": self.scrape_and_summarize_website_text,
        }
