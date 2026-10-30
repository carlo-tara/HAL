# Changelog — a-design

Tutte le modifiche rilevanti a questo agente sono documentate in questo file.

Formato: [Keep a Changelog](https://keepachangelog.com/it/1.1.0/).
Versionamento: [Semantic Versioning](https://semver.org/lang/it/).

## [1.2.3] - 2026-10-30

### Changed

- Sync L0 a-agentzero `extends-version` 1.12.0 → 1.13.0: voci pending = quattro regole di protocollo in `AGENT-PROTOCOL.md` (§ contesto, dichiarazioni, cache: append-only dichiarazioni iniettate, mai reinserire `reasoning_content`, ordering static-first, retention provider) e fix infrastrutturale `scripts/sync-agents.sh` § `report_workspace_links` [sync:safe]; body L1 invariato

## [Unreleased]

### Changed

- illustrator 1.6.1 → 1.6.2: `scripts/generate-image.py` (ToDo N24, doc QwenCloud §connection reuse) — `http_json` riusa una connessione keep-alive `http.client` per host (`_CONNECTIONS`): il loop di `poll_synthesis_task` non apre più una TCP+TLS a ogni poll; retry con connessione nuova solo su drop keep-alive (RemoteDisconnected/BadStatusLine), timeout e altri errori di rete restano `URLError` senza retry (niente duplicazione di POST); `RuntimeError` su HTTP ≥ 400 preservato; rimossa frazione CJK residua nel messaggio di task terminale (sostituita con «non retryabile"); contratto in `tests/test_bundle_http_reuse.py` [sync:safe]

- illustrator 1.6.0 → 1.6.1: fix diagnostici in `scripts/generate-image.py` senza cambio di comportamento funzionale — if annidato multi-modal error combinato (SIM102), `seed` normalizzato con `cast("int | None", ...)` (nessun valore alterato), clausola `except urllib.error.URLError` portata prima di `OSError` nel blocco download (URLError è subclass: prima era irraggiungibile e i fallimenti di download venivano etichettati come "write output")

## [1.2.2] - 2026-10-28

### Fixed

- illustrator 1.5.9 → 1.6.0 (ToDo 2026-10-28, T12/T26): `poll_synthesis_task` passa a backoff esponenziale con intervalli per modalità (tabella doc QwenCloud: image 3s×1.5 cap 15s, video 15s×1.5 cap 60s, asr 5s×1.5), stati terminali completi (`CANCELED`/`UNKNOWN` sollevano subito invece di girare fino al timeout contro il limite 20 QPS) e raccolta multi-output con `finish_reason == "stop"`: output saltati segnalati su stderr e campo `partial` nel JSON dello script; contratto in `tests/test_illustrator_polling.py`

## [1.2.1] - 2026-10-28

### Changed

- Sync L0 a-agentzero `extends-version` 1.11.0 → 1.12.0: voci pending solo infrastruttura L0 (comandi canonici cycle/graph, agent-todo.py flush, utility learn 1.5.0) [sync:safe]; body L1 invariato

## [Unreleased]

### Changed

- Allineato a a-agentzero 1.8.0; body L1 invariato [sync:safe]
- Allineato a a-agentzero 1.8.5; body L1 invariato [sync:safe]

## [1.1.0] - 2026-10-02

### Added

- System 1 (Laya) Gating in Visual Design: routing rapido delle richieste visive (`router.py routing`), selezione automatica del tipo di grafico (`router.py choice`) e scoring di accessibilità WCAG prima di attivare le elaborazioni System 2 [sync:safe]

## [1.0.0] - 2026-10-01

### Added

- Creazione agente unificato a-design (L1).
- Unificazione di charts, illustrator e uiux come skill interne.
- Estensione da a-agentzero @ 1.6.15.
