# HAL Gateway — Platform API (a-harness, /bootstrap profile standard — 2026-10-25)
# Steward owns this file. I gate locali rispecchiano fedelmente
# .github/workflows/ready-for-review.yml (CI-first). Quiet test default (L1 platform-api §8).
# NB: il bundle agenti in agents/ ha una Platform API separata (agents/Makefile).
# L2: agents/project-skills/harness-hal/SKILL.md (symlink .agents/skills/harness-hal).

SHELL := /bin/bash
PYTHON := python3
QUIET ?= 1
LOG_DIR := logs

.PHONY: help test-unit test-int test-e2e check-secrets check-deps check-sast \
	pre-commit check-standards ready-for-review check-parity sync-assets db-up seed-data

help: ## Mostra i target della Platform API
	@awk '/^[a-zA-Z0-9_.-]+:.*## / {split($$0,a,"## "); printf "  make %-18s %s\n", substr(a[1],1,length(a[1])-1), a[2]}' $(MAKEFILE_LIST)

# --- DevSecOps baseline (CI-first security: secrets + deps + SAST, low-noise) ---

check-secrets: ## Secret scanner (scripts/check_secrets.py)
	$(PYTHON) scripts/check_secrets.py

check-deps: ## Dependency audit (scripts/check_deps.py)
	$(PYTHON) scripts/check_deps.py

check-sast: ## SAST low-noise (scripts/check_sast.py)
	$(PYTHON) scripts/check_sast.py

# --- Test tier (unittest discover = insieme CI ready-for-review.yml) ---

test-unit: ## Suite unitaria (QUIET=1 default: 1 riga GREEN, RED selettivo; log settimanale in logs/)
	@mkdir -p $(LOG_DIR)
	@log="$(LOG_DIR)/test-$$(date +%G-W%V).log"; \
	out="$$($(PYTHON) -m unittest discover -s tests 2>&1)"; rc=$$?; \
	printf '%s\n\n' "$$out" >> "$$log"; \
	if [ $$rc -eq 0 ]; then \
		if [ "$(QUIET)" = "1" ]; then \
			printf '%s\n' "$$out" | grep -E '^(Ran [0-9]+ tests|OK)' || true; \
			echo "full GREEN (log: $$log)"; \
		else \
			printf '%s\n' "$$out"; \
		fi; \
	else \
		printf '%s\n' "$$out" | grep -E -B1 -A15 '^(FAIL|ERROR): ' | head -120 || true; \
		printf '%s\n' "$$out" | grep -E '^(Ran [0-9]+ tests|FAILED|OK)' || true; \
		echo "RED (log completo: $$log)"; \
	fi; \
	exit $$rc

test-int: ## N/A su host: CI non separa un tier di integrazione (documentato in L2)
	@echo "test-int: skip — nessun tier separato in CI (vedi L2 harness-hal)"
	@true

test-e2e: ## N/A: nessun test browser/E2E (throttle 1h + mutex PID non applicabili — vedi L2)
	@echo "test-e2e: N/A — nessuna suite E2E (vedi L2 harness-hal)"
	@true

# --- Dual-canon / ambiente ---

check-parity: ## N/A: il bundle agents/ è governato dal proprio gate (agents/Makefile) — documentato in L2
	@true

sync-assets: ## N/A: nessun artefatto canone→runtime nel gateway (documentato in L2)
	@true

db-up: ## N/A: nessun DB effimero in CI; sqlite locale (system2_metrics) auto-gestito
	@echo "db-up: N/A — nessuna risorsa effimera (documentato in L2)"
	@true

seed-data: ## N/A — vedi L2 harness-hal
	@echo "seed-data: N/A (documentato in L2)"
	@true

# --- Gate ---

pre-commit: check-secrets check-deps check-sast ## DevSecOps (CI-first) + syntax gate (compileall)
	$(PYTHON) -m compileall -q *.py scripts

check-standards: pre-commit ## Alias pre-commit

ready-for-review: pre-commit test-unit test-int test-e2e ## Gate sustainable-pace (parity con il workflow CI omonimo)
	@echo "======================================================"
	@echo "Gate OK — nessun errore meccanico."
	@echo "Pace sostenibile: umano può revisionare design alto livello."
	@echo "======================================================"
