---
model: orcarouter/deepseek/deepseek-v4-flash
model-fallback: cursor-default
---

# Graph (L0)

## Objective

Generare Loop o Work Graph in `.cursor/product/work-graph.md` (Plan-only di default). Con **`-y`**: auto-accept + multi-cycle sequenziale fino a fine backlog (ogni nodo = `/slice` o `/cycle`).

## Process

1. **Lean brief** — `bash scripts/harness-prompt-builder.sh render --max-tokens 200 -- …` (no dump ToDo/chat).
2. Carica **a-harness** e la competenza **`graph`** (`a-harness/competencies/graph/SKILL.md`).
3. Esegui la pipeline documentata lì (default Plan-only; `-y` = multi-cycle **deterministico**).
4. **Handoff** — scrivi `.cursor/product/handoff-graph.json` (`handoff-write graph`); multi-cycle legge solo handoff + nodo `next`.
5. Non ridocumentare qui Loop vs Graph Trap — restano nella competenza.

## Usage

```
/graph
/graph ToDo.md
/graph -y
/graph -y ToDo.md
```

## Notes

- Canone operativo: competenza `graph` sotto **a-harness**.
- Tool: `scripts/harness-prompt-builder.sh` (token budget 200, handoff-graph.json).
- Modello preferito: `orcarouter/deepseek/deepseek-v4-flash`; fallback Cursor default.
- Baseline: `a-agentzero/commands/graph.md` → `~/.cursor/commands/` via `/sync !`.
