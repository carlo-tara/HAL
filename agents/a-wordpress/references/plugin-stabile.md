# Plugin stabile — standard di sviluppo

Plugin **stabili** aggiungono funzionalità persistente a WordPress. Restano attivi in produzione e richiedono manutenzione.

---

## Quando usare

- Nuova feature permanente (admin UI, REST API, cron, shortcode)
- Integrazione servizio esterno ongoing
- Estensione tema via plugin (feature toggle, widget, block)

**Non usare** per trasformazioni dati one-shot → vedi [plugin-migrate.md](plugin-migrate.md).

---

## Naming e struttura

| Elemento | Convenzione |
|----------|-------------|
| Slug cartella | `{prefix}{feature}` es. `example-analytics` |
| File principale | `{slug}.php` |
| Text domain | uguale allo slug o `{prefix}-{feature}` |
| Costanti | `{PREFIX}_{FEATURE}_VERSION`, `_PLUGIN_DIR`, `_PLUGIN_URL` |

### Struttura consigliata

```
{slug}/
├── {slug}.php              # Bootstrap
├── readme.txt
├── includes/
│   ├── class-autoloader.php
│   ├── class-activator.php
│   └── class-{feature}.php
├── admin/
│   ├── views/
│   ├── css/
│   └── js/
├── assets/
└── languages/
```

---

## Header plugin (obbligatorio)

```php
<?php
/**
 * Plugin Name:       Nome Leggibile
 * Plugin URI:        https://example.com
 * Description:       Descrizione breve.
 * Version:           1.0.0
 * Requires at least: 6.1
 * Requires PHP:      7.4
 * Author:            Nome Autore
 * Author URI:        https://example.com
 * License:           GPLv2 or later
 * License URI:       https://www.gnu.org/licenses/gpl-2.0.html
 * Text Domain:       my-plugin
 * Domain Path:       /languages
 *
 * @package My_Plugin
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'MY_PLUGIN_VERSION', '1.0.0' );
define( 'MY_PLUGIN_DIR', plugin_dir_path( __FILE__ ) );
define( 'MY_PLUGIN_URL', plugin_dir_url( __FILE__ ) );
define( 'MY_PLUGIN_BASENAME', plugin_basename( __FILE__ ) );
```

Allinea `Version` e costante alla versione in `README.md` del progetto se previsto.

---

## Bootstrap minimo

```php
require_once MY_PLUGIN_DIR . 'includes/class-autoloader.php';

add_action( 'plugins_loaded', function () {
	load_plugin_textdomain(
		'my-plugin',
		false,
		dirname( MY_PLUGIN_BASENAME ) . '/languages'
	);
} );

register_activation_hook( __FILE__, array( 'My_Plugin_Activator', 'activate' ) );
register_deactivation_hook( __FILE__, array( 'My_Plugin_Activator', 'deactivate' ) );
```

---

## Pagina Impostazioni (obbligatoria)

Ogni plugin stabile espone una pagina opzioni:

```php
add_action( 'admin_menu', function () {
	add_options_page(
		__( 'My Plugin', 'my-plugin' ),
		__( 'My Plugin', 'my-plugin' ),
		'manage_options',
		'my-plugin-settings',
		'my_plugin_render_settings'
	);
} );

add_filter( 'plugin_action_links_' . MY_PLUGIN_BASENAME, function ( $links ) {
	$links[] = '<a href="' . esc_url( admin_url( 'options-general.php?page=my-plugin-settings' ) ) . '">'
		. esc_html__( 'Impostazioni', 'my-plugin' ) . '</a>';
	return $links;
} );
```

Se il progetto usa prefisso emoji nel menu (es. Asso2026), segui `CONTRIBUTING.md` del progetto.

---

## Sicurezza

| Regola | Implementazione |
|--------|-----------------|
| Input | `sanitize_*()`, `wp_unslash()`, validazione tipi |
| Output | `esc_html()`, `esc_attr()`, `esc_url()`, `wp_kses_post()` |
| Form admin | `wp_nonce_field()`, `check_admin_referer()` |
| AJAX/REST | `current_user_can()`, nonce, rate limit se pubblico |
| SQL | `$wpdb->prepare()` sempre; no query concatenate |
| File | `validate_file()`, no path traversal |

---

## Hook e performance

- Carica admin assets solo in admin (`is_admin()`)
- Enqueue script/style solo sulle pagine che servono
- Usa transients per cache dati costosi
- Cron: `wp_schedule_event()` in activation, `wp_clear_scheduled_hook()` in deactivation
- Evita query N+1; usa `WP_Query` con parametri appropriati

---

## Feature toggle (se il progetto li usa)

Leggi flag da opzione condivisa (es. `asso2026_core_features`) via helper del progetto.
Non duplicare la fonte di verità.

---

## Test

Se il progetto prevede PHPUnit / RGR:

1. **RED** — test che fallisce
2. **GREEN** — codice minimo
3. **REFACTOR** — migliora mantenendo test verdi

Path tipico: `tests/unit/test-plugin-{slug}.php`

---

## Sync, deploy e packaging

1. Sviluppa in **plugin source** (fonte di verità)
2. Sync verso **plugin runtime** (comando dal profilo sito)
3. Attiva/verifica in admin o via WP-CLI
4. **Genera zip versionato** `{slug}-{versione}.zip` — vedi [plugin-package.md](plugin-package.md)
5. Aggiorna `CHANGELOG.md` / `BACKLOG.md` del progetto se richiesto

Il plugin non è pronto per la consegna senza il file `.zip` installabile da wp-admin.

---

## Checklist pre-consegna

- [ ] Header completo e costanti definite
- [ ] Guard `ABSPATH` su tutti i file PHP
- [ ] Text domain caricato
- [ ] Pagina Impostazioni + link in `plugins.php`
- [ ] Sanitize/escape/nonce su form e output
- [ ] Activation/deactivation hook se serve schema o cron
- [ ] Test passano (se previsti dal progetto)
- [ ] Sync runtime eseguito
- [ ] Zip `{slug}-{versione}.zip` generato (plugin-package.md)
- [ ] Nessuna credenziale hardcoded
