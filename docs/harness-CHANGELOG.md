# Harness changelog — HAL Gateway

Solo **fabbrica** (Makefile, gate, regole, skill L2). Storia prodotto: `CHANGELOG.md` root.

## [Unreleased]

### Added

- 2026-10-30 allineamento catene harness: `harness-hal` 1.0.1 → 1.0.2 e `harness-agentfactory` 1.1.28 → 1.1.29, `extends-version` a-harness → 1.9.2 (L0 `a-agentzero` rilasciato 1.13.0 con regole protocollo AGENT-PROTOCOL; L1 allineati con bump patch contrattuale [sync:safe]; gate `make -C agents version-chains` verde). Body L2 invariati.
- 2026-10-28 split `.env`/`config/runtime.env` + cataloghi `./models/*.json`: regola 6 in `harness-hal` (1.0.0 → 1.0.1) — `.env` solo secret, config non-secret in runtime.env con default allineati in providers.yaml/docker-compose, rigenerazione Zed via `/update-models` (`scripts/update_models.py`). Test contratto `test_compose_ollama`/`test_models_catalog` fissano i default. Dettagli in `docs/operativo.md` (§ split e § cataloghi).
- 2026-10-28 `/learn` 1.5.7 → 1.5.8: «Frammenti CJK nel testo italiano generato» promosso da candidato a voce di `tool-pitfalls.md` (seconda sessione di osservazione, rimedio `grep -rnP` post-scrittura); ottava evidenza per «Parametri numerici respinti come stringhe» (`terminal timeout_ms` 2× → omissione).
- 2026-10-25 `/bootstrap` profile **standard** (a-harness 1.8.1): Makefile root Platform API (specchio CI: check-secrets/deps/sast + `unittest discover`, quiet default con log ISO settimanale in `logs/`; tier int/e2e/parity/db dichiarati N/A in L2), L2 `harness-hal` (`agents/project-skills/`, symlink `.agents/skills/`), `docs/glossary.md`, `docs/bounded-contexts.md`, `product/state/harness-freeze.md`, `logs/` in `.gitignore`. Progress e learnings: esistenti in `product/state/` (niente duplicazione in docs/).

### Changed

- 2026-11-09 dedup L2 da `/sync <` (DUP confermato su ≥2 progetti): i 4 pattern della shell (guide collassabili `<details>`, empty state azionabile, «come leggere» a una riga, click→risultato) promossi da `b2b-explorer-ui-ux` a SoT in `wtp-ux-ui/patterns.md` § «Explorer help & guide», sostituiti da puntatori; bump `wtp-ux-ui` 1.3.67→1.3.68 e `b2b-explorer-ui-ux` 1.0.31→1.0.32 (il 1.0.31 è il sync selettivo della catena parallela già nel file: extends verso `a-copywriter` 1.7.5, il cui push aspetta la propria catena; nessun test CI vincola la catena). Promozione L1 `a-design/uiux` delle parti generiche rinviata: padre dirty in catena parallela (mixed-scope); repliche: copie WTP_App e L1 al commit della catena.
- 2026-11-18 chiusura del debito «rinviata 2026-11-09» (promozione L1 `uiux` delle parti generiche): i 3 canoni chrome (slot brand vs meta di pagina; azioni di output nel menu File della suite; copy UI da origine i18n con fallback) promossi in `a-design/uiux` 1.1.0→1.2.0 § Pattern guida & chrome comuni — trigger (b) della regola: richiesta esplicita dell'utente al report `/sync <`; `wtp-ux-ui` 1.3.69→1.3.70 e `b2b-explorer-ui-ux` 1.0.33→1.0.34 restano con override di progetto + puntatore al canone L1. I 4 pattern shell del 2026-11-09 restano la porzione WTP-specifica in `wtp-ux-ui/patterns.md` § Explorer help & guide. [sync:safe]

### Removed

- 2026-11-18 `harness-agentfactory` ritirata dal canone (repo sorgente AgentFactory definitivamente fuori uso, decisione umana 2026-11-18): rimossa la directory `agents/project-skills/harness-agentfactory/`, i symlink consumer (hal_gateway, brainbeez, InnerCircle, hal_system1, liberating.it), `MIGRATION.md`, i companion rotti `~/.cursor/agents/*.md` (15 symlink verso `/var/www/AgentFactory/` inesistente) e le enumerazioni nei tooling di fabbrica (`sync-agents.sh`, `link-workspace-skills.sh`, `check-editor-links.sh`, `global_config.py`). Riferimenti live sostituiti con HAL/`harness-hal` (AGENTS root e agents, README, `docs/operativo.md`, glossary, bounded-contexts, routing learn); registro storico intatto. [sync:safe]
