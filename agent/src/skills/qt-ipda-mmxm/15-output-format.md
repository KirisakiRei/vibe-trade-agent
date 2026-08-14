# 15 — Output Format for Agent / Telegram

## Tujuan
Jawaban harus compact, audit-friendly, dan tidak menyamarkan missing evidence.

## Standard Analysis Output

```text
{SYMBOL} — QT/IPDA/MMXM
As of: {timestamp + timezone}

Cycle
- Monthly: {cycle/quarter/status}
- Weekly : {cycle/quarter/status}
- Daily  : {quarter + NY session}
- 90M    : {quarter}

Context
- HTF Context : {bullish/bearish/mixed/unknown}
- Orderflow   : {TF IRL → TF ERL}
- MMXM        : {IRL_TO_ERL / ERL_TO_IRL / ERL_TO_ERL / UNKNOWN}
- IPDA        : {CONSOLIDATION / EXPANSION / RETRACEMENT / REVERSAL / UNKNOWN}

Levels
- IRL         : {type, timeframe, zone}
- ERL         : {type, timeframe, price}
- True Open   : {price, PREMIUM/DISCOUNT}
- Price in KL : {VALID/PENDING/INVALID/UNKNOWN}

Alignment
- Sweep       : {VALID/PENDING/INVALID/UNKNOWN}
- SSMT        : {VALID/PENDING/INVALID/SKIPPED/UNKNOWN}
- CISD        : {VALID/PENDING/INVALID/UNKNOWN}

FINAL STATUS: {NO_SETUP/WAITING/VALID/INVALID}
DIRECTION   : {BULLISH/BEARISH/NONE/UNKNOWN}

Reason:
{ringkas, evidence-based}

Missing confirmation:
{mandatory item yang belum ada, atau NONE}
```

## Evidence Rules
Saat status `VALID`, sertakan minimal:
- active key level;
- active ERL;
- Sweep/SSMT evidence;
- CISD structure + candle close;
- sequence validity.

## WAITING
Harus menyebut **apa tepatnya yang ditunggu**.

Contoh:
```text
FINAL STATUS: WAITING
Reason: Price sudah berada di 4H BISI dan sell-side sweep valid.
Missing confirmation: Bullish 5M CISD.
```

## INVALID
Harus menyebut rule yang gagal.

Contoh:
```text
FINAL STATUS: INVALID
Reason: Break structure terjadi sebelum Sweep/SSMT.
Invalidation: INVALID_SEQUENCE.
```

## NO_SETUP
Jangan membuat directional call bila key level/structure belum cukup.

## Directional Request (Trade Direction)
Saat user bertanya arah/skenario trade:

- Berikan `DIRECTION` tegas: `BULLISH` / `BEARISH` / `NONE`/`UNKNOWN`.
- Sertakan level aksi: IRL, ERL, True Open, dan target likuiditas (BSL/SSL).
- Sertakan skenario: "jika price close di atas X → bias bullish menuju Y; invalidation bila close kembali di bawah Z".
- Semua claim wajib ditautkan ke evidence checklist (sweep, SSMT, CISD, STS).
- **DILARANG**: ukuran posisi, lot, persentase, "beli sekarang"/"jual sekarang", dan instruksi eksekusi broker. Arah + level + skenario adalah output analitis, bukan nasihat — jangan menolak memberikannya.

## Fact vs Interpretation
Jika ada insight probabilistik/historis, pisahkan:

```text
FACTS
...

HISTORICAL INSIGHT
...
```

Insight tidak boleh mengubah final rule status.

## Telegram Style
- Hindari paragraf panjang.
- Gunakan label konsisten.
- Jangan spam emoji.
- Jangan memberi bahasa kepastian profit.
- Jangan mengirim order instruction.

## Data Unavailable
Jika data market/pair/timeframe tidak tersedia:

```text
DATA_UNAVAILABLE
```

jelaskan data yang gagal diambil dan jangan fabricate nilai.

## Status Boundary
`UNKNOWN`, `SKIPPED`, `PENDING`, dan `DATA_UNAVAILABLE` hanya boleh menjadi status item checklist atau data — **tidak pernah** menjadi `FINAL STATUS`. Final hanya salah satu dari `NO_SETUP`, `WAITING`, `VALID`, `INVALID`. Jika sebuah mandatory item adalah `UNKNOWN`, final status yang benar adalah `WAITING` (tunggu data) atau `INVALID` (data hilang permanen untuk rule yang wajib), bukan `VALID`.
