# Changelog — a-copywriter

## [Unreleased]

## [1.6.0] - 2026-10-02

### Added
- System 1 (Laya) Gating in Copywriting: routing rapido dei formati di copy (`router.py routing`), scoring anti-AI per il rilevamento di cliché (`router.py score`) e selezione del registro prima di attivare i loop di humanization System 2 [sync:safe]

## [1.5.7] - 2026-09-18

### Changed
- Sync padre: extends-version a-agentzero → 1.6.15 (lean L0 cmds) [sync:safe]




## [1.5.6] - 2026-09-17

### Added
- Frontmatter `model: orcarouter/openai/gpt-4o-mini` + `model-fallback: cursor-default` (OrcaRouter preferred; Cursor default se non raggiungibile) [sync:safe]
- Sync L0 a-agentzero `extends-version: 1.6.14` (preferred model frontmatter) [sync:safe]

## [1.5.5] - 2026-09-15

### Changed
- Sync L0 a-agentzero `extends-version: 1.6.13` (/learn ! ToDo+docs pointer) [sync:safe]


## [1.5.4] - 2026-09-15

### Changed
- Sync L0 a-agentzero `extends-version: 1.6.12` (a-product § Profilo B2B / a-b2b facade) [sync:safe]

## [1.5.3] - 2026-09-15

### Changed
- Sync L0 a-agentzero `extends-version: 1.6.11` (registry a-product) [sync:safe]


## [1.5.2] - 2026-09-15

### Changed
- Appreso da sessione: Reason why in description + regole di ingaggio subagent [sync:safe]



## [1.5.1] - 2026-09-08

### Changed
- Sync L0 a-agentzero `extends-version: 1.6.4` (scaffold commit staged-only) [sync:safe]

## [1.5.0] - 2026-09-07

### Added
- `references/five-copy-blocks.md`: Pain → Promise → Proof per lettore impulsivo; landing breve; no invent proof; stub Constraints/Curiosity [sync:review]
- Ispirazione: Substack Gargiulo ep.1 (5 Copy Blocks) — distillata, non mega-prompt vendor

### Changed
- `publication-types.md` § Landing allineata ai 3 blocchi + max 5 bullet
- Brief minimo + lettura selettiva + tabella output per landing persuasiva

## [1.4.3] - 2026-08-20

### Added
- Sezione microcopy UI/dashboard (frasi corte, verbi d’azione, no formule verbose; Never inject → humanizer) [sync:review]

## [1.4.2] - 2026-08-15

### Changed
- Sync L0 1.6.3 (`extends-version: 1.6.3`): git-track L2 sotto `.gitignore` [sync:safe]


## [1.4.1] - 2026-08-15

### Changed
- Sync L0 1.6.2 (`extends-version: 1.6.2`): registry a-po/a-enrichment + l1-from-proto CC BY-NC-SA distill-only [sync:safe]

## [1.4.0] - 2026-08-13

### Added
- `publication-types.md`: workflow JSON-first (+ render) per contenuti strutturati newsletter/promo/carousel [sync:review]
- `extension-template.md`: guida skill voice dedicata (`*-voice` / voice-as-brand) [sync:review]

### Changed
- `tono-di-voce` 1.0.2: voice-as-brand, gerarchia brand vs voice skill [sync:review]
- Sync L0 1.5.7–1.6.0 (`extends-version: 1.6.0`): l1-from-proto, humanizer Never inject, registry `a-b2b` [sync:safe]

## [1.3.0] - 2026-08-13

### Added
- Humanizer 1.2.0 + italiano-locale 1.2.0: grammatica LLM, leak conversazionale, Trova, voce misurata/osservata, registri/canali, segnali misurabili (da italiano-scrittura-anti-ai; senza iniezione anima) [sync:review]

### Changed
- Workflow/checklist: radar stesura, Trova, grammatica LLM, canali lettore opzionali [sync:review]

## [1.2.0] - 2026-08-13

### Added
- Humanizer 1.1.0: Never inject, tier A/B/C, P0–P2, mode detect/edit, patch vs rewrite, tolerance per tipo, second-pass obbligatorio [sync:review]

### Changed
- Workflow e checklist orchestratore allineati a humanizer 1.1.0; companion `agents/a-copywriter.md` aggiornato [sync:review]

## [1.1.10] - 2026-08-07

### Changed
- Sync L0 1.5.6: L1 `a-charts` registry/discovery → solo extends-version [sync:safe]

## [1.1.9] - 2026-08-03

### Changed
- Sync L0 1.5.5; `tono-di-voce` L1 1.0.2 (voice-as-brand) [sync:review]

## [1.1.8] - 2026-08-03

### Changed
- Sync L0 1.5.4: `/sync <` generalizzazione L2 → solo extends-version [sync:safe]

## [1.1.7] - 2026-08-03

### Added
- publication-types: contenuto strutturato JSON-first (+ render) [sync:review]

### Changed
- Sync L0 1.5.3; `tono-di-voce` L1 1.0.1 (brand vs voice skill) [sync:review]

## [1.1.6] - 2026-07-28

### Changed
- Sync L0 1.5.2: `l1-from-proto` corpus skill esterni (vendor+pin) → solo extends-version [sync:safe]

## [1.1.5] - 2026-07-27

### Changed
- Sync L0 1.5.1: `[sync:safe]` comandi/deploy → solo extends-version [sync:safe]

## [1.1.4] - 2026-07-27

### Changed
- Sync L0 1.5.0: comandi Cursor L0 ereditabili (`commands/`) [sync:safe]

## [1.1.3] - 2026-07-27

### Changed
- Sync L0 1.4.1: `po-interviewer`/discovery opt-in (non adottato); regola authorship proto [sync:safe]

## [1.1.2] - 2026-07-27

### Changed
- Sync L0 1.3.1: file dati ≠ competenze [sync:safe]

## [1.1.1] - 2026-07-27

### Changed
- Sync L0 1.3.0: protocollo competenze (L0 opzionale, asset fuori, cross-dominio) [sync:safe]

## [1.1.0] - 2026-07-27

### Added
- Competenze modulari L1: `tono-di-voce`, `humanizer`, `italiano-locale` sotto `competencies/` [sync:review]
- Orchestratore SKILL.md: workflow brief → tono → draft → humanizer → italiano-locale → checklist [sync:review]
- Template L2: sezione/directory `competencies/{id}/` per override [sync:review]

### Changed
- Sync L0 1.2.0: protocollo competenze path-based; `extends-version: 1.2.0` [sync:review]
- Reference spostati da `references/` alle competenze (vedi mapping sotto) [sync:breaking]

### Removed
- Directory `a-copywriter/references/` (contenuti migrati in `competencies/*/references/`) [sync:breaking]

**Mapping reference → competenza:**

| Ex path | Nuovo path |
|---------|------------|
| `references/scrittura-inclusiva.md` | `competencies/tono-di-voce/references/` |
| `references/anti-ai-it.md` | `competencies/humanizer/references/` |
| `references/humanizer-loop.md` | `competencies/humanizer/references/` |
| `references/scrittura-umana.md` | `competencies/humanizer/references/` |
| `references/editing-avanzato.md` | `competencies/humanizer/references/` |
| `references/purismo-italiano.md` | `competencies/italiano-locale/references/` |
| `references/italiano-vivo.md` | `competencies/italiano-locale/references/` |

Restano in root: `publication-types.md`, `brand-brief-template.md`, `extension-template.md`.

## [1.0.2] - 2026-07-16

### Changed
- Sync L0 1.1.2: skill `/sync` (deploy + report versioni) [sync:safe]

## [1.0.1] - 2026-07-13

### Changed
- Sync L0 1.1.1: sezione Apprendimento da sessione; rimosso riferimento a `GuideStile/` assente nel repo [sync:safe]

## [1.0.0] - 2026-07-13

### Added
- Baseline iniziale — workflow Humanizer, anti-AI, purismo, scrittura inclusiva
- Campi `version` e `extends-version: 1.0.0` (allineato a a-agentzero 1.0.0) [sync:safe]
