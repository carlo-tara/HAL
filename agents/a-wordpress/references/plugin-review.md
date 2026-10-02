# Revisione plugin WordPress

Checklist per la modalità **Revisione** su plugin stabili o migrate (pre-merge, post-implementazione, audit).

---

## Severità findings

| Livello | Significato |
|---------|-------------|
| **Critical** | Sicurezza, perdita dati, fatal error — blocca merge |
| **Warning** | Bug probabile, performance, mancanza idempotenza (migrate) — correggere prima del deploy |
| **Suggestion** | Stile, DRY, doc — miglioramento opzionale |

Formato output:

```markdown
## Critical
- [file:line] Descrizione + fix suggerito

## Warning
- ...

## Suggestion
- ...
```

---

## Checklist generale

### Sicurezza

- [ ] `ABSPATH` guard su ogni file PHP
- [ ] Input sanitizzato (`sanitize_*`, `wp_unslash`)
- [ ] Output escaped (`esc_*`, `wp_kses_post`)
- [ ] Nonce su form e AJAX admin
- [ ] `current_user_can()` su azioni privilegiate
- [ ] `$wpdb->prepare()` su query dinamiche
- [ ] Nessuna credenziale/API key hardcoded
- [ ] Upload/file: validazione path e MIME

### Struttura e standard

- [ ] Header plugin completo
- [ ] Costanti versione/path definite
- [ ] Text domain e `load_plugin_textdomain`
- [ ] Autoload o require ordinati
- [ ] Naming coerente con prefix progetto
- [ ] PHPDoc su classi/metodi pubblici

### Packaging e consegna

- [ ] Versione allineata (header `Version:` = costante `*_VERSION`)
- [ ] Artefatto `{slug}-{versione}.zip` presente e aggiornato
- [ ] Radice zip = cartella slug (formato upload WordPress)
- [ ] Esclusi `.git`, `node_modules`, `tests` e altri artefatti dev

### Plugin stabile

- [ ] Pagina Impostazioni presente
- [ ] Link "Impostazioni" in `plugins.php`
- [ ] Activation/deactivation hook appropriati
- [ ] Assets enqueued solo dove servono
- [ ] Cron registrato e pulito in deactivation
- [ ] Compatibilità feature toggle progetto (se applicabile)

### Plugin migrate

- [ ] Naming `{prefix}migrate-{slug}`
- [ ] Flag idempotenza (`get_option` done/version)
- [ ] Dry-run implementato
- [ ] Log operazioni
- [ ] Admin notice post-completamento
- [ ] Nessun hook permanente senza guard `is_done()`
- [ ] Deactivation non cancella dati migrati
- [ ] Readme documenta rollback/backup

### Performance

- [ ] No query in loop su grandi dataset (batch con `LIMIT`/`offset` o cursor)
- [ ] Transients per dati cacheable
- [ ] Script/style non globali se evitabile

### Test

- [ ] Test PHPUnit presenti se il progetto li richiede
- [ ] Test coprono path critico (migrate dry-run, sanitizer, API)

---

## Review migrate — controlli extra

1. **Riesecuzione:** attivare due volte → nessuna duplicazione/corruzione
2. **Dry-run vs execute:** stessi conteggi in preview; execute modifica solo ciò che promette
3. **Interruzione:** cosa succede se lo script muore a metà batch?
4. **Multisite:** se applicabile, comportamento per sito

---

## Review stabile — controlli extra

1. **Disattivazione:** il sito resta funzionante? Dati orphan?
2. **Disinstallazione:** `uninstall.php` pulisce solo dati del plugin
3. **Conflitti:** stessi hook di altri plugin custom?
4. **i18n:** stringhe wrappate in `__()` / `_e()` con text domain corretto

---

## Perimetro revisione

| In scope | Out of scope |
|----------|--------------|
| Plugin custom del progetto | Core WordPress |
| Integrazione con tema progetto | Plugin third-party (salvo wrapper custom) |
| Sicurezza, idempotenza, lifecycle migrate | SEO copy (delega a-seozoom) |
| Allineamento CONTRIBUTING progetto | Design UI tema |

---

## Dopo la revisione

- Critical/Warning → fix obbligatorio prima di merge/deploy
- Suggestion → proponi fix; implementa solo se richiesto
- Per migrate approvato → ricorda checklist lifecycle fino a disattivazione
