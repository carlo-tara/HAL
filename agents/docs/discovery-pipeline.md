# Pipeline discovery — personas → JTBD → Gherkin → harness

Guida all'uso corretto degli agenti `a-personas`, `a-jtbd`, `a-gherkin`, `a-harness` (HAL L1) e della competenza L0 `po-interviewer`.

**Runtime:** Cursor e Claude Code (deploy dual-runtime). Utility ereditate: `/learn`, `/sync`.

Implementazione TDD post-contratto: [`harness-engineering.md`](harness-engineering.md).

**Upstream product:** prima della pipeline personas→JTBD, `a-product` (o facade `a-b2b`) filtra richieste **feature-only** (anti–Build Trap: Outcome vs Output) e può handoff a `a-po` `/triage`. Product Kata light = Direction → Obstacles → Experiment (routing, non authoring).

---

## Sequenza (pipeline)

```
PRD + mockup
    → a-personas  →  personas.md
    → a-jtbd      →  jtbd.md  (job stories, unmet needs, scenario seeds)
    → a-gherkin   →  features/*.feature
    → a-harness   →  codice (ciclo TDD Red/Green/Refactor)
    → umano       →  revisione design (solo post make ready-for-review)
```

Non saltare gli step: ogni L1 **ferma** se manca l'artefatto upstream.

| Step | Agente | Legge | Scrive |
|------|--------|-------|--------|
| 1 | `a-personas` | `prd.md`, `mockup/` | `personas.md` |
| 2 | `a-jtbd` | `personas.md` | `jtbd.md` |
| 3 | `a-gherkin` | `jtbd.md`, `personas.md` | `features/*.feature` |
| 4 | `a-harness` | `.feature`, `docs/glossary.md`, `Makefile` | codice + test (tiny slices) |

Path product (ordine di lookup): `.cursor/product/` → `.claude/product/` → `product/`.

---

## Ruoli

| Agente | Ruolo | Focus |
|--------|-------|-------|
| `a-personas` | User Researcher | Archetipi + **journey coherence** (no layout/CSS) |
| `a-jtbd` | Job Analyst / JTBD | Job-first, ODI unmet, seeds BDD |
| `a-gherkin` | QA Lead / BDD Spec | Suite `.feature`, expand/secure/perf |
| `a-harness` | Meta-Harness / TDD | Implementazione post-contratto, gate Makefile |

### Path paralleli (non sostituiscono la pipeline)

| Agente | Quando | Non-goal |
|--------|--------|----------|
| `a-po` | Authoring prodotto/GTM (intake, canvas, PRD, offer, prioritize) | Non scrive `.feature` né codice |
| `a-product` | Orchestra product multi-step (delega specialisti; § Profilo B2B per piloti) | Non authora PRD; non esegue enrichment/BDD |
| `a-b2b` | Facade ingresso B2B → a-product § Profilo B2B (delega a-po / personas / jtbd / enrichment) | Non authora package/PRD; non esegue enrichment |
| `a-uiux` | Page shell statica (stack M3, a11y, layout editoriale) | Non encoding grafici (`a-charts`) né microcopy (`a-copywriter`) |

---

## Quickstart

### 0. Deploy

```bash
cd /var/www/HAL/agents
bash deploy-all.sh
# oppure
bash a-agentzero/scripts/sync-agents.sh
```

Symlink in `~/.cursor/skills|agents` e `~/.claude/skills|agents`.

### 1. Personas

```
@a-personas
/create
```

Conferma PO → scrive `personas.md`.

Target mancante in seguito:

```
/add Descrizione in linguaggio naturale della persona non ancora mappata
```

### 2. JTBD

```
@a-jtbd
/create
```

Include discovery unmet. Estensioni NL:

```
/add-story …
/add-need …
```

### 3. Gherkin

```
@a-gherkin
/create
```

Poi, se serve:

```
/expand
/secure
/perf
/add-scenario Descrizione scenario BDD non ancora mappato
```

### 4. Implementazione (a-harness)

```
@a-harness
/cycle
```

Prompt handoff da Gherkin: [`a-product/gherkin/references/handoff-to-dev.md`](../a-product/gherkin/references/handoff-to-dev.md) (delega a `@a-harness /cycle`).

Prerequisito harness nel repo target: `Makefile`, `docs/glossary.md` — vedi [`a-harness/references/harness-scaffold.md`](../a-harness/references/harness-scaffold.md) o `/bootstrap`.

L'umano interviene solo dopo `make ready-for-review` verde (design alto livello).

---

## Modifiche successive (non rifare sempre /create)

Su PRD / mockup / UI code change: parti da **`/triage`** sul layer toccato.

Cascade (segnalazione, non rewrite silenzioso):

```
a-personas /triage → … → escalate a-jtbd /triage
a-jtbd /triage     → … → escalate a-gherkin /triage
a-gherkin /triage  → … → escalate upstream se manca jtbd/personas
a-harness          → … → escalate a-gherkin se manca .feature; a-po se manca slice/US
```

---

## Slash di dominio (sintesi)

### a-personas

`/triage` `/create` `/add` `/check` `/update` `/show` `/gap` `/export`

### a-jtbd

`/triage` `/create` `/map` `/unmet` `/add-story` `/add-need` `/refine` `/prioritize` `/check` `/gap` `/show` `/export`

### a-gherkin

`/triage` `/create` `/build` `/add-scenario` `/expand` `/secure` `/perf` `/validate` `/refine` `/lint` `/gap` `/show` `/export`

### a-harness

`/slice` `/red` `/green` `/refactor` `/cycle` `/ready` `/progress` `/steward` `/bootstrap`

### L0 (tutti)

`/learn ?` · `/learn !` (skill/brand; se necessario `./ToDo.md` / docs) · `/sync ?` · `/sync !` · `/sync <` (generalizzazione L2, solo report)

---

## Regole d'oro

1. **PO conferma** prima di export (po-interviewer)
2. **Hypothesis** ≠ attivo
3. Job **solution-agnostic**; UI = binding
4. Scenari Gherkin **indipendenti**; journey con `@journey`, non ordine di run
5. `/secure` e `/perf` = comportamento osservabile, niente SLA inventati
6. Dual-runtime: stessi agenti in Cursor e Claude

---

## Checklist compatibilità Claude

- [ ] Skill in `~/.claude/skills/a-personas|a-jtbd|a-gherkin|a-harness`
- [ ] Agents in `~/.claude/agents/` (incluso `a-harness.md`)
- [ ] `/learn` e `/sync` in `~/.claude/skills/` (HAL L0; opzionale nel pack stand-alone)
- [ ] Discovery trova `.cursor/product` o `.claude/product`
- [ ] (a-harness) `Makefile` e `docs/glossary.md` nel repo target
- [ ] Bootstrap: SKILL L1 autosufficiente; personas/jtbd/gherkin includono `po-interviewer` venduto
- [ ] Nessun tool solo-Cursor obbligatorio nel happy path

---

## Export pack Claude

```bash
bash scripts/export-discovery-claude.sh [outdir]
```

Produce `claude-discovery-agents-*.zip` con `.claude/skills/{a-personas,a-jtbd,a-gherkin,a-harness}` autosufficienti (`po-interviewer` venduto in personas/jtbd/gherkin; `a-harness` include competenze TDD/DDD locali).

---

## Link

- [a-product/personas/SKILL.md](../a-product/personas/SKILL.md)
- [a-product/jtbd/SKILL.md](../a-product/jtbd/SKILL.md)
- [a-product/gherkin/SKILL.md](../a-product/gherkin/SKILL.md)
- [a-harness/SKILL.md](../a-harness/SKILL.md)
- [harness-engineering.md](harness-engineering.md)
- [po-interviewer](../a-agentzero/competencies/po-interviewer/SKILL.md)
- [AGENT-PROTOCOL.md](../a-agentzero/AGENT-PROTOCOL.md)
