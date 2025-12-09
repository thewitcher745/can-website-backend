from flask import jsonify
import requests

from app_prepare import cache, app
from routes.technicals.urls import TICKER


@app.route("/")
def hello():
    return jsonify("The CAN platform backend API branches off here!")


def get_tickers():
    """
    Fetches the ticker list from Binance.
    """
    tickers_data = cache.get("tickers")

    # If no cache is found, fetch data and set the cache.
    if not tickers_data:
        tickers_data = requests.get(TICKER).json()

        cache.set("tickers", tickers_data, timeout=180)

    return tickers_data


def get_ticker_price(symbol: str, default_price: float):
    """
    Fetches the ticker price for a symbol from Binance.
    """
    tickers_data = get_tickers()

    for ticker in tickers_data:
        if ticker.get("symbol") == f"{symbol.upper()}USDT":
            return ticker.get("price")

    return default_price
