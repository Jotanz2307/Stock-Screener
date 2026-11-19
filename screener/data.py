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


def fetch_fundamentals(tickers: list[str]) -> dict[str, dict]:
    """Kembalikan {kode: {"eps": ..., "bvps": ...}} dari Yahoo Finance.

    EPS = laba bersih per saham 12 bulan terakhir (trailing),
    BVPS = nilai buku per saham. Jika laporan keuangan memakai mata uang
    lain dari harga sahamnya (mis. laporan USD, harga IDR), nilai dikosongkan
    agar tidak salah hitung. Isi manual lewat bagian `fundamentals` di config.
    """
    out = {}
    for t in tickers:
        try:
            info = yf.Ticker(to_yahoo(t)).info
        except Exception as e:
            print(f"[peringatan] gagal ambil fundamental {t}: {e}")
            continue
        price_ccy = info.get("currency")
        report_ccy = info.get("financialCurrency", price_ccy)
        if price_ccy and report_ccy and price_ccy != report_ccy:
            print(f"[peringatan] {t}: laporan {report_ccy}, harga {price_ccy}; EPS/BVPS dikosongkan")
            continue
        out[t.upper()] = {"eps": info.get("trailingEps"), "bvps": info.get("bookValue")}
    return out
