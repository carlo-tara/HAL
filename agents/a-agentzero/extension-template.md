---
name: {dominio}-{progetto}
extends: a-{dominio}
version: 1.0.0
extends-version: 1.0.0
role: default
# primary: true   # opzionale: un solo primary per dominio se multi-figlio
description: >-
  {Descrizione breve: cosa aggiunge per {progetto} rispetto all'agente base a-{dominio}.}
---

# {Titolo human-readable} — estensione progetto

Skill figlia (L2) per **{progetto}**. Eredita da `a-{dominio}` via `extends:`.

All'avvio: carica catena `a-agentzero` → `a-{dominio}` → **questo file**.

`role:` tipici: `default` | `data` | `editorial` | `voice` — vedi AGENT-PROTOCOL § Multi-figlio.

---

## Progetto

| Campo | Valore |
|-------|--------|
| Nome | {nome-progetto} |
| Dominio / sito | {es. esempio.it} |
| Working directory | {path assoluto, es. /var/www/esempio.it} |
| Repo | {path repo se diverso} |
| Ruolo L2 | {default / data / editorial / voice} |

---

## Path locali

| Tipo output | Path |
|-------------|------|
| {es. Contenuti} | `{path}` |
| {es. Asset} | `{path}` |
| {es. SEO export} | `{path}` |
| {es. Plugin source} | `{path}` |

---

## File dati progetto

| File | Path | Note |
|------|------|------|
| {es. Brand} | `.cursor/brands/{nome}.md` | {creato / da creare} |
| {es. Profilo WP} | `.cursor/wordpress/{nome}.md` | {se applicabile} |
| {es. Stile illustrazione} | `.cursor/illustration-styles/{nome}.md` | {se applicabile} |

---

## Override workflow

Solo le differenze rispetto al base L1. Se il workflow è identico, scrivi «Nessun override — segui L1».

{Descrivi override qui, es. passi aggiuntivi, checklist extra, vincoli brand.}

---

## Capacità aggiuntive

Cosa sa fare questo figlio che il base non copre:

- {capacità 1}
- {capacità 2}

---

## Deleghe

| Agente / skill | Ruolo | Quando |
|----------------|-------|--------|
| `{sibling-data}` | data | Import, CSV, manifest, metriche |
| `{sibling-editorial}` | editorial | Title, meta, FAQ, CTA, publish |
| `{slug}-voice` | voice | Tono, registri, rewrite |
| `a-copywriter` | — | Corpo lungo, humanize |
| `a-illustrator` | — | Asset, copertine |
| `a-seozoom` / L2 SEO | — | Keyword da dati reali |
| `a-wordpress` | — | Plugin, migrazioni |
| `a-charts` | — | Grafici, encoding, SVG/D3/canvas |
| `a-b2b` | — | Pilot B2B (facade → a-product § Profilo B2B) |

Compila solo le righe presenti nel repo. **Conflitto stuffing/CTA vs tono → vince voice/brand.**

---

## Regole locali

Regole ferree o preferenze specifiche del progetto (non duplicare L0/L1):

- {regola 1}
- {regola 2}

---

## Agent companion

| Campo | Valore |
|-------|--------|
| Path | `.cursor/agents/{nome}.md` |
| Sync | Allineare `extends-version` e path competenze a ogni sync L2←L1 |

---

## Versionamento

| Campo | Valore |
|-------|--------|
| `version` | Versione del delta L2 (semver) |
| `extends-version` | Versione L1 integrata — aggiorna al sync selettivo |
| CHANGELOG | `.cursor/skills/{dominio}-{progetto}/CHANGELOG.md` |

Alla creazione: imposta `extends-version` alla `version` corrente del padre L1 (`a-{dominio}`).

Sync selettivo: vedi `~/.agents/skills/a-agentzero/references/agent-versioning.md`  
Report: `bash agents/a-agentzero/scripts/agent-version.sh pending .cursor/skills/{dominio}-{progetto}/SKILL.md`

---

## Riferimenti

| Risorsa | Path |
|---------|------|
| Agente base | `~/.agents/skills/a-{dominio}/SKILL.md` |
| Protocollo | `~/.agents/skills/a-agentzero/AGENT-PROTOCOL.md` |
| {doc progetto} | `{path}` |
