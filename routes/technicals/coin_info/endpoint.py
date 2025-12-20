"""
This module contains the endpoint handlers for the crypto details page.
"""

from flask import jsonify, request

from app_prepare import app, cache
from .data_fetching import CoinInfo


def _normalize_symbol(symbol_arg: str | None) -> str | None:
    if not symbol_arg:
        return None
    return symbol_arg.strip().lower().replace("usdt", "")


@app.route("/api/coin_info/cmc")
def get_cmc():
    symbol = _normalize_symbol(request.args.get("symbol"))
    if not symbol:
        return jsonify({"error": "Symbol not provided"}), 400

    cache_key = f"coin_info_cmc_{symbol}"
    cached = cache.get(cache_key)
    if cached:
        return jsonify(cached)

    try:
        data = CoinInfo.fetch_cmc(symbol)
    except Exception as exc:
        return (
            jsonify(
                {"error": "Unable to fetch data from CoinMarketCap", "detail": str(exc)}
            ),
            502,
        )

    cache.set(cache_key, data, timeout=900)
    return jsonify(data)


@app.route("/api/coin_info/meta")
def get_meta():
    symbol = _normalize_symbol(request.args.get("symbol"))
    if not symbol:
        return jsonify({"error": "Symbol not provided"}), 400

    cache_key = f"coin_info_meta_{symbol}"
    cached = cache.get(cache_key)
    if cached:
        return jsonify(cached)

    try:
        data = CoinInfo.fetch_meta(symbol)
    except Exception as exc:
        return (
            jsonify(
                {
                    "error": "Unable to fetch meta data from CoinMarketCap",
                    "detail": str(exc),
                }
            ),
            502,
        )

    # Meta data changes infrequently, so cache for 24h.
    cache.set(cache_key, data, timeout=86400)
    return jsonify(data)



@app.route("/api/coin_info/chart")
def get_chart():
    symbol = _normalize_symbol(request.args.get("symbol"))
    period = int(request.args.get("period", 30))
    if not symbol:
        return jsonify({"error": "Symbol not provided"}), 400

    cache_key = f"coin_info_chart_{symbol}_{period}"
    cached = cache.get(cache_key)
    if cached:
        return jsonify(cached)

    try:
        data = CoinInfo.fetch_chart_data(symbol.upper(), period)
    except Exception as exc:
        return (
            jsonify(
                {
                    "error": "Unable to fetch chart data from Binance API",
                    "detail": str(exc),
                }
            ),
            502,
        )

    # Chart data changes over time, so cache for 1h.
    cache.set(cache_key, data, timeout=3600)
    return jsonify(data)
