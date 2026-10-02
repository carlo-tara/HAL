# Changelog — competenza metriche-analisi (L1)

## [Unreleased]

## [1.0.5] - 2026-09-15

### Added
- Contratto confronto batch: JSON + delta MD, chiave `(keyword, url)`, Δ dashboard, no overwrite scorecard hand, baseline «aspettative» = scorecard+monitor [sync:review]
- Mid-lag EARLY± + chiusura scorecard; segnali deboli (`gsc_pages`/pos↑/`keyword_all`) ≠ OK [sync:review]

## [1.0.4] - 2026-08-13

### Changed
- Ponte esplicito a `topic-cluster` per owner/SERP-overlap oltre cannibalizzazione CSV [sync:review]

## [1.0.3] - 2026-08-13

### Added
- Validazione post-batch: guardrail checklist batch precedenti sugli stessi cluster owner [sync:review]
- PagesWithPotential: scarta driver «fuori perimetro» senza richiesta esplicita; nota `pagine_competitor` = overlap topic [sync:review]

## [1.0.2] - 2026-08-04

### Added
- Pass low-KO: soglia KO <=55 + Pos 4-20, gate owner/intent, step workflow ZO [sync:review]

## [1.0.1] - 2026-08-03

### Added
- § Validazione post-batch e confronti: no ~24h, ranking≠owner, Δ vs batch precedenti [sync:review]

## [1.0.0] - 2026-07-27

### Added
- Baseline L1: glossario/workflow ZA–ZO, PagesWithPotential, competitor project [sync:review]
