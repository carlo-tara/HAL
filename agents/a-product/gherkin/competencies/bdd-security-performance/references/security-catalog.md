# Security catalog (/secure)

Tag: `@security` + sotto-tag.

1. `@authz` — accesso step senza privilegi persona
2. `@input` — input ostile; assert nessun script/dati corrotti; messaggio sicuro
3. `@session` — scadenza a metà, post-logout, back dopo logout
4. `@privacy` — no PII cross-profilo; errori senza leak stack/token
5. `@abuse` — conferma azioni distruttive; idempotenza doppio submit

Infra (pending): TLS, secret scanning, rate limit senza harness → `@security-infra` o untestable.
