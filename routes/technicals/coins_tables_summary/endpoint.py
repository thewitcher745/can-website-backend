"""
This module will contain the endpoint handlers for the mini gadget containing minified versions of the technical tables,
AKA trending, top gainers and top losers. Result is returned as a dict containing the top 5 for each table.
"""

from flask import jsonify

from app_prepare import app, cache
from ..trending.data_fetching import TrendingCoins
from ..top_gainers.data_fetching import TopGainers
from ..top_losers.data_fetching import TopLosers


def select_top_n(full_list: list, n: int = 5) -> list:
    return full_list[: min(n, len(full_list))]


@app.route("/api/coins_tables_summary")
def get_coins_tables_summary():
    data = cache.get("coins_tables_summary")

    # If no cache is found, fetch data again, and set the cache.
    if not data:
        data = {
            "trending": select_top_n(TrendingCoins.scrape_data()),
            "top_gainers": select_top_n(TopGainers.scrape_data()),
            "top_losers": select_top_n(TopLosers.scrape_data()),
        }
        cache.set("coins_tables_summary", data, timeout=600)

    return jsonify(data)
