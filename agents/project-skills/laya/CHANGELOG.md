# Changelog — laya (System 1 Service)

## [1.5.1] - 2026-10-30

### Changed

- Comando canonico `commands/laya.md`: aggiunto frontmatter `version: 1.0.1` (convenzione dei comandi L0), fix dei path `router.py` (`/var/www/HAL` → `/var/www/hal_system1`) e formattazione code-fence; wrapper `.agents/skills/laya-cmd` rigenerato via `link-workspace-skills.sh` [sync:safe]

## [Unreleased]

### Added

- Protocollo Token Budget: strategie A-D formalizzate con telemetria integrata. Strategy A (multi-question anchoring), B (semantic pacing ≤5 opzioni), C (confidence-based routing con escalation automatica), D (attachment filtering). Tracciamento chiamate System1/System2 in `events/token-budget.jsonl`.

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
