"""
This module will contain the endpoint handlers for the fear and greed gadget.
"""

from flask import jsonify, request
import requests
import os

from app_prepare import app, cache
from ..urls import FEAR_AND_GREED, FEAR_AND_GREED_HISTORICAL


@app.route("/api/fng")
def get_fng():
    data = cache.get("fng")

    # If no cache is found, fetch data again, and set the cache.
    if not data:
        API_KEY = os.getenv("CMC_API_KEY")
        headers = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": API_KEY,
        }
        data = requests.get(FEAR_AND_GREED, headers=headers).json().get("data", {})
        cache.set("fng", data, timeout=3600)

    return jsonify(data)


@app.route("/api/fng_historical")
def get_fng_historical():
    limit = request.args.get("limit", 180)
    data = cache.get(f"fng_historical_{limit}")

    # If no cache is found, fetch data again, and set the cache.
    if not data:
        API_KEY = os.getenv("CMC_API_KEY")
        headers = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": API_KEY,
        }
        data = (
            requests.get(f"{FEAR_AND_GREED_HISTORICAL}?limit={limit}", headers=headers)
            .json()
            .get("data", {})
        )
        print(len(data))
        cache.set(f"fng_historical_{limit}", data, timeout=86400)

    return jsonify(data)
