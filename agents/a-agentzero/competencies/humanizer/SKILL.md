---
name: humanizer
kind: competency
version: 1.1.0
description: >-
  Umanizzare i testi così che non sembrino generati da AI: anti-pattern, loop
  avversariale, ritmo/burstiness. Principi cross-dominio (L0).
---

# Competenza L0 — humanizer

Principi generici. Corpus anti-AI, loop e editing avanzato: livello L1 del dominio (es. a-copywriter).

---

## Principi

1. **Draft → audit → rewrite** — ogni output passa da elenco pattern sospetti a riscrittura
2. **Cluster, non pedanteria** — un singolo tropo non basta; conta la densità di pattern da brochure/LLM
3. **Burstiness** — varia lunghezza e struttura delle frasi; evita simmetria da lista
4. **Loop interno** — confronta draft e rewrite; mostra il loop all'utente solo se richiesto
5. **Stesso significato** — umanizzare non cambia i fatti; lunghezza tipicamente ±10%
6. **Never inject** — umanizzare = togliere e affilare, non aggiungere voce, fatti, stakes o candore assenti nel source

---

## Cosa non fa questo L0

- Non elenca pattern IT completi (stanno in L1 `references/`)
- Non sostituisce tono di voce o purismo lessicale (competenze separate)
