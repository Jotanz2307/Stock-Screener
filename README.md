# Stock Screener (IDX)

Screener sederhana untuk saham Bursa Efek Indonesia. Data harga harian diambil
gratis dari Yahoo Finance (kode saham otomatis diberi akhiran `.JK`), lalu
disaring dengan aturan yang kamu tulis di `config.yaml`.

## Cara pakai

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m screener.cli                  # tampilkan hasil
python -m screener.cli --csv hasil.csv  # sekaligus simpan ke CSV
```

## Mengubah aturan

Edit `config.yaml`. Setiap aturan adalah ekspresi pandas, semua aturan harus
terpenuhi (AND). Contoh:

```yaml
rules:
  - "close > sma_50"
  - "rsi_14 < 30"                # oversold
  - "pct_from_52w_high > -10"    # dekat harga tertinggi 52 minggu
```

Kolom yang tersedia: `close`, `volume`, `avg_volume_20`, `sma_20`, `sma_50`,
`rsi_14`, `change_1d_pct`, `change_20d_pct`, `pct_from_52w_high`.

## Struktur

```
screener/data.py        ambil data harga (yfinance)
screener/indicators.py  hitung SMA, RSI, perubahan harga, dll.
screener/rules.py       terapkan aturan filter
screener/cli.py         titik masuk command line
tests/                  tes dengan data buatan (tanpa internet)
```

## Tes

```bash
pytest
```

> Data Yahoo Finance bisa tertunda dan kadang kosong. Ini alat bantu riset,
> bukan saran investasi.
