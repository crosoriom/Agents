import re

def normalize_data(raw_data_list):
    """
    Takes a list of raw product dictionaries from various sources and
    maps them to a unified schema.
    """
    print(f"\n[Processor] Normalizing all collected data...")
    normalized_products = []
    for product in raw_data_list:
        norm_product = {
            'id': product.get('product_id') or product.get('sku'),
            'name': product.get('name') or product.get('productName') or product.get('title'),
            'price': float(re.sub(r'[^\d.]', '', str(product.get('price') or product.get('cost') or product.get('price_str', '0')))),
            'shop_name': product.get('shop_name'),
            'raw_reviews': product.get('reviews') or product.get('customer_feedback') or [product.get('reviews_text')]
        }
        # Calculate quality score
        norm_product['quality_score'] = calculate_quality_score(norm_product)
        normalized_products.append(norm_product)

    print(f"    - Normalized {len(normalized_products)} products.")
    return normalized_products

def calculate_quality_score(product):
    """
    A simple NLP-based function to generate a quality score from reviews.
    This simulates the "AI" part of the agent.
    """
    reviews = product.get('raw_reviews', [])
    if not reviews or not any(reviews):
        return 5.0 # Neutral score if no reviews

    score = 5.0
    positive_words = ['amazing', 'incredible', 'perfect', 'great', 'good']
    negative_words = ['bulky', 'bad', 'poor', 'disappointing']
    
    text = ' '.join(str(r) for r in reviews).lower()
    
    for p_word in positive_words:
        if p_word in text:
            score += 1.5
    for n_word in negative_words:
        if n_word in text:
            score -= 1.5
            
    # Clamp score between 0 and 10
    return max(0.0, min(10.0, score))

def make_decision(normalized_products, preferences):
    """
    Ranks products based on user preferences (weights for price vs. quality).
    """
    print("[Decision Engine] Ranking products based on preferences...")
    if not normalized_products:
        return []

    # Min-max normalization for price and quality to scale them between 0 and 1
    min_price = min(p['price'] for p in normalized_products)
    max_price = max(p['price'] for p in normalized_products)
    min_quality = min(p['quality_score'] for p in normalized_products)
    max_quality = max(p['quality_score'] for p in normalized_products)

    for product in normalized_products:
        # Normalize price (lower is better, so we invert it)
        if max_price == min_price:
            price_score = 1.0
        else:
            price_score = 1 - ((product['price'] - min_price) / (max_price - min_price))
            
        # Normalize quality (higher is better)
        if max_quality == min_quality:
            quality_score = 1.0
        else:
            quality_score = (product['quality_score'] - min_quality) / (max_quality - min_quality)
        
        # Calculate final rank score using user weights
        product['rank_score'] = (price_score * preferences['price']) + (quality_score * preferences['quality'])
    
    # Sort by the final rank score, descending
    return sorted(normalized_products, key=lambda p: p['rank_score'], reverse=True)
