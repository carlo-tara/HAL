# Changelog — a-design

Tutte le modifiche rilevanti a questo agente sono documentate in questo file.

Formato: [Keep a Changelog](https://keepachangelog.com/it/1.1.0/).  
Versionamento: [Semantic Versioning](https://semver.org/lang/it/).

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
