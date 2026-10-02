# Makefile template — Platform API (MVH)

Copia/adatta in root del progetto target. Lo **Steward** è l'unico ruolo che modifica questi target in routine.

```makefile
.PHONY: test-unit test-int test-e2e pre-commit check-standards ready-for-review db-up seed-data check-parity sync-assets

# --- Adapter: sostituire con comandi reali dello stack ---

test-unit:
	@echo "Run unit tests"
	# es. npm test -- --testPathPattern=unit
	# es. pytest tests/unit
	@exit 1

test-int:
	@echo "Run integration tests (skip if N/A — document in L2)"
	# es. npm run test:integration
	@true

test-e2e:
	@echo "Run E2E tests (skip if N/A — document in L2)"
	# es. npm run test:e2e
	@true

# Opz. dual-canon: confronta canone editabile vs copia runtime (fail su drift)
check-parity:
	@echo "Parity check (skip if N/A — document in L2)"
	# es. node scripts/check-dashboard-parity.js
	@true

# Opz. dual-canon: copia canone → runtime (idempotente)
sync-assets:
	@echo "Sync assets canone → runtime (skip if N/A)"
	# es. cp -a static/. data/ && cp templates/... data/
	@true

pre-commit: check-parity
	@echo "Lint, format, typecheck"
	# es. npm run lint:strict && npm run typecheck && npm run format:check
	@exit 1

check-standards: pre-commit

ready-for-review: check-standards test-unit test-int test-e2e
	@echo "======================================================"
	@echo "Gate OK — nessun errore meccanico."
	@echo "Pace sostenibile: umano può revisionare design alto livello."
	@echo "======================================================"

db-up:
	@echo "Start ephemeral DB (optional)"
	# es. docker compose -f docker-compose.test.yml up -d db
	@true

seed-data:
	@echo "Seed test data (optional)"
	# es. npm run db:seed:test
	@true
```

## Note implementazione

- Target devono essere **idempotenti** dove possibile
- Se `test-int` / `test-e2e` non applicabili: `@true` + documentazione esplicita in L2 (non silenzioso)
- Se dual-canon **non** applicabile: lascia `check-parity` / `sync-assets` come `@true` o rimuovili e documenta in L2
- Flag env: helper tipo `envFlagEnabled` — mai `Boolean(process.env…)` (vedi competenza `platform-api`)
- `ready-for-review` è il gate **sustainable-pace** — non rimuovere senora motivo documentato
