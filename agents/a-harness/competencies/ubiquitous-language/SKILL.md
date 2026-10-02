---
name: ubiquitous-language
kind: competency
version: 1.1.0
description: >-
  Linguaggio ubiquo DDD: glossario = semantic layer / ontologia operativa
  (termini, relazioni, regole). Nomi codice/test allineati; Steward in refactor/audit.
---

# Competenza L1 — ubiquitous-language

Guardiano del **semantic layer**: un termine del dominio = un solo nome in codice e test.
`docs/glossary.md` è l’**ontologia operativa** viva (non solo lista sinonimi): entità, relazioni e regole di business che l’agente deve rispettare.

## Regola tassativa

Prima di generare nomi (classi, interfacce, variabili, metodi, scenari test):

1. Leggi `docs/glossary.md` (path L2 può override)
2. Usa **esattamente** i termini definiti
3. Se manca un concetto necessario: aggiungi voce (termine + definizione + sinonimi vietati; relazione/regola se governa comportamento) **prima** di inventare un nome
4. Ogni deviazione = bug da correggere in REFACTOR

## Semantic layer (glossario vivo)

- Glossario e ownership sono **lifecycle-managed**: aggiornati con il dominio, non file morti
- Drift terminologico = perdita di precision/trust per agenti e umani
- Non confondere con `context-budget` (window/file): qui è **contesto semantico di dominio**

Template glossario: [references/glossary-template.md](../../references/glossary-template.md)

## Esempi

| Glossario | Vietato |
|-----------|---------|
| Customer | User, Client, AccountHolder |
| Invoice | Bill, Receipt |
| Shipment | Delivery, Package (se non definito) |

## Quando applicare

- `/slice` Plan — allineamento acceptance ↔ glossario
- `/red` — nomi test e fixture
- `/green` — nomi produzione
- `/refactor` — rename sistematico deviazioni
- `/steward` — audit drift terminologico

## Verifica Steward

In audit: grep sinonimi comuni vs glossario; proponi rename batch sotto test verdi.

## Anti-pattern

- "User" generico quando il dominio dice "Customer"
- Abbreviazioni non nel glossario
- Termini inglesi misti a italiani per la stessa entità
- Glossario statico mai aggiornato mentre il codice evolve
