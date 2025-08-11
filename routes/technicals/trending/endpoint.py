"""
This module contains the endpoint handlers for the trending cryptocurrencies.
"""

from flask import jsonify

from app_prepare import app, cache
from .data_fetching import TrendingCoins


@app.route("/api/trending")
def get_trending():
    """
    Endpoint to get the list of trending cryptocurrencies.
    Uses caching to avoid frequent scraping.
    
    Returns:
        JSON response containing the list of trending coins.
    """
    data = cache.get("trending_coins")

    # If no cache is found, fetch data and set the cache.
    if not data:
        data = TrendingCoins.scrape_data()
        cache.set("trending_coins", data, timeout=10800)  # Cache for 3 hours

    return jsonify(data)
