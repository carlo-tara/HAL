# Pin — github/spec-kit (Spec-Driven Development)

**URL:** https://github.com/github/spec-kit  
**Docs:** https://github.github.io/spec-kit/ · [spec-driven.md](https://github.com/github/spec-kit/blob/main/spec-driven.md)  
**Licenza:** MIT · **Ruolo AF:** metodologia SDD mappata su slash a-harness; **non** dipendenza runtime

> Spec Kit (1.0+) rende le **specifiche eseguibili**: constitution → specify → plan → tasks → implement → converge. a-harness adotta i *principi* utili all’implementazione test-first; lascia discovery a `a-po` / `a-gherkin` e i gate a Make.

## Mappa fasi Spec Kit → a-harness

| Spec Kit | a-harness | Note |
|----------|-----------|------|
| `/speckit.constitution` | L2 `harness-*` + `docs/glossary.md` + invariants / `.cursorrules` | Principi di progetto già nel consumer; non duplicare come fase slash |
| `/speckit.specify` | Prerequisito contratto (`.feature` / US/AC) via `a-po` / `a-gherkin` | **Non inventare** behavior in harness |
| `/speckit.clarify` | `/slice` Plan: domande prima di Act | Ambiguità → stop o delega, non “guess & code” |
| `/speckit.plan` | `/slice` Plan (how tecnico, file, BC) | Stack/arch già vincolati da L2 + Makefile |
| `/speckit.tasks` | Breakdown in medium slice ≤4 file | Un task Spec Kit ≠ un `/cycle`; spezza |
| `/speckit.analyze` | Check cross-artefatto in Plan (prima di `/red`) | Contratto ↔ glossario ↔ BC ↔ file slice; gap → delega |
| `/speckit.implement` | `/cycle` → `/red` → `/green` → `/refactor` | Implementazione = TDD + Make, non codegen one-shot |
| `/speckit.converge` | `/ready` + nuovo `/slice` se residuo | Gate verde ≠ “Converged” di intent; residui → slice esplicito, non silent expand |
| Bug: assess → fix → test | RED (repro) → GREEN → REFACTOR + evidence | Estensione Spec Kit `bug`; AF resta evidence-first |
| Assess idea (intake…decide) | `a-po` (fuori harness) | Non-goal a-harness |

## Adottato (idee operative)

| Idea Spec Kit | Dove in a-harness |
|---------------|-------------------|
| Intent / *what* prima del *how* | Prerequisito contratto; Plan→Act |
| Multi-step refinement (no one-shot) | `/slice` → R/G/Rf → `/ready` |
| Constitution / guardrail organizzativi | L2 + glossary + BC + freeze |
| Cross-artifact consistency prima di implement | Plan check (`analyze` mapping) |
| Converge = confronta artefatti vs codice e chiudi residui | `/ready` + slice residuo |
| Spec come lingua franca (intent umano post-gate) | `sustainable-pace` — umano giudica **intent** |

## Non adottato

- CLI `specify` / `uv tool install specify-cli` come prerequisito AF
- Slash `/speckit.*` o skill `speckit-*` come canone (restano mapping, non alias obbligatori)
- Tree obbligatorio `specs/[N]-feature/` + auto-branch da CLI
- Extensions / presets / bundles Spec Kit (AF ha L0→L1→L2 + competenze)
- Regenerating-all-code-from-spec come unico flusso (brownfield = TDD su codice esistente + Make)
- Parallel creative implementations come default (quando-stuck / un `/cycle` alla volta)

## Uso in chat

Se l’utente cita Spec Kit o SDD: applica la **mappa** sopra; non installare Spec Kit nel repo consumer a meno di richiesta esplicita Steward/bootstrap.
