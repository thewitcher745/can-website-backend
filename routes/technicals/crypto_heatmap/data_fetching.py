"""
This file contains the code related to fetching the data for the crypto heatmap chart.
This is done through a REST API.
"""

import requests
from ..urls import HEATMAP


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

        data = response.json()

        if not isinstance(data, list):
            raise ValueError(
                "Expected a list of cryptocurrencies in the JSON response."
            )

        # Keep only the parts of the data that we need.
        filtered = []
        for coin in data:
            filtered.append(
                {
                    "name": coin.get("name"),
                    "symbol": coin.get("symbol").upper(),
                    "market_cap": int(coin.get("market_cap")),
                    "total_volume": float(coin.get("total_volume")),
                    "current_price": float(coin.get("current_price")),
                    "price_change_percentage_24h": float(
                        coin.get("price_change_percentage_24h")
                    ),
                }
            )

        return filtered
