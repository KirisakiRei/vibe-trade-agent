# QT/IPDA/MMXM Skill Manifest

**Versi rulebook: 1.2.0**

Folder ini berisi skill modular untuk Vibe-Trading/custom agent:

1. `SKILL.md` — entry point dan routing.
2. `01-foundation.md`
3. `02-cycle-quarter.md`
4. `03-market-structure.md`
5. `04-key-levels.md`
6. `05-true-open.md`
7. `06-ipda.md`
8. `07-mmxm.md`
9. `08-orderflow.md`
10. `09-sweep.md`
11. `10-ssmt.md`
12. `11-cisd.md`
13. `12-checklist.md`
14. `13-bullish-setup.md`
15. `14-bearish-setup.md`
16. `15-output-format.md`

Source basis:
- Trading Checklist Engine PRD(2).pdf
- ICT Concepts MMXM Quarterly Theory.pdf

Core rule files harus diperlakukan read-only oleh self-learning layer.

## Changelog

### v1.2.0
- `15-output-format.md`: default Telegram menjadi BRIEF (maks. 12 baris). FULL AUDIT hanya jika user meminta lengkap/audit/detail.
- `SKILL.md`: klausa brevity — jangan load seluruh rulebook untuk pertanyaan singkat.

### v1.1.0
- `09-sweep.md`: `sweepDistanceTolerance` diperjelas sebagai 10% dari *range* key level (`keyLevel.high - keyLevel.low`), bukan persentase dari nilai harga level.
- `SKILL.md`: tambah kontrak Data Requirements (OHLC candle + timezone `America/New_York` + tabel timeframe per cycle).
- `11-cisd.md`: referensi structure diperjelas (`minorStructureHigh` / `minorStructureLow`) tanpa mengubah semantik rule.

### v1.0.0
- Rulebook awal dari kedua PDF sumber, struktur 01–15 + SKILL.md + MANIFEST.md.
