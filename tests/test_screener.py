import numpy as np
import pandas as pd

from screener.data import to_yahoo
from screener.indicators import build_table, rsi
from screener.rules import apply_rules


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
