"""
This file contains the URL's and endpoints for fetching or scraping data.
"""

TOP_GAINERS_LOSERS = "https://coinmarketcap.com/gainers-losers/"
TRENDING = "https://api.coingecko.com/api/v3/search/trending"
HEATMAP = "https://data-api.coindesk.com/asset/v1/top/list?page=1&page_size=100&sort_by=CIRCULATING_MKT_CAP_USD&sort_direction=DESC&groups=ID,PRICE,MKT_CAP,VOLUME,CHANGE,BASIC&toplist_quote_asset=USD"
RECENT_AIRDROPS = "https://airdrops.io/latest/"
FEAR_AND_GREED = "https://pro-api.coinmarketcap.com/v3/fear-and-greed/latest"
FEAR_AND_GREED_HISTORICAL = (
    "https://pro-api.coinmarketcap.com/v3/fear-and-greed/historical"
)
MARKET_DATA = "https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest"
TOP_COINS = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
LONG_SHORT_RATIO_BYBIT = "https://api.bybit.com/v5/market/orderbook?category=linear&symbol={symbol}USDT&limit=500"
LONG_SHORT_RATIO_BINANCE = (
    "https://fapi.binance.com/fapi/v1/depth?symbol={symbol}USDT&limit=1000"
)
LONG_SHORT_RATIO_OKX = (
    "https://www.okx.com/api/v5/market/books-full?instId={symbol}-USDT&sz=500"
)
LONG_SHORT_RATIO_BITGET = "https://api.bitget.com/api/v3/market/orderbook?category=USDT-FUTURES&symbol={symbol}USDT&limit=200"
LONG_SHORT_RATIO_KRAKEN = (
    "https://api.kraken.com/0/public/Depth?pair={symbol}USDT&count=500"
)
TICKER = "https://fapi.binance.com/fapi/v2/ticker/price"
