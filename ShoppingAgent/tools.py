import requests
import json
import time
import os
from bs4 import BeautifulSoup
from knowledge_base import KnowledgeBase

class ToolBox:
    def __init__(self, kb: KnowledgeBase):
        """Initializes the ToolBox with the single, shared Knowledge Base instance."""
        print("[ToolBox] Initialized with shared Knowledge Base.")
        self.kb = kb

    def get_shop_details_from_kb(self) -> str:
        """
        Retrieves the list of shops, their capabilities, and current performance from the knowledge base.
        This should be the FIRST tool called to decide which shops to contact and how.
        """
        print("    > Querying Knowledge Base for all shop details...")
        all_shops = self.kb.get_all_shops()
        return json.dumps(all_shops)

    def _update_performance(self, shop_name: str, method: str, latency: float, success: bool):
        """Internal helper to automatically update the KB."""
        if method in ['api', 'mcp', 'scraping']:
            self.kb.update_shop_performance(shop_name, method, latency, success)

    def make_api_request(self, shop_name: str, url: str, params: dict, headers: dict) -> str:
        """
        Makes an API request to the given URL and AUTOMATICALLY records its performance in the KB.
        The LLM must provide the shop_name and the url from the KB.
        """
        start_time = time.monotonic()

        # Format the shop name to create a standard environment variable name (e.g., "Best Buy" -> "BESTBUY_API_KEY")
        env_var_name = f"{shop_name.replace(' ', '').upper()}_API_KEY"
        api_key = os.getenv(env_var_name)

        if api_key:
            print(f"    > Found API key for '{shop_name}' in env var '{env_var_name}'.")
            if params is None:
                params = {}
            # Add the key to params. We assume the key name is 'apiKey', a common convention.
            if 'apiKey' not in params:
                params['apiKey'] = api_key
                print("      Injecting 'apiKey' into request parameters.")

        try:
            print(f"    > Making API request for '{shop_name}' at: {url}")
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()
            success = True
        except Exception as e:
            result = {"error": str(e)}
            success = False
        
        latency = time.monotonic() - start_time
        self._update_performance(shop_name, 'api', latency, success)
        
        return json.dumps(result)

    def scrape_website(self, shop_name: str, url: str) -> str:
        """
        Scrapes a website at the given URL and AUTOMATICALLY records its performance in the KB.
        Used as a fallback. The LLM must provide the shop_name and a constructed search url.
        """
        start_time = time.monotonic()
        try:
            print(f"    > Scraping website for '{shop_name}' at: {url}")
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)...'}
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            for el in soup(["script", "style"]): el.decompose()
            text = '\n'.join(chunk for chunk in (phrase.strip() for line in (line.strip() for line in soup.get_text().splitlines()) for phrase in line.split("  ")) if chunk)
            result = {'url': url, 'content': text[:20000]}
            success = True
        except Exception as e:
            result = {"error": str(e)}
            success = False
            
        latency = time.monotonic() - start_time
        self._update_performance(shop_name, 'scraping', latency, success)
        
        return json.dumps(result)

    def get_tool_functions(self) -> dict:
        """Returns the dictionary of simplified, self-reporting tools."""
        return {
            "get_shop_details_from_kb": self.get_shop_details_from_kb,
            "make_api_request": self.make_api_request,
            "scrape_website": self.scrape_website,
        }
