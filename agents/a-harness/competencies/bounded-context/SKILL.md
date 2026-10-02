---
name: bounded-context
kind: competency
version: 1.1.0
description: >-
  Contesti delimitati DDD: lavoro in bolla isolata; Fit-to-whole sul semantic
  layer (mappa BC viva). Comunicazione esterna solo via eventi o porte.
---

# Competenza L1 — bounded-context

Isolamento architetturale: un task = un bounded context.
**Fit-to-whole:** ogni slice arricchisce il backbone (`docs/bounded-contexts.md` + glossario), non crea un silo semantico one-off.

## Regola tassativa

1. Lavori **solo** dentro la bolla assegnata (es. `src/modules/billing/`)
2. **Vietato** import diretto da altri moduli/contesti
3. Comunicazione esterna **solo** via:
   - Domain Events (pub/sub documentato)
   - Interfacce pubbliche esplicite (port/adapter)
4. **No** grep o lettura directory fuori contesto assegnato
5. Mappa contesti: `docs/bounded-contexts.md` — artefatto vivo; ownership esplicita per contesto

Template: [references/bounded-context-map-template.md](../../references/bounded-context-map-template.md)

## Fit-to-whole (anti-silo)

- Nuovo lavoro → riusa termini/contesti esistenti dove possibile; estendi la mappa, non un modello parallelo
- Se emerge un BC nuovo: dichiaralo in `/slice` e aggiorna la mappa prima/durante lo slice (non “dopo, forse”)
- Isolamento ≠ frammentazione semantica: confini chiari, linguaggio condiviso sul backbone

## Condizione di uscita

- Linter/architecture test (se presente) conferma assenza import cross-context
- Oppure review manuale Steward: nessun `from '../../other-module'`
- Mappa BC e glossario coerenti col lavoro fatto (nessun silo orfano)

## `/slice`

Deve dichiarare:

- Nome bounded context
- Path root modulo
- Eventi/interfacce pubbliche coinvolte
- Se arricchisce mappa/glossario (Fit-to-whole) o solo codice dentro BC già noto

## Anti-pattern

- "Importo solo questo tipo" da modulo alieno
- Condividere entity tra contesti senza ACL/evento
- Search globale per "capire come fanno gli altri"
- Modello di dominio throwaway non collegato a glossario/mappa BC
