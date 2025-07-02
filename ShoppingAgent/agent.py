from knowledge_base import KnowledgeBase
from orchestrator import ShopCommunicationOrchestrator
from processing import normalize_data, make_decision
from discovery import find_local_stores, get_national_stores, get_international_stores, verify_communication_methods

class AIAgent:
    def __init__(self):
        print("[Agent] Initializing...")
        self.kb = KnowledgeBase()
        self.orchestrator = ShopCommunicationOrchestrator(self.kb)
        self.is_setup_complete = False

    def perform_initial_setup(self, user_location):
        """
        Performs the 'First Use' phase by discovering, verifying
        and adding stores to the Knowledge Base.
        """
        print(f"\n[Agent] Performing initial store discovery for location: '{user_location}'...")

        all_discovered_stores = []
        all_discovered_stores.extend(find_local_stores(user_location))
        all_discovered_stores.extend(get_national_stores())
        all_discovered_stores.extend(get_international_stores())

        print(f"\n[Agent] Beginning verification process for all discovered stores...")
        for store_info in all_discovered_stores:
            # --- VERIFICATION STEP ---
            verified_methods = verify_communication_methods(store_info['name'])

            self.kb.add_shop(
                name=store_info['name'],
                scope=store_info['scope'],
                mcp=verified_methods['mcp'],
                api=verified_methods['api'],
                scraping=True
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
