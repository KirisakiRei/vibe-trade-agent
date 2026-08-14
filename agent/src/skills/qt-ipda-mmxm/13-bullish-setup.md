# 13 — Bullish Setup Validation

## Mandatory Conditions
Bullish setup dapat `VALID` hanya bila seluruh rule berikut terpenuhi sesuai sequence:

1. Ada HTF bullish key level relevan, contoh 4H BISI atau 1H BISI sesuai active context.
2. Harga masuk ke area BISI/key level bullish.
3. True Open telah dicek: idealnya harga berada di discount, atau key level memiliki confluence kuat sesuai rule source.
4. Previous-quarter swing low sudah disweep **atau** bullish SSMT valid.
5. **Setelah** Sweep/SSMT, candle close di atas minor structure high → bullish CISD.
6. Bullish ERL tersedia: swing high yang belum diambil pada timeframe delivery yang sama.
7. Active MMXM untuk setup utama = `IRL_TO_ERL`.

## Sequence

```text
Bullish HTF Key Level
→ Price Enters BISI
→ True Open Context
→ Sell-Side Sweep OR Bullish SSMT
→ Bullish CISD
→ ERL Confirmed
→ IRL_TO_ERL
→ VALID
```

## Waiting States
Jika key level valid tetapi price belum masuk:

```text
WAITING
reason = Waiting for Price to Enter BISI
```

Jika semua mandatory precondition sampai Sweep/SSMT terpenuhi tetapi CISD belum ada:

```text
WAITING
reason = Waiting for Bullish CISD
```

## Invalid Sequence
Jika bullish CISD-like break terjadi sebelum Sweep/SSMT:

```text
INVALID
reason = CISD before Sweep/SSMT
```

## Typical 90M Bullish Reversal Context
Source example:
- HTF bullish key level (mis. 4H BISI) dominan.
- LTF bearish move menuju area tersebut dapat meninggalkan 1H SIBI.
- Bullish expansion dapat menembus 1H SIBI dan membentuk 1H BISI baru.
- Retracement kembali ke 1H BISI.
- Sell-side sweep/SSMT antar-quarter.
- 5M bullish CISD.
- Delivery menuju bullish ERL.

Ini adalah scenario example, bukan mandatory fixed quarter number.

## Output
Jangan menulis `BUY NOW` atau mengeksekusi order. Gunakan:

```text
FINAL STATUS: VALID
DIRECTION: BULLISH
SETUP CONDITIONS: CONFIRMED
```

sertakan evidence dan missing risk/execution details bila user menanyakan entry price.
