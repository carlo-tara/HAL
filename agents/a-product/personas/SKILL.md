---
name: personas
parent: a-product
version: 1.0.20
description: >-
  Reason why: senza profili utente reali e un percorso verificato, si progettano schermate e testi per persone che non esistono. User Researcher integrato in a-product: definisce personas da PRD/mockup con intervista PO, verifica journey coherence vs mockup/PRD, aggiunge personas da NL (/add). Usare per /create, /check, /add, /triage su profilazione utente e journey coherence.
---

# personas — User Profiling & Journey Coherence

Skill di prodotto per personas e **journey coherence** (allineamento flussi a personas attive). Competenza integrata di **a-product**.

---

## Discovery product (portabile)

Ordine: `.cursor/product/` → `.claude/product/` → `product/`

| Artefatto | Ruolo |
|-----------|--------|
| `prd.md` | Input |
| `mockup/` | Input |
| `personas.md` | Output primario |

Se 0 path product: proponi scaffold. Se manca `personas.md` su progetto nuovo → `/create`.

---

## Comandi (slash)

| Invocazione | Obiettivo |
| ----------- | --------- |
| `/triage` | Impatto rapido PRD/UI/code → create/check/update/add/none |
| `/create` | Sessione completa iniziale → `personas.md` |
| `/add` | Personas aggiuntive da comando + descrizione NL |
| `/check` | Compatibilità + coerenza flussi vs personas attive |
| `/update` | Modifica mirata di personas già presenti |
| `/show` | Read-only |
| `/gap` | Lacune; può raccomandare `/add` |
| `/export` | Persiste `personas.md` dopo conferma PO |

---

## Mandato Flow Coherence

Non valutare schermata/feature isolata. Ogni `/check` e triage rilevante risponde anche a:

- Collegamento al journey (`flow_expectations` + `ui_bindings`)?
- Friction vs `digital_skill` / `interaction_style` della **primary** sul percorso default?
- Continuità del modello mentale tra sezioni?

Percorsi advanced per secondary/edge solo se **opt-in**.

---

## Workflow `/create`

```
Task Progress:
- [ ] 1. Discovery product + prd/mockup
- [ ] 2. Evidence pass CON source
- [ ] 3. Bozza candidati (1 primary + fino a 3 secondary/edge) — hypothesis
- [ ] 4. Intervista PO (po-interviewer): 1–2 Q/turno
- [ ] 5. Merge/split; anti-personas
- [ ] 6. Draft: binding UI + flow_expectations
- [ ] 7. Conferma PO
- [ ] 8. /export → handoff jtbd
```

Dettaglio: [references/create-workflow.md](references/create-workflow.md) · formato [references/persona-format.md](references/persona-format.md)
