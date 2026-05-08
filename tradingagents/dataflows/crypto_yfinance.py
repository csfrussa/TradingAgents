from datetime import datetime
from typing import Annotated

import yfinance as yf

from .stockstats_utils import yf_retry


def get_crypto_info(
    symbol: Annotated[str, "crypto ticker symbol, e.g. BTC-USD, ETH-USD"],
    curr_date: Annotated[str, "current date YYYY-MM-DD (unused, kept for interface parity)"] = None,
) -> str:
    """Fetch crypto-specific market data and tokenomics from YFinance.

    Returns price, market cap, supply schedule, volume, and volatility metrics.
    Traditional equity metrics (P/E, EPS, dividends) are omitted — they don't
    apply to decentralised assets.
    """
    try:
        ticker_obj = yf.Ticker(symbol.upper())
        info = yf_retry(lambda: ticker_obj.info)

        if not info:
            return f"No data found for crypto symbol '{symbol}'"

        fields = [
            ("Symbol", info.get("symbol")),
            ("Name", info.get("longName") or info.get("shortName")),
            ("Current Price (USD)", info.get("currentPrice") or info.get("regularMarketPrice")),
            ("Previous Close", info.get("previousClose") or info.get("regularMarketPreviousClose")),
            ("Open", info.get("open") or info.get("regularMarketOpen")),
            ("Day High", info.get("dayHigh") or info.get("regularMarketDayHigh")),
            ("Day Low", info.get("dayLow") or info.get("regularMarketDayLow")),
            ("Market Cap (USD)", info.get("marketCap")),
            ("24h Volume (USD)", info.get("volume24Hr") or info.get("regularMarketVolume")),
            ("Circulating Supply", info.get("circulatingSupply")),
            ("Total Supply", info.get("totalSupply")),
            ("Max Supply", info.get("maxSupply")),
            ("52-Week High", info.get("fiftyTwoWeekHigh")),
            ("52-Week Low", info.get("fiftyTwoWeekLow")),
            ("50-Day Average", info.get("fiftyDayAverage")),
            ("200-Day Average", info.get("twoHundredDayAverage")),
            ("Beta (3-Year)", info.get("beta3Year") or info.get("beta")),
            ("YTD Return", info.get("ytdReturn")),
            ("Exchange", info.get("exchange")),
            ("Currency", info.get("currency")),
            ("Algorithm", info.get("algorithm")),
            ("Start Date", info.get("startDate")),
        ]

        lines = []
        for label, value in fields:
            if value is not None:
                lines.append(f"{label}: {value}")

        header = (
            f"# Crypto Market Data for {symbol.upper()}\n"
            f"# Cryptocurrencies trade 24/7 — no market hours or circuit breakers.\n"
            f"# Traditional equity metrics (P/E, EPS, dividends) do not apply.\n"
            f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        )

        return header + "\n".join(lines)

    except Exception as e:
        return f"Error retrieving crypto info for {symbol}: {str(e)}"
