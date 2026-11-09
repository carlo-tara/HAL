# Mappa residui — HAL

Backlog rinfrescabile (≠ Progress append-only). Igiene: `/todo`.

## P0

_(nessuna)_

## P1

_(nessuna)_

## P2

- [ ] Chiudere il loop della telemetria: `token_budget.py report` come gate pass/fail (exit code) sui vincoli delle skill, non solo contabilità. `#infra` · P2
  - Perché utile: le skill dichiarano vincoli (es. `impersonate`: «≤ 500 token output», checklist a 5 voci) che il report registra senza bocciarli: nessun test dice «finito» (finding `/impersonate kentbeck` 2026-11-08).
  - Acceptance: exit code diverso da zero quando un target è violato (output > 500, violazioni > 0, rapporto S1:S2 sotto target dove dichiarato); test sul comportamento degli exit code in `agents/a-agentzero/scripts/`; almeno una skill a budget che lo richiama come gate.
- [ ] Test di parità tool↔fallback per gli oracoli: scheda via MCP `impersonate` == lettura diretta di `app/oracles.py`. `#product` · P2
  - Perché utile: lo step 7 di `/impersonate` dichiara «stesse schede, stesse chiavi», ma la parità dei due percorsi d'accesso è documentata e non asserita da test; un drift tool/file resta invisibile finché non si rompe (finding `/impersonate kentbeck` 2026-11-08).
  - Acceptance: test in `/var/www/hal_mcp_tools` che serializza ogni oracolo via tool e via fallback e asserisce uguaglianza (o JSON canonico), sull'esempio dei test sul cap `_CARD_FIELDS` (≤ 4000 char).

## Già fatto

_(vuoto — flushato in `./CHANGELOG.md` Unreleased)_
