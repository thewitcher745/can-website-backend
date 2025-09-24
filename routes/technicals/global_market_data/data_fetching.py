import requests
import os

from ..urls import MARKET_DATA


def fetch_global_market_data():
    """
    Fetch global market data including the total market cap change percentage and the total volume change percentage from CoinGecko MARKET_DATA endpoint.

    Returns:
        dict: {
            'marketCapChangePercentage24h': float,
            'volumeChangePercentage24h': float,
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
    quote_data = data.get("quote", {}).get("USD", {})

    active_exchanges = data.get("active_exchanges")
    active_currencies = data.get("active_cryptocurrencies")

    
    total_market_cap = data.get("quote", {}).get("USD", {}).get("total_market_cap")
    total_volume_24h = data.get("quote", {}).get("USD", {}).get("total_volume_24h")
    market_cap_change_percentage_24h_usd = quote_data.get(
        "total_market_cap_yesterday_percentage_change"
    )
    volume_change_percentage_24h = quote_data.get(
        "total_volume_24h_yesterday_percentage_change"
    )

    return {
        "activeExchanges": active_exchanges,
        "activeCurrencies": active_currencies,
        "totalMarketCap": total_market_cap,
        "marketCapChangePercentage24h": market_cap_change_percentage_24h_usd,
        "volumeChangePercentage24h": volume_change_percentage_24h,
        "totalVolume24h": total_volume_24h,
    }
