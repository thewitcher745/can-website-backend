"""
This file contains the code related to fetching the data for the top gainers chart/table.
This is done through webscraping currently (now with BeautifulSoup).
"""

from bs4 import BeautifulSoup
from ..urls import HEATMAP
from playwright.sync_api import sync_playwright


def return_page_after_loading(url, selector=None, wait_time=2000):
    with sync_playwright() as p:
        # Use chromium (it's bundled with Playwright)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Navigate to the page
        page.goto(url, wait_until="domcontentloaded")
        
        # Wait for JavaScript to execute
        page.wait_for_timeout(wait_time)  # Wait for X milliseconds
        
        # Or wait for a specific element
        if selector:
            page.wait_for_selector(selector)
        
        # Get the rendered HTML
        html = page.content()
        browser.close()
        
        return BeautifulSoup(html, 'html.parser')

class CryptoHeatmap:
    @staticmethod
    def scrape_data() -> list[dict]:
        """
        This method will scrape the crypto heatmap (treemap) chart from a URL.

        Returns:
            str: A string form of the HTML in the URL
        """
        chart_selector = "#d3chart"
        soup = return_page_after_loading(HEATMAP, selector=chart_selector)

        chart = soup.select_one(chart_selector)

        return chart.prettify()
