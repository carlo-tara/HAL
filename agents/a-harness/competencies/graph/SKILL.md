---
name: graph
kind: competency
version: 1.3.1
model: orcarouter/deepseek/deepseek-v4-flash
description: >-
  Genera Loop o Work Graph (Markdown + Mermaid) da contesto, file (es. /graph
  ToDo.md) o richiesta esplicita. Flag -y = auto-accept + multi-cycle sequenziale
  fino a fine backlog (ogni nodo = /slice|/cycle). Default Plan-only: scrive
  .cursor/product/work-graph.md; preferisci Loop (anti graph-trap). Lean brief
  ≤200 token + handoff-graph.json via prompt-builder. Use when user invokes
  /graph or needs loop/graph engineering from a series of requests.
---

# Competenza L1 — graph (Loop / Work Graph)

Progetta **come** correre una serie di Richieste nel harness — non esegue Act **salvo** `-y`.
Pin fonti: `references/graph-loop-source.md`.

## Lean / deterministic (obbligatorio)

1. **Brief ≤200 token** — costruisci un brief lean via `scripts/harness-prompt-builder.sh`. **Non dumpare mai** intere chat o file `ToDo.md` / `work-graph.md` nel prompt.
2. **Multi-cycle (`-y`)** — ogni nodo: leggi **solo** `handoff-graph.json` + la riga del nodo su cui si sta lavorando.

## Output (Contratto)
- **Zero verbosità narrativa.**
- Restituisci il Loop Spec, o il Mermaid diagram + Tabella Nodi.
- Assicurati di chiamare `handoff-write graph` e nient'altro per gli update di stato.

Per dettagli su Loop vs Graph, gestione `multi-cycle` sequenziale, risoluzione input e template dell'artefatto:
Leggi `references/graph-extended.md`.
