---
model: orcarouter/deepseek/deepseek-v4-flash
---

# Slice (L0)

## Objective

Aprire uno **slice** Plan: acceptance falsificabile, perimetro ≤4 file (o waiver), effort, append in `product/state/agent-progress.md`. Non avviare `/red` finché lo slice non è accettato.

## Process

1. **Lean brief** — `bash scripts/harness-prompt-builder.sh render --max-tokens 200 --set acceptance='…' --set files='…' -- " /slice acceptance={acceptance} files={files}."`
2. Carica **a-harness** (solo la sezione `/slice` da `a-harness/SKILL.md`) e regole Plan. **Caricamento dinamico:** non caricare mai l'intero L1 `a-harness` in memoria.
3. Competenze on-demand: carica **singolarmente** `session-progress`, `context-budget`, `sustainable-pace`, `ubiquitous-language` o `bounded-context` solo se servono per risolvere ambiguità specifiche.
4. Emetti acceptance + perimetro; **handoff** `product/state/handoff-slice.json` (`handoff-write slice --field acceptance=… --field files=… --field brief=…`).
5. Attendi accept umano prima di Act (salvo istruzione esplicita già data).

## Usage

```
/slice
/slice <titolo o acceptance breve>
```

## Notes

- Canone operativo: **a-harness** (non ridocumentare qui il ciclo RGR).
- Tool: `scripts/harness-prompt-builder.sh` + `handoff-slice.json`.
- Modello preferito: `orcarouter/deepseek/deepseek-v4-flash`; fallback default editor.
- Baseline: `a-agentzero/commands/slice.md`.
