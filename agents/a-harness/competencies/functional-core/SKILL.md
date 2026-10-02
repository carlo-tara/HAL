---
name: functional-core
kind: competency
version: 1.0.1
description: >-
  FCIS: logica di dominio pura e testabile; I/O ai bordi (ACL/adapter).
  Skill = procedura; verità = test/make, non il modello.
  Accept multi-rung: range verbale ⊆ grafo require loadable.
---

# Competenza L1 — functional-core

## Regole

1. **Core** — regole di dominio senza HTTP/DB/UI diretti
2. **Shell** — adapter (ACL), Makefile, CLI, MCP
3. Test RED mirano comportamento core; GREEN non sparge I/O nel dominio
4. Se «verità» dipende dal modello → sbagliato: sposta in test/`make`

## Ladder FCIS / accept range

Su strangler o hub che `require` moduli FCIS estratti a rung:

- Commit / «accept C*n*–C*m*»: lo stage deve includere la **catena loadable** (tutto ciò che l’entry hub già `require`), non solo l’ultimo file
- Il range verbale ⊆ grafo: se il hub è già wired a rung **oltre** *m* su disco, includerli e **segnalare** l’espansione — altrimenti HEAD si spezza
- Path/nome hub e track UI da escludere = **L2**

## Con DDD

- `anti-corruption-layer` ai confini
- `aggregate-root` per mutazioni
- Glossario per nomi core

## Anti-pattern

- Business rules solo in controller/handler
- Skill che «simula» calcoli senza test deterministici
- Commit del solo ultimo FCIS mentre il hub `require` peer ancora untracked
