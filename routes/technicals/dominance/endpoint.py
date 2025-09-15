"""
This module contains the endpoint handlers for market data.
"""

from flask import jsonify

from app_prepare import app, cache
from .data_fetching import fetch_dominance_data


@app.route("/api/dominance")
def get_dominance():
    """
    Endpoint to get the market data including the BTC and ETH market cap dominance
    and their change percentage. Uses caching to avoid frequent fetching.

    Returns:
        JSON response containing the market data.
    """
    data = cache.get("dominance")

    # If no cache is found, fetch data and set the cache.
    if not data:
        data = fetch_dominance_data()
        cache.set("dominance", data, timeout=3600)

    return jsonify(data)
