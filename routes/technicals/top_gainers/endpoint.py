"""
This module will contain the endpoint handlers for the top_gainers table.
"""

from flask import jsonify

from app_prepare import app, cache
from .data_fetching import TopGainers


@app.route("/api/top_gainers")
def get_top_gainers():
    data = cache.get("top_gainers")

    # If no cache is found, fetch data again, and set the cache.
    if not data:
        data = TopGainers.scrape_data()
        cache.set("top_gainers", data, timeout=10800)

    return jsonify(data)
