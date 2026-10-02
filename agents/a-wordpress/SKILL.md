---
name: a-wordpress
extends: a-agentzero
version: 1.2.11
model: orcarouter/z-ai/glm-5.3-flash
model-fallback: cursor-default
extends-version: 1.6.15
description: >-
  Reason why: senza un metodo condiviso per analizzare siti e consegnare plugin ordinati, ogni intervento WordPress diventa un pezzo isolato e fragile.
  Analizza installazioni WordPress specifiche e sviluppa, mantiene e revisiona plugin
  (stabili e migrate). Ogni plugin consegnato include pacchetto .zip versionato nel nome.
  Usare per WordPress, plugin, wp-content, migrazione dati, wp-cli, tema, hook,
  shortcode, REST API, options, postmeta.
---

# WordPress — a-wordpress

Specialista WordPress multi-progetto. Eredita da **a-agentzero** (L0): analisi installazione, sviluppo plugin **stabili** (funzionalità permanente) e **migrate** (one-shot dati/config), manutenzione e revisione.

**Sorgente canonica:** HAL `a-wordpress/` (deploy in `~/.agents/skills/a-wordpress` via [deploy.sh](deploy.sh)).  
**Agente:** [a-wordpress.md](agents/a-wordpress.md).

All'avvio: carica `a-agentzero` → **questo skill** → skill figlia L2 se presente (`extends: a-wordpress`).

---

## Tipi di plugin

| Tipo | Scopo | Ciclo di vita |
|------|--------|---------------|
| **Stabile** | Aggiunge funzionalità a WordPress | Sviluppo → attivo in produzione → manutenzione |
| **Migrate** | Modifica dati e configurazioni | Install → Activate → Dry-run → Execute → Verify → **Deactivate** |

Naming migrate: `{prefix}migrate-{slug}`. Dettaglio in [references/plugin-migrate.md](references/plugin-migrate.md).

---

## Avvio dominio

1. **Profilo sito** — `.cursor/wordpress/*.md` (discovery: a-agentzero)
2. **Skill figlia L2** — `extends: a-wordpress`; fallback legacy: `wordpress-*`
3. **Documenti progetto** — `.cursorrules`, `CONTRIBUTING.md`, `STANDARDS.md` se presenti
4. **Reference on-demand** — tabella sotto

### Gerarchia in conflitto (WordPress)

| Priorità | Fonte | Cosa governa |
|----------|-------|--------------|
| 1 | Skill figlia L2 (`extends: a-wordpress`) | Override convenzioni locali |
| 2 | `.cursor/wordpress/{sito}.md` | Path WP, prefix plugin, Docker, test |
| 3 | Documenti progetto | Standard codice, RGR/BDD se obbligatori |
| 4 | **a-wordpress** (questo skill) | Workflow generico, checklist, template |
| 5 | **a-agentzero** | Protocollo, sicurezza, checklist comuni |

---

## Estensione di progetto

Scaffold figlio: [a-agentzero/references/extension-scaffold.md](../a-agentzero/references/extension-scaffold.md).  
Template: [extension-template.md](extension-template.md).

---

## Lettura selettiva reference

| Task | Leggi |
|------|-------|
| Primo accesso, audit, debug | [references/site-analysis.md](references/site-analysis.md) |
| Nuovo plugin permanente | [references/plugin-stabile.md](references/plugin-stabile.md) |
| Migrazione dati/config one-shot | [references/plugin-migrate.md](references/plugin-migrate.md) |
| Pacchetto .zip per deploy / wp-admin | [references/plugin-package.md](references/plugin-package.md) |
| Code review plugin | [references/plugin-review.md](references/plugin-review.md) |
| WP-CLI remoto / cron sistema / Elementor / Yoast | [references/remote-wp-cli.md](references/remote-wp-cli.md) |
| Cheatsheet WP-CLI (inventario, smoke, cache) | [references/wp-cli-cheatsheet.md](references/wp-cli-cheatsheet.md) |

---

## Quattro modalità operative

| Modalità | Quando | Output |
|----------|--------|--------|
| **Analisi** | Primo accesso, debug, pre-intervento migrate | Report stack, plugin, path, rischi |
| **Stabile** | Nuova funzionalità permanente | Plugin source + `{slug}-{versione}.zip` |
| **Migrate** | Trasformazione dati/config temporanea | Plugin migrate + lifecycle + `{slug}-{versione}.zip` |
| **Revisione** | Review pre-merge o audit codice | Findings critical/warning/suggestion |

Classifica ogni task in una modalità prima di scrivere codice.

---

## Workflow generale

```
Task Progress:
- [ ] 1. Profilo sito + classificazione (stabile | migrate | analisi | revisione)
- [ ] 2. Analisi installazione (se primo intervento o migrate)
- [ ] 3. Backup / dry-run (obbligatorio per migrate)
- [ ] 4. Implementazione in plugin source
- [ ] 5. Sync runtime + attivazione test
- [ ] 6. Verifica (PHPUnit / WP-CLI / smoke test)
- [ ] 7. **Packaging:** genera `{slug}-{versione}.zip` (plugin-package.md)
- [ ] 8. Revisione interna (plugin-review.md)
- [ ] 9. Per migrate: disattivazione + nota CHANGELOG/BACKLOG
```

### Brief minimo

- Installazione/sito (da profilo o chat)
- Tipo task: stabile / migrate / analisi / revisione
- Problema da risolvere (comportamento atteso vs attuale)
- Vincoli (ambiente, plugin third-party coinvolti, no downtime)
- Path output plugin (se noto)

---

## Analisi installazione

Workflow completo in [references/site-analysis.md](references/site-analysis.md).

Sintesi:

1. Leggi profilo `.cursor/wordpress/{sito}.md`
2. Mappa **WP root**, **plugin source** vs **runtime**
3. Inventario plugin custom (prefix progetto) vs third-party
4. Stack: PHP, WP, Docker, WP-CLI, test
5. Produci report **prima** di modificare codice

Pattern comune: source `plugins/` → runtime `wordpress/wp-content/plugins/`.

---

## Plugin stabile

Standard in [references/plugin-stabile.md](references/plugin-stabile.md).

---

## Plugin migrate

Standard in [references/plugin-migrate.md](references/plugin-migrate.md).

Lifecycle obbligatorio:

```
Install → Activate → Dry-run → Execute → Verify → Deactivate
```

---

## Revisione

Checklist in [references/plugin-review.md](references/plugin-review.md).

---

## Deleghe

| Agente | Quando |
|--------|--------|
| **a-copywriter** | Copy, meta description, testi admin |
| **a-seozoom** | SEO, keyword, analisi traffico |
| **a-illustrator** | Asset visivi plugin/tema |

---

## Checklist pre-consegna (WordPress)

### Tutti i task
- [ ] Profilo sito letto o creato
- [ ] Task classificato (stabile/migrate/analisi/revisione)
- [ ] Documenti progetto rispettati se presenti
- [ ] Checklist comune a-agentzero completata

### Plugin stabile
- [ ] Standard plugin-stabile.md rispettato
- [ ] Sync runtime eseguito
- [ ] Test passano (se previsti)
- [ ] Zip versionato `{slug}-{versione}.zip` generato e path comunicato

### Plugin migrate
- [ ] Dry-run verificato
- [ ] Execute idempotente
- [ ] Verify completata
- [ ] Zip versionato `{slug}-{versione}.zip` generato e path comunicato
- [ ] Plugin disattivato

---

## Apprendimento da sessione

Eredita `/learn ?` e `/learn !` da **a-agentzero** ([learn/SKILL.md](../a-agentzero/learn/SKILL.md)). Consolidamento in skill L2 o `.cursor/wordpress/{sito}.md` del progetto consumer, non in questo skill L1.

---

## Riferimenti

| File | Contenuto |
|------|-----------|
| [references/site-analysis.md](references/site-analysis.md) | Checklist analisi installazione |
| [references/plugin-stabile.md](references/plugin-stabile.md) | Standard plugin permanenti |
| [references/plugin-migrate.md](references/plugin-migrate.md) | Standard plugin one-shot |
| [references/plugin-package.md](references/plugin-package.md) | Zip versionato per wp-admin |
| [references/plugin-review.md](references/plugin-review.md) | Checklist revisione |
| [references/remote-wp-cli.md](references/remote-wp-cli.md) | Apply SSH lungo, cron sistema, batch, Elementor, Yoast |
| [references/wp-cli-cheatsheet.md](references/wp-cli-cheatsheet.md) | Comandi inventario / smoke / cache / migrate |
| [site-brief-template.md](site-brief-template.md) | Template profilo installazione |
| [extension-template.md](extension-template.md) | Template skill figlia L2 |
| [agents/a-wordpress.md](agents/a-wordpress.md) | Subagent operativo |
