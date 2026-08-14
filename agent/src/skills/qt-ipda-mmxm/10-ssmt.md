# 10 — SSMT (Sequential SMT)

## Definisi
SSMT adalah divergence antar correlated pair dari quarter ke quarter dan dapat menjadi alternatif konfirmasi ketika explicit sweep tidak terjadi pada symbol utama.

## Data Requirement
Minimal:
- `mainSymbol`
- `correlatedSymbol`

Contoh source:
- EURUSD ↔ GBPUSD
- BTCUSDT ↔ ETHUSDT
- NQ ↔ ES

Correlation pair harus datang dari konfigurasi/user. Jangan menciptakan pair baru tanpa sumber/config.

## Bullish SSMT
Valid divergence sell-side bila salah satu pair sweep previous-quarter low dan pair lainnya tidak, pada konteks quarter/cycle yang comparable.

Contoh:
```text
mainSymbol      : no sweep previousQuarter.low
correlatedSymbol: sweep previousQuarter.low
```

atau sebaliknya.

Output:
```text
BULLISH_SSMT
```

## Bearish SSMT
Valid divergence buy-side bila salah satu pair sweep previous-quarter high dan pair lainnya tidak.

Output:
```text
BEARISH_SSMT
```

## Validity Requirements
SSMT hanya valid bila:
1. kedua pair berada pada cycle dan quarter yang sama;
2. comparison menggunakan structure timeframe yang sama;
3. divergence terjadi di area key level yang relevan;
4. SSMT terjadi sebelum CISD.

## Missing Correlated Pair
Jika correlated pair tidak dikonfigurasi/tersedia:

```text
SSMT = SKIPPED
```

Bukan `INVALID`.

Namun final setup masih membutuhkan rule `Sweep OR SSMT`. Jika SSMT skipped, Sweep harus memenuhi requirement tersebut.

## Anti-Hallucination
Jangan menyimpulkan SSMT hanya dari kemiripan chart atau generic correlation. Harus ada data kedua symbol yang comparable.
