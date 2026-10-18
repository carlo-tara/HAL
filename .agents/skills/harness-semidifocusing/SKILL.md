---
name: harness-semidifocusing
extends: a-harness
version: 2.1.0
extends-version: 1.7.3
description: >-
  Delta harness per semidifocusing: Makefile Platform API (pnpm monorepo, Vitest,
  Playwright, partner-smoke), glossario, bounded contexts, workflow stg-carlo,
  PeerPartnering e Notifications dual-mode.
---

# Harness — semidifocusing

Skill figlia (L2). Eredita da `a-harness`. All'avvio: L0 → L1 → **questo file**.

**Preset bootstrap:** `standard` (2026-09-12).

## Progetto

| Campo             | Valore                                                                                                      |
| ----------------- | ----------------------------------------------------------------------------------------------------------- |
| Nome              | semidifocusing                                                                                              |
| Working directory | `/var/www/semidifocusing`                                                                                   |
| Stack             | TypeScript · React 18 / Vite PWA (`apps/web`) · Hono + Drizzle/SQLite (`apps/api`) · pnpm monorepo · Docker |
| Bootstrap profile | standard                                                                                                    |
| Effort default    | fast per bug/smoke; thorough per feature/BC slice                                                           |

## Path locali

| Artefatto         | Path                                        |
| ----------------- | ------------------------------------------- |
| Platform API      | `Makefile` (root)                           |
| Glossario         | `docs/glossary.md`                          |
| Bounded contexts  | `docs/bounded-contexts.md`                  |
| Progress          | `product/agent-progress.md`                 |
| Learnings         | `product/session-learnings.md`              |
| Freeze            | `product/harness-freeze.md`                 |
| Harness changelog | `docs/harness-CHANGELOG.md`                 |
| Features          | `product/features/`                         |
| Smoke tests       | `apps/api/scripts/qa-*.ts`, `apps/web/e2e/` |

## Target Makefile (gate harness)

| Target                         | Comando effettivo                                                                      |
| ------------------------------ | -------------------------------------------------------------------------------------- |
| `test-unit`                    | `pnpm test` (Vitest unit su `apps/api`)                                                |
| `test-int`                     | `pnpm --filter api run qa:partner-smoke` (smoke integration PeerPartnering su DB test) |
| `test-e2e`                     | `pnpm --filter web exec playwright test` (Playwright smoke su `/installa`)             |
| `pre-commit`                   | `pnpm typecheck` (tsc noEmit su tutti i workspace)                                     |
| `check-standards`              | alias `pre-commit`                                                                     |
| `ready-for-review`             | `check-standards test-unit test-int test-e2e`                                          |
| `check-parity` / `sync-assets` | `@true` (no dual-canon assets)                                                         |
| `db-up`                        | `@true` (SQLite file-backed)                                                           |
| `seed-data`                    | `@true` (script dedicati in `apps/api/scripts/`)                                       |

## Bounded context attivi

Vedi mappa dettagliata in `docs/bounded-contexts.md`.

| Context         | Path modulo                                                                                     | Note                                                     |
| --------------- | ----------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| Identity        | `apps/api/src/identity.ts`, `magicLink.ts`, `loginRateLimit.ts`; `apps/web/src/lib/identity.ts` | Magic link, sessioni, rate limit login                   |
| EventsBooking   | `apps/api/src/store.ts`, `bookingActions.ts`, `eventTiming.ts`                                  | Event CRUD, capacity, waitlist FIFO, reminder trigger    |
| PeerPartnering  | `apps/api/src/partner*.ts`; `apps/web/src/pages/Partner*.tsx`, `lib/partner*.ts`                | Availability, match bilaterale, chat polling, follow-up  |
| Admin           | `apps/api/src/admin.ts`, `uploads.ts`; `apps/web/src/pages/Admin*.tsx`                          | Gestione eventi, persone, gruppi, upload immagini        |
| Notifications   | `apps/api/src/email.ts`, `reminderJob.ts`, `partnerJob.ts`, `ics.ts`                            | Email dual-mode (SMTP→Brevo), reminder cron, ICS         |
| PracticeJournal | `apps/web/src/lib/journalDb.ts`, `pages/Journal*.tsx`                                           | Diario Focusing: Felt Sense, Handle, Shift, Dexie locale |
| SharedKernel    | `packages/types`                                                                                | Zod schema condivisi — nessuna logica di dominio         |
| WebShell        | `apps/web/`                                                                                     | PWA client, routing, cache offline, proxy `/api` DEV     |

## PeerPartnering — Invarianti di dominio

Documentate da sessione (`product/features/partner-focusing.md` e `product/session-learnings.md`):

1. **Match multipli:** una persona può avere più Match aperti in parallelo.
2. **Scadenza automatica:** un Match in attesa scade all'inizio dello slot di Availability (`expiresAt` = slot start Europe/Rome).
3. **Nessun rifiuto esplicito:** non esiste azione "Reject"; la proposta si lascia scadere.
4. **Canali senza campi link nel form:** preferenze canale (zoom, whatsapp, meet, jitsi) senza URL nel form; lo scambio link avviene solo in chat dopo accettazione bilaterale.
5. **Note private:** solo sul client (Dexie IndexedDB), indicizzate per `partnerPersonId`, riproposte al rematch.
6. **UX accessibile:** scelte ampie, 3 tab chiare, microcopy italiano semplice per utenti con bassa digital literacy.

## Notifications — Dual-mode email

1. Modalità supportate: SMTP (locale/staging/test) e Brevo API (produzione/staging configurato).
2. Transizione controllata via variabili d'ambiente (`BREVO_API_KEY` vs `SMTP_*`).
3. Dettagli operativi in `docs/BREVO_SETUP.md`.

## PracticeJournal — Invarianti di dominio

Documentate da sessione (`docs/FOCUS_JOURNALING.md`):

1. **Privacy-by-Design:** le note interiori risiedono unicamente nel client su IndexedDB Dexie (`sdf_journal`).
2. **Struttura metodologica:** cattura i tre elementi chiave del Focusing (Felt Sense corporeo, Handle/Simbolo, Felt Shift) oltre al testo libero.
3. **Piena operatività offline:** fruibile al 100% senza connessione (aereo, ritiri residenziali).
4. **GDPR ed esportazione autonoma:** export completo in formato Markdown o JSON con un clic; cancellazione sicura locale.
5. **Accoppiamento debole:** i riferimenti a incontri partner o eventi sono opzionali e memorizzati unicamente tramite ID senza dipendenze dallo store remoto.

## Override workflow (stg-carlo)

1. **Ramo di lavoro:** Carlo sviluppa e committa unicamente sul branch **`stg-carlo`**.
2. **Nessun merge autonomo su `main`:** non aprire PR e non integrare direttamente su `main`. L'integrazione su `main` è effettuata unicamente dal maintainer (Francesco).
3. **Budget slice:** $\le 4$ file per slice prodotto o WAIVER motivato; gate `make ready-for-review` prima di dichiarare ready.
4. **Sviluppo locale:** `make local` (Docker host network frontend :8080 + API :8787) oppure `make dev` (Vite DEV su :5173 con proxy `/api` verso :8787).
5. **Simulazione PWA vs device reali:** Chrome DevTools non emette `beforeinstallprompt` affidabile; la verifica finale richiede device fisici reali (`docs/INSTALLA_APP.md`).
