"""
This module will contain the endpoint handlers for the crypto heatmap chart.
"""

from flask import jsonify

from app_prepare import app, cache
from .data_fetching import CryptoHeatmap


@app.route("/api/heatmap")
def get_heatmap():
    data = cache.get("heatmap")

    # If no cache is found, fetch data again, and set the cache.
    if not data:
        data = CryptoHeatmap.fetch_data()
        cache.set("heatmap", data, timeout=120)

    return jsonify(data)
