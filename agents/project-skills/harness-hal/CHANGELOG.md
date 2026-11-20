# Changelog — harness-hal

Formato Keep a Changelog + Semantic Versioning. Tag figli: `[sync:safe]`, `[sync:review]`, `[sync:breaking]`.

## [1.0.8] - 2026-11-20

### Changed

- Sync selettivo [sync:safe]: re-pin `extends-version` a-harness 1.11.1→1.11.4 (catena L2←L1 allineata al re-pin dei padri L1), bump patch.

## [1.0.7] - 2026-11-18

### Added

- Regola L2 7 «Rebuild Laya/orchestrator»: runtime in container built dai repo fratelli (`laya-gpu` da `/var/www/hal_system1`, orchestratore da `/var/www/hal_system2`); le modifiche a `hal_gateway` non raggiungono il servizio vivo senza `docker compose up -d --build` nel repo di build e verifica `/health`. Da `/learn !` sessione 2026-11-18.

## [1.0.6] - 2026-11-18

### Changed

- Sync selettivo [sync:safe] da a-harness 1.11.1 (`/sync !`): `extends-version` allineata 1.10.3→1.11.1; voci pending 1.10.4 (sync L0 tooling), 1.10.5 (policy «Costo del gate» + corollario «stdout=file»: eredità dal body L1, target N/A del L2 già allineati alla §Verità del gate), 1.11.0 (policy «Chiusura outcome-driven»: eredità pulita) e 1.11.1 (allineamento L0 tooling) — nessun cambio al body L2. Bump patch via `agent-version.sh`; entry integrata a mano con dichiarazione (lo script non scrive il CHANGELOG).

## [1.0.5] - 2026-11-09

### Added

- Tabella path artefatti, contesto Benchmark: aggiunti `scripts/gold_set_scoring.py` e `benchmark/config/gold_set.schema.json` (infra gold set HT-008: validazione item per famiglia, hit-rate + accuracy per fascia con soglie da `laya_gate`, CLI); nota «scoring gold set (HT-008)». Realineato al genitore committed: `extends-version` 1.10.2 → 1.10.3 (`a-harness` su origin; il 1.10.4 in working tree è di sessione parallela in corso, non referenziato) [sync:safe]

## [1.0.4] - 2026-11-09 (voce aggiunta postuma al bump del 2026-11-08)

### Changed

- Allineato a a-harness 1.10.2 (`extends-version` 1.10.1 → 1.10.2) nella passata di realineo catena del bundle; body L2 non impattato. Voce inserita il 2026-11-09: il bump era arrivato senza changelog (stesso pattern del mirror graph, corretto ora) [sync:safe]

## [1.0.3] - 2026-10-31

### Changed

- Allineato a a-harness 1.10.1 (`extends-version` 1.9.2 → 1.10.1; voci intermedie 1.10.0 (regole `/sync <` brainbeez) e 1.10.1 (policy «Copertura gate»), tutte `[sync:safe]`; body L2 non impattato, nessun delta da adattare) [sync:safe]

## [1.0.2] - 2026-10-25

### Added

- Bootstrap L2 HAL Gateway (profile standard): Platform API root mirror, path artefatti, N/A documentati, freeze config, mirror bundle `agents/`. _(voce retroattiva: CHANGELOG creato il 2026-10-31)_
