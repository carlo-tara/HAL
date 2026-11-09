# Mappa residui — HAL

Backlog rinfrescabile (≠ Progress append-only). Igiene: `/todo`.

Convention: ID stabile `HT-nnn` (non cambia a seguito di riordino); tag di chiusura — `#cycle` = richiudibile con `/cycle` (slice → red → green → refactor sotto gate Make), `#human` = richiede intervento umano (sessioni reali, step cross-repo, validazione).

Delta 2026-11-09 da `/impersonate karpathy hal_gateway` (lente registry `hal_mcp_tools`): le 5 voci sotto (HT-003…HT-007) derivano dai finding della lettura; praise «modello-usato-come-funzione» (`system1_preflight.TaskContract`/`PreflightDecision`) e «calibrazione da telemetria» (`laya_gate.py`) sono già architetture consolidate, senza voce.

## P0

## P1

- [ ] `HT-003` — Run A/B appaiata gated vs baseline senza middleware, con kill criterion dichiarato `#human` · P1 · Benchmark
  - Perché utile: verdetto `/impersonate karpathy` 2026-11-09 — il gating nuovo taglia token ~−53% e tempi ~−46% vs middleware vecchio, ma **resta sopra la baseline `20261017_all` per costo**: il layer System 1 non ha ancora il numero che ne giustifica l'esistenza. Senza un controfattuale esplicito, l'eval dice «migliorato» ma non «vale».
  - Acceptance: run `--system1` e run baseline sulle stesse coppie `(modello, test)` (confronto solo appaiato, `compare_tokens.py`); criterio di kill scritto nel report — se il gate non vince su costo a qualità ~piatta (rubrica), lo strato preflight si dismette; annotare esito nella tabella `history/` del README.

## P2

- [ ] `HT-005` — Gold set etichettato per l'eval raw di Laya (~200 casi/famiglia task) `#human` · P2 · System 1 (Laya)
  - Perché utile: l'accuracy ~96,5% del gate è misurata su **traffico di produzione** (8k chiamate, telemetria margini), non su casi con risposta nota: è calibrazione della soglia, non eval del modello. Un gold set rende l'eval di Laya una regressione riproducibile (benchmark, non impressione) ed è la baseline che il reject di `/impersonate karpathy` chiede («feature AI senza baseline»).
  - Acceptance: set versionato (choice/routing/score/noul, ~200 casi con label per famiglia) + script di scoring in `benchmark/`; il gate e le soglie di `laya_gate.py` ricalibrati sul set; run di regressione agganciata a una make target esistente.

- [ ] `HT-007` — Misura dell'effetto assemblaggio locale vs `assemblaggio_finale` via modello `#human` · P2 · Benchmark
  - Perché utile: run `20261023_8` ha **confermato** l'assemblaggio locale su phi3 (`finish_reason: local_assembly`, qualità 2/2) ma il README dichiara che «l'effetto dell'assemblaggio locale resta da misurare»: oggi è un meccanismo verificato, non un guadagno misurato (token, qualità, tempi vs copia via modello).
  - Acceptance: run dedicata con `estrazione_json_semplificato` a bracci appaiati (gate-forzato locale vs gate-forzato modello) su ≥2 modelli; riga delta nel `history/` + `compare_tokens.py`; se il delta è ≈0, documentare N/A e chiudere con esito negativo dichiarato.


## Già fatto

_(Buffer pre-flush in formato Keep a Changelog: sotto `### Added`, `### Changed`, `### Fixed` o `### Removed`; `/todo` lo svuota nel CHANGELOG.)_
