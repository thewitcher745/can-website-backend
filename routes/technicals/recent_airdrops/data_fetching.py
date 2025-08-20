"""
This file contains the code related to fetching the data for the recent airdrops.
This is done through webscraping currently (now with BeautifulSoup).
"""

import requests
from bs4 import BeautifulSoup

from ..urls import RECENT_AIRDROPS


class RecentAirdrops:
    @staticmethod
    def scrape_data() -> list[dict]:
        """
        This method will fetch the list of recent airdrops through webscraping and return
        it in a dict format.

        Returns:
            list[dict]: The list of recent airdrops with the related information.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://airdrops.io/",
            "Connection": "keep-alive",
        }
        response = requests.get(RECENT_AIRDROPS, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        recent_airdrops = []
        for airdrop_article in soup.select("article.airdrop-click"):
            name = airdrop_article.select_one(
                "div > div > div.air-content-front > a > h3"
            ).get_text(
                strip=True,
            )

            img_url = airdrop_article.select_one(
                "div > div > div.air-thumbnail > img"
            ).get("src")

            is_hot = len(airdrop_article.select("div > div > div.droptemp")) > 0

            # The "CONFIRMED" tag is added if the airdrop_article contains the class "confirmed"
            is_confirmed = "confirmed" in airdrop_article.get_attribute_list("class")

            # Same with FEATURED
            is_featured = "featured" in airdrop_article.get_attribute_list("class")

            recent_airdrops.append(
                {
                    "name": name,
                    "img": img_url,
                    "is_hot": is_hot,
                    "is_confirmed": is_confirmed,
                    "is_featured": is_featured,
                }
            )

        return recent_airdrops
