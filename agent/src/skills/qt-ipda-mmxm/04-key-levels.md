# 04 — Key Levels: BISI, SIBI, IFVG, IRL, ERL

## IRL
IRL adalah area repricing, bukan entry signal.

Project core mendukung:
- BISI
- SIBI
- IFVG
- Order Block hanya sebagai contextual/optional concept bila tersedia; PRD tidak menjadikannya detector wajib karena lebih subjektif.

## BISI — Bullish FVG
Terbentuk bila:

```text
candle[i-2].high < candle[i].low
```

Zona:

```text
bisiLow  = candle[i-2].high
bisiHigh = candle[i].low
```

Konteks: bullish imbalance / repricing area.

## SIBI — Bearish FVG
Terbentuk bila:

```text
candle[i-2].low > candle[i].high
```

Zona:

```text
sibiLow  = candle[i].high
sibiHigh = candle[i-2].low
```

Konteks: bearish imbalance / repricing area.

## IRL Selection
Bullish example:
- IRL = active BISI yang belum invalid dan berada di bawah harga atau sedang disentuh.

Bearish example:
- IRL = active SIBI yang belum invalid dan berada di atas harga atau sedang disentuh.

## ERL
ERL valid adalah swing high/low yang belum diambil.

Bullish:
- primary ERL = swing high terdekat yang belum tersweep pada timeframe yang sama dengan IRL/orderflow.

Bearish:
- primary ERL = swing low terdekat yang belum tersweep pada timeframe yang sama.

## IFVG
SIBI menjadi bullish IFVG/support bila:

```text
candle.close > sibiHigh
```

BISI menjadi bearish IFVG/resistance bila:

```text
candle.close < bisiLow
```

Gunakan body close/close candle; wick saja tidak cukup untuk transformasi yang didefinisikan ini.

## Price Inside Key Level
Harga dianggap masuk key level bila range candle overlap dengan zona:

```text
currentHigh >= keyLevelLow
AND
currentLow <= keyLevelHigh
```

## Priority
Bila HTF dan LTF key level konflik pada area yang sama, HTF lebih dominan.

Contoh: 1H SIBI berada dalam/berdekatan dengan 4H BISI dan 1H SIBI ditembus ke atas → jangan tetap menganggap 1H SIBI sebagai dominant resistance; 4H bullish context lebih dominan.
