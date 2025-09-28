"""
This module contains the endpoint handlers for market data.
"""

from flask import jsonify, request

from app_prepare import app, cache
from .data_fetching import LongShortRatio


@app.route("/api/long_short_ratio")
def get_long_short_ratio():
    """
    Endpoint to get the long/short ratio data for a specific symbol. The symbol is passed as
    a query parameter.

    Returns:
        JSON response containing the long/short ratio data.
    """
    symbol = request.args.get("symbol")

    data = cache.get("long_short_ratio")

    # If no cache is found, fetch data and set the cache.
    if not symbol:
        return jsonify({"error": "Symbol not provided"}), 400

    data = LongShortRatio(symbol).fetch_data()
    cache.set("long_short_ratio", data, timeout=3600)

    return jsonify(data)
