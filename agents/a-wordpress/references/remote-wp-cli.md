# Remote WP-CLI — apply lungo, cron, Elementor, redirect Yoast

Pattern riusabili per publish via SSH + WP-CLI (senza plugin migrate). Path host/script restano nella skill L2 del progetto o nel profilo `.cursor/wordpress/{sito}.md`.

Cheatsheet comandi: [wp-cli-cheatsheet.md](wp-cli-cheatsheet.md). Batch lunghi / migrate: [plugin-migrate.md](plugin-migrate.md).

---

## Timeout SSH su apply lungo

`wp-cli-apply` (o script equivalenti) può superare i limiti di una sessione SSH
interattiva (`Timeout, server … not responding`, exit 255).

**Anti-pattern:** ripetere lo stesso `ssh … bash script.sh` bloccante.

**Pattern:**

1. Copiare gli script sul remoto (`scp` → `/tmp/…`)
2. Lanciare con `nohup` sul droplet, log dedicati e marker di uscita
3. Poll dei log dalla macchina locale; cleanup `/tmp` a fine

Esempio (adattare path WP root e nomi script):

```bash
ssh "$SSH_HOST" "nohup bash -c 'cd \"$WP_ROOT\" && export WP_CLI_ALLOW_ROOT=1 && \
  bash /tmp/wp-cli-apply.sh > /tmp/wp-cli-apply.log 2>&1; \
  echo APPLY_EXIT=\$? >> /tmp/wp-cli-apply.log; \
  bash /tmp/wp-cli-elementor-fix.sh >> /tmp/wp-cli-elementor-fix.log 2>&1; \
  echo FIX_EXIT=\$? >> /tmp/wp-cli-elementor-fix.log; \
  wp cache flush >> /tmp/wp-cli-apply.log 2>&1' >/tmp/wp-cli-deploy.out 2>&1 & echo \$!"
```

Poi: `tail` / `grep APPLY_EXIT|FIX_EXIT` sui log.

---

## Cron di sistema al posto di WP-Cron

Per default WP-Cron gira sulle richieste HTTP e aggiunge latency. In staging/prod:

1. Disabilitare WP-Cron in `wp-config.php` (sopra `/* That's all, stop editing! */`):

```php
define( 'DISABLE_WP_CRON', true );
```

2. Schedulare il runner via **crontab di sistema** (path e wrapper dal profilo sito):

```cron
# Host nativo
* * * * * cd /path/to/wp && wp cron event run --due-now >/dev/null 2>&1

# Docker (adattare container e --path)
* * * * * docker exec {container} wp cron event run --due-now --path=/var/www/html >/dev/null 2>&1

# SSH remoto (se il cron gira sulla macchina di gestione)
* * * * * ssh "$SSH_HOST" 'cd "$WP_ROOT" && export WP_CLI_ALLOW_ROOT=1 && wp cron event run --due-now' >/dev/null 2>&1
```

Documentare nel profilo sito: `DISABLE_WP_CRON` sì/no, riga crontab, comando WP-CLI effettivo.

### Smoke cron

```bash
wp cron event list
wp cron event run --due-now
wp option get timezone_string   # o gmt_offset — allineamento orari
```

---

## Job lunghi: batch + reschedule (cron e migrate)

Un callback che loopa su tutti gli utenti/post **blocca la coda** cron (e può superare timeout SSH se lanciato via WP-CLI interattivo).

**Anti-pattern:** un solo evento che processa l’intero dataset.

**Pattern (plugin stabile o job ricorrente):**

- Batch fissi (es. 50–100 record) + offset in option/transient
- A fine batch: `wp_schedule_single_event( time() + N, 'hook' )` se restano record
- Oppure runner WP-CLI a chunk (vedi sotto)

**Pattern (migrate one-shot):** preferire comando CLI con `--dry-run` / batch espliciti; per apply molto lunghi usare `nohup` (sezione Timeout SSH). Dettaglio lifecycle: [plugin-migrate.md](plugin-migrate.md) § Job lunghi.

Esempio CLI a chunk (adattare al comando del progetto):

```bash
# Ripetere finché exit/conteggio indica fine
wp example-migrate run --limit=100 --offset=0
wp example-migrate run --limit=100 --offset=100
# oppure loop in script nohup sul remoto
```

Scheduling senza duplicati:

```php
if ( ! wp_next_scheduled( 'my_task' ) ) {
	wp_schedule_event( time(), 'hourly', 'my_task' );
}
```

---

## Gate SEO vs fallimento Elementor

| Esito | Significato |
|-------|-------------|
| Apply meta/term OK | Gate pubblicazione SEO soddisfatto (Yoast, descrizioni categoria, post content) |
| `Failed to update custom field '_elementor_data'` | Update JSON Elementor via `wp post meta update` fragile su payload grandi — **non** invalida l’apply SEO |

Verificare prima meta Yoast / `term update` description. Per `_elementor_data` usare migrate dedicato o altro canale; non bloccare il publish SEO sul solo fallimento Elementor.

---

## Redirect Yoast — verifica vs CSV

Prima di (re)importare un CSV redirect:

```bash
wp yoast redirect list
# o wrapper L2 del progetto
```

- In Yoast le **origin** sono tipicamente **senza** `/` iniziale (normalizzare il CSV).
- Messaggio UI «Nessun reindirizzamento è stato importato… già esistono» / 0 righe = **OK** se le origin coincidono — non forzare re-import.
- Catena 301 equivalente al target diretto del CSV è accettabile (A→B→C invece di A→C).

Import CSV di solito **non** è coperto dagli script apply meta; resta passo manuale o migrate.
