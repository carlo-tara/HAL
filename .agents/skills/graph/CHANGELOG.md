# Changelog — graph (L0)

## [1.0.3] - 2026-10-30

### Changed

- Appreso da sessione 2026-10-30 (`/graph -y` re-run #6): verifica pipe su tutte le righe della tabella a ogni re-run (la corruzione può venire da run precedenti — caso righe N11/N14 con pipe grezzi dal 2026-10-25/26); mai a capo dentro la riga durante la riparazione [sync:safe]

## [1.0.2] - 2026-10-27

### Changed

- Appreso da sessione 2026-10-27 (`/graph -y` re-run #4): re-run su work-graph.md = editing chirurgico con ancore a riga singola e verifica celle post-scrittura (pipe per riga costanti); `handoff-write graph` esige `--dir product/state` (default tool `product/` → shadow copy), campi `--field` JSON-first con fallback stringa [sync:safe]

## [1.0.1] - 2026-10-25

### Changed

- Appreso da sessione 2026-10-25: celle di `work-graph.md` mai con pipe grezzi (alternazioni regex) — sfuggire o riformulare [sync:safe]
