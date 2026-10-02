---
name: slice
version: 1.0.0
description: Command slice for HAL workspace.
---

# Slice (L0)

## Objective

Aprire uno **slice** Plan: acceptance falsificabile, perimetro ≤4 file (o waiver), effort, append in `.cursor/product/agent-progress.md`. Non avviare `/red` finché lo slice non è accettato.

## Process

1. **Lean brief** — `bash scripts/harness-prompt-builder.sh render --max-tokens 200 --set acceptance='…' --set files='…' -- " /slice acceptance={acceptance} files={files}."`
2. Carica **a-harness** (`a-harness/SKILL.md`) — tabella slash `/slice` e regole Plan (evidence-first, semantic layer, Spec Kit clarify/analyze). Progressive disclosure: non caricare tutte le competenze in un colpo.
3. Competenze on-demand: `session-progress`, `context-budget`, `sustainable-pace`, `ubiquitous-language`, `bounded-context` se servono.
4. Emetti acceptance + perimetro; **handoff** `.cursor/product/handoff-slice.json` (`handoff-write slice --field acceptance=… --field files=… --field brief=…`).
5. Attendi accept umano prima di Act (salvo istruzione esplicita già data).

## Usage

```
/slice
/slice <titolo o acceptance breve>
```

## Notes

- Canone operativo: **a-harness** (non ridocumentare qui il ciclo RGR).
- Tool: `scripts/harness-prompt-builder.sh` + `handoff-slice.json`.
- Modello preferito: `orcarouter/deepseek/deepseek-v4-flash`; fallback Cursor default.
- Baseline: `a-agentzero/commands/slice.md` → `~/.cursor/commands/` via `/sync !`.
