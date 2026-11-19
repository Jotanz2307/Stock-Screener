import math

import numpy as np
import pandas as pd

from screener.data import TV_BVPS, TV_EPS, parse_tradingview, to_yahoo
from screener.indicators import build_table, rsi
from screener.rules import apply_rules
from screener.valuation import graham_value


def fake_prices(trend: float, n: int = 120) -> pd.DataFrame:
    close = pd.Series(1000 + trend * np.arange(n) + np.sin(np.arange(n)) * 5, dtype=float)
    return pd.DataFrame({"Close": close, "Volume": np.full(n, 2_000_000.0)})


def test_to_yahoo():
    assert to_yahoo("bbca") == "BBCA.JK"
    assert to_yahoo("AAPL.US") == "AAPL.US"


def test_rsi_range():
    r = rsi(fake_prices(2)["Close"]).dropna()
    assert ((r >= 0) & (r <= 100)).all()


def test_rules_filter_uptrend():
    table = build_table({"NAIK": fake_prices(5), "TURUN": fake_prices(-5)})
    hits = apply_rules(table, ["close > sma_50"])
    assert list(hits.index) == ["NAIK"]


def test_graham_value():
    assert graham_value(100, 1000) == 1500.0  # akar(22.5*100*1000)
    assert math.isnan(graham_value(-5, 1000))
    assert math.isnan(graham_value(None, 1000))


def test_rule_below_fair_value():
    prices = {"MURAH": fake_prices(1), "MAHAL": fake_prices(1), "RUGI": fake_prices(1)}
    fundamentals = {
        "MURAH": {"eps": 200, "bvps": 2000},  # harga wajar ~3000, harga ~1100
        "MAHAL": {"eps": 10, "bvps": 100},    # harga wajar ~150
        "RUGI": {"eps": -10, "bvps": 1000},
    }
    table = build_table(prices, fundamentals)
    hits = apply_rules(table, ["close < graham_value"])
    assert list(hits.index) == ["MURAH"]
    assert table.loc["MURAH", "mos_pct"] > 0


def test_parse_tradingview():
    df = pd.DataFrame([
        {"ticker": "IDX:BBCA", "currency": "IDR", "fundamental_currency_code": "IDR", TV_EPS: 450.0, TV_BVPS: 2200.0},
        {"ticker": "IDX:ADRO", "currency": "IDR", "fundamental_currency_code": "USD", TV_EPS: 0.05, TV_BVPS: 0.3},
        {"ticker": "IDX:GOTO", "currency": "IDR", "fundamental_currency_code": "IDR", TV_EPS: float("nan"), TV_BVPS: 80.0},
    ])
    out = parse_tradingview(df)
    assert out["BBCA"] == {"eps": 450.0, "bvps": 2200.0}
    assert "ADRO" not in out  # mata uang laporan beda, dilewati
    assert out["GOTO"]["eps"] is None
