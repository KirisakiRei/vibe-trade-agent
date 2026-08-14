# 14 — Bearish Setup Validation

## Mandatory Conditions
Bearish setup dapat `VALID` hanya bila seluruh rule berikut terpenuhi sesuai sequence:

1. Ada HTF bearish key level relevan, contoh 4H SIBI atau 1H SIBI sesuai active context.
2. Harga masuk ke area SIBI/key level bearish.
3. True Open telah dicek: idealnya harga berada di premium, atau key level memiliki confluence kuat sesuai rule source.
4. Previous-quarter swing high sudah disweep **atau** bearish SSMT valid.
5. **Setelah** Sweep/SSMT, candle close di bawah minor structure low → bearish CISD.
6. Bearish ERL tersedia: swing low yang belum diambil pada timeframe delivery yang sama.
7. Active MMXM untuk setup utama = `IRL_TO_ERL`.

## Sequence

```text
Bearish HTF Key Level
→ Price Enters SIBI
→ True Open Context
→ Buy-Side Sweep OR Bearish SSMT
→ Bearish CISD
→ ERL Confirmed
→ IRL_TO_ERL
→ VALID
```

## Waiting States
Jika key level valid tetapi price belum masuk:

```text
WAITING
reason = Waiting for Price to Enter SIBI
```

Jika Sweep/SSMT valid tetapi bearish CISD belum ada:

```text
WAITING
reason = Waiting for Bearish CISD
```

## Invalid Sequence
Jika bearish CISD-like break terjadi sebelum Sweep/SSMT:

```text
INVALID
reason = CISD before Sweep/SSMT
```

## Typical 90M Bearish Context
Source example:
- active 1H bearish orderflow: 1H SIBI → 1H Swing Low;
- price bergerak menuju/masuk 1H SIBI;
- previous-quarter 5M swing high menjadi liquidity reference;
- buy-side sweep atau bearish SSMT terjadi di key level;
- setelahnya 5M candle close di bawah structure → bearish CISD;
- delivery menuju 1H bearish ERL.

Scenario ini contoh implementasi framework, bukan rule bahwa alignment wajib terjadi di Q4.

## Output
Jangan menulis `SELL NOW` atau mengeksekusi order. Gunakan:

```text
FINAL STATUS: VALID
DIRECTION: BEARISH
SETUP CONDITIONS: CONFIRMED
```

sertakan evidence.
