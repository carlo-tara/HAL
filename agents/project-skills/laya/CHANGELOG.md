# Changelog — laya (System 1 Service)

## [1.7.2] - 2026-10-31

### Changed

- Trasporto L2 per il voto implicito: `_read_completion` legge gli SSE frame-by-frame fino a `[DONE]`/`finish_reason` (l'orchestratore :8910 non chiude il socket dopo la risposta → `response.read()`Whole-body andava in timeout); validato live end-to-end: verdetto S2 registrato come outcome sulla riga d'inferenza (`smart_option` `incorrect`/`correction`).


## [1.7.1] - 2026-10-31

### Added

- `laya_gate.py`: modulo canonico delle soglie e degli helper k-aware del gate — il gateway lo importa via symlink, CLI/tool/gateway condividono per costruzione le stesse soglie (niente più mirror manuale).
- Sezione «votes by family» in `scripts/analyze_telemetry.py` (`make telemetry`): i verdetti calibrati sono raggruppati `noul` vs `decision-family` vs `other` — è l'accettazione della P1 di monitoraggio del gate (decision-family ≥ 20/settimana).
- Voto implicito configurabile end-to-end: `SYSTEM2_URL`/`SYSTEM2_MODEL` in `hal_system1/.env` puntano l'orchestratore locale e `_extract_completion_text` tollera risposte JSON e SSE (`chat.completion.chunk`).


## [1.7.0] - 2026-10-31

### Added

- Gate k-aware sulla Strategy C: `system1_direct` con k≥4 richiede ensemble `top1 ≥ LAYA_DIRECT_MIN_TOP1` (0.8) e self-consistency forzata — misura telemetrica (a k=4 solo 5% dei primi pass ha top1≥0,8); mirror applicato anche al client gateway (`hal_gateway/laya_service.py`, astensione `low_margin` invece di verdetto inaffidabile).
- § Tabella di delega verde/giallo/rossa derivata dai dati `laya_calls` 2026-10-11→30 e dal benchmark S1/S2.

### Changed

- Strategy C: la soglia non è più la `confidence` entropica (inaffidabile: media 0,34 con top1 0,79 a k=2) ma `margin`/`top1_prob`; `router.py routing/choice --json` espone `margin`, `top1_prob`, `recommendation`, `passes`, `request_hash`.
- Voto implicito System 2: l'escalation di `smart_choice`/`smart_route` registra l'esito L2 su `/outcome` (`LAYA_IMPLICIT_VOTES=0` disattiva); `record_outcome` non sovrascrive verdetti esistenti (una inferenza = un voto).


## [1.5.1] - 2026-10-30

### Changed

- Comando canonico `commands/laya.md`: aggiunto frontmatter `version: 1.0.1` (convenzione dei comandi L0), fix dei path `router.py` (`/var/www/HAL` → `/var/www/hal_system1`) e formattazione code-fence; wrapper `.agents/skills/laya-cmd` rigenerato via `link-workspace-skills.sh` [sync:safe]

## [Unreleased]

### Added

- Protocollo Token Budget: strategie A-D formalizzate con telemetria integrata. Strategy A (multi-question anchoring), B (semantic pacing ≤5 opzioni), C (confidence-based routing con escalation automatica), D (attachment filtering). Tracciamento chiamate System1/System2 in `events/token-budget.jsonl`.

## [1.6.0] - 2026-10-30

### Added

- § MCP: tool `laya_outcome` (verdetto `correct|incorrect` + `correction` su `POST /outcome`, Bearer) e eco `request_hash` su `/predict` lato server → ciclo di calibrazione chiuso anche per routing/choice da Zed (cache-hit saltate: una inferenza = un voto). Gate `make test` (suite completa) accanto a `make mcp-test`. [sync:safe]

### Changed

- (a) Rientro di `noul` in inferenza GPU: rimossa la esclusione `noul_gpu_excluded` da `server.py` — i picchi 3–30 s erano eccezioni da GPU contesa (mediana ~2 s); il budget di latenza ora vive nel client/tool (`LAYA_TIMEOUT`, `LAYA_NOUL_TIMEOUT`, retry-once MCP), non nel server. [sync:safe]

## [1.5.0] - 2026-10-29

### Added

- § «Uso via Zed MCP tool»: Laya come context server MCP per Zed — `mcp_laya.py` (JSON-RPC stdio senza dipendenze, wrapper di `laya_service.py` + `POST /systemone`) espone i 7 tool `laya_routing|choice|score|confidence|context|noul|health`; le decisioni restituiscono `selected`/`margin`/`probabilities` e `recommendation` (`system1_direct`|`accept_with_caution`|`escalate_system2`, Strategy C delegata all'agente System 2), `noul` ecoeggia `request_hash` per `/outcome`. DNS fisso `laya.local` (mai IP), `LAYA_NOUL_TIMEOUT=15` s (picchi 3–30 s = eccezioni), Strategy B applicata al confine, diagnostica su stderr e protocollo solo su stdout. Setup idempotente: `scripts/setup_zed_mcp.py` (merge JSONC-aware + backup). Gate: `make mcp-test`. Appreso da sessione MCP Zed 2026-10-29 [sync:safe]

## [1.4.3] - 2026-10-29

### Added

- § Diagnosi rapida — ABSTAIN: contratto degli endpoint (`/v1/predict` nativo/shorthand con auth vs `POST /systemone` per i task senza auth, `{task_type,text,params}` → `{result:{choice,confidence,probabilities},request_hash}`), by-pass onesto di `score` (`score_not_discriminative` — mai fabricare), log canonico `/var/www/hal_system1/log.sqlite` (in HAL `/var/www/laya/log.sqlite` è una directory vuota), escalation con `confidence < 0.3` su etichette tecniche IT inaffidabili. Appreso da sessione fix laya_service 2026-10-29 [sync:safe]

## [1.4.2] - 2026-10-29

### Fixed

- Percorso comando `/laya`: `/var/www/HAL/router.py` → `/var/www/hal_system1/router.py` (path morto: l'agente eseguiva un file inesistente e riportava «ABSTAIN — servizio non raggiungibile» anche con laya-gpu sano su 8091). Allineati `product/adapters/commands/laya.md` (sorgente), `.agents/commands/laya.md`, `.zed/prompts/laya.md`, `commands/laya.md` e `laya-cmd/SKILL.md` (1.0.1). [sync:safe]

### Added

- Nuova § «Diagnosi rapida — ABSTAIN / GPU» in `SKILL.md`: pre-claim di servizio giù (path canonico + `/health` + `docker ps`), semantica `Broken pipe` = client-timeout, check GPU a 4 livelli (env, boot log, `allocated_gb` in `/health`, util `nvidia-smi` sotto carico). Appreso da sessione diagnosi ABSTAIN 2026-10-29 [sync:safe]

## [1.3.0] - 2026-10-21

### Added

- Protocollo Token Budget: strategie A-D formalizzate con telemetria integrata. Strategy A (multi-question anchoring), B (semantic pacing ≤5 opzioni), C (confidence-based routing con escalation automatica), D (attachment filtering). Tracciamento chiamate System1/System2 in `events/token-budget.jsonl`.

## [1.2.1] - previous

### Changed

- Versione corrente prima delle ottimizzazioni token budget.
