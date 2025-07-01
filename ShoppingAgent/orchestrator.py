from communication import fetch_mcp, fetch_api, fetch_web_scrape

class ShopCommunicationOrchestrator:
    def __init__(self, knowledge_base) -> None:
        self.kb = knowledge_base
        self.methods = {
            'mcp': fetch_mcp,
            'api': fetch_api,
            'scraping': fetch_web_scrape
        }

    def fetch_products_from_shop(self, shop_name, query):
        """
        Fetches products from a single shop, using the best available method.
        It adaptively prioritizes methods based on perdormance.
        """
        print(f"\n[Orchestrator] Planning fetch for shop: {shop_name}")
        shop_details = self.kb.get_shop_by_name(shop_name)
        if not shop_details:
            print(f"    ! Shop '{shop_name}' not found in Knowledge Base.")
            return []

        # --- Adaptative Prioritization Logic ---
        available_methods = []
        if shop_details['mcp_enabled']: available_methods.append('mcp')
        if shop_details['api_enabled']: available_methods.append('api')
        if shop_details['scraping_enabled']: available_methods.append('scraping')

        # Calculate a performance score for each method
        def calculate_score(method):
            latency = shop_details[f'{method}_latency']
            success_rate = shop_details[f'{method}_success_rate']
            # We want high success rate and low latency. Add 0.01 to avoid division by zero.
            return success_rate / (latency + 0.01)

        # Sort methods by performance score, descending
        sorted_methods = sorted(available_methods, key=calculate_score, reverse=True)
        print(f"    - Prioritized methods: {sorted_methods}")

        # Execution loop
        for method in sorted_methods:
            fetch_function = self.methods[method]
            data, latency, success = fetch_function(shop_name, query)

            # CRITICAL: Update the knowledge base with the performance of this attempt
            self.kb.update_shop_performance(shop_name, method, latency, success)

            if success and data:
                print(f"    - Succesfully retrieved data using {method}.")
                # Add shop_name to each product for later reference
                for item in data:
                    item['shop_name'] = shop_name
                return data

        print(f"    ! Failed to retrieve data from {shop_name} using all available methods.")
        return []
