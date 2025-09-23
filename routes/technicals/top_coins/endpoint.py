"""
This module contains the endpoint handlers for the trending cryptocurrencies.
"""

from flask import jsonify

from app_prepare import app, cache
from .data_fetching import TopCoins


@app.route("/api/top_market_cap_coins")
def get_top_coins():
    """
    Endpoint to get the list of top cryptocurrencies.
    Uses caching to avoid frequent scraping.

    Returns:
        JSON response containing the list of top coins.
    """
    data = cache.get("top_market_cap_coins")

    # If no cache is found, fetch data and set the cache.
    if not data:
        data = TopCoins.fetch_data()
        cache.set("top_market_cap_coins", data, timeout=3600)

    return jsonify(data)


@app.route("/api/top_volume_coins")
def get_top_volume_coins():
    """
    Endpoint to get the list of top cryptocurrencies (by 24h volume).
    Uses caching to avoid frequent scraping.

    Returns:
        JSON response containing the list of top coins.
    """
    data = cache.get("top_volume_coins")

    # If no cache is found, fetch data and set the cache.
    if not data:
        data = TopCoins.fetch_data(sort_by="volume_24h")
        cache.set("top_volume_coins", data, timeout=3600)

    return jsonify(data)
