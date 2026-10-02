---
name: harness-agentfactory
extends: a-harness
version: 1.1.24
extends-version: 1.7.0
description: >-
  Delta harness per HAL (sorgente canonica skill L0/L1): Platform API
  Makefile, glossario, bounded contexts, bootstrap standard, gate version/shell;
  obbligo Red→Green→Refactor su ogni update agenti/skill (anche da altri progetti).
---

# Harness — HAL (L2)

Skill figlia (L2). Eredita da `a-harness`. All'avvio: L0 → L1 → **questo file**.

**Plugin** = override/path. **Preset** = `standard` (bootstrap 2026-09-09).

HAL è la **sorgente canonica** di skill/agenti, non un'app consumer. Stack = Markdown skill + bash tooling. Gate Make usano tooling reale (`agent-version.sh`, `sync-agents.sh --dry-run`, `bash -n`), non stub npm/pytest.

## Progetto

| Campo | Valore |
|-------|--------|
| Nome | HAL |
| Working directory | `/var/www/HAL/agents` |
| Stack | skills / markdown / bash (meta-repo) |
| Bootstrap profile | **standard** |
| Effort default | thorough |

## Path locali

| Artefatto | Path |
|-----------|------|
| Platform API | `Makefile` (root) |
| Glossario | `docs/glossary.md` |
| Bounded contexts | `docs/bounded-contexts.md` |
| Progress | `.cursor/product/agent-progress.md` |
| Learnings (opz.) | `.cursor/product/session-learnings.md` |
| Contratti RED skill | `.cursor/product/contracts/check-harness-*.sh` |
| Freeze | `.cursor/product/harness-freeze.md` (Makefile, GHA, hooks, RGR rule, AGENT-PROTOCOL) |
| Playbook DUP L2 | `docs/playbook-l2-dup-cut.md` |
| Consumer STALE report | `make sync-consumer-stale` |
| Harness changelog | `docs/harness-CHANGELOG.md` |
| Features | `.cursor/product/features/` (se presenti) |
| Hooks | `.cursor/hooks.json` + `agent-skill-{pretool,edit,stop}-rgr.sh` (deny senza slice; remind; stop+make) |
| CI remota | `.github/workflows/ready-for-review.yml` (`make ready-for-review` su push/PR `main`) |
| Rules | `.cursor/rules/agents-rgr-mandatory.mdc` (+ `tdd-*.mdc`) |
| Agent instructions | `AGENTS.md` (root) |

## Target Makefile

| Target | Comando effettivo | Note |
|--------|-------------------|------|
| `test-unit` | `version-chains` (L0/L1/L2, fail on STALE) + `sync-agents.sh --dry-run` | Gate salute eredità |
| `version-chains` | `agent-version.sh chain` per L0 + ogni L1 + L2 harness | Exit ≠ 0 se STALE |
| `pre-commit` | `check-parity` + `shell-syntax` + `frontmatter-all` + `shellcheck-ok` + `md-links` | Parse bash + frontmatter + lint + link |
| `shell-syntax` | `bash -n` su script in `SHELL_SCRIPTS` (Makefile) | Parse-only (veloce) |
| `frontmatter-all` | `scripts/check-frontmatter-all.sh` | Unico gate frontmatter (L0/L1/L2 + competencies) |
| `shellcheck-ok` | `scripts/check-shellcheck.sh` | Lint error-severity (≠ `bash -n`) |
| `md-links` | `scripts/check-md-links.sh` | Link relativi docs/skill |
| `ready-proof` | `scripts/check-ready-proof.sh` | RGR: ≤4 file / waiver env **o** `- WAIVER_FILES_GT4: 1` in ultima sessione progress; version→CHANGELOG |
| `install-git-hooks` | `scripts/install-git-hooks.sh` | pre-commit → `make pre-commit` |
| `sync-consumer-stale` | `scripts/sync-consumer-stale.sh --dry-run` | Report STALE L2 consumer |
| `check-standards` | alias `pre-commit` | |
| `ready-for-review` | `check-standards` + `test-unit` + `test-int` + `test-e2e` + `ready-proof` | Gate sustainable-pace |
| `test-int` | `@true` | **N/A** — no app/integration suite |
| `test-e2e` | `@true` | **N/A** — no browser/E2E product |
| `db-up` / `seed-data` | `@true` | **N/A** — no DB applicativo |
| `check-parity` / `sync-assets` | `@true` | **N/A** — no dual-canon runtime assets |

## Permission modes (L2)

Vedi L1 `a-harness/references/permission-modes.md`.

| Point | Policy HAL |
|-------|---------------------|
| **On Slice** | **Fail** se manca `Makefile` o acceptance; **fail** se >4 file senza waiver; **fail** se update agenti/skill senza dichiarazione fase RGR |
| **On Red** | **Fail** se si modifica body skill/agente di produzione prima del contratto fallente |
| **On Green** | **Fail** se `make test-unit` / `make pre-commit` ≠ 0; **fail** se GREEN senza RED documentato in progress |
| **On Ready** | **Fail** se `make ready-for-review` ≠ 0 |
| **On Steward** | **Fail** se gate Make rotto, freeze violato, o rules/hooks RGR rimossi senza waiver |

Plan→Act: niente `/green` finché `/slice` ha acceptance e perimetro file accettato. Update agenti/skill = RGR obbligatorio (anche da lavori consumer). Non dichiarare autonomia multi-slice.

## Effort (opz.)

| Task type | Effort |
|-----------|--------|
| Rename / frontmatter bump scoped | fast |
| Nuova competenza / L1 delta | thorough |
| Bootstrap / steward / Makefile | thorough |
| Sync selettivo STALE | thorough (perimetro versioning) |
| Sync-bump L1 (solo version/CHANGELOG) | fast se ≤ pochi agenti; thorough se batch ampio |
| Clear backlog dirty `a-*/` | thorough — coda di slice per BC, non un Act |

## Bounded context attivi

| Context | Path modulo | Note |
|---------|-------------|------|
| Protocol / L0 | `a-agentzero/` | Protocollo, sync, learn, comandi L0 |
| Domain Agents / L1 | `a-*/` (eccetto agentzero) | Skill di dominio + competencies |
| Consumer Delta / L2 | `.cursor/skills/harness-agentfactory/` (+ consumer repos) | Delta progetto; qui = harness del meta-repo |
| Tooling / Sync-Deploy | `deploy-all.sh`, `a-*/deploy.sh`, `a-agentzero/scripts/`, `scripts/` | Deploy dual-runtime, version report |
| Docs / Harness meta | `docs/`, `Makefile`, `.cursor/product/` | Glossario, BC, progress, Platform API |

## Override workflow

### Obbligo Red → Green → Refactor (agenti/skill)

**Fail policy** su ogni modifica ad agenti/skill in questo repo (L0/L1/competenze/L2 in-repo/agents), **anche** se la richiesta nasce da un progetto consumer (promozione L2→L1, fix cross-sito, `/sync <`).

| Fase | Significato in HAL (meta-repo) | Exit |
|------|------------------------------------------|------|
| `/slice` | Acceptance + ≤4 file; append progress | Plan accettato |
| `/red` | Solo contratto verificabile che **fallisce** (check/assert/gate); **niente** body skill produzione | `make test-unit` o check dichiarato ≠ 0 |
| `/green` | Minimo YAGNI su skill/agente + version/CHANGELOG | `make test-unit` + `make pre-commit` = 0 |
| `/refactor` | Pulizia / anti-DUP sotto verdi; no feature nuova | `make test-unit` = 0 |
| `/ready` | Gate sostenibile | `make ready-for-review` = 0 |

**Contratti RED (meta-repo):** preferisci script greppabili in `.cursor/product/contracts/check-harness-*.sh` (exit ≠ 0 in RED, = 0 in GREEN). Non sostituiscono `make test-unit` come gate salute catena; li documentano in progress come check dichiarato. Se un ID/stringa compare anche nel frontmatter (es. `model:`), limita ordine e presenza al **body della sezione** sotto il heading di contratto — non greppare l’intero file o il check fallisce in falso positivo.

**Integrazione fonti esterne → L1:** default = **principi** (mapping + non-adopt espliciti), **enrich** competenze/reference esistenti + pin in `a-harness/SKILL.md`, **nessuna competency nuova**, ≤4 file (L2 `extends-version` pin-only con WAIVER stesso BC). Vietato adottare SaaS/CLI/MCP/offensive come Platform API AF.

Vietato: edit “completo” senza fasi; usare `/sync !` al posto di RGR; patchare L1 da workspace consumer senza progress + gate Make su HAL.

**Clear backlog (dirty tree):** se lo stop-hook segnala N path sotto `a-*/`, non un mega-GREEN. Sequenza di slice per **bounded context** (un L1 / commit, o batch sync-bump dedicato). Waiver >4 file solo **dentro** lo stesso BC. Autonomia multi-slice resta vietata; il backlog si smaltisce come coda di slice, non come un solo Act.

DDD/TDD prodotto app: N/A (nessuna suite app). `/cycle` = slice→R→G→Rf→ready con contratto esplicito.

Enforcement progetto: `AGENTS.md`, `.cursor/rules/agents-rgr-mandatory.mdc`, hooks RGR, questa L2.

## Definition of Done (HAL)

Uno slice su agenti/skill è **Done** solo se:

1. Progress: `slice|accepted` → `red` → `green` → (`refactor` o skip motivato) → `ready|gate`
2. `make ready-for-review` = **0** (include `ready-proof` se ci sono path dirty)
3. `version` bump ⇒ `CHANGELOG` nello stesso slice
4. ≤4 file agent/skill **oppure** `WAIVER_FILES_GT4=1` documentato in progress (un solo BC)
5. Nessun path in `harness-freeze.md` toccato senza `freeze-waiver` steward
6. Intent umano chiaro in ≤2 frasi (anti shadow-code)

## Steward notes

- Profile **standard** + RGR obbligatorio su agenti/skill (2026-09-09).
- **Freeze attivo:** `.cursor/product/harness-freeze.md` — cadenza `/steward` settimanale.
- **Hooks RGR:**
  - `preToolUse` + `failClosed`: **deny** Write/StrReplace su body skill/agenti senza `/slice` aperto in `agent-progress.md` (garanzia dura)
  - `afterFileEdit`: remind non-blocking (non è enforcement; il deny è solo preToolUse)
  - `stop`: se dirty `a-*/` o `.cursor/skills/` → esegue `make ready-for-review` e follow-up (FAIL se gate≠0; se gate=0 ricorda che Make≠tree pulito)
- **CI remota:** GitHub Actions `ready-for-review` (+ shellcheck apt) su push/PR `main`.
- **Git hook locale:** `make install-git-hooks` → `.git/hooks/pre-commit` lancia `make pre-commit`.
- **Qualità Make:** un solo frontmatter (`frontmatter-all`); `shell-syntax` ≠ `shellcheck-ok`; più `md-links` / `ready-proof`.
- **STALE consumer:** `make sync-consumer-stale` (report); apply bump nei repo consumer con RGR — vedi playbook DUP.
- **Ambito `ready-proof`:** osserva solo `a-*/` e `.cursor/skills/` in **questo** repo. Le L2 in un consumer (`/var/www/{repo}/.cursor/skills/`) non sono gate AF: version/CHANGELOG e `make` si verificano **nel** repo target (se assente → check greppabili dichiarati in progress).
- **a-uiux:** L1 per static/a11y/layout; consumer L2 restano delta token/IA.
- **Versioni README:** verità live = `sync-agents.sh --dry-run`.
- **Liste L1:** una sola fonte (`Makefile` `L1_AGENTS` / `sync-agents.sh`); docs e `.cursor/commands/*` puntano a `make version-chains` / `make test-unit` — no `for d in a-…` paralleli. **Dopo** cambio registry L0/PROTOCOL: nello stesso slice (o immediato follow-up) allinea `a-agentzero/agents/a-agentzero.md` (tabella + scaffold + Perimetro) e `a-agentzero/SKILL.md` § Deleghe ai 13 L1; non attribuire PageSpeed/CWV alla riga L1 `a-seozoom` (CWV solo L2). Contratto: `check-harness-agentzero-deleghe-l1.sh`.
- **`docs/harness-CHANGELOG.md`:** `## [Unreleased]` solo delta non rilasciati; storico shippato → sezione Released (non archivio infinito in Unreleased).
- Prossimo passo tipico: `/slice` → `/cycle`; `/steward` settimanale.

Deleghe e slash: eredità L1 (`a-gherkin` / `a-po` / `/steward` / `/learn` / `/sync`).
