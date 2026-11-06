---
name: impersonate
version: 1.0.1
description: >-
  Reason why: senza lenti esperte dichiarate, la revisione di codice/design/spec
  dipende dall'opinione del momento e l'artefatto viene letto una volta sola.
  /impersonate rilegge l'artefatto dalla prospettiva di un oracolo di ingegneria
  di prodotto (28 registry deterministico in hal_mcp_tools): scheda con `?` per
  la selezione di sessione, lente + domande canoniche per il giudizio.
---

# /impersonate — Oracoli di ingegneria di prodotto (L2)

## Obiettivo

Leggere codice, design e specifiche dal punto di vista di una personalità famosa
dell'ingegneria di prodotto (l'«oracolo»). Il server MCP `hal_mcp_tools` serve la
lente come **dato deterministico** (`impersonate` → registry `app/oracles.py`,
zero LLM nel perimetro): l'agente host interpreta l'artefatto con quella lente e
produce finding, non biografia.

## Oracoli nel registry (28)

- **codice**: `kentbeck` (Beck), `unclebob` (R. C. Martin), `martinfowler`,
  `kleppmann`, `karpathy`
- **prodotto**: `seiden`, `gothelf`, `donaldnorman`, `nireyal`, `martycagan`,
  `teresatorres`, `melissaperri` (anche `melissaperry`), `osterwalder`,
  `kahneman`, `ericries`, `ulwick` (anche `ulwik`), `kalbach`, `wesbush`,
  `seanellis`, `donnaweber`, `carlgold`, `ronkohavi`, `stephenwendel`, `toddolson`
- **strategia**: `rogermartin`, `danpink`, `chankim`, `rumelt`

## Process

1. **Parsing argomento**:
   - `/impersonate ?` → selezione oracoli per la sessione corrente.
   - `/impersonate <oracolo> [target]` → lente applicata al target (file, diff,
     spec, sezione di design).
2. **Lazy-load del target** (come `/review`): mai file interi > 100 righe;
   sezioni con `start_line`/`end_line`; diff letto solo se ≤ 150 righe, altrimenti
   per path. Traccia: `python3 agents/a-agentzero/scripts/token_budget.py log lazy_load <path> <righe> <totale>`.
3. **Scheda**: invoca il tool MCP `impersonate` (in Zed: `hal_mcp_tools_impersonate`)
   con `oracle="<id o nome>"`; usa `lens`, `questions`, `praise`, `reject` come
   griglia di lettura. Nome ignoto → il tool suggerisce i candidati più prossimi:
   proponilo, non indovinare di testa tua.
4. **Selezione (`/impersonate ?`)**: invoca il tool con `oracle="?"` e
   `context="<una riga che riassume il task di questa sessione>"`; da `matched[]`
   (ranking deterministico token∩tag) e dall'indice scegli **2–4 oracoli** e, per
   ciascuno, una riga «perché qui, in questa sessione». Il giudizio di scelta è
   dell'agente (System 2): il tool dà solo menu e ordinamento.
5. **Interpretazione in voce**: produci finding inquadrati nelle domande canoniche
   dell'oracolo. Le massime vanno citate come parafrasi; **mai inventare citazioni**;
   niente anacronismi o barzellette sulla persona. Se l'artefatto tocca un dominio
   fuori dalla lente dell'oracolo, dichiaralo («fuori dal mio campo») e passa.
6. **Più oracoli**: sezioni separate, una per oracolo, stessa griglia (finding →
   domanda canonica → azione); non mescolare le voci.
7. Se l'MCP `hal_mcp_tools` non è raggiungibile: leggi `app/oracles.py` in
   `/var/www/hal_mcp_tools` (stesse schede, stesse chiavi) — fallback a parità di
   dati, non di ranking.

## Checklist

- [ ] Scheda letta DAL TOOL (o fallback file), non dalla memoria del modello
- [ ] Finding nelle domande canoniche, non critica generica
- [ ] Nessuna citazione inventata, nessuna biografia al posto del giudizio
- [ ] `?`: selezione con motivo per oracolo
- [ ] Lazy-load rispettato, contesto magro (≤ 500 token output)

## Expected output

- **Nessun preambolo narrativo.**
- `/impersonate <oracolo> <target>`: tabella compatta
  `| Finding | Domanda canonica | Azione proposta |` + verdetto finale in una
  riga (praise/reject). Se target omesso: verdetto sul contesto discusso.
- `/impersonate ?`: `id — perché serve a questa sessione (una riga)` per 2–4
  oracoli scelti, attingendo a `matched[]` + indice.

## Telemetria

```bash
python3 agents/a-agentzero/scripts/token_budget.py init
python3 agents/a-agentzero/scripts/token_budget.py log lazy_load <path> <lines_read> <total_lines>
python3 agents/a-agentzero/scripts/token_budget.py log s2_call   # interpretazione in voce
python3 agents/a-agentzero/scripts/token_budget.py log output 350
python3 agents/a-agentzero/scripts/token_budget.py report        # events/token-budget.jsonl
```

## Usage

```
/impersonate ?
/impersonate kentbeck src/order_service.py
/impersonate unclebob "modulo ordini: dipende da billing e dai report"
/impersonate martycagan docs/PRD.md
/impersonate kleppmann schema.sql
/impersonate rumelt product/roadmap-q1.md
```

## Notes

- Registry: `app/oracles.py` del progetto `/var/www/hal_mcp_tools` (tier
  deterministico/zero crediti, regola di progetto). Aggiungere un oracolo = nuova
  entry + unit test (cap scheda ≤ 4000 char serializzati; vincolo `_CARD_FIELDS`
  asserito dai test) → poi `/version`.
- Filtro di missione del registry (finding `/impersonate martycagan`): nuovo
  oracolo solo se copre una lente assente nell'indice E l'esperimento sul valore
  (voce `#product` in ToDo) è verde. Niente espansione del registry a valore non
  dimostrato: è la riga che tiene la feature factory fuori dal tier
  deterministico.
- Il tool non contiene LLM: la persona è una lente testuale; a «parlare» è
  l'agente host, che non deve trasformarla in caricatura.
- `/sync <` valuterà la promozione a L0 se il comando è riusato tra progetti.
