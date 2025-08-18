"""
This module will contain the endpoint handlers for the top_gainers table.
"""

from flask import jsonify

from app_prepare import app, cache
from .data_fetching import CryptoHeatmap


@app.route("/api/heatmap")
def get_heatmap():
    data = cache.get("heatmap")

    # If no cache is found, fetch data again, and set the cache.
    if not data:
        data = CryptoHeatmap.scrape_data()
        cache.set("heatmap", data, timeout=10800)

    return jsonify(data)
