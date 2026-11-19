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


# --- TradingView ---------------------------------------------------------
# Memakai library tidak resmi `tradingview-screener` (endpoint screener
# TradingView). Bisa berhenti bekerja jika TradingView mengubah situsnya.
TV_EPS = "earnings_per_share_diluted_ttm"
TV_BVPS = "book_value_per_share_fq"


def parse_tradingview(df: pd.DataFrame) -> dict[str, dict]:
    """Ubah hasil screener TradingView jadi {kode: {"eps", "bvps"}}."""
    out = {}
    for _, r in df.iterrows():
        code = str(r["ticker"]).split(":")[-1].upper()
        price_ccy = r.get("currency")
        report_ccy = r.get("fundamental_currency_code") or price_ccy
        if price_ccy and report_ccy and price_ccy != report_ccy:
            print(f"[peringatan] {code}: laporan {report_ccy}, harga {price_ccy}; EPS/BVPS dikosongkan")
            continue
        eps, bvps = r.get(TV_EPS), r.get(TV_BVPS)
        out[code] = {
            "eps": None if pd.isna(eps) else float(eps),
            "bvps": None if pd.isna(bvps) else float(bvps),
        }
    return out


def fetch_fundamentals_tradingview(tickers: list[str]) -> dict[str, dict]:
    """Ambil EPS dan BVPS semua saham sekaligus dari TradingView (IDX)."""
    from tradingview_screener import Query

    symbols = [f"IDX:{t.strip().upper()}" for t in tickers]
    _, df = (
        Query()
        .set_tickers(*symbols)
        .select("name", "currency", "fundamental_currency_code", TV_EPS, TV_BVPS)
        .limit(len(symbols))
        .get_scanner_data()
    )
    return parse_tradingview(df)


def get_fundamentals(tickers: list[str], source: str = "tradingview") -> dict[str, dict]:
    """Ambil EPS/BVPS dari sumber pilihan; saham yang gagal dicoba lewat Yahoo."""
    data: dict[str, dict] = {}
    if source == "tradingview":
        try:
            data = fetch_fundamentals_tradingview(tickers)
        except Exception as e:
            print(f"[peringatan] TradingView gagal ({e}); pakai Yahoo Finance")
    missing = [t for t in tickers if t.upper() not in data]
    if missing:
        data.update(fetch_fundamentals(missing))
    return data
