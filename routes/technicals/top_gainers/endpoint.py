from flask import jsonify

from app_prepare import app
from .data_fetching import TopGainers


@app.route("/api/top_gainers")
def get_top_gainers():
    return jsonify(TopGainers.scrape_data())
