# HAL Agent Platform API — gates for the canonical skills/markdown/bash library
# Steward owns this file. No product app stack (npm/pytest) — gates use real tooling.

SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c

.PHONY: test-unit test-int test-e2e pre-commit check-standards ready-for-review \
	db-up seed-data check-parity sync-assets shell-syntax version-chains \
	frontmatter-all shellcheck-ok md-links ready-proof tools-shellcheck install-git-hooks \
	sync-consumer-stale

ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
VERSION_SH := $(ROOT)/a-agentzero/scripts/agent-version.sh
SYNC_SH := $(ROOT)/a-agentzero/scripts/sync-agents.sh

L1_AGENTS := a-b2b a-copywriter a-design a-harness a-product a-seozoom a-wordpress

SHELL_SCRIPTS := \
	$(ROOT)/deploy-all.sh \
	$(ROOT)/a-agentzero/scripts/agent-version.sh \
	$(ROOT)/a-agentzero/scripts/sync-agents.sh \
	$(ROOT)/scripts/export-a-harness-claude.sh \
	$(ROOT)/scripts/export-discovery-claude.sh \
	$(ROOT)/scripts/check-frontmatter-all.sh \
	$(ROOT)/scripts/check-md-links.sh \
	$(ROOT)/scripts/check-editor-links.sh \
	$(ROOT)/scripts/link-workspace-skills.sh \
	$(ROOT)/scripts/check-shellcheck.sh \
	$(ROOT)/scripts/check-ready-proof.sh \
	$(ROOT)/scripts/install-git-hooks.sh \
	$(ROOT)/scripts/sync-consumer-stale.sh \
	$(ROOT)/.cursor/hooks/agent-skill-edit-rgr.sh \
	$(ROOT)/.cursor/hooks/agent-skill-stop-gate.sh \
	$(ROOT)/.cursor/hooks/agent-skill-pretool-rgr.sh \
	$(ROOT)/a-design/deploy.sh

L2_HARNESS := $(ROOT)/project-skills/harness-agentfactory/SKILL.md

# --- Real gates for this meta-repo ---

test-unit: version-chains
	@echo ">>> sync-agents --dry-run (report L1 ← L0 + L0 commands)"
	@bash "$(SYNC_SH)" --dry-run
	@echo "test-unit OK"

version-chains:
	@echo ">>> Version chains (fail on STALE)"
	@stale=0; \
	out="$$(bash "$(VERSION_SH)" chain "$(ROOT)/a-agentzero/SKILL.md" 2>&1)"; \
	echo "$$out"; \
	if echo "$$out" | grep -q "STALE"; then stale=1; fi; \
	for agent in $(L1_AGENTS); do \
		skill="$(ROOT)/$${agent}/SKILL.md"; \
		if [[ ! -f "$$skill" ]]; then echo "Missing $$skill" >&2; exit 1; fi; \
		out="$$(bash "$(VERSION_SH)" chain "$$skill" 2>&1)"; \
		echo; echo "--- $${agent} ---"; echo "$$out"; \
		if echo "$$out" | grep -q "STALE"; then stale=1; fi; \
	done; \
	if [[ -f "$(L2_HARNESS)" ]]; then \
		out="$$(bash "$(VERSION_SH)" chain "$(L2_HARNESS)" 2>&1)"; \
		echo; echo "--- L2 harness-agentfactory ---"; echo "$$out"; \
		if echo "$$out" | grep -q "STALE"; then stale=1; fi; \
	fi; \
	if [[ "$$stale" -ne 0 ]]; then \
		echo "FAIL: one or more version chains are STALE" >&2; \
		exit 1; \
	fi; \
	echo "version-chains OK (no STALE)"

test-int:
	@echo "test-int N/A (agent library, no application integration suite) — documented in L2"
	@true

test-e2e:
	@echo "test-e2e N/A (agent library, no application E2E suite) — documented in L2"
	@true

check-parity:
	@bash "$(ROOT)/scripts/check-editor-links.sh"

sync-assets:
	@echo "sync-assets N/A — documented in L2"
	@true

# Quality pack: bash -n (parse) + frontmatter-all + shellcheck (lint) + md links
pre-commit: check-parity shell-syntax frontmatter-all shellcheck-ok md-links
	@echo "pre-commit OK"

shell-syntax:
	@echo ">>> bash -n on key shell scripts"
	@for f in $(SHELL_SCRIPTS); do \
		[[ -f "$$f" ]] || continue; \
		echo "  bash -n $$f"; \
		bash -n "$$f" || exit 1; \
	done
	@echo "shell-syntax OK"

frontmatter-all:
	@bash "$(ROOT)/scripts/check-frontmatter-all.sh"

shellcheck-ok:
	@bash "$(ROOT)/scripts/check-shellcheck.sh"

md-links:
	@bash "$(ROOT)/scripts/check-md-links.sh"

ready-proof:
	@bash "$(ROOT)/scripts/check-ready-proof.sh"

tools-shellcheck:
	@mkdir -p "$(ROOT)/.tools"
	@curl -fsSL -o /tmp/shellcheck.tar.xz \
	  https://github.com/koalaman/shellcheck/releases/download/v0.10.0/shellcheck-v0.10.0.linux.x86_64.tar.xz
	@tar -xJf /tmp/shellcheck.tar.xz -C /tmp
	@cp /tmp/shellcheck-v0.10.0/shellcheck "$(ROOT)/.tools/shellcheck"
	@chmod +x "$(ROOT)/.tools/shellcheck"
	@"$(ROOT)/.tools/shellcheck" --version | head -2

install-git-hooks:
	@bash "$(ROOT)/scripts/install-git-hooks.sh"

sync-consumer-stale:
	@bash "$(ROOT)/scripts/sync-consumer-stale.sh" --dry-run

check-standards: pre-commit

# ready-proof runs after standards+tests; waiver BC packages with WAIVER_FILES_GT4=1
ready-for-review: check-standards test-unit test-int test-e2e ready-proof
	@echo "======================================================"
	@echo "Gate OK — nessun errore meccanico."
	@echo "Pace sostenibile: umano può revisionare design alto livello."
	@echo "======================================================"

db-up:
	@echo "db-up N/A (no application database) — documented in L2"
	@true

seed-data:
	@echo "seed-data N/A — documented in L2"
	@true
