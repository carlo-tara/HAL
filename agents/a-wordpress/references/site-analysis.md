# Analisi installazione WordPress

Checklist per la modalità **Analisi**. Esegui prima di qualsiasi intervento su plugin stabili o migrate.

---

## Prerequisiti

- Profilo sito in `.cursor/wordpress/{sito}.md` (o onboarding da `site-brief-template.md`)
- Accesso al filesystem del progetto
- Credenziali da `.env` — **non committare, non loggare**

---

## Checklist

```
Task Progress (analisi):
- [ ] 1. Leggi profilo sito
- [ ] 2. Mappa path WP root, plugin source, plugin runtime, tema
- [ ] 3. Identifica stack (Docker, hosting, PHP, WP)
- [ ] 4. Inventario plugin custom vs third-party
- [ ] 5. Verifica accesso WP-CLI / DB (se necessario al task)
- [ ] 6. Leggi log/errori rilevanti
- [ ] 7. Produci report strutturato
```

---

## Step 1 — Profilo sito

Leggi `.cursor/wordpress/*.md`:

- **1 file** → usalo
- **2+ file** → chiedi quale installazione (o inferisci da path/dominio)
- **0 file** → fermati, proponi onboarding da `site-brief-template.md`

---

## Step 2 — Path e struttura

Verifica nel repo:

| Elemento | Cosa cercare |
|----------|--------------|
| WP root | `wp-config.php`, `wp-load.php` |
| Plugin source | Cartella `plugins/` separata da runtime |
| Plugin runtime | `wp-content/plugins/` |
| Tema | `themes/` o `wp-content/themes/` |
| Mu-plugins | `wp-content/mu-plugins/` |
| Uploads | `wp-content/uploads/` |

**Pattern comune:** source in `plugins/` → sync/copia in `wordpress/wp-content/plugins/`.

Documenta se source ≠ runtime e il comando di sync usato dal progetto.

---

## Step 3 — Stack tecnico

| Info | Come ottenerla |
|------|----------------|
| Versione PHP | `php -v`, Docker image, `wp cli info` |
| Versione WP | `wp core version`, header in `wp-includes/version.php` |
| Docker | `docker-compose.yml`, service name, porte |
| WP-CLI | Comando documentato nel profilo o `which wp` |
| Database | `.env` → `MYSQL_*`, prefisso tabelle in `wp-config.php` |

---

## Step 4 — Inventario plugin

Separa:

| Categoria | Criterio | Azione agente |
|-----------|----------|---------------|
| **Custom stabile** | Prefix progetto, no `-migrate-` | Manutenzione, estensione |
| **Custom migrate** | Prefix + `-migrate-` | Verifica se già eseguito/disattivato |
| **Third-party** | Da wordpress.org o vendor | Non modificare; wrappare in plugin custom se serve |

Per ogni plugin custom, annota: slug, tipo (stabile/migrate), versione, stato attivo/inattivo.

---

## Step 5 — Accesso operativo

| Tool | Uso |
|------|-----|
| WP-CLI | Inventario/smoke: [wp-cli-cheatsheet.md](wp-cli-cheatsheet.md); cron/remoto: [remote-wp-cli.md](remote-wp-cli.md) |
| PHPUnit | Test unitari plugin/tema |
| Log | `wp-content/debug.log`, log Docker, `error.log` |

**Regola:** per migrate, verifica sempre backup DB prima di esecuzione.

---

## Step 6 — Log e errori

Se il task riguarda un bug:

1. `wp-content/debug.log` (se `WP_DEBUG_LOG` attivo)
2. Log container / hosting
3. Errori PHP recenti nel profilo o in chat

Non modificare codice finché il report non è completo.

---

## Template report

Usa questo formato in output:

```markdown
# Analisi WordPress — {nome-sito}

## Stack
- WP root: {path}
- PHP: {version} | WordPress: {version}
- Ambiente: {local|staging|prod}
- Docker: {sì/no, service}

## Path plugin
- Source: {path}
- Runtime: {path}
- Sync: {comando o "coincidono"}

## Tema attivo
- {slug} @ {path}

## Plugin custom
| Slug | Tipo | Versione | Attivo |
|------|------|----------|--------|
| ... | stabile/migrate | ... | sì/no |

## Plugin third-party rilevanti
- {elenco breve}

## Accesso
- WP-CLI: {comando}
- Test: {comando phpunit}

## Rischi / note
- {backup mancante, plugin migrate ancora attivo, versioni obsolete, ...}

## Raccomandazioni
1. {azione prioritaria}
2. ...
```

---

## Quando ripetere l'analisi

- Primo intervento su un progetto
- Prima di ogni plugin **migrate**
- Dopo upgrade major WP/PHP
- Quando l'utente segnala comportamento anomalo non spiegato dal codice
