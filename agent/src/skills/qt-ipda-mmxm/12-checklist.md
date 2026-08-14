# 12 — Master Checklist Rule Engine

## Tujuan
Mengubah seluruh hasil analysis menjadi status setup yang konsisten dan explainable.

## Urutan Checklist Top-Down
| # | Item | Item Status |
|---|---|---|
| 1 | Active Cycle identified | PENDING / VALID / INVALID |
| 2 | Active Orderflow identified | PENDING / VALID / INVALID |
| 3 | Active MMXM identified | PENDING / VALID / INVALID |
| 4 | IRL identified | PENDING / VALID / INVALID |
| 5 | ERL identified | PENDING / VALID / INVALID |
| 6 | IPDA phase identified | PENDING / VALID / INVALID |
| 7 | Price inside key level | PENDING / VALID / INVALID |
| 8 | True Open confluence checked | PENDING / VALID / INVALID |
| 9 | Sweep or SSMT occurred | PENDING / VALID / INVALID / SKIPPED |
| 10 | CISD confirmed | PENDING / VALID / INVALID |
| 11 | Target ERL defined | PENDING / VALID / INVALID |
| 12 | Final setup conclusion | NO_SETUP / WAITING / VALID / INVALID |

## Final Status Semantics
### NO_SETUP
Belum ada key level/struktur candidate yang valid untuk diproses sebagai setup.

### WAITING
Candidate setup ada, tetapi mandatory rule berikutnya belum terpenuhi.

Contoh:
- key level ada, price belum masuk;
- Sweep sudah valid, CISD masih pending.

### VALID
Semua mandatory rule terpenuhi sesuai sequence.

### INVALID
Ada mandatory rule gagal atau sequence salah.

Contoh:
- CISD terjadi sebelum Sweep/SSMT;
- mandatory context sudah ter-invalidate.

## Hard Gates
Setup **tidak boleh** `VALID` bila:
- key level belum tersedia;
- ERL belum ditentukan;
- Sweep atau SSMT belum terjadi;
- CISD belum terjadi;
- CISD hanya wick;
- sequence salah.

## SSMT SKIPPED
Jika no correlated pair:
- item SSMT = `SKIPPED`;
- jangan otomatis final `INVALID`;
- evaluasi apakah Sweep memenuhi `Sweep OR SSMT` gate.

## Explainability
Setiap item harus menyimpan/menyebut:
- status;
- evidence;
- reason;
- timestamp/timeframe bila relevan.

Jangan hanya mengeluarkan final label tanpa alasan.

## Analysis-Only Mapping
`VALID` berarti **setup conditions confirmed menurut rulebook**, bukan instruksi atau eksekusi buy/sell.
