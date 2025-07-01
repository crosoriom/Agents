from knowledge_base import KnowledgeBase
from orchestrator import ShopCommunicationOrchestrator
from processing import normalize_data, make_decision
from discovery import find_local_stores, get_national_stores, get_international_stores

class AIAgent:
    def __init__(self):
        print("[Agent] Initializing...")
        self.kb = KnowledgeBase()
        self.orchestrator = ShopCommunicationOrchestrator(self.kb)
        self.is_setup_complete = False

    def perform_initial_setup(self, user_location):
        """
        Performs the 'First Use' phase by discovering and adding stores
        from real-world data sources.
        """
        print(f"\n[Agent] Performing initial store discovery for location: '{user_location}'...")

        # 1. Discover local stores
        local_stores = find_local_stores(user_location)
        for store in local_stores:
            self.kb.add_shop(
                name=store['name'],
                scope=store['scope'],
                mcp=False,
                api=False,
                scraping=True
            )

        # 2. Add national stores
        national_stores = get_national_stores()
        for store in national_stores:
            self.kb.add_shop(
                name=store['name'],
                scope=store['scope'],
                mcp=store.get('mcp', False),
                api=store.get('api', False),
                scraping=store.get('scrapping', True)
            )

        # 3. Add international stores
        international_stores = get_international_stores()
        for store in international_stores:
            self.kb.add_shop(
                name=store['name'],
                scope=store['scope'],
                mcp=store.get('mcp', False),
                api=store.get('api', False),
                scraping=store.get('scrapping', True)
            )

        self.is_setup_complete = True
        print("[Agent] Initial setup complete. Knowledge Base is populated.")

    def search_products(self, query, preferences):
        """The main function to handle a user's search query."""
        if not self.is_setup_complete:
            print("[Agent] ERROR: Agent has not been set up. Please run initial setup.")
            return []

        print(f"\n[Agent] Starting new search for '{query}'...")
        all_shops = self.kb.get_all_shops()
        raw_product_data = []

        for shop in all_shops:
            products = self.orchestrator.fetch_products_from_shop(shop['name'], query)
            if products:
                raw_product_data.extend(products)
        
        if not raw_product_data:
            print("\n[Agent] Search concluded. No products found.")
            return []

        normalized_products = normalize_data(raw_product_data)
        ranked_products = make_decision(normalized_products, preferences)
        
        print("\n[Agent] Search concluded. Returning ranked results.")
        return ranked_products
        
    def display_shop_performance(self):
        """Shows the learned performance metrics for all shops."""
        if not self.is_setup_complete:
            return

        print("\n" + "="*50)
        print("          Current Shop Performance Metrics")
        print("="*50)
        all_shops = self.kb.get_all_shops()
        for shop in all_shops:
            print(f"Shop: {shop['name']}")
            print(f"  - MCP:      Success Rate: {shop['mcp_success_rate']:.2f}, Avg Latency: {shop['mcp_latency']:.2f}s")
            print(f"  - API:      Success Rate: {shop['api_success_rate']:.2f}, Avg Latency: {shop['api_latency']:.2f}s")
            print(f"  - Scraping: Success Rate: {shop['scraping_success_rate']:.2f}, Avg Latency: {shop['scraping_latency']:.2f}s")
        print("="*50 + "\n")
