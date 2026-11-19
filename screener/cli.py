"""Jalankan: python -m screener.cli [--config config.yaml] [--csv hasil.csv]"""
import argparse

from screener.pipeline import load_config, load_data, screen


def main() -> None:
    p = argparse.ArgumentParser(description="Stock screener saham IDX")
    p.add_argument("--config", default="config.yaml")
    p.add_argument("--csv", help="simpan hasil ke file CSV")
    args = p.parse_args()

    cfg = load_config(args.config)
    prices, fundamentals = load_data(
        cfg["tickers"], cfg.get("period", "1y"),
        cfg.get("fundamentals_source", "tradingview"), cfg.get("fundamentals"),
    )
    rules = cfg.get("rules", [])
    table, hits = screen(prices, fundamentals, rules)

    print(f"Aturan: {' AND '.join(rules) or '(tidak ada)'}")
    print(f"Lolos {len(hits)} dari {len(table)} saham\n")
    print(hits.to_string() if len(hits) else "Tidak ada yang lolos.")
    if args.csv:
        hits.to_csv(args.csv)
        print(f"\nDisimpan ke {args.csv}")


if __name__ == "__main__":
    main()
