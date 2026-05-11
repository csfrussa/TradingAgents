import unittest

import pytest

from cli.utils import normalize_ticker_symbol
from tradingagents.agents.utils.agent_utils import build_instrument_context
from tradingagents.dataflows.asset_detection import detect_asset_type, normalize_b3_ticker


@pytest.mark.unit
class TickerSymbolHandlingTests(unittest.TestCase):
    def test_normalize_ticker_symbol_preserves_exchange_suffix(self):
        self.assertEqual(normalize_ticker_symbol(" cnc.to "), "CNC.TO")

    def test_build_instrument_context_mentions_exact_symbol(self):
        context = build_instrument_context("7203.T")
        self.assertIn("7203.T", context)
        self.assertIn("exchange suffix", context)


@pytest.mark.unit
class B3AssetDetectionTests(unittest.TestCase):
    # --- detection ---
    def test_detects_on_share(self):
        self.assertEqual(detect_asset_type("PETR4"), "b3")

    def test_detects_pn_share(self):
        self.assertEqual(detect_asset_type("VALE3"), "b3")

    def test_detects_unit_fii(self):
        self.assertEqual(detect_asset_type("KNRI11"), "b3")

    def test_detects_etf(self):
        self.assertEqual(detect_asset_type("BOVA11"), "b3")

    def test_detects_bdr(self):
        self.assertEqual(detect_asset_type("MSFT34"), "b3")

    def test_detects_with_sa_suffix(self):
        self.assertEqual(detect_asset_type("VALE3.SA"), "b3")

    def test_detects_lowercase_input(self):
        self.assertEqual(detect_asset_type("petr4"), "b3")

    # --- non-B3 should not be detected as b3 ---
    def test_us_stock_not_b3(self):
        self.assertEqual(detect_asset_type("AAPL"), "stock")

    def test_canadian_stock_not_b3(self):
        self.assertEqual(detect_asset_type("CNC.TO"), "stock")

    def test_crypto_not_b3(self):
        self.assertEqual(detect_asset_type("BTC"), "crypto")

    def test_hk_stock_not_b3(self):
        self.assertEqual(detect_asset_type("0700.HK"), "stock")

    def test_spy_not_b3(self):
        self.assertEqual(detect_asset_type("SPY"), "stock")

    # --- normalization ---
    def test_normalize_appends_sa(self):
        self.assertEqual(normalize_b3_ticker("PETR4"), "PETR4.SA")

    def test_normalize_idempotent(self):
        self.assertEqual(normalize_b3_ticker("VALE3.SA"), "VALE3.SA")

    def test_normalize_knri11(self):
        self.assertEqual(normalize_b3_ticker("KNRI11"), "KNRI11.SA")

    def test_normalize_lowercase(self):
        self.assertEqual(normalize_b3_ticker("itub4"), "ITUB4.SA")

    # --- cli normalization ---
    def test_cli_normalize_b3(self):
        self.assertEqual(normalize_ticker_symbol("petr4"), "PETR4.SA")

    def test_cli_normalize_b3_with_sa(self):
        self.assertEqual(normalize_ticker_symbol("VALE3.SA"), "VALE3.SA")

    # --- instrument context ---
    def test_b3_context_mentions_b3(self):
        context = build_instrument_context("PETR4.SA")
        self.assertIn("B3", context)
        self.assertIn("BRL", context)
        self.assertIn("CVM", context)


if __name__ == "__main__":
    unittest.main()
