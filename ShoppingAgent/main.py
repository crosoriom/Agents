from agent import AIAgent

def print_results(results):
    if not results:
        print("Sorry, I couldn't find any matching products.")
        return
        
    print("\n" + "*"*50)
    print("              Top Recommendations")
    print("*"*50)
    for i, product in enumerate(results):
        print(f"#{i+1}: {product['name']} from {product['shop_name']}")
        print(f"  - Price: ${product['price']:.2f}")
        print(f"  - Quality Score: {product['quality_score']:.1f}/10.0")
        print(f"  - Final Rank Score: {product['rank_score']:.3f}")
        print("-" * 20)

def main():
    ai_agent = AIAgent()

    print("Welcome to the AI Shopping Agent!")
    print("First, I need to build my knowledge base of stores.")
    location = input("Please enter your location (e.g., 'New York, NY', 'San Francisco, CA'): ")
    
    ai_agent.perform_initial_setup(location)
    
    # Show initial (default) performance
    ai_agent.display_shop_performance()

    preferences = {'price': 0.5, 'quality': 0.5} # Default balanced preference

    while True:
        print("\nWhat would you like to search for? (type 'pref' to change preferences, 'quit' to exit)")
        query = input("> ")

        if query.lower() == 'quit':
            break
        
        if query.lower() == 'pref':
            try:
                price_weight = float(input("Enter weight for price (0.0 to 1.0): "))
                quality_weight = float(input("Enter weight for quality (0.0 to 1.0): "))
                total = price_weight + quality_weight
                preferences = {'price': price_weight/total, 'quality': quality_weight/total}
                print(f"Preferences updated: Price {preferences['price']:.2f}, Quality {preferences['quality']:.2f}")
            except ValueError:
                print("Invalid input. Please enter numbers.")
            continue

        results = ai_agent.search_products(query, preferences)
        print_results(results)

        # After each search, show how the agent has "learned"
        ai_agent.display_shop_performance()

if __name__ == "__main__":
    main()
