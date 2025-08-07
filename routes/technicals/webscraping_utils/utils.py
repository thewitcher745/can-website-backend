"""
This file would contain the common functions used in webscraping for data.
"""

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

driver_options = Options()
driver_options.add_argument("--headless")
driver = webdriver.Firefox(options=driver_options)
