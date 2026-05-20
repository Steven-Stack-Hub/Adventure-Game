#!/usr/bin/env python3
"""AI Trader for crypto arbitrage.
This script fetches live spot prices from public exchange APIs, compares quotes,
and identifies potential cross-exchange arbitrage opportunities.
"""

import math
import sys
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

import requests

EXCHANGES = {
    "Binance": {
        "url": "https://api.binance.com/api/v3/ticker/price",
        "mapper": lambda symbol: symbol.replace("/", ""),
        "params": lambda symbol: {"symbol": symbol},
        "extract": lambda data: float(data["price"]),
    },
    "KuCoin": {
        "url": "https://api.kucoin.com/api/v1/market/orderbook/level1",
        "mapper": lambda symbol: symbol.replace("/", "-"),
        "params": lambda symbol: {"symbol": symbol},
        "extract": lambda data: float(data["price"]),
    },
    "Coinbase": {
        "url": "https://api.coinbase.com/v2/prices/{symbol}/spot",
        "mapper": lambda symbol: symbol.replace("/", "-"),
        "params": lambda symbol: {},
        "extract": lambda data: float(data["data"]["amount"]),
    },
}

MARKETS = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
FEE_RATE = 0.001  # 0.1% fee per leg
MIN_NET_SPREAD = 0.0025  # 0.25% net profit threshold


@dataclass
class Quote:
    exchange: str
    symbol: str
    price: float
    fetched_at: float


def fetch_price(exchange_name: str, symbol: str) -> Optional[Quote]:
    config = EXCHANGES[exchange_name]
    mapped = config["mapper"](symbol)
    url = config["url"].format(symbol=mapped)
    params = config["params"](mapped)

    try:
        response = requests.get(url, params=params, timeout=6)
        response.raise_for_status()
        data = response.json()
        price = config["extract"](data)
        return Quote(exchange=exchange_name, symbol=symbol, price=price, fetched_at=time.time())
    except Exception as exc:
        print(f"Warning: failed to fetch {symbol} from {exchange_name}: {exc}")
        return None


def collect_quotes(symbol: str) -> List[Quote]:
    quotes: List[Quote] = []
    for exchange in EXCHANGES:
        quote = fetch_price(exchange, symbol)
        if quote is not None:
            quotes.append(quote)
    return quotes


def find_arbitrage(quotes: List[Quote]) -> Optional[Dict[str, object]]:
    if len(quotes) < 2:
        return None

    best_opportunity: Optional[Dict[str, object]] = None
    for buy in quotes:
        for sell in quotes:
            if buy.exchange == sell.exchange:
                continue
            gross_spread = (sell.price - buy.price) / buy.price
            net_spread = gross_spread - 2 * FEE_RATE
            if net_spread <= MIN_NET_SPREAD:
                continue
            profit = net_spread * 100
            if best_opportunity is None or net_spread > best_opportunity["net_spread"]:
                best_opportunity = {
                    "symbol": buy.symbol,
                    "buy_exchange": buy.exchange,
                    "buy_price": buy.price,
                    "sell_exchange": sell.exchange,
                    "sell_price": sell.price,
                    "gross_spread": gross_spread,
                    "net_spread": net_spread,
                    "profit_pct": profit,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
                }
    return best_opportunity


def ai_signal(opportunity: Dict[str, object]) -> str:
    score = opportunity["net_spread"]
    if score > 0.01:
        action = "strong"
    elif score > 0.005:
        action = "moderate"
    else:
        action = "weak"
    return (
        f"AI arbitrage signal: {action.upper()} opportunity for {opportunity['symbol']} — "
        f"BUY on {opportunity['buy_exchange']} at {opportunity['buy_price']:.2f}, "
        f"SELL on {opportunity['sell_exchange']} at {opportunity['sell_price']:.2f}. "
        f"Estimated net profit {opportunity['profit_pct']:.2f}% after fees."
    )


def print_quotes(quotes: List[Quote]) -> None:
    print("\nLive quotes:")
    for quote in sorted(quotes, key=lambda q: (q.symbol, q.exchange)):
        print(f"  {quote.symbol} on {quote.exchange}: {quote.price:.6f}")


def select_symbol() -> str:
    print("Available market symbols:")
    for idx, symbol in enumerate(MARKETS, start=1):
        print(f"  {idx}. {symbol}")
    choice = input("Choose a symbol number or type a symbol: ").strip()
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(MARKETS):
            return MARKETS[idx]
    if choice.upper() in MARKETS:
        return choice.upper()
    print(f"Invalid choice, defaulting to {MARKETS[0]}")
    return MARKETS[0]


def main() -> int:
    print("AI Trader: Crypto Arbitrage Scanner")
    symbol = select_symbol()
    quotes = collect_quotes(symbol)
    if not quotes:
        print("No quotes were fetched. Check your internet connection or the exchange APIs.")
        return 1
    print_quotes(quotes)

    opportunity = find_arbitrage(quotes)
    if opportunity:
        print("\nArbitrage opportunity found!")
        print(ai_signal(opportunity))
    else:
        print("\nNo arbitrage opportunity above threshold was found.")
        print("Try a different symbol or run again later.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
