# WP-CLI — cheatsheet operativo

Comandi di analisi, smoke e manutenzione usati da **a-wordpress**. Prefissa sempre con il wrapper del profilo sito (`docker exec … wp`, `ssh … wp`, o `wp` nativo). Path WP da `.cursor/wordpress/{sito}.md`.

Apply lungo / cron di sistema / Elementor / Yoast: [remote-wp-cli.md](remote-wp-cli.md).  
Migrate custom: [plugin-migrate.md](plugin-migrate.md).

---

## Inventario e stack

```bash
wp cli info
wp core version
wp core is-installed
wp plugin list
wp plugin list --status=active
wp theme list
wp theme list --status=active
wp option get siteurl
wp option get home
wp option get blogname
wp option get template
wp option get stylesheet
```

---

## Contenuti e meta (con cautela)

```bash
wp post list --post_type=post --posts_per_page=5 --fields=ID,post_title,post_status
wp post list --post_type=page --posts_per_page=5
wp post meta get {ID} {meta_key}
wp term list category --fields=term_id,name,slug,count
wp option get {option_name}
```

`wp db query` solo se necessario e dopo backup; preferire `$wpdb->prepare` / plugin migrate per scritture.

---

## Cron

```bash
wp cron event list
wp cron event run --due-now
wp cron test
```

Con `DISABLE_WP_CRON` + crontab di sistema: vedi [remote-wp-cli.md](remote-wp-cli.md) § Cron.

---

## Cache e manutenzione

```bash
wp cache flush
wp rewrite flush
wp transient delete --all          # solo se richiesto; impatto alto
wp eval 'echo WP_DEBUG ? "on" : "off";'
```

---

## Plugin (deploy zip)

```bash
wp plugin install /path/to/{slug}-{versione}.zip --activate
wp plugin deactivate {slug}
wp plugin is-active {slug}
wp plugin get {slug}
```

Packaging: [plugin-package.md](plugin-package.md).

---

## Migrate (pattern)

```bash
wp {prefix}migrate-{slug} run --dry-run
wp {prefix}migrate-{slug} run
wp {prefix}migrate-{slug} status
# batch lunghi (se supportati dal comando)
wp {prefix}migrate-{slug} run --limit=100 --offset=0
```

Registrare comandi solo se `defined( 'WP_CLI' ) && WP_CLI`.

---

## Smoke post-intervento (checklist minima)

```
Task Progress (smoke WP-CLI):
- [ ] wp core version / wp cli info
- [ ] wp plugin list (custom attesi attivi; migrate disattivati)
- [ ] wp option get siteurl + home coerenti
- [ ] wp cron event list (niente backlog anomalo)
- [ ] wp cache flush (dopo apply/migrate se previsto)
- [ ] Campione: wp post list / option get rilevanti al task
```

---

## Wrapper tipici (documentare nel profilo)

| Ambiente | Esempio |
|----------|---------|
| Docker | `docker exec {container} wp --path=/var/www/html …` |
| SSH + path | `ssh "$SSH_HOST" "cd \"$WP_ROOT\" && WP_CLI_ALLOW_ROOT=1 wp …"` |
| Locale | `wp --path=/var/www/example/wordpress …` |

Non hardcodare host/path nello skill L1: restano in L2 o `.cursor/wordpress/{sito}.md`.
