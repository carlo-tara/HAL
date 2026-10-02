# Changelog — AgentFactory

Tutte le modifiche rilevanti a livello **repo** (Mappa residui / wave chiuse).  
Formato [Keep a Changelog](https://keepachangelog.com/it/1.1.0/).  
I CHANGELOG degli agenti (`a-*/CHANGELOG.md`) restano ownership di `/version`.

## [Unreleased]

### Added
- Promozione pattern sibling `role: data` + `role: editorial` in `a-seozoom` § Estensioni L2 — `a-seozoom` 1.8.11 (`35ebe87`)
- Valutazione Substack in `a-seozoom` → **resta L2 NEED-N** (solo GiocoStrategico; nessun 2° sito) — `/graph -y` n4
- `/sync <` su cwd AgentFactory: inventario L2 in-repo + consumer noti `/var/www` (`sync` 1.1.2)
- HFDP Fase 1–4 su a-harness: Template Method/Hollywood su `/cycle`; Adapter↔ACL / Facade↔Make; stati Plan|Act|Stuck|Ready; `references/gof-meta-patterns.md` (`a-harness` 1.5.7–1.5.10)
- `/graph -y` multi-cycle fino a fine backlog (`graph` 1.2.0)
- `/todo` flush «Già fatto» → questo file (`todo` 1.1.0)

### Changed
- DUP L2 consumer tagliati (`/graph -y` n1–n3): rimossa `liberating-tone-of-voice` da GiocoStrategico; split `seozoom-piratesstraps` + editorial thin; stub `seo-geo-specialist` liberating.it
- Playbook DUP: nota repo target senza git/Make (gate N/A, check greppabili); L2 `harness-agentfactory` 1.1.20 ambito `ready-proof`
- Facade `a-b2b` 2.1.2: Outcome/Success signal (anti–Build Trap) allineata a a-product
- Docs operativo/discovery/README: Build Trap / Product Kata
- L2 extension-template: org/reward → L2 only; `a-po` triage handoff feature-only
- Verifica pin L2 `b2b-*`: 2× `extends: a-b2b`; 0× `a-product` accidentale

### Already shipped (riferimento)
- Fold Profilo B2B + facade a-b2b + `/learn` ToDo/docs (`e24c41b`)
- Escaping the Build Trap → a-product 1.2.0 (`7a74469`)
- `/sync !` deploy post Build Trap/Kata
