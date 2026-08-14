# 08 — Orderflow

## Definisi
Orderflow bukan hanya label bullish/bearish. Orderflow menjawab:

> Timeframe mana yang sedang delivering, dari IRL apa, menuju ERL apa?

## Bullish Orderflow
Valid bila:
- ada BISI aktif pada timeframe tersebut;
- target swing high timeframe tersebut belum diambil;
- harga bergerak dari/reprice area BISI menuju swing high.

Format:
```text
1H BISI → 1H Swing High
```

## Bearish Orderflow
Valid bila:
- ada SIBI aktif pada timeframe tersebut;
- target swing low timeframe tersebut belum diambil;
- harga bergerak dari/reprice area SIBI menuju swing low.

Format:
```text
1H SIBI → 1H Swing Low
```

## Timeframe Integrity
Tidak boleh mencampur primary IRL dan primary ERL lintas timeframe.

- 1H IRL → 1H ERL
- 4H IRL → 4H ERL
- Daily IRL → Daily ERL

HTF boleh menjadi context dominan tetapi bukan alasan untuk mengganti ERL timeframe secara diam-diam.

## Orderflow Change
Jika opposing key level ditembus dengan body close dan key level baru terbentuk, evaluasi ulang orderflow. Jangan mempertahankan label lama tanpa re-validation.

## Output Minimum
- timeframe;
- direction;
- source IRL type + zone;
- target ERL type + price;
- evidence;
- HTF context yang mendukung/berlawanan.
