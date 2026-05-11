import re

KNOWN_CRYPTO_SYMBOLS = {
    "BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", "AVAX", "DOT", "MATIC",
    "LINK", "UNI", "LTC", "BCH", "XLM", "ATOM", "ALGO", "VET", "ICP", "FIL",
    "AAVE", "EOS", "XTZ", "EGLD", "THETA", "XMR", "DASH", "NEO", "ZEC",
    "SHIB", "TRX", "NEAR", "FTM", "HBAR", "GRT", "MANA", "SAND", "ENJ", "CHZ",
    "COMP", "YFI", "SNX", "MKR", "CRV", "SUSHI",
    "OP", "ARB", "APT", "SUI", "SEI", "INJ", "TIA",
    "PEPE", "FLOKI", "BONK", "WIF",
    "USDT", "USDC", "BUSD", "DAI",
}

CRYPTO_QUOTE_CURRENCIES = {"USD", "USDT", "USDC", "BTC", "ETH", "BNB", "EUR", "GBP"}


def detect_asset_type(ticker: str) -> str:
    """Return 'crypto', 'b3', or 'stock' for the given ticker.

    Handles YFinance format (BTC-USD), slash format (BTC/USD), and bare symbols (BTC).
    B3 tickers follow the pattern: 4 uppercase letters + 1-2 digits (e.g. PETR4, VALE3, KNRI11).
    """
    ticker = ticker.upper().strip()

    # Normalise separators so we handle both BTC-USD and BTC/USD
    normalised = ticker.replace("/", "-")
    parts = normalised.split("-")

    if len(parts) == 2 and parts[1] in CRYPTO_QUOTE_CURRENCIES:
        return "crypto"
    if parts[0] in KNOWN_CRYPTO_SYMBOLS:
        return "crypto"

    # B3: 4 uppercase letters + 1-2 digits, optionally followed by .SA
    base = ticker.removesuffix(".SA")
    if re.match(r'^[A-Z]{4}\d{1,2}$', base):
        return "b3"

    return "stock"


def normalize_crypto_ticker(ticker: str) -> str:
    """Normalize a crypto ticker to YFinance format (SYMBOL-USD).

    BTC  → BTC-USD
    ETH/USD → ETH-USD
    BTC-USDT → BTC-USDT  (kept as-is)
    AAPL.TO  → AAPL.TO  (stock suffix, untouched)
    """
    ticker = ticker.strip().upper()

    # Slash format: BTC/USD → BTC-USD
    if "/" in ticker:
        ticker = ticker.replace("/", "-")

    # If already has a dash, check if it looks like a crypto pair
    if "-" in ticker:
        base, quote = ticker.split("-", 1)
        if quote in CRYPTO_QUOTE_CURRENCIES:
            return ticker

    # Bare known symbol: BTC → BTC-USD
    if ticker in KNOWN_CRYPTO_SYMBOLS:
        return f"{ticker}-USD"

    return ticker


def normalize_b3_ticker(ticker: str) -> str:
    """Normalize a B3 ticker to YFinance format (append .SA if missing).

    PETR4   → PETR4.SA
    VALE3.SA → VALE3.SA  (already normalized)
    KNRI11  → KNRI11.SA
    """
    ticker = ticker.strip().upper()
    if not ticker.endswith(".SA"):
        return f"{ticker}.SA"
    return ticker
