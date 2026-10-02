# `/llms.txt` — evidence reframe (lean)

Distillato da `vendor/claude-seo/skills/seo-geo/references/llmstxt-evidence.md` (MIT).  
Pin: [claude-seo-source.md](../../../references/claude-seo-source.md). Fonte primaria in conflitto: **Google Search Central**.

## TL;DR AF

- Google Search (incl. AI Overviews / AI Mode) **ignora** `llms.txt` — non ranking, non citazione.
- Nessun major AI search system ha documentato consumo di `llms.txt` terzi (stato pin claude-seo).
- **Ship comunque** come optionality a basso costo / utilità per **agent docs** (siti developer, Mintlify-style).
- In audit: report **presence** e qualità file; **non** assegnare peso citazione.

## Dove conta

| Contesto | Valore |
|----------|--------|
| Docs prodotto / API / library | Alto per coding agents (Cursor, Claude Code, …) |
| Sito business non-dev | Difensivo / futuro; zero costo |
| Promessa “+citazioni AI” | Vietata senza fonte primaria aggiornata |

## Content Signals / Link headers

Policy L2 utili (bot access, anti-esposizione): non trattarli come leva citabilità Google. Soften rispetto a “must have per GEO”.

Aggiornare questo file quando Google o un provider LLM pubblica consumo confermato di `llms.txt`.
