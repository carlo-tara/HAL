# Lead research output + Apollo 3-step

Contratto per discovery/qualifica **batch** (liste account) e formalizzazione Apollo. Complementa la cascade HubSpot→Apollo→LeadMagic→SQLite in `a-enrichment`.

## Apollo 3-step (esplicito)

Usare in domain-first e quando Apollo non è solo "match su miss HubSpot":

1. **Organization search** — filtri size, industry/keywords, location (da ICP L2).
2. **People search** — titles / seniority da ICP; domain o org id; preferire email status verified se disponibile.
3. **People enrichment** — email / LinkedIn / name+company; poi LeadMagic su miss se in scope.

Allineare filtri a L2; non inventare titoli o industrie fuori guardrail.

## Output contract — batch lead research

### Summary

- Total leads found
- High priority (fit 8–10) / Medium (5–7) / Low (1–4)
- Average fit score

### Per lead

| Campo | Obbligatorio |
|-------|----------------|
| Company name + website | sì |
| Priority / fit score (1–10) + reason | sì |
| Industry + size | sì se noti |
| Why they're a good fit (2–3 ragioni evidenza-based) | sì |
| Target decision-maker (role/title) | sì |
| LinkedIn (company o person) | se disponibile |
| Value proposition for them | sì (ipotesi esplicita se non validata) |
| Outreach **strategy** / angle | sì |
| Conversation starters | consigliati |

Marcare ogni claim come `evidence` o `hypothesis`.

### Strategy ≠ draft

- `a-enrichment` produce **strategy / angle / starters**.
- Draft cold email o call script → delega `a-copywriter` (template L2) o skill L2 sales — non fase obbligatoria enrichment.

## CSV vs master SQLite

| Artefatto | Ruolo |
|-----------|--------|
| **SQLite master** | Sorgente di verità enrichment per product line |
| **CSV / report** | Handoff operativo (CRM import, share, triage) |

Non trattare il CSV come secondo master. Se si fa merge nel master, documentarlo nelle next actions.

## Credits / prerequisites

A fine run, riportare lookup per provider (HubSpot / Apollo / LeadMagic / altri L2).

Se manca una API key: skip della fase senza fallire l'intero workflow (affine a `SKIP_*`); dichiararlo nel report.
