import os
from dotenv import load_dotenv
from knowledge_base import KnowledgeBase
from discovery import find_local_stores, get_national_stores, get_international_stores, verify_communication_methods
from llm_agent import LLMAgent

# Load environment variables from a .env file
load_dotenv()

def perform_initial_setup(kb: KnowledgeBase):
    """
    Performs the 'First Use' phase by discovering, verifying
    and adding stores to the Knowledge Base.
    """
    location = input("Please enter your location to find local stores (e.g., 'New York, NY'): ")
    print(f"\n[Setup] Performing store discovery for location: '{location}'...")

    all_discovered_stores = []
    all_discovered_stores.extend(find_local_stores(location))
    all_discovered_stores.extend(get_national_stores())
    all_discovered_stores.extend(get_international_stores())

    print(f"\n[Setup] Verifying communication methods for all discovered stores...")
    for store_info in all_discovered_stores:
        # --- VERIFICATION STEP ---
        # In a real app, you might have more robust checks here
        verified_methods = verify_communication_methods(store_info['name'])

        kb.add_shop(
            name=store_info['name'],
            scope=store_info['scope'],
            mcp=verified_methods.get('mcp', False),
            api=verified_methods.get('api', False),
            scraping=True
        )

    print("\n[Setup] Initial setup complete. Knowledge Base is populated.")


def main():
    """
    The main entry point for the LLM-powered shopping agent.
    """
    if not os.getenv("GEMINI_API_KEY"):
        print("\nFATAL ERROR: GEMINI_API_KEY environment variable not set.")
        return

    # 1. Initialize the Knowledge Base
    kb = KnowledgeBase()

    # 2. Run the discovery and setup process
    perform_initial_setup(kb)
    
    # 3. Initialize the LLM Agent, giving it the populated Knowledge Base
    print("\n[Main] Initializing the AI Shopping Assistant with discovered store data...")
    llm_agent = LLMAgent(knowledge_base=kb)
    print("[Main] AI Assistant is ready.")

    print("\nWelcome to the AI Shopping Assistant!")
    print("I will search for products in the stores I've just discovered.")

    while True:
        print("\nWhat would you like to search for? (type 'quit' to exit)")
        query = input("> ")

        if query.lower() == 'quit':
            print("Goodbye!")
            break
        
        if not query.strip():
            continue
            
        final_recommendation = llm_agent.process_user_query(query)

        print("\n" + "*"*50)
        print("      AI Assistant Recommendation")
        print("*"*50)
        print(final_recommendation)
        print("*"*50)


if __name__ == "__main__":
    main()
