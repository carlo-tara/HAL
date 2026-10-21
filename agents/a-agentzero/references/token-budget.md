# Token Budget — Protocollo di riduzione token (L0)

**Versione riferimento:** 1.0.0  
**Data:** 2026-10-21  
**Livello:** L0 (globale, non sovrascrivibile)

---

## Obiettivo

Ridurre l'output token degli agenti HAL senza perdere informazioni né qualità, mantenendo il context window sotto soglia critica e massimizzando il rapporto System1:System2.

## Metriche target

| Metrica | Target | Misura |
|---------|--------|--------|
| Output per sessione | < 500 token | Tracciato da `token_budget.py` |
| Context caricato | < 50K token | Somma frontmatter skill + file letti |
| Rapporto S1:S2 | ≥ 3:1 | Conteggio chiamate router vs reasoning |
| File per slice | ≤ 4 | Permission mode, waiver se >4 |
| Diff letto | ≤ 150 righe | Tiering automatico |
| Preambolo narrativo | 0 | Regola enforced |

---

## Le 13 Strategie

### Esistenti (7) — formalizzate con telemetria

| # | Strategia | Dove | Telemetria |
|---|-----------|------|------------|
| 1 | **Laya router pre-filtering** | `laya/SKILL.md` | `s1_routing_calls` |
| 2 | **≤4 file limits per slice** | `permission-modes.md` | `files_per_slice` |
| 3 | **Version gating** | `agent-version.sh` | `version_checks` |
| 4 | **Frontmatter checks** | `check-frontmatter-all.sh` | `fm_validations` |
| 5 | **Diff-tiering** | `improve/SKILL.md`, `review/SKILL.md` | `diff_lines_read` |
| 6 | **"No narrative" output** | `a-agentzero/SKILL.md` | `narrative_violations` |
| 7 | **Confidence-based routing** | `laya/SKILL.md` Strategy C | `confidence_escalations` |

### Nuove (6) — da implementare

| # | Strategia | Dove | Telemetria |
|---|-----------|------|------------|
| 8 | **Skip preamble enforcement** | Tutte le skill L0 | `preamble_skips` |
| 9 | **Lazy-load large files** | `a-agentzero/SKILL.md` | `lazy_load_hits` |
| 10 | **Chunk-based scoring** | `improve/SKILL.md` | `chunk_scores` |
| 11 | **Semantic pacing** | `laya/SKILL.md` Strategy B | `semantic_truncations` |
| 12 | **Multi-question anchoring** | `laya/SKILL.md` Strategy A | `anchored_decisions` |
| 13 | **Attachment filtering** | `a-agentzero/SKILL.md` | `attachments_summarized` |

---

## Flusso operativo

```
Richiesta utente
    │
    ▼
[1] Skip preamble? → No saluti, no "Reason why" auto-evidenti
    │
    ▼
[2] Laya triage/routing → System 1 pre-filtro
    │   ├─ Se confidence > 0.8 → esecuzione veloce
    │   ├─ Se confidence 0.3-0.8 → retry con sfida
    │   └─ Se confidence < 0.3 → escalation System 2
    │
    ▼
[3] Lazy-load: leggi solo righe rilevanti (start_line/end_line)
    │   └─ Mai leggere file interi se > 100 righe
    │
    ▼
[4] Diff-tiering: se diff > 150 righe, path-by-path
    │   └─ Mai riversare diff totale nel contesto
    │
    ▼
[5] Chunk-based scoring: frammenta input prima di System 2
    │   └─ Score < threshold → scarta proposta
    │
    ▼
[6] Attachment filtering: riassume liste lunghe ("15x .JPG")
    │
    ▼
[7] Output compatto: tabella/lista, zero narrativa
    │   └─ Max 500 token output
    │
    ▼
[8] Log telemetria in events/token-budget.jsonl
```

---

## Modulo telemetria

**File:** `a-agentzero/scripts/token_budget.py`

Il modulo traccia automaticamente:
- Tokens in/out per sessione
- Chiamate System1 vs System2
- File letti e dimensioni
- Dimensione diff processati
- Violazioni regole (preamboli, dump contesti)

**Esecuzione:**
```bash
python3 scripts/token_budget.py init        # Inizia tracciamento
python3 scripts/token_budget.log s1_call    # Log chiamata System1
python3 scripts/token_budget.log s2_call    # Log chiamata System2
python3 scripts/token_budget.log file_read path lines
python3 scripts/token_budget.log diff_read lines
python3 scripts/token_budget.log output tokens
python3 scripts/token_budget.log violation type
python3 scripts/token_budget report         # Report finale
```

**Output JSONL:** `events/token-budget.jsonl`

---

## Regole di sicurezza

- Nessun segreto nei log telemetrici
- Gli eventi storici non vanno mai cancellati
- Il tree può essere modificato in parallelo: leggere da HEAD prima di modificare
- `.env` non tracciato, solo nomi variabili e stato valorizzato/non

---

## Riferimenti correlati

- `laya/SKILL.md` — System 1 service e strategie A-D
- `improve/SKILL.md` — Diff-tiering e scoring euristico
- `review/SKILL.md` — Revisione mirata al diff
- `a-harness/references/permission-modes.md` — Policy ≤4 file
- `a-harness/references/harness-extended.md` — Lean cmd protocol, quiet test execution
