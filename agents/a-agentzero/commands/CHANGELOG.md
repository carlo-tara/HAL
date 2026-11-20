# Changelog — comandi L0 (`agents/a-agentzero/commands`)

Storico dei bump dei comandi L0 HAL, migrato il 2026-11-20 dai mirror
`.agents/skills/<cmd>/CHANGELOG.md` (specchi generati, rimossi: la sede unica
delle skill-comando è la globale `~/.agents/skills/`, pubblicata da
`publish-global-commands.sh` dal canone). Le versioni senza voce vivono nello
storico git del canonico. Un bump va applicato al canonico e rigenerato
subito (`/sync !`), mai sugli specchi.

## graph

### [1.0.5] - 2026-11-19

### Changed

- Canone path-free (de-racing step 4, bf67d62): gli script L0 sono invocati con path assoluto `/var/www/hal_gateway/...`, niente dipendenza dal mount. [sync:safe]

### [1.0.4] - 2026-11-09

### Changed

- Nota Tool builder/handoff: da workspace consumer il path canonico è `agents/scripts/harness-prompt-builder.sh` (symlink HAL), non `scripts/` del consumer — la nota rv9 era un path-miss. Bump originato dal canonico `commands/graph.md` (commit 2f37faf, `a-agentzero` 1.13.2); changelog del mirror aggiunto ora (mancava al rigenerato) + pin `tests/test_graph_rerun_rules.py` aggiornato. [sync:safe]

### [1.0.3] - 2026-10-30

### Changed

- Appreso da sessione 2026-10-30 (`/graph -y` re-run #6): verifica pipe su tutte le righe della tabella a ogni re-run (la corruzione può venire da run precedenti — caso righe N11/N14 con pipe grezzi dal 2026-10-25/26); mai a capo dentro la riga durante la riparazione [sync:safe]

### [1.0.2] - 2026-10-27

### Changed

- Appreso da sessione 2026-10-27 (`/graph -y` re-run #4): re-run su work-graph.md = editing chirurgico con ancore a riga singola e verifica celle post-scrittura (pipe per riga costanti); `handoff-write graph` esige `--dir product/state` (default tool `product/` → shadow copy), campi `--field` JSON-first con fallback stringa [sync:safe]

### [1.0.1] - 2026-10-25

### Changed

- Appreso da sessione 2026-10-25: celle di `work-graph.md` mai con pipe grezzi (alternazioni regex) — sfuggire o riformulare [sync:safe]

## cycle

### [1.0.1] - 2026-10-25

### Changed

- Appreso da sessione 2026-10-25: condizione STOP legittima solo con probe empirico datato nella riga del grafo [sync:safe]

## version

### [1.3.3] - 2026-11-20

### Changed

- «L0 command — canonico vs specchi» riscritta: il mirror `.agents/skills/<cmd>` non è più uno specchio vivo (sede unica skill-comando: globale); changelog dei comandi trasferito in questo file canonico; `tests/test_l0_command_canonical.py` allineato (assenza mirror + pin dinamici).

### [1.3.2] - 2026-11-19

### Changed

- Canone path-free (de-racing step 4, bf67d62): script L0 invocati con path assoluto `/var/www/hal_gateway/...`. [sync:safe]

### [1.3.1] - 2026-10-30

### Added

- Regole di coerenza: «L0 command — canonico vs mirror» — il bump va applicato al canonico `agents/a-agentzero/commands/<cmd>.md` e il mirror rigenerato subito (`.agents/skills/<cmd>/SKILL.md`, `.zed/prompts/<cmd>.md`, `product/adapters/commands/<cmd>.md` sono rigenerati da `/sync !`); caso graph 1.0.3, 2026-10-30. Changelog avviato a 1.3.1: le versioni precedenti vivono nello storico git del canonico [sync:safe]

## learn

### [1.0.1] - 2026-11-20

### Changed

- Rimosso dal Processo il riferimento al mirror `.agents/skills/learn/` (sede unica: skill globale + deep bundle invariato). Bump originato dalla dismissione dei wrapper locali dei comandi L0 — refuso di sweep: la frase identica era già stata corretta in `sync.md` nello stesso intervento, `learn.md` era rimasta indietro (le auto-descrizioni dei canoni vanno grepate, non ricordate).

## sync

### [1.0.1] - 2026-11-20

### Changed

- Rimosso dal Processo il riferimento al mirror `.agents/skills/sync/` (sede unica: skill globale + deep bundle invariato); nota «wrapper generato (prompt/skill globale)». Bump originato dalla dismissione dei wrapper locali dei comandi L0.
