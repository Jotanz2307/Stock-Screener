"""Ambil data harga harian saham IDX dari Yahoo Finance."""
import pandas as pd
import yfinance as yf


def to_yahoo(ticker: str) -> str:
    """BBCA -> BBCA.JK (saham Bursa Efek Indonesia)."""
    t = ticker.strip().upper()
    return t if "." in t else f"{t}.JK"


def fetch_prices(tickers: list[str], period: str = "1y") -> dict[str, pd.DataFrame]:
    """Kembalikan {kode: DataFrame OHLCV}. Saham tanpa data dilewati."""
    out = {}
    for t in tickers:
        try:
            df = yf.Ticker(to_yahoo(t)).history(period=period, auto_adjust=True)
        except Exception as e:  # koneksi gagal, kode salah, dll.
            print(f"[peringatan] gagal ambil {t}: {e}")
            continue
        if df.empty:
            print(f"[peringatan] tidak ada data untuk {t}")
            continue
        out[t.upper()] = df
    return out
