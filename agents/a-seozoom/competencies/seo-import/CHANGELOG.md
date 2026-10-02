# Changelog — competenza seo-import (L1)

## [Unreleased]

## [1.0.5] - 2026-09-15

### Added
- Flag `usable` su `sources.seozoom` in import-report (`ok` resta false; FAILED ma usabile esplicito) [sync:safe]
- GTM soft-fail: auto `accessNotConfigured` o env `SEO_IMPORT_SOFT_GTM=1` → skipped senza hard-fail analytics [sync:safe]

## [1.0.4] - 2026-09-15

### Fixed
- Summary SeoZoom in `import-report` quando validate stampa JSON multi-riga (`}` → metriche `per_url_ok`/`missing_critical`/…) [sync:safe]

## [1.0.3] - 2026-08-13

### Added
- Cloudflare: export batch (`cf_*.csv`) vs API live multi-zona per confronto traffico reale [sync:review]

## [1.0.2] - 2026-08-03

### Added
- FAILED ma usabile; retry export timeout (`--force`); batch misto competitor [sync:review]

## [1.0.1] - 2026-08-03

### Added
- § Latest batch e manifest check (algoritmo resolve + output minimo) [sync:review]

## [1.0.0] - 2026-07-27

### Added
- Baseline L1: import/export multi-fonte, Playwright-only, troubleshooting [sync:review]
