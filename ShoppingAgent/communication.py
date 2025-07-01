# communication.py
import time
import random

def fetch_mcp(shop_name, query):
    """Simulates fetching data from a shop's MCP endpoint."""
    print(f"  > Attempting MCP connection to {shop_name} for '{query}'...")
    latency = random.uniform(0.1, 0.5) # MCP is fast
    time.sleep(latency)
    
    # Simulate a high success rate for MCP
    if random.random() < 0.98: 
        print(f"  ✓ MCP Success from {shop_name}")
        data = [
            {'product_id': 'MCP_123', 'name': 'Premium Wireless Headphones', 'price': 299.99, 'currency': 'USD', 'stock': 50, 'reviews': ["Amazing sound quality!", "Battery life is incredible."]},
            {'product_id': 'MCP_456', 'name': 'Budget Wired Headphones', 'price': 49.99, 'currency': 'USD', 'stock': 100, 'reviews': ["Good for the price."]}
        ]
        return data, latency, True
    else:
        print(f"  ✗ MCP Failed for {shop_name}")
        return None, latency, False

def fetch_api(shop_name, query):
    """Simulates fetching data from a shop's REST API."""
    print(f"  > Attempting API connection to {shop_name} for '{query}'...")
    latency = random.uniform(0.3, 1.0) # API is a bit slower
    time.sleep(latency)

    # Simulate a good success rate for API
    if random.random() < 0.90:
        print(f"  ✓ API Success from {shop_name}")
        data = [
            {'sku': 'API-789', 'productName': 'Pro Gamer Headset', 'cost': 150.0, 'available': True, 'customer_feedback': [{'rating': 5, 'comment': 'Perfect for gaming.'}]},
        ]
        return data, latency, True
    else:
        print(f"  ✗ API Failed for {shop_name}")
        return None, latency, False

def fetch_web_scrape(shop_name, query):
    """Simulates fetching data via web scraping."""
    print(f"  > Attempting Web Scrape on {shop_name} for '{query}'...")
    latency = random.uniform(1.5, 4.0) # Scraping is slow and brittle
    time.sleep(latency)

    # Simulate a lower success rate for scraping
    if random.random() < 0.70:
        print(f"  ✓ Scraping Success from {shop_name}")
        data = [
            {'title': 'Noise-Cancelling Over-Ear Headphones', 'price_str': '$199.99', 'in_stock': 'yes', 'reviews_text': "Great noise cancellation but a bit bulky."}
        ]
        return data, latency, True
    else:
        print(f"  ✗ Scraping Failed for {shop_name}")
        return None, latency, False
