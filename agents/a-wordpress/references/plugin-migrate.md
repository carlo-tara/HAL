# Plugin migrate — standard one-shot

Plugin **migrate** modificano dati e configurazioni WordPress in modo **temporaneo**. Ciclo di vita: installa → attiva → esegue → verifica → **disattiva**.

---

## Quando usare

- Migrazione postmeta, options, tassonomie
- Pulizia dati legacy (shortcode, meta obsoleti)
- Trasformazione bulk contenuti (es. Divi → HTML)
- Riconfigurazione plugin third-party (Yoast, ACF, …)
- Import one-shot da JSON/CSV

**Non usare** per feature permanenti → vedi [plugin-stabile.md](plugin-stabile.md).

---

## Naming

| Elemento | Convenzione |
|----------|-------------|
| Slug cartella | `{prefix}migrate-{slug}` es. `example-migrate-yoast-cleanup` |
| Option flag | `{prefix}_migrate_{slug}_done` o `{prefix}_migrate_{slug}_version` |
| Text domain | uguale allo slug |

---

## Lifecycle obbligatorio

```
Install → Activate → Dry-run → Execute → Verify → Deactivate
```

```
Task Progress (migrate):
- [ ] 1. Analisi installazione (site-analysis.md)
- [ ] 2. Backup DB documentato
- [ ] 3. Dry-run eseguito e output verificato
- [ ] 4. Execute con idempotenza
- [ ] 5. Verify (conteggi, campione record, smoke test)
- [ ] 6. Admin notice "disattiva il plugin"
- [ ] 7. Disattivazione plugin
- [ ] 8. **Packaging:** zip `{slug}-{versione}.zip` (plugin-package.md)
- [ ] 9. Nota in CHANGELOG/BACKLOG progetto
```

---

## Requisiti obbligatori

### 1. Idempotenza

La migrazione non deve corrompere dati se eseguita due volte.

```php
function example_migrate_is_done() {
	return (bool) get_option( 'example_migrate_yoast_cleanup_done', false );
}

function example_migrate_mark_done( $count = 0 ) {
	update_option( 'example_migrate_yoast_cleanup_done', true, false );
	update_option( 'example_migrate_yoast_cleanup_count', (int) $count, false );
	update_option( 'example_migrate_yoast_cleanup_at', current_time( 'mysql' ), false );
}
```

All'avvio, se già completata → admin notice informativa, nessuna riesecuzione.

### 2. Dry-run

Modalità preview senza scrivere nel DB (o con transazione rollback):

- Admin: checkbox "Solo anteprima" o pulsante separato
- WP-CLI: flag `--dry-run` se il progetto supporta WP-CLI

Output dry-run: conteggi, campione 5–10 record, errori previsti.

### 3. Log operazioni

- Transient admin: `set_transient( 'example_migrate_log', $lines, HOUR_IN_SECONDS )`
- Oppure file in `wp-content/uploads/example-migrate-{date}.log` (mai in repo)

Logga: timestamp, record ID, azione, errori.

### 4. Admin notice post-migrazione

```php
add_action( 'admin_notices', function () {
	if ( ! example_migrate_is_done() ) {
		return;
	}
	printf(
		'<div class="notice notice-success is-dismissible"><p>%s</p></div>',
		esc_html__( 'Migrazione completata. Disattiva il plugin Example Migrate Yoast Cleanup.', 'example-migrate-yoast-cleanup' )
	);
} );
```

### 5. Deactivation hook

- **Non** cancellare dati migrati
- Opzionale: pulire transient/log temporanei
- Documentare rollback manuale se possibile

---

## Struttura consigliata

```
{prefix}migrate-{slug}/
├── {prefix}migrate-{slug}.php
├── includes/
│   ├── class-migrator.php      # Logica migrazione
│   ├── class-admin.php         # UI dry-run / execute
│   └── class-wp-cli.php        # Opzionale: comandi CLI
├── admin/
│   └── views/
│       └── migrate-page.php
└── readme.txt
```

Pagina admin tipica: **Strumenti → {Nome Migrazione}** o sotto Impostazioni.

---

## Hook — cosa evitare

| Vietato | Motivo |
|---------|--------|
| Hook permanenti su `init`/`save_post` senza guard | Riesecuzione continua |
| Feature toggle condivisi con plugin stabili | Accoppiamento indebito |
| SQL diretto senza `$wpdb->prepare()` | Sicurezza |
| `UPDATE wp_*` ad hoc da script esterni | Usa il plugin migrate |

Se serve un hook temporaneo, guard obbligatorio:

```php
add_action( 'init', function () {
	if ( example_migrate_is_done() ) {
		return;
	}
	// ...
} );
```

---

## WP-CLI (opzionale)

Se WP-CLI è disponibile nel progetto:

```bash
wp example-migrate run --dry-run
wp example-migrate run
wp example-migrate status
```

Registra comandi solo se `defined( 'WP_CLI' ) && WP_CLI`.

Cheatsheet: [wp-cli-cheatsheet.md](wp-cli-cheatsheet.md). Apply remoto lungo: [remote-wp-cli.md](remote-wp-cli.md).

---

## Job lunghi: batch + reschedule

Migrate su dataset grandi non devono girare in un unico callback WP-Cron né in una sessione SSH bloccante.

| Approccio | Quando |
|-----------|--------|
| Flag `--limit` / `--offset` (o equivalente) sul comando CLI | Preferito per one-shot controllabile |
| Loop in script `nohup` sul remoto | Apply multi-step / timeout SSH |
| Batch PHP + `wp_schedule_single_event` | Solo se il lavoro è ricorrente (stabile), non tipico per migrate |

**Regole:**

1. Dry-run sul campione o sul primo batch prima dell’execute completo
2. Idempotenza per batch (ripartenza da offset sicuro)
3. Non affidarsi a WP-Cron HTTP: in prod usare `DISABLE_WP_CRON` + `wp cron event run --due-now` (remote-wp-cli.md)
4. Dopo execute lungo: `wp cache flush` se il progetto lo prevede; verify a campione

Esempio:

```bash
wp example-migrate run --dry-run --limit=50
wp example-migrate run --limit=100 --offset=0
# ripetere offset finché status/conteggio indica fine
```

---

## Verifica post-esecuzione

| Check | Come |
|-------|------|
| Conteggio record | `wp post list`, query con `$wpdb->get_var` |
| Campione manuale | 5 post/pagine in admin |
| Option/meta | `wp option get`, `get_post_meta` su campione |
| Frontend | Smoke test URL critici |
| Log errori | `debug.log` pulito dopo migrate |

---

## Rollback

Documenta nel readme del plugin:

1. Cosa fa la migrazione (tabelle, meta keys, options)
2. Se il rollback è automatico (raro) o manuale
3. Procedura restore da backup se rollback non supportato

**Default:** backup DB prima di execute; rollback = restore backup.

---

## Riferimento pattern

Plugin esistente con dry-run e WP-CLI: `divi-to-html-importer` (migrazione contenuti Divi → HTML).

---

## Checklist pre-consegna

- [ ] Naming `{prefix}migrate-{slug}`
- [ ] Flag idempotenza implementato
- [ ] Dry-run funzionante
- [ ] Dataset grandi: batch (`--limit`/`--offset` o nohup) documentati
- [ ] Log operazioni
- [ ] Admin notice "disattiva il plugin"
- [ ] Deactivation hook sicuro
- [ ] Nessun hook permanente senza guard
- [ ] Backup richiesto/documentato prima di execute
- [ ] Verify completata
- [ ] Zip `{slug}-{versione}.zip` generato (plugin-package.md)
- [ ] Plugin disattivato dopo successo
- [ ] CHANGELOG/BACKLOG aggiornato
