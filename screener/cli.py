"""Jalankan: python -m screener.cli [--config config.yaml] [--csv hasil.csv]"""
import argparse

import yaml

from screener.data import fetch_prices, get_fundamentals
from screener.indicators import build_table
from screener.rules import apply_rules


def main() -> None:
    p = argparse.ArgumentParser(description="Stock screener saham IDX")
    p.add_argument("--config", default="config.yaml")
    p.add_argument("--csv", help="simpan hasil ke file CSV")
    args = p.parse_args()

    with open(args.config) as f:
        cfg = yaml.safe_load(f)

    prices = fetch_prices(cfg["tickers"], cfg.get("period", "1y"))
    fundamentals = get_fundamentals(list(prices), cfg.get("fundamentals_source", "tradingview"))
    # Nilai manual di config menimpa data Yahoo
    for t, vals in (cfg.get("fundamentals") or {}).items():
        fundamentals.setdefault(t.upper(), {}).update(vals)
    table = build_table(prices, fundamentals)
    rules = cfg.get("rules", [])
    hits = apply_rules(table, rules)

    print(f"Aturan: {' AND '.join(rules) or '(tidak ada)'}")
    print(f"Lolos {len(hits)} dari {len(table)} saham\n")
    print(hits.sort_values("mos_pct", ascending=False, na_position="last").to_string() if len(hits) else "Tidak ada yang lolos.")
    if args.csv:
        hits.to_csv(args.csv)
        print(f"\nDisimpan ke {args.csv}")


if __name__ == "__main__":
    main()
