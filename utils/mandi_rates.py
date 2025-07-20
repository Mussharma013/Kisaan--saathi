import requests

def get_mandi_rates(crop_name=None, market_name=None):
    """
    Fetches mandi rates from AgmarkNet API (or a similar source).
    This is a conceptual placeholder as AgmarkNet API is not public/straightforward.
    You might need to scrape or use a different dataset.
    """
    print(f"Fetching mandi rates for crop: {crop_name}, market: {market_name}")
    # Placeholder for actual API call or data retrieval logic
    # Example AgmarkNet API is complex and often requires specific parameters/auth.

    # Mock Data for demonstration
    mock_data = [
        {"crop": "Wheat", "market": "Varanasi", "date": "2025-07-20", "min_price": 2200, "max_price": 2400, "unit": "Quintal"},
        {"crop": "Rice", "market": "Varanasi", "date": "2025-07-20", "min_price": 3000, "max_price": 3500, "unit": "Quintal"},
        {"crop": "Potato", "market": "Varanasi", "date": "2025-07-20", "min_price": 1500, "max_price": 1800, "unit": "Quintal"},
        {"crop": "Tomato", "market": "Lucknow", "date": "2025-07-20", "min_price": 1000, "max_price": 1200, "unit": "Quintal"}
    ]

    if crop_name:
        mock_data = [item for item in mock_data if crop_name.lower() in item['crop'].lower()]
    if market_name:
        mock_data = [item for item in mock_data if market_name.lower() in item['market'].lower()]

    return mock_data

if __name__ == '__main__':
    rates = get_mandi_rates(crop_name="wheat", market_name="Varanasi")
    print("Mandi Rates:", rates)