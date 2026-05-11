from datetime import datetime
from typing import Annotated

import yfinance as yf

from .stockstats_utils import yf_retry

# Map digit suffix to share class for contextual annotation
_SHARE_CLASS = {
    "3": "ON (Ordinária — voting)",
    "4": "PN (Preferencial — preferred, typically higher liquidity)",
    "5": "PNA",
    "6": "PNB",
    "8": "PNE",
    "11": "Unit / FII / ETF",
    "34": "BDR (Brazilian Depositary Receipt)",
}


def _infer_share_class(ticker: str) -> str:
    """Return share class description based on numeric suffix (e.g. PETR4 → PN)."""
    base = ticker.upper().removesuffix(".SA")
    digits = "".join(c for c in base if c.isdigit())
    return _SHARE_CLASS.get(digits, f"Class {digits}")


def get_b3_stock_info(
    symbol: Annotated[str, "B3 ticker in YFinance format, e.g. PETR4.SA, VALE3.SA, KNRI11.SA"],
    curr_date: Annotated[str, "current date YYYY-MM-DD (unused, kept for interface parity)"] = None,
) -> str:
    """Fetch B3-specific fundamental and market data from YFinance.

    Returns BRL-denominated metrics, share class, dividend policy (JCP vs dividends),
    Ibovespa membership, and key valuation ratios relevant to Brazilian equities.
    Traditional equity reporting differs from the US: companies report under IFRS/BR GAAP,
    pay dividends quarterly, and may distribute Juros sobre Capital Próprio (JCP).
    """
    try:
        ticker_obj = yf.Ticker(symbol.upper())
        info = yf_retry(lambda: ticker_obj.info)

        if not info:
            return f"No data found for B3 symbol '{symbol}'"

        share_class = _infer_share_class(symbol)

        fields = [
            ("Symbol", info.get("symbol")),
            ("Company Name", info.get("longName") or info.get("shortName")),
            ("Share Class", share_class),
            ("Exchange", info.get("exchange")),
            ("Currency", info.get("currency", "BRL")),
            ("Sector", info.get("sector")),
            ("Industry", info.get("industry")),
            ("Country", info.get("country")),
            # Price metrics
            ("Current Price (BRL)", info.get("currentPrice") or info.get("regularMarketPrice")),
            ("Previous Close (BRL)", info.get("previousClose") or info.get("regularMarketPreviousClose")),
            ("Day High (BRL)", info.get("dayHigh") or info.get("regularMarketDayHigh")),
            ("Day Low (BRL)", info.get("dayLow") or info.get("regularMarketDayLow")),
            ("52-Week High (BRL)", info.get("fiftyTwoWeekHigh")),
            ("52-Week Low (BRL)", info.get("fiftyTwoWeekLow")),
            ("50-Day Average (BRL)", info.get("fiftyDayAverage")),
            ("200-Day Average (BRL)", info.get("twoHundredDayAverage")),
            # Size & liquidity
            ("Market Cap (BRL)", info.get("marketCap")),
            ("Enterprise Value (BRL)", info.get("enterpriseValue")),
            ("Volume (shares)", info.get("regularMarketVolume") or info.get("volume")),
            ("Average Volume 10d", info.get("averageVolume10days")),
            ("Float Shares", info.get("floatShares")),
            ("Shares Outstanding", info.get("sharesOutstanding")),
            # Brazilian valuation ratios (P/L = P/E, P/VP = P/B, DY = Dividend Yield)
            ("P/L (Price/Earnings)", info.get("trailingPE")),
            ("P/L Forward", info.get("forwardPE")),
            ("P/VP (Price/Book)", info.get("priceToBook")),
            ("EV/EBITDA", info.get("enterpriseToEbitda")),
            ("EV/Revenue", info.get("enterpriseToRevenue")),
            ("PEG Ratio", info.get("pegRatio")),
            # Profitability
            ("Revenue (BRL)", info.get("totalRevenue")),
            ("EBITDA (BRL)", info.get("ebitda")),
            ("Net Income (BRL)", info.get("netIncomeToCommon")),
            ("Gross Margin", info.get("grossMargins")),
            ("EBITDA Margin", info.get("ebitdaMargins")),
            ("Net Profit Margin", info.get("profitMargins")),
            ("Operating Margin", info.get("operatingMargins")),
            # Returns
            ("ROE (Return on Equity)", info.get("returnOnEquity")),
            ("ROA (Return on Assets)", info.get("returnOnAssets")),
            # Dividends — Brazilian companies may pay via JCP (tax-deductible dividend substitute)
            ("Dividend Yield (DY)", info.get("dividendYield")),
            ("Trailing Annual Dividend Rate (BRL)", info.get("trailingAnnualDividendRate")),
            ("Payout Ratio", info.get("payoutRatio")),
            ("Last Dividend Date", info.get("lastDividendDate")),
            # Debt & balance sheet
            ("Total Debt (BRL)", info.get("totalDebt")),
            ("Total Cash (BRL)", info.get("totalCash")),
            ("Debt/Equity Ratio", info.get("debtToEquity")),
            ("Current Ratio", info.get("currentRatio")),
            ("Book Value per Share (BRL)", info.get("bookValue")),
            # Analyst consensus
            ("Analyst Recommendation", info.get("recommendationKey")),
            ("Target Mean Price (BRL)", info.get("targetMeanPrice")),
            ("Number of Analyst Opinions", info.get("numberOfAnalystOpinions")),
            # Volatility
            ("Beta (5Y Monthly)", info.get("beta")),
            ("52-Week Change", info.get("52WeekChange")),
        ]

        lines = []
        for label, value in fields:
            if value is not None:
                lines.append(f"{label}: {value}")

        header = (
            f"# B3 Stock Data for {symbol.upper()}\n"
            f"# Exchange: B3 (Brasil, Bolsa, Balcão) — São Paulo, Brazil\n"
            f"# Market hours: 10:00–17:00 BRT (UTC-3), Mon–Fri\n"
            f"# Benchmark index: Ibovespa (IBOV)\n"
            f"# Regulatory body: CVM (Comissão de Valores Mobiliários)\n"
            f"# Financial reports: ITR (quarterly) and DFP (annual) filed with CVM\n"
            f"# Dividend note: Brazilian companies may pay Juros sobre Capital Próprio (JCP)\n"
            f"#   as a tax-efficient substitute for dividends — both count toward total yield.\n"
            f"# Currency: BRL (Brazilian Real). SELIC rate directly impacts cost of capital\n"
            f"#   and valuation multiples for all Brazilian equities.\n"
            f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        )

        return header + "\n".join(lines)

    except Exception as e:
        return f"Error retrieving B3 info for {symbol}: {str(e)}"
