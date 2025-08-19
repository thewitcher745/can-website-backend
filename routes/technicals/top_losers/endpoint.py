"""
This module will contain the endpoint handlers for the top_gainers table.
"""

from flask import jsonify

from app_prepare import app, cache
from .data_fetching import TopLosers


@app.route("/api/top_losers")
def get_top_losers():
    data = cache.get("top_losers")

    # If no cache is found, fetch data again, and set the cache.
    if not data:
        data = TopLosers.scrape_data()
        cache.set("top_losers", data, timeout=120)

    return jsonify(data)
