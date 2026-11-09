# Changelog — graph (L0)

## [1.0.4] - 2026-11-09

### Changed

- Nota Tool builder/handoff: da workspace consumer il path canonico è `agents/scripts/harness-prompt-builder.sh` (symlink HAL), non `scripts/` del consumer — la nota rv9 era un path-miss. Bump originato dal canonico `commands/graph.md` (commit 2f37faf, `a-agentzero` 1.13.2); changelog del mirror aggiunto ora (mancava al rigenerato) + pin `tests/test_graph_rerun_rules.py` aggiornato. [sync:safe]

## [1.0.3] - 2026-10-30

### Changed

- Appreso da sessione 2026-10-30 (`/graph -y` re-run #6): verifica pipe su tutte le righe della tabella a ogni re-run (la corruzione può venire da run precedenti — caso righe N11/N14 con pipe grezzi dal 2026-10-25/26); mai a capo dentro la riga durante la riparazione [sync:safe]

## [1.0.2] - 2026-10-27

### Changed

- Appreso da sessione 2026-10-27 (`/graph -y` re-run #4): re-run su work-graph.md = editing chirurgico con ancore a riga singola e verifica celle post-scrittura (pipe per riga costanti); `handoff-write graph` esige `--dir product/state` (default tool `product/` → shadow copy), campi `--field` JSON-first con fallback stringa [sync:safe]

## [1.0.1] - 2026-10-25

### Changed

- Appreso da sessione 2026-10-25: celle di `work-graph.md` mai con pipe grezzi (alternazioni regex) — sfuggire o riformulare [sync:safe]
