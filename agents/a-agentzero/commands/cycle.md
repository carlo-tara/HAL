---
model: orcarouter/deepseek/deepseek-v4-flash
model-fallback: cursor-default
---

# Cycle (L0)

## Objective

Eseguire lo **skeleton** `/cycle`: slice → red → green → refactor → ready → flush progress, sotto gate Make e permission-modes. Non inventare un secondo loop.

## Process

1. **Handoff-in** — se esiste `.cursor/product/handoff-slice.json`, leggilo (`handoff-read slice`); non ri-chiedere acceptance/files già lockati.
2. **Lean brief** — `bash scripts/harness-prompt-builder.sh render --max-tokens 200 -- …` dallo handoff (acceptance + files only).
3. Carica **a-harness** (`a-harness/SKILL.md`) § `/cycle` (Template Method / Hollywood) — skeleton **deterministico**, non ri-pianificare le fasi.
4. Se Plan aperto senza accept: ripeti scelte; **non** avviare `/red`.
5. Competenze fase on-demand: `tdd-red` / `tdd-green` / `tdd-refactor` / `session-progress` / `sustainable-pace` (una fase alla volta).
6. Aggiorna `handoff-cycle.json` (o riusa slice) con fase corrente; `ready=0` solo con `MAKE_EXIT` osservato nel run corrente.

## Usage

```
/cycle
/cycle <contesto slice già accettato>
```

## Notes

- Canone operativo: **a-harness**.
- Tool: `scripts/harness-prompt-builder.sh` + `handoff-slice.json` / `handoff-cycle.json`.
- Modello preferito: `orcarouter/deepseek/deepseek-v4-flash`; fallback Cursor default.
- Baseline: `a-agentzero/commands/cycle.md` → `~/.cursor/commands/` via `/sync !`.
