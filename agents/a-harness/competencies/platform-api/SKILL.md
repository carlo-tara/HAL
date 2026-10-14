---
name: platform-api
kind: competency
version: 1.2.0
description: >-
  Makefile come Platform API: solo target documentati; CI-first; quiet test default;
  throttling/mutex per E2E; bootstrap profiles minimal|standard; consumer hygiene opzionale.
---

# Competenza L1 — platform-api

Il **Makefile** (o equivalente documentato in L2) è la Platform API: distributore automatico di ambienti puliti.

## Regole (sempre attive)

1. **Non inventare** script setup ad hoc (bash one-off, npm script non documentati)
2. Usa **solo** target elencati in `Makefile` o tabella L2 `harness-*`
3. Se target mancante → `/bootstrap` o `/steward` (non workaround silenzioso)
4. Preferire target Make che **batchano** verify invece di 20 invocazioni ad hoc
5. Credenziali/API esterne → MCP L2 o CLI documentata; non curl-in-skill
6. **Flag env booleani:** non usare `Boolean(process.env.FOO)` — stringhe `"0"` / `"false"` / `"off"` (case-insensitive) restano truthy in JS. Helper tipico: truthy solo se valorizzato e non in quel set (es. `envFlagEnabled`). Nomi prefisso e path lib → L2
7. **Dual-canon asset (se applicabile):** se il runtime preferisce una copia generata (`data/`, `dist/`, …) rispetto al canone editabile (`static/`, `src/`, `templates/`, …), documenta in L2: (a) path canone vs path runtime, (b) target `sync-assets` (o nome locale), (c) gate `check-parity` in `pre-commit` / `ready-for-review`. Drift canone≠runtime = fail
8. **Test runner Quiet mode:** i target di test della Platform API (`test-unit`, `test-int`, `test-quiet`) devono supportare o adottare la modalità quiet per default (`QUIET=1`, `--quiet`), evitando lo streaming verboso nel context window dell'agente.
9. **Throttling e Mutex per test E2E / Browser (`test-e2e`):**
   - **Rate limit orario:** i test browser/BDD pesanti sono differiti se eseguiti entro 60 minuti da un esito verde (`DEFERRED: ran X mins ago (< 1h)`), a meno di override esplicito (`FORCE=1` o `--force`).
   - **Concurrency guard (Mutex):** lockfile basato su PID (`logs/.test-e2e.lock`) per evitare collisioni quando più pipeline o sotto-agenti girano simultaneamente (`SKIP / CONCURRENT`).

## Target minimi attesi

| Target             | Ruolo                                                                   |
| ------------------ | ----------------------------------------------------------------------- |
| `test-unit`        | Test unitari slice                                                      |
| `test-int`         | Integration (opz. skip in L2 se N/A)                                    |
| `test-e2e`         | E2E (concurrency guard + hourly throttle 1h; opz. skip in L2 se N/A)    |
| `test-quiet`       | Opz. — esecuzione quiet della suite unit/int per preservare il contesto |
| `pre-commit`       | Lint + format + typecheck (+ `check-parity` se dual-canon)              |
| `check-standards`  | Alias o wrapper pre-commit                                              |
| `ready-for-review` | Gate finale sustainable-pace                                            |
| `db-up`            | Ambiente DB effimero (se applicabile)                                   |
| `seed-data`        | Seed dati test (se applicabile)                                         |
| `check-parity`     | Opz. — verify canone ↔ runtime asset (dual-canon)                       |
| `sync-assets`      | Opz. — copia canone → runtime (nome locale ok, es. `sync-dashboard`)    |

### Target opzionali (consumer hygiene)

Documentati in [consumer-platform-hygiene.md](../../references/consumer-platform-hygiene.md). Nomi locali in L2:

| Target (es.)                 | Ruolo                                                                     |
| ---------------------------- | ------------------------------------------------------------------------- |
| `check-cursor-whitelist`     | Path versionati sotto `.cursor/` non gitignored                           |
| `check-harness-commit-scope` | No commit misti Platform API + WIP prodotto (denylist L2)                 |
| `test-coverage`              | Coverage su suite unit **piena** (audit; spesso fuori `ready-for-review`) |
| `check-dead-code`            | Scan euristico unreferenced / orphan tests (non proof)                    |

Template: [makefile-template.mk](../../references/makefile-template.mk)

## `/bootstrap`

Profiles: [bootstrap-profiles.md](../../references/bootstrap-profiles.md)

1. Scegli **minimal** | **standard**
2. Copia/adatta Makefile; senza `make test` reale non dichiarare autonomia
3. Documenta comandi stack in L2
4. Verifica `make ready-for-review` raggiungibile
5. (standard) glossary + bounded-contexts + progress template
6. (opz. steward) consumer hygiene + hooks leggeri — vedi [consumer-platform-hygiene.md](../../references/consumer-platform-hygiene.md)

Solo **steward** (o `/bootstrap` guidato) modifica la Platform API in produzione.

## Policy

Vedi [permission-modes.md](../../references/permission-modes.md) § Policy — On Slice fallisce se Makefile assente.

## Anti-pattern

- `curl | bash` setup inventato in chat
- Modificare package.json scripts senza aggiornare Makefile
- Target Makefile non idempotenti senza documentazione
- Scalare agent autonomy con stub eterni al posto di test
- Coverage subset presentata come verità completa
