"""Alur utama screener: ambil data -> hitung indikator -> terapkan aturan.

Dipakai oleh CLI (screener/cli.py) dan dashboard (app.py).
"""
import pandas as pd
import yaml

from screener.data import fetch_prices, get_fundamentals
from screener.indicators import build_table
from screener.rules import apply_rules


def load_config(path: str = "config.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def load_data(tickers: list[str], period: str = "1y", source: str = "tradingview",
              manual: dict | None = None) -> tuple[dict[str, pd.DataFrame], dict[str, dict]]:
    """Ambil harga harian dan EPS/BVPS. `manual` menimpa data dari internet."""
    prices = fetch_prices(tickers, period)
    fundamentals = get_fundamentals(list(prices), source) if prices else {}
    for t, vals in (manual or {}).items():
        fundamentals.setdefault(t.upper(), {}).update(vals)
    return prices, fundamentals


def screen(prices: dict, fundamentals: dict, rules: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Kembalikan (tabel semua saham, saham yang lolos), urut dari diskon terbesar."""
    table = build_table(prices, fundamentals)
    if not table.empty:
        table = table.sort_values("mos_pct", ascending=False, na_position="last")
    hits = apply_rules(table, rules) if not table.empty else table
    return table, hits
