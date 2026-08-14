# 09 — Sweep (Swept Liquidity)

## Definisi
Sweep terjadi saat liquidity dari quarter sebelumnya diambil quarter berikutnya di/sekitar key level, lalu harga kembali melewati level tersebut dengan close sesuai arah reversal.

## Bullish Sweep
Candidate condition:

```text
currentQuarter.low < previousQuarter.swingLow
```

Confirmation:

```text
candle.close > previousQuarter.swingLow
```

Required context:
1. previous quarter memiliki finalized swing low;
2. current quarter mengambil level tersebut;
3. ada candle close kembali di atas swing low;
4. kejadian berada di area BISI atau bullish HTF key level yang relevan.

Makna: sell-side liquidity diambil dan bullish reaction dikonfirmasi.

## Bearish Sweep
Candidate condition:

```text
currentQuarter.high > previousQuarter.swingHigh
```

Confirmation:

```text
candle.close < previousQuarter.swingHigh
```

Required context:
1. previous quarter memiliki finalized swing high;
2. current quarter mengambil level tersebut;
3. ada candle close kembali di bawah swing high;
4. kejadian berada di area SIBI atau bearish HTF key level yang relevan.

Makna: buy-side liquidity diambil dan bearish reaction dikonfirmasi.

## Key Level Proximity
Sweep dianggap valid di dalam atau dekat key level.

Default tolerance dari PRD, dihitung terhadap **range key level** (bukan nilai harga level itu sendiri):

```text
keyLevelRange          = keyLevel.high - keyLevel.low
sweepDistanceTolerance = keyLevelRange * 0.10
```

Sweep distance dihitung dari pergerakan harga melewati batas level (low level untuk bullish sweep, high level untuk bearish sweep):

```text
sweepDistance = |candle.low  - previousQuarter.swingLow|   # bullish
sweepDistance = |candle.high - previousQuarter.swingHigh|  # bearish

sweep distance <= sweepDistanceTolerance  →  dalam tolerance, sweep valid
```

Contoh: key level 1.0800–1.0850 → range 0.0050 → tolerance 0.0005 (10% dari range). Sweep sejauh 0.0004 masih dianggap valid; 0.0008 tidak.

Jangan membuat tolerance lain kecuali config/user menentukan.

## Mandatory Sequence

```text
Key Level Touched
→ Sweep OR SSMT
→ CISD
```

Jika CISD terjadi sebelum Sweep/SSMT:

```text
INVALID_SEQUENCE
```

## Quarter Integrity
Sweep yang dipakai untuk setup harus mereferensikan swing quarter sebelumnya sesuai cycle/structure timeframe yang sedang dianalisis.
