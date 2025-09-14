"""
This file contains the code related to fetching the data for the trending cryptocurrencies.
This is done by calling the CoinGecko TRENDING REST API.
"""

import requests
import os
from ..urls import TRENDING


class TrendingCoins:
    @staticmethod
    def scrape_data() -> list[dict]:
        """
        Fetch the list of trending cryptocurrencies from the CoinGecko TRENDING REST API and return
        it in a dict format with selected fields.

        Returns:
            list[dict]: The list of trending coins with the related information.
        """
        api_key = os.getenv("x-cg-demo-api-key")
        if not api_key:
            raise RuntimeError(
                "CoinGecko API key missing in environment variable 'x-cg-demo-api-key'."
            )

        url = TRENDING.replace("x_cg_demo_api_key", api_key)
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        trending_coins = []
        # The API returns a dict with a key 'coins' which is a list of objects, each with an 'item' key
        coins = data.get("coins", [])
        for coin_entry in coins:
            item = coin_entry.get("item", {})
            name = item.get("name", "")
            symbol = item.get("symbol", "")
            price = float(item.get("data", {}).get("price", ""))
            change = float(
                item.get("data", {})
                .get("price_change_percentage_24h", {})
                .get("usd", "")
            )
            volume = float(
                item.get("data", {})
                .get("total_volume", "")
                .replace(",", "")
                .replace("$", "")
            )
            market_cap = float(
                item.get("data", {})
                .get("market_cap", "")
                .replace(",", "")
                .replace("$", "")
            )
            sparkline = item.get("data", {}).get("sparkline", None)

            trending_coins.append(
                {
                    "name": name,
                    "symbol": symbol,
                    "price": price,
                    "change": change,
                    "volume": volume,
                    "market_cap": market_cap,
                    "sparkline": sparkline,
                }
            )
        return trending_coins
