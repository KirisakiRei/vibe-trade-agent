# 07 — MMXM Model Delivery

## Tujuan
MMXM mendeskripsikan bentuk delivery liquidity yang aktif.

## Model 1 — IRL → ERL
**Priority setup utama.**

Bullish:
- IRL = BISI;
- ERL = swing high yang belum diambil;
- harga berada di/baru reprice dari BISI;
- orderflow menuju swing high.

Bearish:
- IRL = SIBI;
- ERL = swing low yang belum diambil;
- harga berada di/baru reprice dari SIBI;
- orderflow menuju swing low.

Label:
```text
IRL_TO_ERL
```

## Model 2 — ERL → IRL
Terjadi setelah objective tercapai dan harga mencari repricing.

Bullish context setelah swing high diambil:
- harga mulai kembali ke BISI/IFVG.

Bearish context setelah swing low diambil:
- harga mulai kembali ke SIBI/IFVG.

Label:
```text
ERL_TO_IRL
```

## Model 3 — ERL → ERL
Menandakan strong trend tanpa repricing jelas ke IRL.

Bullish:
- swing high pertama diambil;
- harga langsung menuju swing high berikutnya.

Bearish:
- swing low pertama diambil;
- harga langsung menuju swing low berikutnya.

Label:
```text
ERL_TO_ERL
```

Berikan warning:
```text
STRONG_TREND_NOT_PREFERRED_FOR_ENTRY
```

## Priority Rule
Untuk checklist setup project, `IRL_TO_ERL` adalah model yang harus diprioritaskan dan menjadi requirement pada bullish/bearish validation yang didefinisikan PRD.

Jangan memaksa `VALID` setup utama saat model aktif adalah ERL→IRL atau ERL→ERL kecuali user secara eksplisit menambahkan setup type lain di masa depan.
