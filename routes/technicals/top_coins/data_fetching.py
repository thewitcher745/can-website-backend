"""
This file contains the code related to fetching the data for the top cryptocurrencies list.
This is done by calling the CoinGecko TRENDING REST API.
"""

import requests
import os

from ..urls import TOP_COINS


class TopCoins:
    @staticmethod
    def fetch_data(n: int = 10, sort_by: str = "market_cap") -> list[dict]:
        """
        Fetch the list of top cryptocurrencies from the CoinMarketCap REST API and return
        it in a dict format with selected fields.

        Args:
            n (int): The number of top coins to fetch.

        Returns:
            list[dict]: The list of top coins with the related information.
        """
        api_key = os.getenv("CMC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "CoinMarketCap API key missing in environment variable 'CMC_API_KEY'."
            )

        headers = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": api_key,
        }

        response = requests.get(
            f"{TOP_COINS}?limit={n}&sort={sort_by}", headers=headers
        )
        response.raise_for_status()

        data = response.json().get("data")
        top_coins = []
        # The API returns a dict with a key 'coins' which is a list of objects, each with an 'item' key
        for coin_entry in data:
            name = coin_entry.get("name", "")
            symbol = coin_entry.get("symbol", "")
            quote_data = coin_entry.get("quote").get("USD")
            price = float(quote_data.get("price", ""))
            price_change_percentage_24h = float(
                quote_data.get("percent_change_24h", "")
            )
            price_change_percentage_7d = float(
                quote_data.get("percent_change_7d", "")
            )
            market_cap = float(quote_data.get("market_cap", ""))
            volume = float(quote_data.get("volume_24h", ""))

            top_coins.append(
                {
                    "name": name,
                    "symbol": symbol,
                    "price": price,
                    "change_24h": price_change_percentage_24h,
                    "change_7d": price_change_percentage_7d,
                    "volume_24h": volume,
                    "market_cap": market_cap,
                }
            )
        return top_coins
