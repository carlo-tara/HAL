# Nuovi L1 da proto / corpus esterni — regola di authorship

Appreso da sessione discovery (personas / JTBD / Gherkin) e da arricchimento L1 da repo skill upstream (marketingskills / claude-seo / Labat → a-seozoom).

## Regola

Quando l'utente fornisce un **proto-prompt** per un nuovo agente L1 (o un'estensione), **oppure** un **corpus di skill esterne** (repo Git di skill/marketing/domain pack):

1. **Non copiarlo** nel `SKILL.md` / `agents/*.md` / `competencies/*/SKILL.md` come testo definitivo
2. **Comprendilo, criticarlo ed estenderlo**: contraddizioni, conflitti col protocollo L0, framework mistificati, anti-pattern di dominio, overlap con competenze già presenti
3. **Allinea** a: `po-interviewer` (se intervista PO), handoff a file, ID stabili, no emoji-status, anti-invention, dati progetto (es. `seo/` per metriche — mai inventare numeri)
4. Solo dopo: scaffold L1/competenze + reference distillate + template + registrazione ecosistema

## Vendor upstream (repo skill esterni)

Se il corpus va tenuto aggiornabile nel tempo:

| Pezzo | Dove |
|-------|------|
| Clone locale | `vendor/{nome}/` (**gitignored** — non committare il tree) |
| Pin SHA + mapping distillazione | `a-{dominio}/references/{nome}-source.md` (committato) |
| Update | script `a-{dominio}/scripts/update-*.sh` + comando progetto `.cursor/commands/…` |
| Post-update | confronta delta skills ↔ mapping; **non** riscrivere auto le competenze AF |

Adozione **opt-in per dominio**: importa solo le skill pertinenti all’L1 ospite; il resto resta nel vendor.  
Esempi canone: `a-seozoom/references/marketingskills-source.md` · `claude-seo-source.md` · `labat-seo-geo-aeo-source.md`.

### Licenza e multi-corpus

- **MIT/Apache/equivalente chiaro:** clone + distillazione lean con attribution nel pin.
- **CC BY-NC-SA / non-commercial / share-alike:** **solo distillazione** — prose e checklist originali HAL; attribution in CHANGELOG/pin; **non** copiare ZIP/skill verbatim né redistribuire i pack upstream nel canone AF (es. Product-Manager-Skills → a-po).
- **Nessuna SPDX / LICENSE assente:** clone solo per consultazione; nelle skill AF **riscrivere** checklist (no dump verbatim del `SKILL.md` upstream); citare autore nel pin.
- **Più corpus sullo stesso L1:** ogni repo ha pin+update propri; tabella **Non adottato** esplicita; se due fonti confliggono su un claim (es. rich result Google), **fonte primaria del motore** (docs Google/Bing) vince, poi il corpus meglio allineato — non la checklist più lunga.

### Identità dominio (es. SEO)

Non sostituire il modello operativo L1 (es. batch `seo/{YYMMDD}/`) con il runtime dell’upstream (crawl-first, slash `/seo`, MCP, PDF agency) salvo richiesta esplicita e L2.

## Checklist minima di critica

- [ ] Input/output sono artefatti file, non solo chat?
- [ ] C'è ratifica PO o si inventa il dominio?
- [ ] Termini di framework dichiarati (niente ibridi non nominati)?
- [ ] Slash completi di lifecycle (create/update/export/triage…), non solo due comandi demo?
- [ ] Compatibile dual-runtime Cursor + Claude (bootstrap self-contained o deploy)?
- [ ] (Se corpus esterno) pin + mapping + update path; competenze distillate lean, non dump del vendor?
- [ ] (Se no SPDX) nessuna copia verbatim; solo metodologia riscritta?
- [ ] (Se CC BY-NC-SA / NC) nessuna redistribuzione pack; distillazione + attribution only?
- [ ] (Se multi-corpus) override conflitti documentato nel pin?
- [ ] Ship: con tree sporco, commit prima solo `a-{dominio}/` (+ asset strettamente legati); registry L0/`deploy-all`/README bulk in commit dedicato (vedi `docs/operativo.md` § Ship)?

## Anti-pattern

- Redistribuire pack/ZIP skill upstream sotto CC BY-NC-SA (o licenza NC) dentro HAL
- Incollare il proto / SKILL upstream come system prompt e dichiarare l'agente “pronto”
- Auto-attivazione con rewrite silenzioso degli artefatti
- Desired Outcomes ODI = scenari Gherkin 1:1 senza seeds
- Scenari BDD ordine-dipendenti (“N alimenta N+1”)
- Committare interi clone `vendor/` o adottare tutto un marketplace marketing dentro un L1 SEO-only
- Mescolare in un commit WIP di altri L1/L0/README solo perché coesistono nel working tree
