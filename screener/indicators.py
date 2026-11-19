"""Hitung indikator teknikal dari data harga harian."""
import pandas as pd


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / period, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / period, adjust=False).mean()
    rs = gain / loss
    return 100 - 100 / (1 + rs)


def summarize(df: pd.DataFrame) -> dict:
    """Ringkas satu saham jadi satu baris angka terbaru."""
    close = df["Close"]
    vol = df["Volume"]
    last = close.iloc[-1]
    high_52w = close.tail(252).max()
    return {
        "close": float(last),
        "volume": float(vol.iloc[-1]),
        "avg_volume_20": float(vol.tail(20).mean()),
        "sma_20": float(close.rolling(20).mean().iloc[-1]),
        "sma_50": float(close.rolling(50).mean().iloc[-1]),
        "rsi_14": float(rsi(close).iloc[-1]),
        "change_1d_pct": float((last / close.iloc[-2] - 1) * 100) if len(close) > 1 else 0.0,
        "change_20d_pct": float((last / close.iloc[-21] - 1) * 100) if len(close) > 20 else 0.0,
        "pct_from_52w_high": float((last / high_52w - 1) * 100),
    }


def build_table(prices: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = {t: summarize(df) for t, df in prices.items() if len(df) >= 50}
    return pd.DataFrame.from_dict(rows, orient="index").round(2)
