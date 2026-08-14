# 06 — IPDA Phase of Price

## Phase Set
Gunakan hanya:
- `CONSOLIDATION`
- `EXPANSION`
- `RETRACEMENT`
- `REVERSAL`

## Q1 Rule
Q1 hanya boleh diklasifikasikan sebagai:
- Consolidation, atau
- Expansion.

Jika hasil awal memberi Retracement/Reversal pada Q1, kategorisasi ulang atau tandai classification conflict; jangan menerima fase tersebut sebagai Q1 final.

## Consolidation
Rule kuantitatif MVP:

```text
quarterRange < averageRangeLookback * consolidationThreshold
```

Default:

```text
averageRangeLookback = 5 quarter sebelumnya
consolidationThreshold = 0.75
```

Artinya quarter range < 75% rata-rata 5 quarter sebelumnya.

Tambahan corroboration dari source:
- tidak ada strong close di atas/bawah swing quarter sebelumnya;
- body candle cenderung overlap.

Karena "strong close" dan "cenderung overlap" tidak diberi formula numerik di source, jangan menciptakan threshold sendiri. Jika tool tidak memiliki definisi eksplisit, gunakan hanya sebagai qualitative corroboration atau `UNKNOWN`.

## Expansion
Rule kuantitatif MVP:

```text
quarterRange > averageRangeLookback * expansionThreshold
```

Default:

```text
expansionThreshold = 1.2
```

Direction:

```text
quarter.close > quarter.open → Bullish
quarter.close < quarter.open → Bearish
```

Expansion lebih kuat bila:
- external liquidity diambil; atau
- movement meninggalkan BISI/SIBI baru.

## Retracement
Terjadi setelah expansion saat harga kembali ke IRL tanpa menembus dominant key level.

Bullish retracement:
- ada bullish expansion sebelumnya;
- harga turun kembali ke BISI;
- tidak ada body close di bawah BISI.

Bearish retracement:
- ada bearish expansion sebelumnya;
- harga naik kembali ke SIBI;
- tidak ada body close di atas SIBI.

## Reversal
Bullish reversal:
- sebelumnya bearish delivery menuju BISI;
- harga masuk BISI;
- opposing SIBI ditembus ke atas dengan body close;
- BISI baru terbentuk dari bullish expansion.

Bearish reversal:
- sebelumnya bullish delivery menuju SIBI;
- harga masuk SIBI;
- opposing BISI ditembus ke bawah dengan body close;
- SIBI baru terbentuk.

## Phase Transition
- Setelah Expansion → Retracement, Consolidation, atau Reversal.
- Setelah Retracement → Expansion diharapkan.
- Setelah Reversal → Expansion diharapkan.

"Diharapkan" adalah anticipation, bukan jaminan. Report fakta current phase dan expected next phase secara terpisah.
