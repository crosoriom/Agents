# agent.py
from knowledge_base import KnowledgeBase
from orchestrator import ShopCommunicationOrchestrator
from processing import normalize_data, make_decision

class AIAgent:
    def __init__(self):
        print("[Agent] Initializing...")
        self.kb = KnowledgeBase()
        self.orchestrator = ShopCommunicationOrchestrator(self.kb)

    def perform_initial_setup(self):
        """Simulates the 'First Use' phase: discovering and adding stores."""
        print("\n[Agent] Performing initial store discovery...")
        self.kb.add_shop(name="TechNerdia", scope="national", mcp=True, api=True, scraping=True)
        self.kb.add_shop(name="GadgetGalaxy", scope="international", mcp=False, api=True, scraping=True)
        self.kb.add_shop(name="LocalElectronics", scope="local", mcp=False, api=False, scraping=True)
        print("[Agent] Initial setup complete.")

    def search_products(self, query, preferences):
        """The main function to handle a user's search query."""
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
