---
name: knowledge-{progetto}
extends: a-knowledge
version: 1.0.0
extends-version: 1.0.0
description: >-
  Knowledge per {progetto} — eredita a-knowledge e aggiunge corpus, path e convenzioni locali.
---

# Knowledge {progetto} — estensione progetto

Skill figlia (L2). Eredita `a-agentzero` → `a-knowledge` → **questo file**.

---

## Progetto

| Campo | Valore |
| ----- | ------ |
| Nome | {nome-progetto} |
| Working directory | {path assoluto} |
| Corpus sorgenti | {path libri/doc} |

---

## Path locali

| Tipo | Path |
| ---- | ---- |
| Sorgenti (input) | `{path}` |
| Skill generate (output) | `{path, es. .agents/skills/}` |
| Workdir estrazione | `{path, es. /tmp/book_skill_work}` |

---

## Override workflow

{Nessun override — segui L1 | descrivi override: modo estrattore forzato, depth, modello}

---

## Capacità aggiuntive

- {capacità 1, es. glossario di dominio}

---

## Deleghe

| Agente | Quando |
| ------ | ------ |
| `a-copywriter` | Voce dei testi propri |
| `a-seozoom` | SEO/GEO di doc pubblica |
| `a-design` | Cheatsheet, grafici |
| `a-harness` | Gate Make, versioning skill generate |

---

## Regole locali

- {regola 1, es. modello di distillazione preferito}

---

## Versionamento

| Campo | Valore |
| ----- | ------ |
| `version` | Versione delta L2 |
| `extends-version` | Versione `a-knowledge` integrata |
| CHANGELOG | `.agents/skills/knowledge-{progetto}/CHANGELOG.md` |

Alla creazione: `extends-version` = `version` corrente di `a-knowledge`.
Sync: `agent-version.sh pending .agents/skills/knowledge-{progetto}/SKILL.md`.
