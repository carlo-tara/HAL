# Cycle (L0)

## Objective

Eseguire lo **skeleton** `/cycle`: slice → red → green → refactor → ready → flush progress, sotto gate Make e permission-modes. Non inventare un secondo loop.

## Process

1. **Handoff-in** — se esiste `product/state/handoff-slice.json`, leggilo (`handoff-read slice`); non ri-chiedere acceptance/files già lockati.
2. **Lean brief** — `bash scripts/harness-prompt-builder.sh render --max-tokens 200 -- …` dallo handoff (acceptance + files only).
3. Carica **a-harness** (solo la sezione § `/cycle` da `a-harness/SKILL.md`) (Template Method / Hollywood) — skeleton **deterministico**, non ri-pianificare le fasi. **Caricamento dinamico:** non caricare mai l'intero L1 `a-harness`.
4. Se Plan aperto senza accept: ripeti scelte; **non** avviare `/red`.
5. Competenze fase on-demand: carica **singolarmente** la competenza di fase attiva (`tdd-red`, `tdd-green`, `tdd-refactor`, `session-progress`, `sustainable-pace`) una fase alla volta. Rimuovi la precedente dal contesto prima di procedere.
6. **Troncamento log test:** Durante i cicli RED e GREEN, quando esegui `make test` o run di test tramite il tool `terminal`, imposta sempre `head_lines: 5` e `tail_lines: 15` per evitare context dumping, focalizzandoti solo sul riepilogo degli errori (exit code e traceback finale).
7. Aggiorna `handoff-cycle.json` (o riusa slice) con fase corrente; `ready=0` solo con `MAKE_EXIT` osservato nel run corrente.

## Usage

```
/cycle
/cycle <contesto slice già accettato>
```

## Notes

- Canone operativo: **a-harness**.
- Tool: `scripts/harness-prompt-builder.sh` + `handoff-slice.json` / `handoff-cycle.json`.
- Modello preferito: `orcarouter/deepseek/deepseek-v4-flash`; fallback default editor.
- Baseline: `a-agentzero/commands/cycle.md`.
