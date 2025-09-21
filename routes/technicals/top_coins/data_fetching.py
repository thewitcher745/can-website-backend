"""
This file contains the code related to fetching the data for the top cryptocurrencies list.
This is done by calling the CoinGecko TRENDING REST API.
"""

import requests
import os

from ..urls import TOP_COINS


class TopCoins:
    @staticmethod
    def fetch_data(n: int = 10) -> list[dict]:
        """
        Fetch the list of top cryptocurrencies from the CoinGecko REST API and return
        it in a dict format with selected fields.

        Args:
            n (int): The number of top coins to fetch.

        Returns:
            list[dict]: The list of top coins with the related information.
        """
        api_key = os.getenv("x-cg-demo-api-key")
        if not api_key:
            raise RuntimeError(
                "CoinGecko API key missing in environment variable 'x-cg-demo-api-key'."
            )

        response = requests.get(
            f"{TOP_COINS}?per_page={n}&page=1&sparkline=true&price_change_percentage=24h,7d,30d&vs_currency=usd"
        )
        response.raise_for_status()
        data = response.json()
        top_coins = []
        # The API returns a dict with a key 'coins' which is a list of objects, each with an 'item' key
        for coin_entry in data:
            id = coin_entry.get("id", "")
            name = coin_entry.get("name", "")
            symbol = coin_entry.get("symbol", "")
            price = float(coin_entry.get("current_price", ""))
            price_change_percentage_24h = float(
                coin_entry.get("price_change_percentage_24h_in_currency", "")
            )
            price_change_percentage_7d = float(
                coin_entry.get("price_change_percentage_7d_in_currency", "")
            )
            price_change_percentage_30d = float(
                coin_entry.get("price_change_percentage_30d_in_currency", "")
            )
            sparkline = coin_entry.get("sparkline_in_7d", None).get("price", [])
            market_cap = float(coin_entry.get("market_cap", ""))
            volume = float(coin_entry.get("total_volume", ""))

            top_coins.append(
                {
                    "name": name,
                    "symbol": symbol,
                    "price": price,
                    "2h_change": price_change_percentage_24h,
                    "7d_change": price_change_percentage_7d,
                    "30d_change": price_change_percentage_30d,
                    "volume": volume,
                    "market_cap": market_cap,
                    "sparkline": sparkline,
                }
            )
        return top_coins
