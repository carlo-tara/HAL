---
name: geo-citabilita
kind: competency
version: 1.2.0
description: >-
  GEO/AEO e citabilità AI: distinzione sintesi AI vs answer surfaces, agent readiness,
  extractability, audit menzioni, ricerca on-site. Solo L1 (no baseline L0).
---

# Competenza L1 — geo-citabilita (a-seozoom)

Canoni GEO / AEO / agent readiness e ricerca interna da insight SEO. Policy registrar, Cloudflare e path: **skill L2**.

Corpus ricerca on-site: [references/ricerca-on-site-seo-geo.md](references/ricerca-on-site-seo-geo.md).  
Extractability: [references/ai-extractability.md](references/ai-extractability.md).  
`llms.txt`: [references/llmstxt-evidence.md](references/llmstxt-evidence.md).  
Pin: [marketingskills-source.md](../../references/marketingskills-source.md) · [claude-seo-source.md](../../references/claude-seo-source.md) · [labat-seo-geo-aeo-source.md](../../references/labat-seo-geo-aeo-source.md).

---

## Quando applicare

Menzioni AI, citabilità, agent readiness, Content Signals, FAQ/copy per answer surfaces, ricerca on-site da `monitored.csv`, audit “AI search readiness”.

---

## GEO vs AEO (non confondere)

| Termine | Superficie | Focus |
|---------|------------|-------|
| **GEO** | Sintesi AI (Perplexity, ChatGPT Search, Gemini, AI Overviews) | Fatti, entity, E-E-A-T osservabile, originalità, bot access |
| **AEO** | Answer surfaces (featured snippet, PAA, voice-like) | H2 domanda, blocco 40–60 parole, definizioni, liste/tabelle |
| **Google AI Overviews / AI Mode** | Sotto-insieme Google | = **SEO people-first** + indexability; niente file/markup speciali obbligatori |

Default: scrivi per le persone, organizza per chiarezza. Stats di boost citazione: solo con fonte, mai come promesse quantitative sul progetto.

Metodologia checklist ispirata a Labat (SEO/GEO/AEO); override rich-result → `schema-markup`.

---

## Agent readiness (policy L2)

1. Carica prima L2: policy e limiti infrastrutturali
2. **Content Signals** (opz. L2): es. `ai-train=no, search=yes, ai-input=yes` — utili a policy, **non** leva citazione Google
3. **`llms.txt`:** report presence; optionality / agent-docs; **non** peso ranking — [llmstxt-evidence.md](references/llmstxt-evidence.md)
4. Link headers verso indice curato: solo se L2 li richiede; non claim citabilità
5. **DNS-AID / Markdown for Agents:** fail tipici = infra L2; non inventare workaround
6. **Anti-esposizione:** no Link header verso indici bulk; robots/canonical in L2

FAQ e copy citabile: `onpage-seo` (+ `tono-di-voce`). Schema → `schema-markup` (FAQ/HowTo ≠ leva SERP Google).

---

## Pilastri citabilità

1. **Structure** — answer block 40–60 parole, H2 question-shaped, tabelle dove serve
2. **Authority** — fonti, statistiche datate, attribution (no credenziali inventate)
3. **Presence** — dove i motori già citano: piano L2; non spam directory

Dettaglio checklist GEO/AEO: [ai-extractability.md](references/ai-extractability.md).  
Cluster topico: `topic-cluster`.

### Bot AI in robots.txt

Verificare (policy L2): GPTBot / ChatGPT-User, PerplexityBot, ClaudeBot / anthropic-ai, Google-Extended, Bingbot.  
Bloccare training-only (es. CCBot) può restare compatibile con search bot — decisione L2.

---

## Ricerca on-site allineata a SEO/GEO

1. Canone L1: ricerca-on-site-seo-geo.md
2. Playbook operativo (motore/script): **solo L2**
3. Dopo export `monitored.csv`: mappa intent + build secondo L2
4. Indice ricerca **non** indicizzato da Google (`Disallow`)
5. GA4 `search`: review vs mappa intent (L2)

---

## Override L2 tipici

Policy Cloudflare/registrar, path `llms.txt`, playbook Pagefind, mappa intent, allow/deny bot AI — `competencies/geo-citabilita/SKILL.md` nel figlio.
