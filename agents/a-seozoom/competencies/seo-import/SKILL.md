---
name: seo-import
kind: competency
version: 1.1.0
description: >-
  Gestisce l'importazione, il parsing e la pulizia dei dataset massivi da
  SeoZoom, GSC e GA4 usando Playwright/scripts per aggirare API limits.
  Orchestra la normalizzazione in file SQLite o JSONL per analisi metriche.
---

# Competenza L1 — seo-import

Data Engineering / ETL per dataset SEO e metriche organiche.

## Diff-Tiering e Context Limit

- Non riversare mai i CSV grezzi nel contesto LLM.
- Usa script Python per aggregare, filtrare (es. eliminazione keyword < 10 volume) o scrivere su un DB SQLite locale a zero token.
- Passa all'LLM solo statistiche, top N e schema di output (metadata).

## Output (Contratto)

- **Zero verbosità narrativa.**
- Output: Fornisci lo script di scraping/parsing, o lo schema DB SQLite validato, e nient'altro.

Per il dettaglio sull'automazione headless (Playwright), i formati manifest SEO e il troubleshooting ETL:
Leggi `references/seo-import-extended.md`.
