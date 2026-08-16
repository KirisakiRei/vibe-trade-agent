---
name: qt-ipda-mmxm
description: Analisis market top-down berbasis Quarterly Theory (QT), IPDA Phase of Price, MMXM, IRL/ERL, True Open, Sweep/SSMT, dan CISD. Gunakan untuk monitoring dan validasi setup secara analysis-only; jangan mengeksekusi order.
category: strategy
---

# QT / IPDA / MMXM Trading Analysis Skill

## Tujuan
Gunakan skill ini untuk membaca market secara objektif berdasarkan framework QT, IPDA, MMXM, dan checklist rules milik project. Skill ini adalah **rulebook analisis**, bukan sistem auto-trading.

## Source of Truth
Skill ini disusun dari:
- `Trading Checklist Engine PRD(2).pdf`
- `ICT Concepts MMXM Quarterly Theory.pdf`

Jika generic trading knowledge bertentangan dengan skill ini, **skill ini menang**. Jangan mengisi rule yang tidak didefinisikan dengan asumsi sendiri.

## Prinsip Inti
1. QT = waktu; IPDA = bagaimana harga bergerak; key level = lokasi/tujuan konteks.
2. Analisis wajib top-down: Monthly → Weekly → Daily → 90 Minute → Micro bila diperlukan.
3. Setiap timeframe/cycle memiliki IRL dan ERL sendiri. Jangan mencampur target antar timeframe.
4. HTF key level lebih dominan daripada LTF key level bila konflik di area yang sama.
5. Setup prioritas adalah `IRL → ERL`.
6. Sweep atau SSMT antar-quarter di area key level harus terjadi sebelum CISD.
7. CISD wajib menggunakan **candle close**, bukan wick.
8. Tanpa key level, ERL, Sweep/SSMT, atau CISD yang diwajibkan, setup tidak boleh `VALID`.
9. Missing evidence tidak boleh diganti dengan inference.
10. Mode project saat ini adalah **analysis-only**: jangan membuat, mengirim, atau mengeksekusi order.

## Output Directional Analysis (Wajib Dipahami)
Analisis skill ini **wajib sampai ke kesimpulan arah** (bias/valid setup), bukan berhenti di deskripsi netral. Ketika user meminta arah atau skenario trade:

- **Berikan** : `DIRECTION` tegas (BULLISH/BEARISH/NONE), level-level kunci (IRL, ERL, True Open), skenario harga (HVN→LVN, target liquidity), kondisi validasi, dan status setup (`VALID`/`WAITING`/`INVALID`/`NO_SETUP`).
- **Hubungkan** setiap klaim ke evidence checklist (sweep, SSMT, CISD, close di atas/bawah level).
- **Yang dilarang hanya** : ukuran posisi (position sizing), persentase lot, instruksi "beli/jual sekarang", dan eksekusi order. Memberikan arah + level + skenario adalah analisis, BUKAN nasihat eksekusi.
- Prinsip 4 (Analysis, not advice) dari system prompt tidak melarang directional analysis — ia melarang *prescription of position sizes dan order execution*. Jangan menolak menjawab arah dengan alasan "tidak boleh kasih saran".

## Brevity (Wajib untuk Telegram)
Default output adalah **BRIEF** di `15-output-format.md`: maksimal 12 baris, label + nilai, tanpa esai dan tanpa tabel.
Jangan load seluruh supporting file untuk pertanyaan singkat. Load hanya langkah yang dibutuhkan untuk `DIRECTION` + `FINAL STATUS`.
Format FULL AUDIT hanya jika user meminta `lengkap` / `audit` / `detail`.

## Urutan Analisis Wajib

```text
Identify Active Cycle
→ Identify Active Orderflow
→ Identify Active MMXM
→ Identify IRL
→ Identify ERL
→ Identify IPDA Phase
→ Check Price vs Key Level
→ Check True Open
→ Check Sweep / SSMT
→ Check CISD
→ Final Checklist Status
```

## Final Status
Gunakan hanya:
- `NO_SETUP`
- `WAITING`
- `VALID`
- `INVALID`

`SKIPPED`, `PENDING`, dan `UNKNOWN` hanya untuk item checklist, bukan final status.

## Data Requirements
Sumber data wajib adalah candlestick OHLC dengan timestamp timezone `America/New_York`. Jangan gunakan timezone server sebagai referensi quarter.

Field minimal per candle:
```text
timestamp, open, high, low, close
```

Timeframe data yang dibutuhkan sesuai struktur cycle:
| Cycle | Data Timeframe | Struktur Swing |
|---|---|---|
| Monthly | 4H | candle 4H per minggu |
| Weekly | 1H | candle 1H per hari |
| Daily | 15M | candle 15M per 6 jam |
| 90 Minute | 5M | candle 5M per 90 menit |
| Micro (opsional) | 1M | candle 1M per 22.5 menit |

Data yang tidak tersedia atau timeframe yang belum lengkap harus dilaporkan sebagai `DATA_UNAVAILABLE` atau label `provisional` pada item terkait; jangan pernah mengisi nilai default buatan.

## File yang Harus Dibaca Sesuai Kebutuhan
- `01-foundation.md` — filosofi, hierarchy, authority, anti-hallucination.
- `02-cycle-quarter.md` — Monthly/Weekly/Daily/90M/Micro, waktu NY, quarter, swing.
- `03-market-structure.md` — struktur likuiditas dan hubungan antar-cycle.
- `04-key-levels.md` — BISI, SIBI, IFVG, IRL, ERL, prioritas HTF.
- `05-true-open.md` — True Open, premium/discount, confluence.
- `06-ipda.md` — Consolidation, Expansion, Retracement, Reversal.
- `07-mmxm.md` — IRL→ERL, ERL→IRL, ERL→ERL.
- `08-orderflow.md` — active delivery per timeframe.
- `09-sweep.md` — swept liquidity dan sequence.
- `10-ssmt.md` — Sequential SMT antar correlated pair.
- `11-cisd.md` — Change In State of Delivery.
- `12-checklist.md` — rule engine dan status.
- `13-bullish-setup.md` — validasi bullish.
- `14-bearish-setup.md` — validasi bearish.
- `15-output-format.md` — format jawaban/Telegram.

## Aturan Penggunaan Context
Jangan load semua supporting file tanpa kebutuhan. Load file yang relevan dengan langkah analisis saat ini. Jika user meminta audit lengkap, load seluruh chain yang dibutuhkan.

## Rule Ambiguity
Jika data atau definisi tidak cukup untuk menentukan kondisi:
- gunakan `UNKNOWN` atau `DATA_UNAVAILABLE` pada item;
- jelaskan data yang hilang;
- jangan mengubahnya menjadi `VALID`.

## Scope
Allowed: market analysis, monitoring, explanation, research, historical review, backtest/simulation.

Forbidden: live order execution, autonomous buy/sell, broker action, mengubah core rules tanpa instruksi eksplisit user.
