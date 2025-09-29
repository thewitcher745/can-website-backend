"""
This file contains the code related to fetching the data for the crypto heatmap chart.
This is done through a REST API.
"""

import requests
from ..urls import HEATMAP
from utils import round_to_precision
from routes.general import get_ticker_price


class CryptoHeatmap:
    @staticmethod
    def fetch_data():
        """
        Fetches crypto heatmap data from the HEATMAP API endpoint using a regular GET request.

        Returns:
            A list of dictionaries, each representing a cryptocurrency and its market data as per the expected JSON structure.

        Raises:
            requests.HTTPError: If the request fails.
            ValueError: If the response is not valid JSON or is not a list.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
        }
        response = requests.get(HEATMAP, headers=headers)
        response.raise_for_status()

        data = response.json().get("Data").get("LIST")

        if not isinstance(data, list):
            raise ValueError(
                "Expected a list of cryptocurrencies in the JSON response."
            )

        # Keep only the parts of the data that we need.
        filtered = []
        for coin in data:
            default_price = float(coin.get("PRICE_USD"))
            price = get_ticker_price(coin.get("SYMBOL").upper(), default_price)
            volume = float(coin.get("SPOT_MOVING_24_HOUR_QUOTE_VOLUME_DIRECT_USD"))
            symbol = coin.get("SYMBOL").upper()

            filtered.append(
                {
                    "name": coin.get("NAME"),
                    "symbol": symbol,
                    "market_cap": int(coin.get("TOTAL_MKT_CAP_USD")),
                    "total_volume": float(round_to_precision(volume, symbol)),
                    "current_price": float(round_to_precision(price, symbol)),
                    "price_change_percentage_24h": float(
                        coin.get("SPOT_MOVING_24_HOUR_CHANGE_PERCENTAGE_USD")
                    ),
                }
            )

        return filtered
