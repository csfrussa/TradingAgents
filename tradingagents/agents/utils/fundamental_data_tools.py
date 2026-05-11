from langchain_core.tools import tool
from typing import Annotated
from tradingagents.dataflows.interface import route_to_vendor
from tradingagents.dataflows.crypto_yfinance import get_crypto_info as _get_crypto_info_impl
from tradingagents.dataflows.b3_yfinance import get_b3_stock_info as _get_b3_stock_info_impl


@tool
def get_b3_stock_info(
    symbol: Annotated[str, "B3 ticker in YFinance format, e.g. PETR4.SA, VALE3.SA, KNRI11.SA"],
    curr_date: Annotated[str, "current date YYYY-MM-DD"] = None,
) -> str:
    """
    Retrieve fundamental and market data for a Brazilian stock listed on B3.
    Returns BRL-denominated metrics including P/L (P/E), P/VP (P/B), DY (dividend yield),
    EV/EBITDA, ROE, ROA, share class (ON/PN/Unit/FII/BDR), and CVM context.
    Use this instead of get_fundamentals for B3 assets (asset_type == 'b3').
    Args:
        symbol (str): B3 ticker in YFinance format, e.g. PETR4.SA, VALE3.SA, KNRI11.SA
        curr_date (str): Current date YYYY-MM-DD (optional)
    Returns:
        str: Formatted report with B3 market and fundamental data in BRL
    """
    return _get_b3_stock_info_impl(symbol, curr_date)


@tool
def get_crypto_info(
    symbol: Annotated[str, "crypto ticker symbol, e.g. BTC-USD, ETH-USD"],
    curr_date: Annotated[str, "current date YYYY-MM-DD"] = None,
) -> str:
    """
    Retrieve crypto market data and tokenomics for a cryptocurrency symbol.
    Returns price, market cap, circulating supply, volume, and volatility metrics.
    Use this instead of get_fundamentals/get_balance_sheet for crypto assets.
    Args:
        symbol (str): Crypto ticker, e.g. BTC-USD, ETH-USD, SOL-USD
        curr_date (str): Current date YYYY-MM-DD (optional)
    Returns:
        str: Formatted report with crypto market and tokenomics data
    """
    return _get_crypto_info_impl(symbol, curr_date)


@tool
def get_fundamentals(
    ticker: Annotated[str, "ticker symbol"],
    curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"],
) -> str:
    """
    Retrieve comprehensive fundamental data for a given ticker symbol.
    Uses the configured fundamental_data vendor.
    Args:
        ticker (str): Ticker symbol of the company
        curr_date (str): Current date you are trading at, yyyy-mm-dd
    Returns:
        str: A formatted report containing comprehensive fundamental data
    """
    return route_to_vendor("get_fundamentals", ticker, curr_date)


@tool
def get_balance_sheet(
    ticker: Annotated[str, "ticker symbol"],
    freq: Annotated[str, "reporting frequency: annual/quarterly"] = "quarterly",
    curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"] = None,
) -> str:
    """
    Retrieve balance sheet data for a given ticker symbol.
    Uses the configured fundamental_data vendor.
    Args:
        ticker (str): Ticker symbol of the company
        freq (str): Reporting frequency: annual/quarterly (default quarterly)
        curr_date (str): Current date you are trading at, yyyy-mm-dd
    Returns:
        str: A formatted report containing balance sheet data
    """
    return route_to_vendor("get_balance_sheet", ticker, freq, curr_date)


@tool
def get_cashflow(
    ticker: Annotated[str, "ticker symbol"],
    freq: Annotated[str, "reporting frequency: annual/quarterly"] = "quarterly",
    curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"] = None,
) -> str:
    """
    Retrieve cash flow statement data for a given ticker symbol.
    Uses the configured fundamental_data vendor.
    Args:
        ticker (str): Ticker symbol of the company
        freq (str): Reporting frequency: annual/quarterly (default quarterly)
        curr_date (str): Current date you are trading at, yyyy-mm-dd
    Returns:
        str: A formatted report containing cash flow statement data
    """
    return route_to_vendor("get_cashflow", ticker, freq, curr_date)


@tool
def get_income_statement(
    ticker: Annotated[str, "ticker symbol"],
    freq: Annotated[str, "reporting frequency: annual/quarterly"] = "quarterly",
    curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"] = None,
) -> str:
    """
    Retrieve income statement data for a given ticker symbol.
    Uses the configured fundamental_data vendor.
    Args:
        ticker (str): Ticker symbol of the company
        freq (str): Reporting frequency: annual/quarterly (default quarterly)
        curr_date (str): Current date you are trading at, yyyy-mm-dd
    Returns:
        str: A formatted report containing income statement data
    """
    return route_to_vendor("get_income_statement", ticker, freq, curr_date)