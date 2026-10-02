# Harness Engineering — Meta-Harness HAL

Guida **meta** per **`a-harness`**: posizione, omonimi, maturity, evoluzione.  
Operativo (slash, competenze, bootstrap): [`a-harness/SKILL.md`](../a-harness/SKILL.md).  
Umano: [`a-harness-manuale-utente.md`](a-harness-manuale-utente.md) (§13 man).

**Equazione:** Agent = Model + Harness. a-harness = skill-layer di *processo* sopra Cursor/Claude — non competitor IDE/VM.

---

## Evoluzione e manutenzione

1. **Analisi** → aggiorna piano e/o pin `*-source.md`; **non** implementare in quel passo
2. **Execute** → deliverable del piano; **non** editare `.plan.md` in implementazione
3. Pin/reference = traccia stabile; piano Cursor = artefatto di sessione
4. **Documentazione comandi:** canone = manuale §13; se «tutti i comandi» è ambiguo, chiarisci perimetro (harness+L0+Make vs discovery) prima di scrivere
5. **Ownership docs:** SKILL = operativo (slash, cycle, deleghe); `harness-engineering` = meta (omonimi, maturity, evoluzione); manuale = umano (+ man). Non riduplicare tabelle principi/slash/deleghe tra i tre
6. **Razionalizzazione:** snellisci per dedup/merge di reference e pin omogenei; **non** rimuovere gate né competenze di fase; `/slice` e `/cycle` restano orchestrazione in SKILL (no competency dedicata)

Pin: [`pin-curated-lists.md`](../a-harness/references/pin-curated-lists.md) + pin singoli in `a-harness/references/*-source.md`.

---

## Omonimi «Harness»

| Nome | Cosa è | Relazione AF |
|------|--------|--------------|
| **a-harness** | Meta-Harness processo (TDD/DDD/Steward) | Questo sistema |
| Harness.io | CD SaaS | Solo analogie policy |
| harness.lol | CLI multi-agent | Solo permission/resume |
| DeepSeek Harness (dsh) | Runtime Cordis | Solo plugin/preset; no `npx dsh` |
| Cursor Cloud harness | VM + video | Five-layer + PR-as-proof; no VM product |

---

## Framework vs Harness vs Meta-Harness

| | Framework | Harness runtime | **a-harness** |
|--|-----------|-----------------|---------------|
| Fai | Scrivi il loop | Configuri e lanci | Competenze/slash su IDE già harness |
| Esempio | LangGraph | Cursor, Claude Code, DSH | Skill-layer AF |

`/cycle` = loop lieve (verify/retry/stop), non autonomia lunga.

---

## Pipeline

```
a-po → a-gherkin (.feature) → a-harness (TDD) → umano (intent post-gate)
```

Handoff: [`handoff-from-gherkin.md`](../a-harness/references/handoff-from-gherkin.md)  
Architettura: [`harness-architecture.md`](../a-harness/references/harness-architecture.md) · Plan/Act: [`permission-modes.md`](../a-harness/references/permission-modes.md)

| Persona | Competenza | Ruolo |
|---------|------------|-------|
| Navigator | `tdd-red`, `tdd-refactor` | Test, architettura |
| Driver | `tdd-green`, `when-stuck` | Codice minimo |
| Steward | `steward` | Makefile, CI, hooks |

---

## Maturity

| Livello | Stato |
|---------|-------|
| L2 Skilled | Skills/competencies |
| **L3 Enforced** | **Target:** Make + hooks + permission modes |
| L4 Measured | Scorecard steward; checkpoint irreversibili |

---

## Artefatti progetto

| File | Template |
|------|----------|
| `Makefile` | [`makefile-template.mk`](../a-harness/references/makefile-template.mk) |
| Progress / learnings / freeze | templates in `a-harness/references/` |
| L2 skill | [`extension-template.md`](../a-harness/extension-template.md) |

Bootstrap: [`harness-scaffold.md`](../a-harness/references/harness-scaffold.md)  
Steward periodico: [`steward-audit-checklist.md`](../a-harness/references/steward-audit-checklist.md)

```bash
bash a-harness/deploy.sh   # oppure deploy-all.sh
```

Pack Claude stand-alone (solo a-harness):

```bash
bash scripts/export-a-harness-claude.sh
# → dist/a-harness-claude-latest.zip
```
