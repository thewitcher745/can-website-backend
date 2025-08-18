"""
This file contains the code related to fetching the data for the trending cryptocurrencies.
This is done through webscraping with BeautifulSoup.
"""

import requests
from bs4 import BeautifulSoup
from ..urls import TRENDING


class TrendingCoins:
    @staticmethod
    def scrape_data() -> list[dict]:
        """
        This method will fetch the list of trending cryptocurrencies through webscraping and return
        it in a dict format.

        Returns:
            list[dict]: The list of trending coins with the related information.
        """
        response = requests.get(TRENDING)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        table = soup.select_one(".cmc-table tbody")
        if not table:
            return []
        table_rows = table.find_all("tr")

        trending_coins = []
        for row in table_rows:
            row_cols = TrendingCoins.get_row_cols(row)
            name = TrendingCoins.get_name(row_cols)
            symbol = TrendingCoins.get_symbol(row_cols)
            price = TrendingCoins.get_price(row_cols)
            change_24h = TrendingCoins.get_change_24h(row_cols)
            change_7d = TrendingCoins.get_change_7d(row_cols)
            change_30d = TrendingCoins.get_change_30d(row_cols)
            market_cap = TrendingCoins.get_market_cap(row_cols)
            volume_24h = TrendingCoins.get_volume_24h(row_cols)

            trending_coins.append(
                {
                    "name": name,
                    "symbol": symbol,
                    "price": price,
                    "change_24h": change_24h,
                    "change_7d": change_7d,
                    "change_30d": change_30d,
                    "market_cap": market_cap,
                    "volume_24h": volume_24h,
                }
            )

        return trending_coins

    @staticmethod
    def get_row_cols(row):
        """Extract all columns from a table row."""
        return row.find_all("td")

    @staticmethod
    def get_name(cols):
        """Extract the full name of the coin."""
        try:
            return cols[2].select_one("a.cmc-link div div p").get_text(strip=True)
        except Exception:
            return ""

    @staticmethod
    def get_symbol(cols):
        """Extract the symbol of the coin."""
        try:
            return cols[2].select_one("a.cmc-link div div div p").get_text(strip=True)
        except Exception:
            return ""

    @staticmethod
    def get_price(cols):
        """Extract the price of the coin."""
        try:
            return cols[3].get_text(strip=True).replace("$", "")
        except Exception:
            return ""

    @staticmethod
    def get_change_24h(cols):
        """
        Extract the 24h price change percentage of the coin. Gets the sign of
        the change from a classname of the 'caret' icon elemet.
        """
        try:
            caret_element = cols[4].find("span").find("span")
            # If the element has a class of "icon-Caret-down", the sign is negative.
            if "icon-Caret-down" in caret_element.get("class"):
                return -float(
                    cols[4].find("span").get_text(strip=True).replace("%", "")
                )
            # If the element has a class of "icon-Caret-up", the sign is positive.
            else:
                return float(cols[4].find("span").get_text(strip=True).replace("%", ""))
        except Exception:
            return ""

    @staticmethod
    def get_change_7d(cols):
        """Extract the 7d price change percentage of the coin."""
        try:
            caret_element = cols[5].find("span").find("span")
            # If the element has a class of "icon-Caret-down", the sign is negative.
            if "icon-Caret-down" in caret_element.get("class"):
                return -float(
                    cols[5].find("span").get_text(strip=True).replace("%", "")
                )
            # If the element has a class of "icon-Caret-up", the sign is positive.
            else:
                return float(cols[5].find("span").get_text(strip=True).replace("%", ""))
        except Exception:
            return ""

    @staticmethod
    def get_change_30d(cols):
        """Extract the 30d price change percentage of the coin."""
        try:
            caret_element = cols[6].find("span").find("span")
            # If the element has a class of "icon-Caret-down", the sign is negative.
            if "icon-Caret-down" in caret_element.get("class"):
                return -float(
                    cols[6].find("span").get_text(strip=True).replace("%", "")
                )
            # If the element has a class of "icon-Caret-up", the sign is positive.
            else:
                return float(cols[6].find("span").get_text(strip=True).replace("%", ""))
        except Exception:
            return ""

    @staticmethod
    def get_market_cap(cols):
        """Extract the market cap of the coin."""
        try:
            return cols[7].get_text(strip=True).replace("$", "")
        except Exception:
            return ""

    @staticmethod
    def get_volume_24h(cols):
        """Extract the 24h volume of the coin."""
        try:
            return cols[8].get_text(strip=True).replace("$", "")
        except Exception:
            return ""
