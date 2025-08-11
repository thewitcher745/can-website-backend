"""
This file contains the code related to fetching the data for the top gainers chart/table.
This is done through webscraping currently (now with BeautifulSoup).
"""

import requests
from bs4 import BeautifulSoup
from ..urls import TOP_GAINERS


class TopGainers:
    @staticmethod
    def scrape_data() -> list[dict]:
        """
        This method will fetch the list of top gainers through webscraping and return
        it in a dict format.

        Returns:
            list[dict]: The list of top gainers with the related information.
        """
        response = requests.get(TOP_GAINERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        table = soup.select_one(".cmc-table tbody")
        if not table:
            return []
        table_rows = table.find_all("tr")

        top_gainers = []
        for row in table_rows:
            row_cols = TopGainers.get_row_cols(row)
            coin_full_name = TopGainers.get_coin_full_name(row_cols)
            coin_symbol = TopGainers.get_coin_symbol(row_cols)
            coin_price = TopGainers.get_coin_price(row_cols)
            coin_change = TopGainers.get_coin_change(row_cols)
            coin_volume = TopGainers.get_coin_volume(row_cols)

            top_gainers.append(
                {
                    "coin_full_name": coin_full_name,
                    "coin_symbol": coin_symbol,
                    "coin_price": coin_price,
                    "coin_change": coin_change,
                    "coin_volume": coin_volume,
                }
            )

        return top_gainers

    @staticmethod
    def get_row_cols(row) -> list:
        """
        This method will return the list of columns in a row.
        Args:
            row: The row to get the columns from.
        Returns:
            list: The list of columns in the row.
        """
        return row.find_all("td")

    @staticmethod
    def get_coin_full_name(row_cols: list) -> str:
        """
        This method will extract the coin full name from a row.
        Args:
            row: The row to extract the coin full name from.
        Returns:
            str: The coin full name.
        """
        try:
            # Adjust selector if the structure changes
            return row_cols[1].select_one("a.cmc-link div div p").get_text(strip=True)
        except Exception:
            return ""

    @staticmethod
    def get_coin_symbol(row_cols: list) -> str:
        """
        This method will extract the coin symbol from a row.
        Args:
            row: The row to extract the coin symbol from.
        Returns:
            str: The coin symbol.
        """
        try:
            return (
                row_cols[1].select_one("a.cmc-link div div div p").get_text(strip=True)
            )
        except Exception:
            return ""

    @staticmethod
    def get_coin_price(row_cols: list) -> str:
        """
        This method will extract the coin price from a row.
        Args:
            row: The row to extract the coin price from.
        Returns:
            str: The coin price.
        """
        try:
            return row_cols[2].find("span").get_text(strip=True).replace("$", "")
        except Exception:
            return ""

    @staticmethod
    def get_coin_change(row_cols: list) -> str:
        """
        This method will extract the coin change from a row.
        Args:
            row: The row to extract the coin change from.
        Returns:
            str: The coin change.
        """
        try:
            return row_cols[3].find("span").get_text(strip=True)
        except Exception:
            return ""

    @staticmethod
    def get_coin_volume(row_cols: list) -> str:
        """
        This method will extract the coin volume from a row.
        Args:
            row: The row to extract the coin volume from.
        Returns:
            str: The coin volume.
        """
        try:
            return row_cols[4].get_text(strip=True).replace("$", "")
        except Exception:
            return ""

