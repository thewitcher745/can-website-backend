"""
This file contains the code related to fetching the data for the top gainers chart/table.
This is done through webscraping currently.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from .urls import TOP_GAINERS
from ..webscraping_utils import driver


class TopGainers:
    @staticmethod
    def scrape_data() -> list[dict]:
        """
        This method will fetch the list of top gainers through webscraping and return
        it in a dict format.

        Returns:
            list[dict]: The list of top gainers with the related information.
        """

        driver.get(TOP_GAINERS)

        table_rows = driver.find_elements(By.CSS_SELECTOR, ".cmc-table tbody")[
            0
        ].find_elements(By.TAG_NAME, "tr")

        # Iterate through the rows of the table and put each in a dict in a list of dicts
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

        print(top_gainers)  # TODO: Remove this

        return top_gainers

    @staticmethod
    def get_row_cols(row: WebElement) -> list[WebElement]:
        """
        This method will return the list of columns in a row.

        Args:
            row (WebElement): The row to get the columns from.

        Returns:
            list[WebElement]: The list of columns in the row.
        """
        return row.find_elements(By.TAG_NAME, "td")

    @staticmethod
    def get_coin_full_name(row_cols: list[WebElement]) -> str:
        """
        This method will extract the coin full name from a row.

        Args:
            row (WebElement): The row to extract the coin full name from.

        Returns:
            str: The coin full name.
        """
        coin_full_name: str = (
            row_cols[1].find_element(By.CSS_SELECTOR, "a.cmc-link div div p").text
        )

        return coin_full_name

    @staticmethod
    def get_coin_symbol(row_cols: list[WebElement]) -> str:
        """
        This method will extract the coin symbol from a row.

        Args:
            row (WebElement): The row to extract the coin symbol from.

        Returns:
            str: The coin symbol.
        """
        coin_symbol: str = (
            row_cols[1].find_element(By.CSS_SELECTOR, "a.cmc-link div div div p").text
        )

        return coin_symbol

    @staticmethod
    def get_coin_price(row_cols: list[WebElement]) -> str:
        """
        This method will extract the coin price from a row.

        Args:
            row (WebElement): The row to extract the coin price from.

        Returns:
            str: The coin price.
        """
        coin_price: str = (
            row_cols[2].find_element(By.TAG_NAME, "span").text.replace("$", "")
        )

        return coin_price

    @staticmethod
    def get_coin_change(row_cols: list[WebElement]) -> str:
        """
        This method will extract the coin change from a row.

        Args:
            row (WebElement): The row to extract the coin change from.

        Returns:
            str: The coin change.
        """
        coin_change: str = row_cols[3].find_element(By.TAG_NAME, "span").text

        return coin_change

    @staticmethod
    def get_coin_volume(row_cols: list[WebElement]) -> str:
        """
        This method will extract the coin volume from a row.

        Args:
            row (WebElement): The row to extract the coin volume from.

        Returns:
            str: The coin volume.
        """
        coin_volume: str = row_cols[4].text.replace("$", "")

        return coin_volume
