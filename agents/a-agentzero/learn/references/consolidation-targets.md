# Target di consolidamento /learn

Mappa operativa per `/learn !`: dove persistere ogni tipo di apprendimento nel repo corrente.

**Principio:** preferisci sempre il livello più specifico (L2 + file dati) rispetto a L1/L0 globali.

**Promozione verso L1/L0:** solo se (a) pattern validato su **≥2 progetti consumer**, e (b) l'utente chiede esplicitamente regola cross-repo oppure `/learn !` con target L1 indicato. Altrimenti resta in L2.  
**Scansione strutturata L2:** `/sync <` (vedi [l2-generalization.md](../../sync/references/l2-generalization.md)) — report candidati; non scrive.

**Anti-grasso L2:** non consolidare nel figlio ciò che è già nel padre L0/L1 — usa puntatore. Se trovi duplicazione, taglia il L2 invece di arricchirlo.

**Ambito changelog (`/learn !`):** ogni voce consolidata va in `### Progetto` o `### HAL` in `.cursor/product/session-learnings.md`. Progetto = L2/brand/rules/CONTRIBUTING/`./ToDo.md`/`docs/` del consumer; HAL = `a-*/`, protocollo L0, harness meta-repo, ToDo/docs AF.

**Routing:** preferenza permanente → skill/brand/rules; residuo actionable → `./ToDo.md` (**se necessario**); spiegazione/UL/BC/howto → `docs/` o README (**se necessario**). Vedi tabella Destinazione in `learn/SKILL.md`.

---

## Per tipo di apprendimento

| Tipo | Target primario | Sezione tipica | Note |
|------|-----------------|----------------|------|
| Lessico / tono / inclusività | `.cursor/brands/{brand}.md` | tabella Usa / Evita | No duplicare in SKILL se già in brand |
| Registri / struttura / writing-rules (voice pesante) | `.cursor/skills/{slug}-voice/` o `*-tone-of-voice` | registri, checklist | Solo se brand non basta; vedi L0 tono-di-voce |
| Regole copy / formato brevi | `.cursor/skills/{dominio}-{progetto}/` o writing-rules | checklist o tabella | Delta, non corpus |
| Workflow dominio | `.cursor/skills/{dominio}-{progetto}/SKILL.md` | § Workflow, § Invariants | Solo delta progetto |
| Template articoli / schema | `.cursor/skills/copywriter-{progetto}/template-*.md` o schema JSON | regole tabella | Se specifico del progetto |
| SEO / meta / FAQ | `.cursor/skills/seozoom-{progetto}/` (o sibling `role: editorial`) | checklist GEO | No metriche inventate; no restatement L1 |
| Illustrazioni / asset | `.cursor/illustration-styles/{nome}.md` + skill L2 | path, QA, stile | Credenziali restano in `.env` |
| Vincolo always-on su path | `.cursor/rules/{nome}.mdc` | body + `globs` | Usa solo se la regola è automatica |
| Checklist repo-wide | `.cursorrules` o `CONTRIBUTING.md` | checklist pre-consegna | Non duplicare skill |
| Script / path hardcoded | `scripts/` + doc in SKILL L2 | Invariants | Non refactorare script non correlati |
| Pattern cross-progetto (≥2 siti) | L1 o L0 pertinenti | competenza / protocollo | Solo su richiesta esplicita |
| Residuo / follow-up / techdebt / bug aperto | `./ToDo.md` | Attività P0\|P1\|P2 + `#tag` | Solo se necessario; formato Mappa residui; igiene → `/todo` |
| Glossario / sinonimi (UL) | `docs/glossary.md` | voce termine | Doc locale; non skill se è solo naming |
| Confini / owner path (BC) | `docs/bounded-contexts.md` | riga contesto | Doc locale |
| Howto / operativo repo | `docs/operativo.md`, `README.md`, `.cursor/product/README.md` | sezione pertinente | Solo gap reale; no chat dump |

---

## Repo HAL (questo progetto)

| Tipo | Target |
|------|--------|
| Brand / tono HAL | `.cursor/brands/agentfactory.md` |
| Comandi Cursor L0 (baseline) | `a-agentzero/commands/*.md` (pubblicati da `/sync !`) |
| Comandi Cursor override AF | `.cursor/commands/*.md` |
| Protocollo agenti | `a-agentzero/AGENT-PROTOCOL.md`, `SKILL.md` |
| Skill L1 dominio | `a-{dominio}/SKILL.md` + `CHANGELOG.md` |
| Piani decisionali | `.cursor/plans/` |
| Residui actionable | `./ToDo.md` |
| Glossario / BC / operativo | `docs/glossary.md`, `docs/bounded-contexts.md`, `docs/operativo.md` |

Non consolidare in HAL regole specifiche di siti consumer: vanno nelle skill L2 / ToDo / docs dei rispettivi repository.

---

## Progetti consumer (pattern generico)

Per ogni sito/blog/WP con skill L2:

| Tipo | Target tipico |
|------|----------------|
| Tono / brand | `.cursor/brands/{slug}.md` |
| Override slash command | `.cursor/commands/{nome}.md` (solo se diverso da L0 user) |
| Skill dominio | `.cursor/skills/{dominio}-{slug}/SKILL.md` |
| Brief WordPress | `.cursor/wordpress/{slug}.md` |
| Manifest SEO | `seo/export-manifest.json` |
| Preferenze intervista PO / formato personas | L2 `personas-*` o `.cursor/product/README.md` |
| Convenzioni schema `personas.md` / campi extra | L2; template L1 solo se globali |
| Job map / unmet heuristics di progetto | L2 `jtbd-*` o meta accettata in `jtbd.md` (non fiction) |
| Glossary step Gherkin / tag progetto | L2 `gherkin-*` o `features/README.md` |
| Path artefatti / dual-runtime note | `.cursor/product/README.md` (o `.claude/product/`, `product/`) |
| Authorship nuovi L1 da proto-prompt o corpus skill esterni | `a-agentzero/references/l1-from-proto.md` (critica/estensione, non copia; vendor+pin se aggiornabile) |
| Export pack Claude discovery | `scripts/export-discovery-claude.sh` + doc pipeline |
| Residui actionable | `./ToDo.md` (root consumer) |
| Doc prodotto / path artefatti | `.cursor/product/README.md`, `docs/` se presenti |

**Discovery — non consolidare con `/learn !`:** bozze `hypothesis` non ratificate, microcopy one-off, PRD grezzi, segreti. Task già chiusi in sessione → non ToDo.

---

## Cosa non consolidare mai

- Password, API key, token, contenuto `.env`
- Output temporanei (log, path cache, ID sessione)
- Istruzioni «fix solo questo file una volta»
- Metriche GSC/SeoZoom non importate in `seo/`
- Intere conversazioni — solo regole estratte e atomiche

---

## Formato voce in skill (canone)

Preferisci bullet operativo, non narrativa:

```markdown
- [ ] Durate in minuti: notazione `60'`, `20'` (non «minuti» o «min»)
```

In tabella brand:

```markdown
| durate in minuti: notazione `60'`, `20'` | «60 minuti», «20 min» |
```

Aggiungi in CHANGELOG:

```markdown
### Changed
- Appreso da sessione: notazione minuti con apostrofo (`60'`) [sync:safe]
```
