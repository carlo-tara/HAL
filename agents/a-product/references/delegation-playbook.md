# Delegation Playbook — a-po

## Scope
How `a-po` delegates to specialists and merges outputs into product decisions.

## Delegation contract
1. **Objective** — one clear question
2. **Context** — product constraints + known facts
3. **Required output format**
4. **Acceptance checks**

## Specialist routing

### a-personas / a-jtbd
Use when profile or jobs are missing/unclear. Do not author personas.md or jtbd.md yourself if the specialist exists.  
Serve **switch interview** (hire/timeline/Four Forces) → `a-jtbd` `/interview` (`prep` | `guide` | `synth`); non usare `po-interviewer` per interviste cliente.

### a-gherkin
Use when acceptance criteria / BDD suite is needed after shape/validate/prioritize **or after `/prd`** with US+AC (DoR light met). Do not write `.feature` in a-po.

### Internal: PRD vs skill (AF)
**PRD** = cosa/perché (Epic/US/AC). **Skill** = come l’AI esegue un processo ripetibile. Sequenza: chiudi/aggiorna PRD → solo poi candidati skill tracciati a US; se emergono decisioni di prodotto in una skill, torna al PRD. Non mettere SOP passo-passo nel PRD.

### Internal: lean-canvas → validate / copy
After `/canvas`, route riskiest boxes to `evidence-probe` (`/validate`). Align Moore/package to canvas UVP via `positioning-offer` before copy. Do not hand canvas raw to investors — translate. Canvas feeds Vision; `/prd` owns Epic/US.

### a-copywriter
Use for messaging, landing, or outreach *copy* after positioning (and canvas UVP, if any) is decided.

### a-charts
Use for KPI / funnel / market-series visuals from real numbers (including ISTAT/Unioncamere exports).

### a-seozoom
Use when a content/SEO growth loop needs technical SEO/GEO work.

### a-b2b
Use when the work is a full **B2B pilot** (multi-agent package + enrichment + consolidation), not a single product-shape task.

### a-enrichment
Use only when the PO explicitly needs list/enrich/gate work. Open-data market aggregates stay in `market-public-data` — do not route startup/ISTAT sizing through enrichment by default.

## VoltAgent-style peer map (HAL)

| Peer intent | HAL |
|-------------|--------------|
| UX research / personas | `a-personas` / `a-jtbd` |
| Requirements / PRD prose | `a-po` `/prd` |
| Requirements / AC BDD | `a-gherkin` |
| Landing / marketing copy | `a-copywriter` |
| KPI visuals | `a-charts` |
| Multi-agent B2B pilot | `a-b2b` |
| CRM list enrich | `a-enrichment` (rare) |

## Consolidation
1. Tag findings `evidence` | `hypothesis`
2. Guardrails L2 first, then evidence (including cited PA open data)
3. One merged output: decisions, risks, next actions
