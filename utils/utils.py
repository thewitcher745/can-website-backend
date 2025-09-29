from os import path, getcwd
import random
import json


def get_slug(filename):
    # Extract the slug from the filename

    return path.splitext(path.basename(filename))[0]


def get_random_thumbnail(seed: str = None):
    # Gets a random thumbnail link from the cached links with a seed, if provided
    with open(path.join(getcwd(), "static/thumbnail_placeholders.json"), "r") as f:
        if seed:
            random.seed(seed)
        return random.choice(json.load(f))


def get_price_precision(symbol: str):
    with open(path.join(getcwd(), "static/precisions.json"), "r") as f:
        return json.load(f).get(symbol, 7)


def round_to_precision(price: float, symbol: str):
    "Returns the rounded price based on the symbol's precision in string format, with exactly the right number of decimal points."
    return f"{float(price):.{get_price_precision(symbol)}f}"
