"""Uji dashboard dengan data buatan (tanpa internet)."""
import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest

import screener.pipeline as pipeline


def fake_load_data(tickers, period="1y", source="tradingview", manual=None):
    n = 120
    prices = {}
    for i, t in enumerate(tickers):
        close = pd.Series(1000 + (i + 1) * np.arange(n), dtype=float,
                          index=pd.date_range("2026-01-01", periods=n))
        prices[t] = pd.DataFrame({"Close": close, "Volume": np.full(n, 2_000_000.0)})
    fundamentals = {tickers[0]: {"eps": 200, "bvps": 2000}}  # sisanya kosong
    return prices, fundamentals


def test_dashboard_renders(monkeypatch):
    monkeypatch.setattr(pipeline, "load_data", fake_load_data)
    at = AppTest.from_file("../app.py", default_timeout=30).run()
    assert not at.exception
    assert at.metric[0].value == "10"   # 10 saham di config.yaml
    assert at.metric[2].value == "1"    # hanya saham pertama punya harga wajar
    assert len(at.dataframe) >= 1


def test_dashboard_bad_rule(monkeypatch):
    monkeypatch.setattr(pipeline, "load_data", fake_load_data)
    at = AppTest.from_file("../app.py", default_timeout=30).run()
    at.sidebar.text_area[1].set_value("harga >>> 5").run()
    assert not at.exception
    assert "tidak valid" in at.error[0].value
