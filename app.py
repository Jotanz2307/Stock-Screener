"""Dashboard stock screener. Jalankan: streamlit run app.py"""
import pandas as pd
import streamlit as st

from screener.pipeline import load_config, load_data, screen
from screener.rules import apply_rules

st.set_page_config(page_title="Stock Screener IDX", layout="wide")
cfg = load_config()

COLUMNS = {
    "close": st.column_config.NumberColumn("Harga", format="localized"),
    "graham_value": st.column_config.NumberColumn("Harga wajar", format="localized"),
    "mos_pct": st.column_config.NumberColumn("MoS %", format="%.1f%%",
                                             help="Positif = harga di bawah harga wajar"),
    "eps": st.column_config.NumberColumn("EPS", format="%.1f"),
    "bvps": st.column_config.NumberColumn("BVPS", format="%.1f"),
    "rsi_14": st.column_config.NumberColumn("RSI 14", format="%.1f"),
    "sma_20": st.column_config.NumberColumn("SMA 20", format="localized"),
    "sma_50": st.column_config.NumberColumn("SMA 50", format="localized"),
    "change_1d_pct": st.column_config.NumberColumn("1H %", format="%.2f%%"),
    "change_20d_pct": st.column_config.NumberColumn("20H %", format="%.2f%%"),
    "pct_from_52w_high": st.column_config.NumberColumn("dari puncak 52M %", format="%.1f%%"),
    "volume": st.column_config.NumberColumn("Volume", format="%d"),
    "avg_volume_20": st.column_config.NumberColumn("Rata vol 20H", format="%d"),
}
ORDER = list(COLUMNS)


@st.cache_data(ttl=3600, show_spinner="Mengambil data saham...")
def cached_data(tickers: tuple, period: str, source: str, manual: dict):
    return load_data(list(tickers), period, source, manual)


# --- Sidebar: pengaturan ------------------------------------------------
with st.sidebar:
    st.header("Pengaturan")
    tickers_text = st.text_area("Kode saham (pisahkan koma atau baris baru)",
                                "\n".join(cfg["tickers"]), height=180)
    tickers = tuple(dict.fromkeys(
        t.strip().upper() for t in tickers_text.replace(",", "\n").splitlines() if t.strip()))
    rules_text = st.text_area("Aturan filter (satu per baris, semua harus terpenuhi)",
                              "\n".join(cfg.get("rules", [])), height=150)
    rules = [r.split("#")[0].strip() for r in rules_text.splitlines()
             if r.split("#")[0].strip()]
    periods = ["6mo", "1y", "2y", "5y"]
    period = st.selectbox("Periode harga", periods,
                          index=periods.index(cfg.get("period", "1y")))
    sources = ["tradingview", "yahoo"]
    source = st.selectbox("Sumber EPS/BVPS", sources,
                          index=sources.index(cfg.get("fundamentals_source", "tradingview")))
    if st.button("Ambil ulang data"):
        cached_data.clear()
    st.caption("Data tersimpan 1 jam. Alat bantu riset, bukan saran investasi.")

st.title("Stock Screener IDX")

if not tickers:
    st.info("Isi minimal satu kode saham di sidebar.")
    st.stop()

prices, fundamentals = cached_data(tickers, period, source, cfg.get("fundamentals") or {})
if not prices:
    st.error("Tidak ada data harga yang berhasil diambil. Periksa koneksi internet atau kode saham.")
    st.stop()

try:
    table, hits = screen(prices, fundamentals, [])
    hits = apply_rules(table, rules)
except Exception as e:
    st.error(f"Aturan filter tidak valid: {e}")
    st.stop()

# --- Ringkasan ----------------------------------------------------------
undervalued = table["mos_pct"].gt(0).sum()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Saham dipantau", len(table))
c2.metric("Lolos filter", len(hits))
c3.metric("Di bawah harga wajar", int(undervalued))
c4.metric("MoS terbesar", f"{table['mos_pct'].max():.1f}%" if table["mos_pct"].notna().any() else "-",
          table["mos_pct"].idxmax() if table["mos_pct"].notna().any() else None, delta_color="off")

missing = sorted(set(tickers) - set(prices))
if missing:
    st.warning(f"Data harga tidak ditemukan: {', '.join(missing)}")

# --- Tabel --------------------------------------------------------------
tab_hits, tab_all = st.tabs([f"Lolos filter ({len(hits)})", f"Semua saham ({len(table)})"])
for tab, df in ((tab_hits, hits), (tab_all, table)):
    with tab:
        if df.empty:
            st.write("Tidak ada saham yang lolos semua aturan.")
        else:
            st.dataframe(df[ORDER], column_config=COLUMNS, width="stretch")
            st.download_button("Unduh CSV", df.to_csv().encode(),
                               file_name="hasil_screener.csv", key=f"dl-{id(df)}")

# --- Detail satu saham --------------------------------------------------
st.subheader("Detail saham")
pick = st.selectbox("Pilih saham", list(table.index))
row = table.loc[pick]
d1, d2, d3, d4 = st.columns(4)
d1.metric("Harga", f"{row['close']:,.0f}", f"{row['change_1d_pct']:.2f}%")
d2.metric("Harga wajar Graham", "-" if pd.isna(row["graham_value"]) else f"{row['graham_value']:,.0f}")
d3.metric("Margin of safety", "-" if pd.isna(row["mos_pct"]) else f"{row['mos_pct']:.1f}%")
d4.metric("RSI 14", f"{row['rsi_14']:.1f}")

close = prices[pick]["Close"]
chart = pd.DataFrame({
    "Harga": close,
    "SMA 20": close.rolling(20).mean(),
    "SMA 50": close.rolling(50).mean(),
})
if not pd.isna(row["graham_value"]):
    chart["Harga wajar"] = row["graham_value"]
st.line_chart(chart)
if pd.isna(row["graham_value"]):
    st.caption("Harga wajar Graham tidak tersedia: EPS atau BVPS kosong atau negatif.")
