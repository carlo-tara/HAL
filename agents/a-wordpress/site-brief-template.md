# Profilo installazione WordPress — {nome-sito}

Copia questo file in `.cursor/wordpress/{nome-sito}.md` nel progetto e compila ogni sezione.
L'agente `a-wordpress` lo legge all'avvio (skill in `a-wordpress/SKILL.md`, deploy via `a-wordpress/deploy.sh`).

---

## Identità

| Campo | Valore |
|-------|--------|
| **Nome sito** | {nome-sito} |
| **URL** | https://example.com |
| **Ambiente** | local / staging / prod |

---

## Path

| Campo | Path |
|-------|------|
| **WP root** | `/var/www/example/wordpress` |
| **Plugin source** (fonte di verità) | `/var/www/example/plugins` |
| **Plugin runtime** | `/var/www/example/wordpress/wp-content/plugins` |
| **Tema attivo** | `/var/www/example/themes/{slug}` |

> Se source e runtime coincidono, indica lo stesso path in entrambe le righe.

---

## Convenzioni plugin

| Campo | Valore |
|-------|--------|
| **Prefix plugin custom** | `example-` |
| **Text domain pattern** | `{prefix}{slug}` es. `example-core` |
| **Naming stabile** | `{prefix}{feature}` es. `example-analytics` |
| **Naming migrate** | `{prefix}migrate-{slug}` es. `example-migrate-yoast-cleanup` |

---

## Stack

| Campo | Valore |
|-------|--------|
| **PHP target** | 8.1+ |
| **WordPress target** | 6.4+ |
| **Docker Compose** | `docker-compose up -d` (service: `wordpress`) |
| **WP-CLI** | `docker exec {container} wp --path=/var/www/html` |
| **DISABLE_WP_CRON** | sì / no (prod: sì + crontab sistema) |
| **Cron runner** | `* * * * * cd {WP root} && wp cron event run --due-now` (o wrapper Docker/SSH) |
| **Sync source → runtime** | `rsync -a plugins/ wordpress/wp-content/plugins/` (adatta al progetto) |
| **Cartella zip plugin** | `plugins/` o `dist/` (artefatti `{slug}-{versione}.zip`) |
| **Script packaging** | `scripts/dev/package-{slug}-plugin.sh` (se presente) |

---

## Test

| Campo | Valore |
|-------|--------|
| **PHPUnit** | `phpunit tests/unit/` |
| **BDD features** | `bdd/features/` |
| **Workflow test** | RGR / BDD / nessuno |

---

## Documenti progetto

| Documento | Path |
|-----------|------|
| Regole AI | `.cursorrules` |
| Contributing | `CONTRIBUTING.md` |
| Standards | `STANDARDS.md` |
| Changelog | `CHANGELOG.md` |
| Backlog | `BACKLOG.md` |

---

## Plugin custom attivi

Elenco noto (aggiornabile dall'agente in analisi):

| Slug | Tipo | Note |
|------|------|------|
| `{prefix}core` | stabile | Funzionalità core |
| `{prefix}analytics` | stabile | Analytics |
| `{prefix}migrate-*` | migrate | One-shot, disattivare dopo uso |

---

## Credenziali e accesso

> **Mai committare credenziali.** Documentare solo dove trovarle.

| Risorsa | Dove |
|---------|------|
| Database | `.env` → `MYSQL_*` |
| WP admin | `.env` o password manager |
| API keys | `.env` |

---

## Note e vincoli

- Backup prima di migrate: {procedura}
- Plugin third-party vietati da modificare: {elenco}
- Hosting / vincoli deploy: {note}
- Cron: WP-Cron disabilitato? crontab documentato? (vedi a-wordpress `remote-wp-cli.md`)
