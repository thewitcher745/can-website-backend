"""
This module contains the data fetching logic for long/short ratio data.
"""

import requests

from ..urls import (
    LONG_SHORT_RATIO_BYBIT,
    LONG_SHORT_RATIO_BINANCE,
    LONG_SHORT_RATIO_OKX,
    LONG_SHORT_RATIO_BITGET,
    LONG_SHORT_RATIO_KRAKEN,
    TICKER,
)


class LongShortRatio:
    def __init__(self, symbol):
        self.symbol = symbol.upper()

        try:
            response = requests.get(TICKER.format(symbol=self.symbol))
            response.raise_for_status()
            self.ticker = float(
                response.json()
                .get("result", None)
                .get("list", None)[0]
                .get("last_price", None)
            )
        except (requests.exceptions.HTTPError, TypeError, IndexError, KeyError):
            self.ticker = None

    def fetch_data(self):
        return {
            "bybit": self.fetch_bybit(),
            "binance": self.fetch_binance(),
            "okx": self.fetch_okx(),
            "bitget": self.fetch_bitget(),
            "kraken": self.fetch_kraken(),
        }

    def fetch_bybit(self):
        url = LONG_SHORT_RATIO_BYBIT.format(symbol=self.symbol)
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            return None

        try:
            orderbook = response.json()["result"]
        except KeyError:
            return None

        try:
            bids = orderbook["b"]
            asks = orderbook["a"]
            total_bids = sum([float(b[1]) for b in bids])
            total_asks = sum([float(a[1]) for a in asks])

            if self.ticker is None:
                return None

            return {
                "long": total_bids * self.ticker,
                "short": total_asks * self.ticker,
                "longPercentage": total_bids / (total_bids + total_asks) * 100,
                "ratio": total_bids / total_asks,
            }
        except KeyError:
            return None

    def fetch_binance(self):
        url = LONG_SHORT_RATIO_BINANCE.format(symbol=self.symbol)

        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            return None

        try:
            bids = response.json()["bids"]
            asks = response.json()["asks"]
            total_bids = sum([float(b[1]) for b in bids])
            total_asks = sum([float(a[1]) for a in asks])

            return {
                "long": total_bids * self.ticker,
                "short": total_asks * self.ticker,
                "longPercentage": total_bids / (total_bids + total_asks) * 100,
                "ratio": total_bids / total_asks,
            }
        except (IndexError, KeyError, TypeError):
            return None

    def fetch_okx(self):
        url = LONG_SHORT_RATIO_OKX.format(symbol=self.symbol)

        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            return None

        try:
            bids = response.json()["data"][0]["bids"]
            asks = response.json()["data"][0]["asks"]
            total_bids = sum([float(b[1]) for b in bids])
            total_asks = sum([float(a[1]) for a in asks])

            return {
                "long": total_bids * self.ticker,
                "short": total_asks * self.ticker,
                "longPercentage": total_bids / (total_bids + total_asks) * 100,
                "ratio": total_bids / total_asks,
            }
        except (IndexError, KeyError, TypeError):
            return None

    def fetch_bitget(self):
        url = LONG_SHORT_RATIO_BITGET.format(symbol=self.symbol)

        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            return None

        try:
            bids = response.json()["data"]["b"]
            asks = response.json()["data"]["a"]
            total_bids = sum([float(b[1]) for b in bids])
            total_asks = sum([float(a[1]) for a in asks])

            return {
                "long": total_bids * self.ticker,
                "short": total_asks * self.ticker,
                "longPercentage": total_bids / (total_bids + total_asks) * 100,
                "ratio": total_bids / total_asks,
            }
        except (IndexError, KeyError, TypeError):
            return None

    def fetch_kraken(self):
        url = LONG_SHORT_RATIO_KRAKEN.format(symbol=self.symbol)

        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            return None

        try:
            result = response.json()["result"]
            # Return the first key from the result
            bids = result[list(result.keys())[0]]["bids"]
            asks = result[list(result.keys())[0]]["asks"]
            total_bids = sum([float(b[1]) for b in bids])
            total_asks = sum([float(a[1]) for a in asks])

            return {
                "long": total_bids * self.ticker,
                "short": total_asks * self.ticker,
                "longPercentage": total_bids / (total_bids + total_asks) * 100,
                "ratio": total_bids / total_asks,
            }
        except (IndexError, KeyError, TypeError):
            return None
