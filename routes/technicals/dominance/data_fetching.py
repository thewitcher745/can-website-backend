import requests
import os

from ..urls import MARKET_DATA


def fetch_dominance_data():
    """
    Fetch BTC and ETH market cap dominance and their change percentage from CoinGecko MARKET_DATA endpoint.

    Returns:
        dict: {
            'btcDominance': float,
            'ethDominance': float,
            'btcDominanceChange': float,
            'ethDominanceChange': float,
        }
    """
    api_key = os.getenv("CMC_API_KEY")
    if not api_key:
        raise RuntimeError("CMC API key missing in environment variable 'CMC_API_KEY'.")

    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": api_key,
    }
    response = requests.get(MARKET_DATA, headers=headers)
    response.raise_for_status()
    data = response.json().get("data", {})

    btc_dominance = data.get("btc_dominance")
    eth_dominance = data.get("eth_dominance")
    btc_dominance_change = data.get("btc_dominance_24h_percentage_change")
    eth_dominance_change = data.get("eth_dominance_24h_percentage_change")

    return {
        "btcDominance": btc_dominance,
        "ethDominance": eth_dominance,
        "btcDominanceChange": btc_dominance_change,
        "ethDominanceChange": eth_dominance_change,
    }