---
name: seozoom-{progetto}
extends: a-seozoom
version: 1.0.0
extends-version: 1.5.0
competencies:
  - seo-import
  - metriche-analisi
  - onpage-seo
  - geo-citabilita
  - seo-audit
  - schema-markup
  - programmatic-seo
  - site-architecture
  - hreflang-i18n
  - topic-cluster
  - google-ads
description: >-
  SEO/GEO per {progetto} — eredita a-seozoom e aggiunge path contenuti, build e regole locali.
---

# SEO/GEO {progetto} — estensione progetto

Skill figlia (L2). Eredita `a-agentzero` → `a-seozoom` → **questo file**.  
Competenze: risolvi L1 (e override sotto `competencies/{id}/` se presenti). Nessuna baseline L0 SEO. Dichiarare nel frontmatter solo gli id che il progetto userà (opt-in).

---

## Progetto

| Campo | Valore |
|-------|--------|
| Nome | {nome-progetto} |
| Dominio | {es. esempio.it} |
| Working directory | {path assoluto} |
| Tipo sito | statico / WordPress / altro |

---

## Credenziali e path

| Path / variabile | Valore |
|------------------|--------|
| Export SEO | `seo/YYMMDD/` |
| Sitemap | `{path sitemap-enriched.json}` |
| Contenuti | `{path content/}` |
| `SEOZOOM_PROJECT` | {nome in SeoZoom} |
| `SEOZOOM_PROJECT_COMPETITOR` | opzionale |
| `GSC_SITE_URL` | {es. sc-domain:esempio.it} |

---

## Tipi di pagina e dove intervenire

| Tipo | URL esempio | Dove scrivere | Note build |
|------|-------------|---------------|------------|
| | | | |

---

## Modalità operative

| Modalità | Competenza L1 | Note L2 |
|----------|---------------|---------|
| **Import** | `seo-import` | Skip fonti / soglie manifest |
| **Analisi** | `metriche-analisi` | Soglie Vol/KO/CTR locali |
| **Cluster** | `topic-cluster` | Owner URL / hub-spoke locale |
| **Ottimizzazione** | `onpage-seo` | Path contenuti, build |
| **GEO / AEO / ricerca on-site** | `geo-citabilita` | Playbook motore, bot AI |
| **Audit** | `seo-audit` | Scope Quick/Full / Spider |
| **Schema** | `schema-markup` | Path template JSON-LD |
| **i18n** | `hreflang-i18n` | Locale dichiarate |
| **pSEO** | `programmatic-seo` | Playbook + dati |
| **IA** | `site-architecture` | Albero URL locale |
| **PageSpeed** | — | Solo workflow locale |

---

## Competenze L2 (opzionale)

Crea solo override necessari:

```
.cursor/skills/seozoom-{progetto}/competencies/
  seo-import/SKILL.md
  metriche-analisi/SKILL.md
  onpage-seo/SKILL.md
  geo-citabilita/SKILL.md
  seo-audit/SKILL.md
  schema-markup/SKILL.md
  programmatic-seo/SKILL.md
  site-architecture/SKILL.md
  hreflang-i18n/SKILL.md
  topic-cluster/SKILL.md
```

```yaml
---
name: seo-import
kind: competency
version: 1.0.0
extends-version: 1.0.0   # = version L1 a-seozoom/competencies/seo-import/
description: >-
  Override seo-import per {progetto}.
---
```

Body: **solo delta**. Check: `bash agents/a-agentzero/scripts/agent-version.sh competency-chain .cursor/skills/seozoom-{progetto}/competencies/{id}/SKILL.md`

---

## Override workflow ottimizzazione

{Descrivi step 1-N specifici del progetto.}

---

## Skill di progetto (deleghe)

| Skill | Path | Quando |
|-------|------|--------|
| | `.cursor/skills/` | |
| a-copywriter / tono-di-voce | | Title/meta/FAQ e copy lungo |

---

## Comandi build / verifica

```bash
# Adatta al progetto
```

---

## Ricerca on-site (se presente)

Canone L1: `a-seozoom/competencies/geo-citabilita/references/ricerca-on-site-seo-geo.md`.

| Campo | Valore |
|-------|--------|
| Motore | {es. Pagefind} |
| Playbook L2 | `{path}` |
| Mappa intent | `{path}` |

---

## Regole locali

- {regola 1}
- Ogni numero con fonte in `seo/`
- Non inventare metriche
- Title/meta/FAQ: `onpage-seo` + `tono-di-voce` (a-copywriter); keyword CSV ≠ copy letterale

---

## Versionamento

| Campo | Valore |
|-------|--------|
| `version` | Delta L2 |
| `extends-version` | Versione `a-seozoom` (1.5.0+) |
| CHANGELOG | `.cursor/skills/seozoom-{progetto}/CHANGELOG.md` |

Sync: `agent-version.sh pending .cursor/skills/seozoom-{progetto}/SKILL.md`
