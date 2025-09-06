from json import load
from os import path

LOGOS_DIR = "./static/cmc-cache"

# Load the JSON data once when the module is imported
with open(path.join(LOGOS_DIR, "logo_links.json")) as f:
    _logo_links_data = load(f)


def get_logo_link_from_symbol(symbol: str) -> str:
    # Returns a link to the logo of a coin with a given symbol.
    return _logo_links_data.get(symbol.upper(), "")
