"""
This module contains the endpoint handlers for market data.
"""

from flask import jsonify

from app_prepare import app, cache
from .data_fetching import fetch_global_market_data


@app.route("/api/market_data")
def get_global_market_data():
    """
    Endpoint to get the market data including the BTC and ETH market cap dominance
    and their change percentage. Uses caching to avoid frequent fetching.

    Returns:
        JSON response containing the market data.
    """
    data = cache.get("market_data")

    # If no cache is found, fetch data and set the cache.
    if not data:
        data = fetch_global_market_data()
        cache.set("market_data", data, timeout=3600)

    return jsonify(data)
