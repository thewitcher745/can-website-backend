"""
This module will contain the endpoint handlers for the recent_airdrops section.
"""

from flask import jsonify

from app_prepare import app, cache
from .data_fetching import RecentAirdrops


@app.route("/api/recent_airdrops")
def get_recent_airdrops():
    data = cache.get("recent_airdrops")

    # If no cache is found, fetch data again, and set the cache.
    if not data:
        data = RecentAirdrops.scrape_data()
        cache.set("recent_airdrops", data, timeout=3600)

    return jsonify(data)
