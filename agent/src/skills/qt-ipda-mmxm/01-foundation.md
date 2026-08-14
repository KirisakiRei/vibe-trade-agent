# 01 — Foundation & Analysis Doctrine

## Filosofi Dasar
Framework memandang market sebagai delivery dari liquidity ke liquidity melalui repricing dan struktur waktu. Tujuan analisis bukan menebak arah, tetapi mengidentifikasi:
- di mana harga sedang berada;
- dari liquidity/key level mana delivery berasal;
- liquidity/ERL mana yang menjadi objective;
- cycle dan phase apa yang sedang aktif;
- apakah alignment untuk setup sudah benar-benar terkonfirmasi.

## Tiga Komponen Utama
- **QT (Quarterly Theory):** konteks waktu — kapan fase/kejadian relevan diantisipasi.
- **IPDA Phase of Price:** bentuk delivery — bagaimana harga bergerak.
- **Key Level:** lokasi — area repricing/objective yang membuat QT dan IPDA memiliki konteks.

Tanpa key level yang relevan, jangan memaksakan setup QT/IPDA.

## Hierarki Top-Down

```text
Monthly Cycle     → Defines Objective
Weekly Cycle      → Defines Bias
Daily Cycle       → Defines Reversal Zone
90 Minute Cycle   → Defines Execution
Micro Cycle       → Defines Internal Delivery
```

Micro hanya alat observasi internal/presisi. Bila konflik dengan 90 Minute Orderflow, prioritaskan 90 Minute.

## Master Reading Sequence

```text
Cycle
→ Orderflow
→ MMXM
→ IRL
→ ERL
→ IPDA Phase
→ Alignment at Key Level
→ Sweep/SSMT
→ CISD
→ Final Status
```

## Authority Rules
1. Data aktual market.
2. Core rules skill ini.
3. Deterministic calculation/tool output.
4. Learned insight/historical observation.
5. Generic model knowledge.

Learned insight tidak boleh mengganti core rule.

## Hard Rules
- Selalu top-down.
- Jangan mencampur IRL/ERL dari timeframe berbeda sebagai satu pair delivery.
- HTF lebih dominan jika LTF key level berlawanan di area yang sama.
- Sweep atau SSMT harus terjadi sebelum CISD.
- CISD wajib berdasarkan body close/close candle terhadap structure, bukan wick.
- Setup tidak boleh `VALID` jika mandatory evidence belum tersedia.

## Dynamic, Bukan Memaksa Skenario
IF→THEN digunakan untuk antisipasi berdasarkan quarter sebelumnya, bukan memaksa harga mengikuti pola. Entry/alignment dapat muncul di Q2, Q3, atau Q4 bergantung kapan key level disentuh dan sequence Sweep/SSMT → CISD terkonfirmasi.

## Analysis-Only
Walaupun source framework menggunakan istilah entry/execute, project ini hanya menyatakan kondisi setup. Bila seluruh rule terpenuhi, keluarkan `VALID`, bukan melakukan order.
