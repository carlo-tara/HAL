---
name: site-architecture
kind: competency
version: 1.0.1
description: >-
  Information architecture SEO: gerarchia pagine, URL, navigazione, link interni,
  hub-spoke. XML sitemap tecnico → seo-audit. Solo L1 (no baseline L0).
---

# Competenza L1 — site-architecture (a-seozoom)

Pianificazione struttura sito. Distillato da upstream `marketingskills/skills/site-architecture` (MIT).  
Pin: [marketingskills-source.md](../../references/marketingskills-source.md).

---

## Quando applicare

Sitemap mentale / albero pagine, ristrutturazione IA, URL design, strategia link interni, breadcrumbs.  
**Non** per XML sitemap tecnico (→ `seo-audit`) né solo markup breadcrumb (→ `schema-markup`).

---

## Principi

1. **3-click** — pagine money raggiungibili in ≤ 3 click dalla home (regola empirica)
2. **Flat quanto basta** — profondità solo se la nav resta chiara
3. **URL leggibili** — lowercase, hyphen, gerarchia che rispecchia IA
4. **Nessun orphan** — ogni URL importante ha in-link contestuali + nav
5. **Hub-spoke** per cluster tematici / pSEO (`programmatic-seo`)

Template per tipo sito: [ia-patterns.md](references/ia-patterns.md). Upstream: `site-type-templates.md`, `navigation-patterns.md`, `mermaid-templates.md`.

---

## Gerarchia (livelli)

| Livello | Ruolo | Esempio |
|---------|-------|---------|
| L0 | Home | `/` |
| L1 | Sezioni primarie | `/features`, `/blog` |
| L2 | Pagine sezione | `/features/analytics` |
| L3+ | Dettaglio | `/docs/api/auth` |

Nav header: **4–7** item + CTA a destra. Footer a colonne (product / resources / company / legal).

---

## Link interni

- Ancore descrittive (no “clicca qui”)
- Pagine autorità → spoke orphan o nuovi URL strategici (da priorità `metriche-analisi`)
- Evitare over-optimization exact-match su ogni anchor
- Dopo cambio IA: piano redirect 301 (implementazione WP → **a-wordpress**)

---

## Alias / scorciatoia SERP

Per intent «query scorciatoia» (es. brand concatenato senza spazio) può servire un URL dedicato **senza** una nuova guida editoriale completa:

- Preferisci landing sottile o route generata dal build/CMS, con FAQ e link verso gli **owner** esistenti (anti-cannibal)
- Includi URL in sitemap e cleanup delle route generate
- Path, template e test CI: skill L2

Non creare una seconda pagina «piena» sullo stesso cluster se esiste già un owner.

---

## Output atteso

- Albero ASCII (o Mermaid se complesso) con URL
- Mappa nav header/footer
- Lista orphan / troppo profondi
- Impatto SEO: cluster, hub, URL da preservare + redirect
