# 02 — Cycle & Quarter Rules

## Prinsip Fractal Time
Setiap quarter dari sebuah cycle merepresentasikan satu full cycle pada level di bawahnya. Mekanisme sama, skala berbeda.

## Cycle Hierarchy
| Cycle | Key Level | Structure TF | Durasi 1 Quarter | Peran |
|---|---|---:|---:|---|
| Monthly | Weekly | 4H | 1 minggu | Defines Objective |
| Weekly | Daily | 1H | 1 hari | Defines Bias |
| Daily | 4H | 15M | 6 jam | Defines Reversal Zone |
| 90 Minute | 1H | 5M | 90 menit | Defines Execution |
| Micro | 15M | 1M | 22.5 menit | Defines Internal Delivery |

Micro bersifat optional/subordinate untuk project awal.

## Monthly Cycle
- Q1 = Week 1
- Q2 = Week 2
- Q3 = Week 3
- Q4 = Week 4
- Week 5 bila ada = ekstensi Q4.
- Structure swing: candle 4H per minggu.

## Weekly Cycle
- Q1 = Senin
- Q2 = Selasa
- Q3 = Rabu
- Q4 = Kamis
- Jumat = Delivery / Completion Day.
- Structure swing: candle 1H per hari.

## Daily Cycle
Reference timezone wajib: `America/New_York`.

Daily Cycle dimulai 18:00 New York Time:
- Q1 = 18:00–00:00 — Asia
- Q2 = 00:00–06:00 — London
- Q3 = 06:00–12:00 — NY AM
- Q4 = 12:00–18:00 — NY PM

Structure swing: candle 15M per 6 jam.

Jangan menggunakan timezone server untuk menentukan quarter.

## 90 Minute Cycle
Satu Daily Quarter (6 jam) berisi satu full 90 Minute Cycle yang memiliki 4 quarter × 90 menit.

Contoh untuk Daily Q3 06:00–12:00 NY:
- Q1 = 06:00–07:30 — 18 candle 5M
- Q2 = 07:30–09:00 — 18 candle 5M
- Q3 = 09:00–10:30 — 18 candle 5M
- Q4 = 10:30–12:00 — 18 candle 5M

Structure swing: candle 5M.

Untuk Daily quarter lain, gunakan pembagian 4 × 90 menit yang sama dari start quarter tersebut.

## Swing High / Low per Quarter
Untuk completed quarter:

```text
quarterSwingHigh = max(candle.high) dalam quarter
quarterSwingLow  = min(candle.low) dalam quarter
```

Gunakan structure timeframe milik cycle:
- Monthly → 4H
- Weekly → 1H
- Daily → 15M
- 90M → 5M

Swing completed quarter menjadi referensi liquidity untuk quarter berikutnya.

Quarter yang belum selesai boleh dipakai untuk monitoring sementara, tetapi jangan anggap swing sementara sebagai final reference tanpa label provisional.

## IF → THEN Anticipation
### Bila Q1 Consolidation
- Q1: liquidity menumpuk; tandai swing Q1.
- Q2: antisipasi expansion menuju key level; tandai swing Q2.
- Q3: antisipasi retracement/reversal saat masuk key level; cari Sweep/SSMT dan tunggu CISD.
- Q4: expansion dapat terjadi bila alignment sudah confirmed.

### Bila Q1 Expansion
- Q1: move kuat dan kemungkinan meninggalkan IRL baru; tandai swing Q1.
- Q2: antisipasi retracement/consolidation menuju IRL; tandai swing Q2.
- Q3: cari swept swing Q2 atau SSMT di key level; tunggu CISD.
- Q4: expansion dapat terjadi bila alignment confirmed.

Ini adalah anticipation logic, bukan rule bahwa entry wajib terjadi di Q4.
