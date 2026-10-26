# HAL — Autonomous Agent & Zed Framework

**HAL** è la piattaforma canonica e multi-progetto per agenti autonomi, skill modulari e comandi operativi, con supporto integrato per **Zed**.

---

## 🚀 Caratteristiche Principali

- **Integrazione Zed Editor**: Supporto nativo per l'editor Zed tramite link simbolici e mappature di prompt automatiche.
- **Architettura Cognitiva a Due Livelli**:
  - **System 1 (Laya)**: Svolge compiti preliminari ad alta velocità (routing, scelta discreta, scoring euristico, pre-filtro `noul`) con HTTP session pooling e cache in-memory `@lru_cache`. Per richieste atomiche, a basso rischio e brevi (istruzione + fonte < `PREFLIGHT_SHORT_MAX_CHARS`, 400 caratteri) il preflight remoto è saltato: `preflight` restituisce `abstain` con `reason=preflight_skipped_atomic`, senza consumare il budget e conservando fonte e formato; il chiamante procede in locale.
  - **System 2 (Reasoning)**: Riservato al ragionamento profondo, pianificazione, generazione di codice e refactoring.
- **Gateway Core Avanzato (v2.3.0) — [Verificato & Integrato in CI]**:
  - **Cache L1 Esatta (`07`)**: Chiave composita Redis con hashing SHA-256 dei contenuti reali dei file di contesto, TTL configurato per profilo d'uso e validazione dei tool boundary (**Verificato**).
  - **Retention & Redaction (`05`)**: Oscuramento preventivo di segreti, API key e token nei log con placeholder tipizzati (`{{secret:...}}`) e scansione PII protetta in scrittura JSONL (**Verificato**).
  - **Circuit Breaker & Session (`19`)**: Derivazione deterministica del `session_id`, State Machine del circuit breaker con controllo probe half-open concorrenti (`probe_in_flight`) e risoluzione con fallback automatico (**Verificato**).
  - **System 2 Provider & Routing Policy (`SystemTwoEngine`, `SystemRoutingPolicy`, `SystemEvaluationEngine`)**: Provider reali/mock configurabili, risoluzione per profilo e capability, policy di instradamento S1/S2 e motore di evaluation con replay, shadow mode e gate di rollback automatico (**Verificato**).
    - Il gate richiede rubriche con copertura sufficiente, qualità semantica indipendente e campioni di latenza serving; rifiuta output troncati o evidenza mancante. La durata end-to-end (`seconds`), che può includere il caricamento del modello, resta separata dalla latenza serving (`latency_ms`).
  - **Security Gates CI (`check_secrets.py`, `check_deps.py`, `check_sast.py`)**: Controlli automatici low-noise per secret scanning, audit delle dipendenze runtime con supporto advisory e SAST Python integrati nel gate GitHub Actions (**Verificato**).
- **Ecosistema Agenti L1**: 8 agenti primari che ereditano dall'agente radice `a-agentzero`.

---

## 📁 Struttura del Workspace

- `agents/`: Sorgenti canoniche di tutti gli agenti, skill, competenze e script.
- `scripts/`: Script di utilità e gate CI (secret scanning, dependency audit, SAST audit, benchmark).
- `Makefile`: Platform API locale — gate di review specchio CI (`make ready-for-review`) e suite unit (`make test-unit`).
- `tests/`: Suite completa dei test unitari e di integrazione (eseguita in CI da `.github/workflows/ready-for-review.yml`; dipendenze di sviluppo in `requirements-dev.txt`).
- `benchmark/`: Runner, report e storico dei benchmark System 1/System 2; `hal_system2` è la sorgente canonica, vedi [benchmark/README.md](benchmark/README.md).
- `.agents/skills/`: Symlink condivisi per tutte le skill L0/L1/L2.
- `.zed/prompts/`: Prompt e comandi convertiti ed esposti come slash-command in Zed.
- `router.py` / `laya_service.py`: Interfaccia di System 1 (Laya) con supporto per routing e batch scoring.

---

## 🛠️ Quick Start & Sincronizzazione

Per rigenerare tutti i link simbolici e le mappature dei prompt per Zed:

```bash
bash agents/scripts/link-workspace-skills.sh
```

La versione di ogni wrapper `.agents/skills/<comando>/SKILL.md` generato viene dal campo `version:` nel frontmatter del comando canonico (`agents/a-agentzero/commands/<comando>.md`, default `1.0.0`): il bump va fatto lì, non sul wrapper.

Per eseguire i gate di review localmente (specchio di `.github/workflows/ready-for-review.yml`):

```bash
make test-unit
make ready-for-review
```

Per testare il router System 1 (Laya):

```bash
python3 router.py triage "analizza metriche seo"
python3 router.py routing "ottimizza query db" --routes a-harness a-wordpress a-b2b
```

Per eseguire i test unitari del Gateway Core:

```bash
python3 -m unittest discover -s tests
```

Per verificare che le copie del runner nel gateway coincidano con `hal_system2`:

```bash
bash benchmark/scripts/sync_hal_system2.sh check   # `apply` copia canonico → gateway
```

---

## 🤖 Agenti Primari (L1)

1. **`a-agentzero` (L0)**: Radice del protocollo, sicurezza, versioni e workflow.
2. **`a-harness`**: Meta-Harness TDD XP, Steward, DDD e gate Make.
3. **`a-product`**: Product Discovery, PRD, Personas, JTBD e BDD Gherkin.
4. **`a-seozoom`**: SEO/GEO multi-progetto, import dati, metriche, on-page, audit e Google Ads.
5. **`a-design`**: UI/UX, Data Visualization (Charts) e Brand Illustrator.
6. **`a-copywriter`**: Copywriting web, Humanizer anti-AI e italiano locale.
7. **`a-b2b`**: Piloti B2B, contact/account research e CRM cascade.
8. **`a-wordpress`**: Analisi installazioni, plugin stabili e migrate.
9. **`a-knowledge`**: Knowledge / Context Engineering - libri e doc tecnici (PDF/EPUB/DOCX/HTML) in skill on-demand; estrazione CPU-first, distillazione una-tantum, book-to-skill.

---

## 📄 License & Versioning

Questo progetto adotta [Semantic Versioning](https://semver.org/lang/it/) e il formato [Keep a Changelog](https://keepachangelog.com/it/1.1.0/). Vedi [CHANGELOG.md](CHANGELOG.md).
