# Auto Ontology side-car — pin e mapping (runtime esterno, non corpus di distillazione)

Reason why: a differenza dei clone in `agents/vendor/` (corpus da criticare/distillare secondo
`a-agentzero/references/l1-from-proto.md`), questo pin governa un **runtime MCP side-car**:
deve essere riproducibile, misurato e aggiornabile solo col rituale controllato del PRD
`docs/29_auto_ontology_semantic_layer.md` §6 AO-2.1.

## Sorgente

- Upstream: <https://github.com/gogoymh/auto-ontology-mcp> — Apache-2.0; opera derivata da
  NVIDIA Auto Ontology (attribuzione nel `NOTICE` del clone, che vive **fuori** dal bundle HAL).
- Clone locale: `/home/carlo/auto-ontology-mcp`. **Deviazione dal PRD (che prevedeva
  `/opt/auto-ontology-mcp`)**: il 2026-11-20 `sudo` non era interattivo in sessione agente.
  Le proprietà rilevanti (pin per SHA, fuori dal workspace, dipendenze dal lock a monte) sono
  invariate. Per ripristinare `/opt`: `sudo mkdir -p /opt/auto-ontology-mcp && sudo chown
  carlo !$`, spostare il clone, aggiornare questo file, la entry Zed e la riga BC in
  `docs/bounded-contexts.md`.
- Avvio: `uv --directory /home/carlo/auto-ontology-mcp run auto-ontology-mcp` (stdio).

<!-- PIN:START -->
| Campo | Valore |
|-------|--------|
| Commit | `0fb5ecf765e4cfbe3c86634c5c52a3b2e752923a` (`0fb5ecf`) |
| Version (`pyproject.toml`) | 0.6.1 |
| Data commit | 2026-11-18 11:49:28 +0900 |
| Subject (PR squash-merged) | The dry-run limit avoids the derived-table wrap on MySQL and SQL Server (#22) |
| KPI-1 `tools/list` (`TOOLSETS=answer`) | **13 tool / 15.782 char** (`model_dump` json; il ≈12k del README è la serializzazione di richiesta del client — per questo la baseline è la misura propria) |
| Evidenza misure | `logs/ao-sidecar/kpi1-0fb5ecf.txt` (hal_gateway) |
| Suite upstream al pin | `uv run pytest` → **254 passed, 5 skipped** (PG/Oracle senza env) |
| Invarianti CONTRIBUTING | verificati al primo insediamento: guard read-only in `datasources.py`/`store.py`/`knowledge.py`; nessuna dipendenza con API key; nessun invio dati fuori dal client |
| Env di servizio | `AUTO_ONTOLOGY_HOME=~/.auto-ontology-mcp` (dir 700, db 600), `TOOLSETS=answer`, `ALLOW_DATASOURCE_TOOLS=0`, `MAX_ROWS=100` (ceiling), `VAULT` unset (vault default interno) |
| Demo installata | datasource `demo` + KB: 3 sources / 12 passages / 16 concepts / 3 action items |
| Aggiornato il | 2026-11-20 — primo insediamento (AO-2) |
<!-- PIN:END -->

## Rituale di aggiornamento (ricorrente — PRD §6 AO-2.1, 7 passi)

1. `git fetch --tags --prune` + `git log PIN..origin/main -- pyproject.toml` → release = commit di
   bump `version` (upstream non pubblica tag né release; CONTRIBUTING reg. 5).
2. `git diff --stat PIN..NEW` + grep dei 3 invarianti CONTRIBUTING.
3. Snapshot logici: `export NAME -o ontology.yaml` per datasource + `export-wiki`; oltre a
   `cp -a ~/.auto-ontology-mcp`.
4. Rehearsal migrazione su copia (`AUTO_ONTOLOGY_HOME=/tmp/ao-dry`) + `uv run pytest`.
5. Bump: `git pull --ff-only` + `uv sync` + **re-misura KPI-1** (nomi tool prima, char dopo).
6. Nuova riga nel blocco PIN qui sopra (`version`, SHA, subject, delta KPI-1).
7. Regressione → revert allo SHA del pin precedente (questo file è il registro).

## Mapping con HAL

- Routing delle domande: canone in `docs/bounded-contexts.md` §«Routing delle domande» (link, non copia).
- Consumatori: `a-knowledge` §Deleghe (riga dedicata); agente Zed via `context_servers`.
- Trasporto: **stdio solo** — HTTP = N/A documentato (PRD §7).
- Licenza: `LICENSE`+`NOTICE` esistono solo nel clone; nel bundle HAL resta questo riferimento
  (nessun dump di `guidance.py`, che è derivato da prompt NVIDIA).
