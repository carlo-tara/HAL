---
name: graph
version: 1.0.3
description: Command graph for HAL workspace.
---

# Graph (L0)

## Objective

Generare Loop o Work Graph in `product/state/work-graph.md` (Plan-only di default). Con **`-y`**: auto-accept + multi-cycle sequenziale fino a fine backlog (ogni nodo = `/slice` o `/cycle`).

## Process

1. **Lean brief** — `bash scripts/harness-prompt-builder.sh render --max-tokens 200 -- …` (no dump ToDo/chat).
2. Carica **a-harness** e la competenza **`graph`** (`a-harness/competencies/graph/SKILL.md`).
3. Esegui la pipeline documentata lì (default Plan-only; `-y` = multi-cycle **deterministico**).
4. **Handoff** — scrivi `product/state/handoff-graph.json` (`handoff-write graph`); multi-cycle legge solo handoff + nodo `next`.
5. Non ridocumentare qui Loop vs Graph Trap — restano nella competenza.

## Usage

```
/graph
/graph ToDo.md
/graph -y
/graph -y ToDo.md
```

## Notes

- **Celle tabella `work-graph.md`**: mai pipe grezzi dentro una cella (alternazioni regex, opzioni tipo `a` o `b` separate da barra verticale): sfuggirli o riformulare con `/` — un pipe spezza la cella e corrompe la riga (caso 2026-10-25, riga N7).
- **Re-run `graph -y` su `work-graph.md` existente**: editing chirurgico con ancore a riga singola e verifica delle celle dopo la scrittura (pipe per riga costanti), non riscrittura integrale. Verificare il conteggio pipe su **tutte le righe della tabella**, non solo quelle scritte nel re-run: la corruzione può venire da run precedenti (caso 2026-10-30: righe N11/N14 con pipe grezzi dal 2026-10-25/26); nella riparazione, mai a capo dentro la riga.
- **Handoff**: `handoff-write graph` risolve il default `product/state/` dalla root dello script; nei workspace consumer passare sempre `--out product/state/handoff-graph.json` (vedi `learn/references/tool-pitfalls.md` § Writer canonico); campi `--field` JSON-first con fallback stringa.
- Canone operativo: competenza `graph` sotto **a-harness**.
- Tool: `scripts/harness-prompt-builder.sh` (token budget 200, handoff-graph.json).
- Baseline: `a-agentzero/commands/graph.md`.
