---
name: wordpress-{progetto}
extends: a-wordpress
version: 1.0.0
extends-version: 1.0.0
description: >-
  WordPress per {progetto} — eredita a-wordpress e aggiunge path, prefix e convenzioni locali.
---

# WordPress {progetto} — estensione progetto

Skill figlia (L2). Eredita `a-agentzero` → `a-wordpress` → **questo file**.

---

## Progetto

| Campo | Valore |
|-------|--------|
| Nome | {nome-progetto} |
| Working directory | {path assoluto} |

---

## Profilo sito

| File | Path |
|------|------|
| Profilo WP | `.cursor/wordpress/{nome-sito}.md` |

### Path installazione

| Campo | Valore |
|-------|--------|
| WP root | `{path}` |
| Plugin source | `{path}` |
| Plugin runtime | `{path}` |
| Prefix plugin | `{prefix}` |
| Test command | `{comando}` |
| Cartella zip | `{plugins/ o dist/}` |
| Script packaging | `{scripts/package-*.sh o generico}` |

---

## Override workflow

{Nessun override | RGR/BDD obbligatori, sync custom, etc.}

---

## Deleghe

| Agente | Quando |
|--------|--------|
| `a-copywriter` | Testi admin, meta |
| `a-seozoom` | SEO plugin |

---

## Regole locali

- {regola 1}

---

## Versionamento

| Campo | Valore |
|-------|--------|
| `version` | Versione delta L2 |
| `extends-version` | Versione `a-wordpress` integrata |
| CHANGELOG | `.cursor/skills/wordpress-{progetto}/CHANGELOG.md` |

Alla creazione: `extends-version` = `version` corrente di `a-wordpress`.  
Sync: [agent-versioning.md](../../a-agentzero/references/agent-versioning.md) — `agent-version.sh pending .cursor/skills/wordpress-{progetto}/SKILL.md`
