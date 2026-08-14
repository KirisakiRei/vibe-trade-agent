# 11 — CISD (Change In State of Delivery)

## Definisi
CISD adalah konfirmasi bahwa delivery harga berubah arah. Dalam framework ini, tanpa CISD setup tidak boleh `VALID`.

## Sequence Precondition
CISD hanya valid jika:
1. harga sudah masuk key level;
2. Sweep atau SSMT sudah terjadi;
3. candle close mengonfirmasi break structure sesuai arah.

Jika break/close terjadi sebelum Sweep/SSMT:

```text
CISD = INVALID_SEQUENCE
```

## Bullish CISD
Setelah sweep low atau bullish SSMT:

```text
candle.close > minorStructureHigh
```

maka CISD bullish valid.

Default structure reference:
- `minorStructureHigh` = opposing structure high terakhir yang terbentuk sebelum sweep (dalam konteks bullish sering merupakan `lastLowerHigh` sebelum sweep).

Alternatif teknis source:
- local swing high dari `N` candle sebelum sweep;
- default `N = 5` pada execution timeframe.

Untuk 90 Minute execution:
- CISD timeframe = 5M.

## Bearish CISD
Setelah sweep high atau bearish SSMT:

```text
candle.close < minorStructureLow
```

maka CISD bearish valid.

Default structure reference:
- `minorStructureLow` = opposing structure low terakhir yang terbentuk sebelum sweep (dalam konteks bearish sering merupakan `lastHigherLow` sebelum sweep).

Alternatif teknis source:
- local swing low dari `N` candle sebelum sweep;
- default `N = 5` pada execution timeframe.

## Body Close Rule
**Wick tidak boleh dianggap CISD.**

Gunakan close candle:
- bullish: close di atas structure high;
- bearish: close di bawah structure low.

## Evidence Output
Saat menyatakan CISD valid, sertakan:
- direction;
- execution timeframe;
- sweep/SSMT event sebelumnya;
- structure level yang ditembus;
- candle timestamp;
- candle close;
- sequence validity.

Jika salah satu evidence tidak tersedia, jangan fabricate.
