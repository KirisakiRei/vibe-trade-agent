# AGENT.md

## 1. Project Mission

Project ini adalah custom fork dari:

`https://github.com/HKUDS/Vibe-Trading`

Tujuan utama project adalah membangun **AI Trading Analysis Agent 24/7** berbasis Vibe-Trading yang menggunakan trading framework milik project:

* QT
* IPDA
* MMXM
* ICT / Smart Money concepts terkait
* custom trading checklist
* custom trading rules

Agent digunakan untuk:

* monitoring market
* membaca market structure
* menjalankan analisis multi-timeframe
* mengevaluasi trading checklist
* menjelaskan kondisi market
* melakukan research dan backtesting
* menyimpan pengalaman/insight
* berinteraksi melalui Telegram
* melakukan scheduled analysis 24/7

**Project ini BUKAN auto-trading system.**

Jangan menambahkan live order execution, broker auto-execution, copy trading, atau autonomous money management kecuali user secara eksplisit mengubah scope project di masa depan.

---

# 2. Primary Architecture Principle

Gunakan Vibe-Trading sebagai fondasi.

Jangan rewrite agent framework dari nol.

Pertahankan sebanyak mungkin arsitektur upstream dan lakukan modifikasi secara:

* modular
* minimally invasive
* backward-compatible bila memungkinkan
* mudah di-rebase/merge dari upstream
* mudah diuji
* mudah di-disable
* configuration-driven

Target architecture:

```text
Market Data
    │
    ▼
Vibe-Trading Tools
    │
    ▼
QT / IPDA / MMXM Skills
    │
    ▼
Trading Analysis Agent
    │
    ├── Current Market Analysis
    ├── Checklist Evaluation
    ├── Historical Research
    ├── Backtest
    ├── Memory
    └── Learning Layer
            │
            ▼
      Telegram Channel
            │
            ▼
           User
```

Scheduled analysis:

```text
Scheduler
    │
    ▼
Load Market Data
    │
    ▼
Load Trading Rules
    │
    ▼
Analyze
    │
    ▼
NO_SETUP / WAITING / VALID / INVALID
    │
    ▼
Store Result
    │
    ▼
Telegram Notification
```

---

# 3. Development Workflow

Gunakan workflow berikut untuk setiap task:

**Understand → Inspect → Plan → Implement → Verify → Report**

Sebelum mengubah code:

1. baca `AGENT.md`
2. inspect implementasi upstream yang relevan
3. pahami data flow saat ini
4. pahami existing tests
5. tentukan perubahan minimum
6. hindari duplicate implementation

Jangan mengasumsikan struktur repository berdasarkan dokumentasi lama.

Repository Vibe-Trading dapat berubah.

Selalu inspect source code aktual terlebih dahulu.

---

# 4. Upstream Preservation

Repository ini adalah fork/customization dari Vibe-Trading.

Jangan melakukan rewrite besar tanpa alasan kuat.

Prioritaskan:

```text
extension > adapter > wrapper > small modification > rewrite
```

Jika fitur upstream sudah tersedia, gunakan fitur tersebut.

Contoh:

* Telegram → gunakan channel runtime bawaan bila memenuhi kebutuhan
* scheduler → gunakan scheduler bawaan
* memory → extend memory bawaan
* skill system → gunakan skill loader bawaan
* backtest → gunakan backtest infrastructure bawaan
* market data → gunakan provider/tool infrastructure bawaan
* agent loop → extend, jangan ganti tanpa alasan kuat

Setiap modifikasi terhadap upstream core harus memiliki alasan yang jelas.

---

# 5. Trading Rule Authority

Trading rules milik user adalah **source of truth**.

Agent tidak boleh mengganti rule berdasarkan:

* general trading knowledge
* model training knowledge
* internet opinion
* strategi bawaan Vibe-Trading
* hasil reasoning agent
* self-learning
* backtesting semata

Urutan authority:

```text
1. User Trading Rules
2. Project Skill Files
3. Explicit Project Configuration
4. Deterministic Calculations
5. Historical Research / Learned Insight
6. Generic Model Knowledge
```

Jika terdapat konflik, rule dengan authority lebih tinggi menang.

---

# 6. Core Trading Framework

Framework utama project:

```text
QT
↓
Cycle / Quarter
↓
Higher Timeframe Context
↓
Orderflow
↓
IPDA
↓
MMXM
↓
IRL
↓
ERL
↓
Key Level Interaction
↓
True Open Context
↓
Sweep / SSMT
↓
CISD
↓
Final Checklist
```

Detail final rule tidak ditulis langsung di file ini.

Rules akan diletakkan sebagai dedicated project skills.

`AGENT.md` hanya menetapkan bahwa rules tersebut authoritative.

---

# 7. Trading Skill Architecture

Trading rules harus dipisahkan secara modular.

Target awal:

```text
skills/
└── qt-ipda-mmxm/
    ├── SKILL.md
    ├── 01-foundation.md
    ├── 02-cycle-quarter.md
    ├── 03-market-structure.md
    ├── 04-key-levels.md
    ├── 05-true-open.md
    ├── 06-ipda.md
    ├── 07-mmxm.md
    ├── 08-orderflow.md
    ├── 09-sweep.md
    ├── 10-ssmt.md
    ├── 11-cisd.md
    ├── 12-checklist.md
    ├── 13-bullish-setup.md
    ├── 14-bearish-setup.md
    └── 15-output-format.md
```

Lokasi aktual harus mengikuti mekanisme skill loader Vibe-Trading yang ditemukan di source code saat implementasi.

Jangan memaksakan path di atas jika upstream memiliki convention yang berbeda.

`SKILL.md` menjadi entry point.

Supporting files digunakan untuk detail rules agar context tetap efisien.

---

# 8. Core Rules Must Be Immutable

Ini requirement kritis.

Trading framework utama tidak boleh diubah oleh self-learning.

Core rules harus dianggap:

```text
LOCKED
IMMUTABLE BY AGENT
HUMAN CONTROLLED
VERSIONED
```

Agent tidak boleh otomatis:

* menghapus mandatory confirmation
* mengubah definisi setup valid
* mengubah sequence trading
* mengganti definisi CISD
* mengganti definisi Sweep
* mengganti definisi SSMT
* mengubah cycle/quarter rule
* mengubah BISI/SIBI rule
* mengubah IRL/ERL rule
* menurunkan confirmation requirement
* menciptakan rule trading baru sebagai rule resmi

Perubahan core rule hanya dilakukan setelah explicit human instruction.

---

# 9. Self-Learning Philosophy

Gunakan kemampuan persistent memory dan self-evolving skill Vibe-Trading, tetapi tambahkan governance.

Self-learning project ini berarti:

```text
Observe
↓
Store
↓
Evaluate
↓
Research
↓
Generate Insight
↓
Reuse Insight
```

Bukan:

```text
Observe Loss
↓
Rewrite Core Trading Rules
```

Learning layer boleh belajar:

* performance per symbol
* performance per session
* performance per quarter
* performance per timeframe
* market regime
* recurring market behavior
* historical setup statistics
* importance of optional confluences
* backtest observations
* research conclusions
* analysis mistakes
* successful reasoning patterns
* failed reasoning patterns
* data quality observations

Contoh learned insight yang valid:

```text
BTC Daily Q3 setups historically perform better
when Sweep + SSMT + CISD are all present.
```

Contoh learning yang TIDAK valid:

```text
CISD sering terlambat, maka mulai sekarang
CISD tidak wajib.
```

Yang kedua harus ditolak.

---

# 10. Learning Storage Separation

Pisahkan knowledge menjadi minimal:

```text
CORE RULES
    │
    └── read-only for agent

LEARNED INSIGHTS
    │
    └── writable

MEMORY
    │
    └── writable

RESEARCH RESULTS
    │
    └── writable

PROPOSED RULE CHANGES
    │
    └── writable but never auto-applied
```

Jika upstream self-evolving skill tools dapat melakukan save/patch/delete, tambahkan protection agar agent tidak dapat memodifikasi protected trading-rule files.

Implementasikan allowlist/denylist atau equivalent governance mechanism.

Contoh conceptual policy:

```text
qt-ipda-mmxm/core/*
    → agent write DENIED

learned/*
    → agent write ALLOWED

research/*
    → agent write ALLOWED

proposals/*
    → agent write ALLOWED
```

Gunakan struktur aktual yang paling sesuai dengan repository.

---

# 11. Rule Change Proposal

Agent boleh menyarankan perubahan.

Agent tidak boleh menerapkannya sendiri.

Flow:

```text
Observation
    ↓
Research
    ↓
Backtest
    ↓
Potential Improvement
    ↓
PROPOSAL
    ↓
Human Review
    ↓
Approve / Reject
```

Proposal harus memiliki:

* current rule
* proposed change
* reason
* historical evidence
* sample size
* backtest result bila tersedia
* potential benefit
* risk
* affected files
* rollback plan

Tidak boleh auto-merge ke core skill.

---

# 12. Learning Auditability

Semua perubahan writable learning state harus dapat dilacak.

Jika memungkinkan simpan:

* timestamp
* source
* symbol
* timeframe
* observation
* confidence
* evidence
* related analysis/session
* created by
* previous value
* new value

Self-learning harus:

* inspectable
* reversible
* auditable

Hindari hidden mutation.

---

# 13. Analysis-Only Mode

Project harus default ke:

```text
ANALYSIS_ONLY=true
```

Atau mekanisme konfigurasi equivalent.

Pada mode ini:

Allowed:

* market data access
* research
* technical analysis
* backtest
* simulation
* memory
* skills
* scheduler
* Telegram communication
* reporting

Forbidden:

* live buy
* live sell
* live position modification
* exchange withdrawal
* broker execution
* autonomous order submission

Jika upstream memiliki trading connectors, jangan hapus sembarangan karena dapat menyulitkan upstream merge.

Lebih baik:

* disable
* gate
* exclude from agent tool registry
* reject execution tools in project mode

---

# 14. No Hallucinated Confirmation

Agent tidak boleh menganggap suatu kondisi terpenuhi tanpa data.

Jika data tidak cukup:

```text
UNKNOWN
SKIPPED
DATA_UNAVAILABLE
```

sesuai context.

Jangan mengganti missing data dengan reasoning spekulatif.

Contoh:

```text
SSMT pair unavailable
```

bukan:

```text
SSMT kemungkinan bullish.
```

Untuk mandatory rule:

```text
missing confirmation
→ setup cannot be VALID
```

---

# 15. Checklist Status

Final setup state harus konsisten menggunakan:

```text
NO_SETUP
WAITING
VALID
INVALID
```

Supporting checklist item dapat memiliki:

```text
PENDING
VALID
INVALID
SKIPPED
UNKNOWN
```

Interpretasi:

### NO_SETUP

Belum terdapat struktur/setup yang relevan.

### WAITING

Setup candidate ada tetapi masih menunggu confirmation wajib.

### VALID

Semua mandatory rules terpenuhi dengan sequence benar.

### INVALID

Mandatory rule gagal atau sequence invalid.

### SKIPPED

Hanya untuk optional/non-applicable rule.

---

# 16. Analysis Explanation

Setiap analysis harus explainable.

Jangan hanya menghasilkan:

```text
BTC LONG
```

Output harus menjelaskan alasan.

Minimum analysis output:

```text
Symbol
Timestamp

Active Cycle
Active Quarter

HTF Context
Orderflow
IPDA Phase
MMXM Model

IRL
ERL
True Open

Price Inside Key Level
Sweep
SSMT
CISD

Final Status

Evidence
Missing Confirmation
Invalidation Reason
```

Agent harus membedakan:

```text
FACT
```

dengan:

```text
INTERPRETATION
```

dan:

```text
LEARNED HISTORICAL INSIGHT
```

---

# 17. Telegram Is Primary User Interface

Production interface utama adalah Telegram.

Gunakan adapter Telegram native Vibe-Trading terlebih dahulu.

Jangan membuat Telegram bot framework kedua jika adapter existing sudah cukup.

Telegram harus mendukung:

* direct conversation
* current market analysis
* follow-up questions
* scheduled analysis delivery
* notification setup
* session reset
* health/status check

Contoh:

```text
User:
Analisa BTC sekarang.

Agent:
BTCUSDT
...
STATUS: WAITING
Waiting for bullish 5M CISD.
```

Follow-up:

```text
User:
Kenapa belum valid?
```

Agent harus mempertahankan context yang relevan.

---

# 18. Telegram Security

Bot production harus private/restricted.

Jangan default ke public access.

Gunakan mechanism upstream seperti:

* allowlist
* Telegram user ID
* authorized username
* pairing

sesuai implementation aktual.

Bot token:

* environment/config secret
* tidak hardcode
* tidak commit ke Git
* tidak print ke log
* tidak expose melalui frontend

`.env`, secret config, token, API key harus masuk `.gitignore`.

---

# 19. Scheduler

Gunakan scheduler bawaan Vibe-Trading bila memenuhi kebutuhan.

Scheduler digunakan untuk:

* periodic market analysis
* routine research
* periodic learning review
* scheduled summary

Untuk execution timeframe 5M, scheduler awal dapat berjalan sekitar candle-close interval yang relevan.

Jangan melakukan continuous LLM call setiap detik.

Preferred model:

```text
Market interval/event
        ↓
Scheduler
        ↓
Agent Run
```

bukan:

```text
Infinite LLM loop
```

Tujuannya:

* mengurangi token
* mengurangi API cost
* mengurangi duplicate analysis
* meningkatkan determinism

---

# 20. Notification Policy

Jangan spam Telegram setiap scheduler run jika tidak ada perubahan berarti.

Ideal behavior:

```text
NO_SETUP → NO_SETUP
    no notification

WAITING → WAITING same reason
    no notification

NO_SETUP → WAITING
    notify

WAITING → VALID
    notify

WAITING → INVALID
    notify

VALID → INVALIDATED
    notify
```

Periodic heartbeat/summary dapat dibuat terpisah.

Implementasikan deduplication bila diperlukan.

---

# 21. Market Analysis Persistence

Simpan analysis history agar dapat digunakan untuk:

* audit
* debugging
* learning
* historical evaluation
* comparison
* performance study

Minimum useful metadata:

```text
analysis_id
symbol
timestamp
market_data_timestamp
timeframes
cycle
quarter
orderflow
ipda
mmxm
irl
erl
true_open
sweep
ssmt
cisd
final_status
reason
skill_version
model
```

Gunakan existing persistence infrastructure bila tersedia.

Jangan membuat database kedua tanpa kebutuhan.

---

# 22. Skill Versioning

Trading skill harus memiliki version identifier.

Contoh:

```text
qt-ipda-mmxm v1.0.0
```

Setiap analysis sebaiknya dapat diketahui menggunakan rule version apa.

Hal ini penting karena historical analysis harus dapat direproduksi.

---

# 23. Backtesting and Research

Backtest bukan authority untuk mengubah core rule.

Backtest digunakan untuk:

* evaluate historical performance
* compare contexts
* identify regime sensitivity
* measure optional confluence
* discover weaknesses
* generate proposals

Hindari overfitting.

Jika agent menghasilkan conclusion dari historical research, sertakan:

* data range
* symbol
* timeframe
* number of samples
* assumptions
* metrics
* limitations

Jangan menyatakan sebuah pattern profitable hanya dari sample kecil.

---

# 24. Telegram Deployment Target

Production target:

```text
Internet
   │
   ▼
Domain
   │
   ▼
Nginx
   │
   ▼
Vibe-Trading API / Web UI

Vibe-Trading Runtime
   │
   └── Telegram Adapter
           │
           ▼
        Telegram
```

Domain/Nginx terutama digunakan untuk:

* HTTPS
* Web UI
* API
* optional webhook endpoint
* observability/admin access

Telegram dapat menggunakan polling terlebih dahulu jika lebih sederhana.

Jangan memaksakan webhook kecuali dibutuhkan.

---

# 25. VPS Deployment

Production harus mudah dijalankan setelah reboot.

Preferred deployment should use one clear process management strategy.

Contoh candidates:

* systemd
* Docker Compose

Pilih berdasarkan existing repository support dan maintainability.

Jangan menjalankan production hanya dari SSH terminal foreground.

Production requirement:

```text
auto start
auto restart
logs
health check
secret management
persistent storage
backup
```

---

# 26. Nginx

Saat deployment:

* gunakan reverse proxy
* gunakan HTTPS
* redirect HTTP → HTTPS
* support WebSocket/SSE bila diperlukan Vibe-Trading
* set reasonable proxy timeout untuk long agent runs
* jangan expose internal service port langsung ke internet jika tidak perlu

Target:

```text
127.0.0.1:<internal-port>
        ↑
      Nginx
        ↑
     HTTPS
```

Jangan mengubah port atau network configuration tanpa inspect deployment target terlebih dahulu.

---

# 27. Production Secrets

Secret yang mungkin digunakan:

* LLM API key
* Telegram bot token
* market-data credentials
* optional external APIs

Rules:

```text
NEVER COMMIT SECRET
NEVER HARDCODE SECRET
NEVER LOG FULL SECRET
```

Provide `.env.example` jika diperlukan.

Example hanya menggunakan placeholder.

---

# 28. Observability

Tambahkan log yang berguna untuk:

```text
agent start
channel start
scheduler run
market data failure
skill load failure
analysis start/end
analysis state change
Telegram delivery
learning write
learning proposal
```

Jangan log:

* full API keys
* Telegram token
* private credentials

Errors harus actionable.

---

# 29. Failure Handling

Jika market data gagal:

```text
do not fabricate analysis
```

Return appropriate error/state.

Jika LLM gagal:

* retry secara terbatas
* log error
* jangan loop tanpa batas

Jika Telegram gagal:

* analysis tidak harus hilang
* save result
* retry delivery bila reasonable

Jika skill gagal load:

* fail visibly
* jangan fallback diam-diam ke generic trading analysis

---

# 30. Testing Requirements

Setiap project-specific modification harus memiliki test jika reasonable.

Prioritas test:

### Self-learning protection

Verify bahwa agent tidak dapat mengubah protected core trading skill.

### Skill loading

Verify custom QT/IPDA/MMXM skill terdeteksi.

### Checklist behavior

Verify mandatory confirmations.

### Telegram authorization

Verify unauthorized users ditolak.

### Scheduler

Verify scheduled analysis dapat trigger agent.

### Notification deduplication

Verify repeated identical state tidak menyebabkan spam.

### Persistence

Verify restart tidak menghilangkan required persistent state.

---

# 31. Regression Protection

Sebelum commit:

1. run existing upstream tests yang relevan
2. run project-specific tests
3. run lint/type checks bila tersedia
4. verify CLI masih bekerja
5. verify server masih boot
6. verify Telegram adapter masih bekerja

Jangan memperbaiki unrelated failures dengan rewrite besar.

Report unrelated pre-existing failure secara terpisah.

---

# 32. Coding Standards

Gunakan:

* clear naming
* small functions
* explicit types
* structured errors
* dependency injection bila architecture mendukung
* module boundaries yang jelas
* configuration over hardcoding
* reusable services
* testable code

Hindari:

* giant services
* hidden global state
* duplicated rule logic
* magic numbers
* silent exception swallowing
* unnecessary abstractions
* unrelated refactors

---

# 33. Trading Logic Must Not Be Duplicated

Satu rule harus memiliki satu canonical source.

Jangan mendefinisikan:

```text
CISD rule di prompt
+
CISD rule di Python
+
CISD rule di Telegram formatter
```

dengan isi berbeda.

Pisahkan:

```text
Rule definition
        ↓
Analysis/evaluation
        ↓
Presentation
```

Presentation tidak boleh mempunyai business logic.

---

# 34. Prompt Design

System/agent prompt harus compact.

Jangan memasukkan seluruh trading rule puluhan halaman ke base system prompt.

Gunakan skill loader/supporting files.

System prompt cukup menjelaskan:

* project purpose
* authority hierarchy
* analysis-only constraint
* no hallucinated confirmation
* skill usage requirements
* core-rule immutability

Load detailed trading knowledge hanya ketika relevan.

---

# 35. Context Efficiency

Project harus menjaga penggunaan token.

Prefer:

```text
structured market state
+
relevant skill sections
+
recent relevant memory
```

daripada:

```text
entire market history
+
entire trading rulebook
+
entire conversation
```

Gunakan existing context compression/memory infrastructure bila tersedia.

---

# 36. Human Control

User selalu mempunyai authority tertinggi.

Agent harus meminta explicit authorization untuk:

* changing core trading rules
* enabling live trading
* adding broker execution
* altering risk rules
* deleting learned history
* destructive migrations

Jangan membuat keputusan consequential secara diam-diam.

---

# 37. Development Phases

## Phase 1 — Baseline

Goal:

```text
clone
install
run
understand
```

Tasks:

* clone upstream
* install dependencies
* run tests
* run CLI
* run Web/API
* inspect skills
* inspect memory
* inspect channel runtime
* inspect scheduler
* inspect persistence

Jangan modifikasi sebelum baseline berjalan.

---

## Phase 2 — Project Customization

Goal:

```text
make Vibe-Trading safe for our rule-based analyst
```

Tasks:

* analysis-only mode
* self-learning governance
* immutable core skill protection
* learned-insight storage
* rule-change proposal mechanism
* project config
* logging

---

## Phase 3 — Trading Skills

Goal:

```text
encode complete QT/IPDA/MMXM trading system
```

Tasks:

* create all skill markdown files
* preserve user rule terminology
* preserve rule sequence
* identify mandatory vs optional conditions
* define output format
* add skill versioning
* test skill retrieval

Do not invent missing trading rules.

If source rules are ambiguous, mark ambiguity for user review.

---

## Phase 4 — Telegram

Goal:

```text
chat with Vibe-Trading through private Telegram bot
```

Tasks:

* configure Telegram
* restrict allowed user
* test conversation
* test follow-up context
* test `/reset` or equivalent session controls
* verify no secrets leak

---

## Phase 5 — 24/7 Analysis

Goal:

```text
scheduled analysis
```

Tasks:

* enable scheduler
* define initial symbols
* define analysis interval
* store analysis result
* detect state transitions
* deliver meaningful transitions to Telegram
* prevent spam

---

## Phase 6 — VPS Production

Goal:

```text
stable 24/7 deployment
```

Tasks:

* push fork
* clone/pull on VPS
* configure environment
* configure process manager
* configure persistent directories
* configure domain
* configure Nginx
* configure HTTPS
* verify restart recovery
* verify Telegram
* verify scheduler

---

## Phase 7 — Validation

Before declaring production ready:

```text
Manual Analysis
      ↕
Agent Analysis
```

Compare multiple historical/current market cases.

Verify:

* Cycle
* Quarter
* BISI/SIBI
* IRL
* ERL
* True Open
* IPDA
* MMXM
* Sweep
* SSMT
* CISD
* Final Status

Any repeated mismatch must be investigated.

---

# 38. Current Project Scope

Current scope:

```text
YES
- AI market analyst
- 24/7 monitoring
- QT/IPDA/MMXM rules
- custom skills
- persistent memory
- bounded self-learning
- historical research
- backtesting
- Telegram
- Web/API
- VPS
- scheduler
- notifications
```

Current scope:

```text
NO
- autonomous live trading
- automatic broker execution
- copy trading
- changing core rules automatically
- autonomous leverage decisions
- autonomous money management
```

---

# 39. Definition of Done

Project v1 dianggap berhasil jika:

1. Vibe-Trading berjalan stabil di VPS.
2. Telegram bot terhubung dan restricted ke authorized user.
3. Custom QT/IPDA/MMXM skills berhasil dimuat.
4. Agent dapat menganalisis symbol berdasarkan trading rules project.
5. Agent menghasilkan status:

   * NO_SETUP
   * WAITING
   * VALID
   * INVALID
6. Agent dapat menjelaskan alasan setiap status.
7. Missing confirmation tidak boleh di-infer.
8. Scheduler dapat menjalankan analysis 24/7.
9. State change penting dapat dikirim ke Telegram.
10. Duplicate notification dapat dikendalikan.
11. Memory tetap tersedia setelah restart.
12. Self-learning dapat menyimpan insight.
13. Self-learning tidak dapat mengubah core trading rules.
14. Semua perubahan learning dapat diaudit.
15. Tidak ada live order execution.
16. Domain + HTTPS + Nginx berjalan.
17. Service kembali hidup setelah VPS reboot.
18. Basic tests dan project-specific tests lulus.

---

# 40. Builder Reporting Format

Setelah menyelesaikan task, laporkan singkat:

```text
Implemented
- ...

Files Changed
- ...

Behavior
- ...

Verification
- ...

Remaining
- ...

Risks / Notes
- ...
```

Jangan memberikan narasi panjang jika tidak diperlukan.

---

# 41. Critical Rules for AI Builder

Always:

* inspect before editing
* preserve upstream architecture
* follow project trading rules
* keep core rules immutable
* keep project analysis-only
* protect secrets
* add tests for critical behavior
* prefer existing Vibe-Trading capabilities
* keep modifications modular
* document project-specific deviations

Never:

* invent trading rules
* silently change trading rules
* allow self-learning to rewrite core strategy
* hallucinate missing market confirmation
* enable live execution
* hardcode credentials
* expose Telegram bot publicly by default
* rewrite upstream unnecessarily
* claim something is tested when it was not tested
        