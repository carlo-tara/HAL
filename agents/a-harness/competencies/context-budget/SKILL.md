---
name: context-budget
kind: competency
version: 1.2.0
description: >-
  Carico cognitivo = context window: max 4 file attivi, no directory intere,
  offload output grandi su FS, progressive disclosure competenze; brief slash
  ≤200 token via prompt-builder + handoff-*.json.
---

# Competenza L1 — context-budget

L'equazione **carico cognitivo team = context window agente**. Contesto troppo ampio → allucinazioni e context rot.

## Regole (sempre attive)

1. **Max 4 file** in contesto attivo simultaneo per un task
2. **Vietato** caricare intere directory o grep globale fuori necessità
3. **Cambio dominio/bounded context** → chiudi contesto precedente; riapri solo file essenziali
4. **Allineamento** a `bounded-context`: letture limitate al modulo assegnato
5. **`/slice`** deve elencare esplicitamente i file nel budget prima di RED/GREEN
6. **Offload** output tool/log grandi su file (progress / artifact); non gonfiare la chat
7. **Progressive disclosure** — carica competenze on-demand per fase, non tutto L1 in un colpo
8. Onboarding `/slice`: glossary + makefile + modulo — non embedding product esterno
9. **Brief slash ≤200 token** — per `/graph` `/slice` `/cycle` `/todo` usa `scripts/harness-prompt-builder.sh` (`render --max-tokens 200`); niente wall-of-text
10. **Handoff JSON** — stato tra passi in `.cursor/product/handoff-{graph,slice,cycle,todo}.json` (non transcript); leggi/scrivi via `handoff-read` / `handoff-write`

## Escalation

Se servono più di 4 file:

- Spezza lo slice in sotto-slice
- Oppure documenta waiver temporaneo in chat (1 frase: perché serve il 5° file)

## Anti-pattern

- `@Codebase` o search repo-wide per task localizzato
- Tenere aperti file di moduli non correlati "per comodità"
- Handoff impliciti tra contesti senza `/slice` esplicito
- Passare ToDo/work-graph/progress interi come prompt a sotto-agenti
