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
            # Find the columns of the row to extract the data from.
            cols = TopGainers.get_row_cols(row)

            name = TopGainers.get_name(cols)
            symbol = TopGainers.get_symbol(cols)
            price = TopGainers.get_price(cols)
            change = TopGainers.get_change(cols)
            volume = TopGainers.get_volume(cols)

            top_gainers.append(
                {
                    "name": name,
                    "symbol": symbol,
                    "price": price,
                    "change": change,
                    "volume": volume,
                }
            )

        return top_gainers

    @staticmethod
    def get_row_cols(row) -> list:
        """This method will return the list of columns in a row."""
        return row.find_all("td")

    @staticmethod
    def get_name(cols: list) -> str:
        """Extract the full name of the coin."""
        try:
            return cols[1].select_one("a.cmc-link div div p").get_text(strip=True)
        except Exception:
            return ""

    @staticmethod
    def get_symbol(cols: list) -> str:
        """Extract the symbol of the coin."""
        try:
            return cols[1].select_one("a.cmc-link div div div p").get_text(strip=True)
        except Exception:
            return ""

    @staticmethod
    def get_price(cols: list) -> str:
        """Extract the price of the coin."""
        try:
            return float(cols[2].find("span").get_text(strip=True).replace("$", "").replace(",", ""))
        except Exception:
            return ""

    @staticmethod
    def get_change(cols: list) -> str:
        """Extract the change of the coin."""
        try:
            return float(cols[3].find("span").get_text(strip=True).replace("%", ""))
        except Exception:
            return ""

    @staticmethod
    def get_volume(cols: list) -> str:
        """Extract the volume of the coin."""
        try:
            return int(cols[4].get_text(strip=True).replace("$", "").replace(",", ""))
        except Exception:
            return ""
