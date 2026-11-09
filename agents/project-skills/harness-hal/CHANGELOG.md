# Changelog — harness-hal

Formato Keep a Changelog + Semantic Versioning. Tag figli: `[sync:safe]`, `[sync:review]`, `[sync:breaking]`.

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
