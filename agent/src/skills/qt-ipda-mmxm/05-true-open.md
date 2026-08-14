# 05 — True Open

## Definisi
True Open adalah Q2 Open dari setiap cycle dan digunakan sebagai:
- referensi premium/discount;
- timing setelah Q1 memberi informasi awal;
- confluence untuk menilai kualitas lokasi key level.

## True Open per Cycle
- Monthly = Open Week 2
- Weekly = Open Selasa
- Daily = Open 00:00 New York Time
- 90 Minute = Open Q2 dari 90 Minute Cycle yang berjalan

## Premium / Discount
Jika:

```text
currentPrice > trueOpen
```

maka:
- zone = `PREMIUM`
- directional filter = fokus SELL.

Jika:

```text
currentPrice < trueOpen
```

maka:
- zone = `DISCOUNT`
- directional filter = fokus BUY.

## High-Confluence Location
Sell setup lebih kuat bila:
- harga di atas True Open;
- SIBI/key level sell berada di atas True Open.

Buy setup lebih kuat bila:
- harga di bawah True Open;
- BISI/key level buy berada di bawah True Open.

## Low-Probability Location
Sell setup lebih lemah bila harga dan SIBI berada di bawah True Open.

Buy setup lebih lemah bila harga dan BISI berada di atas True Open.

## Rule Interpretation
True Open adalah filter/confluence, bukan pengganti mandatory sequence Sweep/SSMT → CISD.

Jika True Open berlawanan tetapi source checklist masih mengizinkan key level dengan confluence kuat, jangan otomatis menandai setup invalid hanya berdasarkan True Open. Laporkan sebagai lower-probability/weak confluence kecuali rule lain invalid.

## Timing
Q1 terutama berfungsi sebagai observasi/informasi. Fokus dapat meningkat saat Q2/True Open dimulai, tetapi jangan menganggap Q1 sebagai larangan mutlak untuk semua analisis.
