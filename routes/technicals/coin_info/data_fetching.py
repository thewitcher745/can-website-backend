"""The code in this file fetches the data related to the separated coin information webpage."""

import os
from typing import Any, Dict, Optional

import requests

from ..urls import COIN_INFO_META, COIN_INFO_CMC


class CoinInfo:
    @staticmethod
    def _extract_asset(data: Dict[str, Any], symbol: str) -> Dict[str, Any]:
        """
        Normalize the CMC response which can be keyed by symbol or numerical id.
        """
        symbol_key = symbol.upper()
        asset: Optional[Any] = data.get(symbol_key)

        if asset is None and len(data) == 1:
            asset = next(iter(data.values()))
        elif asset is None:
            # Try fallback by slug/id match
            asset = next(iter(data.values()), None)

        if isinstance(asset, list):
            asset = asset[0] if asset else None

        if not isinstance(asset, dict):
            raise ValueError("Unexpected asset payload returned by CoinMarketCap.")

        return asset

    @staticmethod
    def fetch_cmc(symbol: str) -> dict:
        """
        Fetch the part of the coin information that comes from CMC. This includes everything except the coin's chart data.

        Args:
            symbol (str): The symbol of the coin.

        Returns:
            dict: Normalized coin information pulled from CoinMarketCap.
        """
        api_key = os.getenv("CMC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "CoinMarketCap API key missing in environment variable 'CMC_API_KEY'."
            )

        headers = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": api_key,
        }

        response = requests.get(COIN_INFO_CMC.format(symbol=symbol), headers=headers)
        response.raise_for_status()

        data = response.json().get("data")
        if not isinstance(data, dict) or not data:
            raise ValueError("Unexpected response shape received from CoinMarketCap.")

        asset = CoinInfo._extract_asset(data, symbol)
        quote_usd = asset.get("quote", {}).get("USD", {})

        return {
            "name": asset.get("name"),
            "symbol": asset.get("symbol"),
            "market_cap": quote_usd.get("market_cap"),
            "diluted_market_cap": quote_usd.get("fully_diluted_market_cap"),
            "volume_24h": quote_usd.get("volume_24h"),
            "change_1h": quote_usd.get("percent_change_1h"),
            "change_24h": quote_usd.get("percent_change_24h"),
            "change_7d": quote_usd.get("percent_change_7d"),
            "change_30d": quote_usd.get("percent_change_30d"),
            "dominance": quote_usd.get("market_cap_dominance"),
            "rank": asset.get("cmc_rank"),
        }

    @staticmethod
    def fetch_meta(symbol: str) -> dict:
        """
        Fetch the meta information of the coin.

        Args:
            symbol (str): The symbol of the coin.

        Returns:
            dict: Normalized coin information pulled from CoinMarketCap.
        """
        api_key = os.getenv("CMC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "CoinMarketCap API key missing in environment variable 'CMC_API_KEY'."
            )

        headers = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": api_key,
        }

        response = requests.get(COIN_INFO_META.format(symbol=symbol), headers=headers)
        response.raise_for_status()
        data = response.json().get("data")
        if not isinstance(data, dict) or not data:
            raise ValueError("Unexpected response shape received from CoinMarketCap.")

        asset = CoinInfo._extract_asset(data, symbol)
        urls = asset.get("urls") or {}
        normalized_urls = {
            key: [link for link in value if isinstance(link, str) and link]
            for key, value in urls.items()
            if isinstance(value, list)
        }

        return {
            "name": asset.get("name"),
            "symbol": asset.get("symbol"),
            "description": asset.get("description"),
            "logo": asset.get("logo"),
            "urls": normalized_urls,
        }
