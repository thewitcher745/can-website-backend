import requests
from ..urls import MARKET_DATA

def fetch_market_data():
    """
    Fetch BTC and ETH market cap dominance and total market cap change percentage from CoinGecko MARKET_DATA endpoint.

    Returns:
        dict: {
            'btc_dominance': float,
            'eth_dominance': float,
            'market_cap_change_percentage_24h_usd': float
        }
    """
    response = requests.get(MARKET_DATA)
    response.raise_for_status()
    data = response.json().get('data', {})

    market_cap_percentage = data.get('market_cap_percentage', {})
    btc_dominance = market_cap_percentage.get('btc')
    eth_dominance = market_cap_percentage.get('eth')
    market_cap_change_percentage_24h_usd = data.get('market_cap_change_percentage_24h_usd')

    return {
        'btc_dominance': btc_dominance,
        'eth_dominance': eth_dominance,
        'market_cap_change_percentage_24h_usd': market_cap_change_percentage_24h_usd
    }
