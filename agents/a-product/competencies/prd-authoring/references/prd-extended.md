
## Slash `/prd` (profilo af)

| Arg | Ruolo |
|-----|--------|
| `draft` | Prima bozza Contesto→… da brief/personas/jtbd/PO |
| `refine` | Epic/US/AC; spezza storie; gate Sistema; NON-goals; backlog aperto |
| `live-check` | Checklist vivo: Done, OQ, Epic↔US, artifact (se presente), sizing, sprint |

Default se omesso: chiedi `draft` | `refine` | `live-check` (1 Q).

## Slash `/ms-prd` (profilo ms)

Senza argomento: genera o aggiorna PRD schema Claude + estensioni sotto. Niente `live-check` né guida sizing.

---

## Intake (prima di scrivere)

Chiedi solo ciò che manca (una domanda alla volta; estrai dalla chat ciò che è già detto):

1. **Nome** prodotto/feature e problema
2. **Chi lo userà** (persona/team) e perché — da `personas.md` / PO, non inventare
3. **Ambito**: nuovo | feature su esistente | update PRD già scritto
4. **User story già note** in conversazione o artefatti
5. **Path output**:
   - profilo **af**: default `product/prd.md`
   - profilo **ms**: cartella PRD progetto se esiste; altrimenti `product/PRD_<slug>_v<ver>.md`

Fonti: brief, lean-canvas, personas.md, jtbd.md. Profilo **af**: Distingui **Evidenza** vs **Ipotesi**; collega job story `JS-XX` quando presenti. Profilo **ms**: niente colonne Evidenza/Ipotesi né job story obbligatorie.

---

## Workflow profilo af (ordine fisso)

```
1. Contesto e Vision — problema, vision, perché ora, NON-goals
2. Utenti target — personas specifiche (Evidenza / Ipotesi)
3. Epic Map — obiettivo + US collegate (bidirezionale)
4. User Stories — Come… voglio… così da… (US-XX) + Epic esplicita + AC
5. Definition of Done — contratto globale team (≠ AC)
6. Backlog aperto — noti ma non ancora in Epic/US
7. KPIs — segnale in produzione
8. Domande aperte — owner + scadenza
9. Glossario — solo termini usati
10. Artifact e Versioni — SOLO se richiesto (reference dedicata)
11. Checkpoint PO → path canone
```

Path: `product/prd.md`. Snapshot opzionale: `prd-YYYY-MM-DD.md` se il PO chiede versioning esplicito.

Versione documento: nuovo → **1.0**; revisioni contenuto → minor (1.1, …).

---

## Workflow profilo ms

```
1. Contesto e Vision — problema, vision, Vincoli, NON-goals, utenti target
2. Epic Map — blocchi (A/B…) se casi distinti; obiettivo + US collegate
3. User Story — Come / voglio / per + Epic + AC (no job story)
4. Definition of Done — Livello A (baseline) + Livello B (prodotto)
5. Backlog aperto
6. Domande aperte — owner + stato
7. Glossario — solo termini usati
8. Artifact e Versioni — SOLO se richiesto
9. Checkpoint PO
```

**Versione documento (ms):** continua la serie esistente (es. 0.7 → 0.8). Nuovo senza storia → 0.1 o 1.0 a scelta del PO.

### DoD profilo ms

| Livello | Ruolo |
|---------|--------|
| **A — Baseline rilascio** | US in scope con AC ok; nessuna OQ bloccante; PRD aggiornato; OK PO |
| **B — Condizioni prodotto** | Checklist specifica (accessi, dati, integrazioni) compilata col PO |

---

## Formato User Story

Hard line break Markdown (due spazi a fine riga su Epic / Come / voglio).

**Profilo af** (`così da`):

```
**Epic:** EPIC-1 Nome epic␠␠
**Come** persona,␠␠
**voglio** azione,␠␠
**così da** beneficio.
```

**Profilo ms** (`per`):

```
**Epic:** EPIC-A1 Nome epic␠␠
**Come** persona,␠␠
**voglio** azione,␠␠
**per** beneficio.
```

ID profilo ms: `US-A01` / `US-B01` (per blocco) oppure `US-01`. ≥1 AC verificabile (≥2 se dettagli PO). Profilo af: ≥2 AC preferiti.

---

## QA pre-consegna

- Epic↔US bidirezionale (niente orfani)
- Formula corretta per profilo (af: **così da**; ms: **per**) + hard-break
- Glossario = solo termini usati; nessun placeholder su campi già forniti
- Gate persona **Sistema** (vedi template del profilo)
- Artifact assente se non richiesto
- Profilo **af**: OQ con owner+scadenza; NON-goals; KPI/`live-check` se applicabile
- Profilo **ms**: DoD A completo + B solo se discusso

---

## Formato evidenza (profilo af)

Per **PRD** af, strategia prodotto e notes di perimetro:

1. **Niente tag inline** `[E]` / `[I]` nel corpo
2. Dopo ogni sezione sostanziale: blocco **Evidenza** poi **Ipotesi**
3. Job stories preferite come `JS-XX` con **Quando / voglio / così da** se il PO lo chiede
4. **AC** = Acceptance Criteria verificabili
5. L2 può imporre path dual-path; questo è il canone L1 af

---

## Regole ferree

1. PRD = **cosa/perché**; *come* (UI pixel, API) → design / Technical Spec
2. Vision prima delle storie — mai feature dump senza filo
3. Persona specifica; beneficio percepibile da utente reale
4. Persona **Sistema**: solo se il beneficio tocca un utente — vedi template gate
5. AC ≠ DoD; OQ con owner; esplicitare NON-goals
6. Anti-invention: no quote/personas/metriche inventate
7. Skill VS PRD: decisioni di prodotto nel PRD; procedure ripetibili → skill dopo
8. Artifact e Versioni solo su richiesta esplicita
9. Scegli un profilo per documento; non mischiare formula af/ms nello stesso file

---

## Skill VS PRD (PO)

1. PRD prima (fonte di verità)
2. Processi ripetibili nel PRD → candidati skill
3. Skill deriva dal PRD; scelte nuove → aggiorna PRD prima
4. Evita skill orfane e PRD che descrivono SOP
5. Evolve PRD → aggiorna skill impattate

---

## Anti-pattern

- Soluzione UI al posto del bisogno
- Storie mammoth; AC vaghi; PRD mai aggiornato
- Completeness theater
- Fondere Lean Canvas dentro il PRD come sostituto
- Sezione Artifact di default
- US senza Epic; mischiare profilo af e ms

---

## Output

- File PRD + Decision summary (delta)
- Lista OQ aperte; storie Ready per `/prioritize` o `a-gherkin`
- Next: `/prioritize`, `a-gherkin`, o candidati skill (lista, non implementare qui)
- Da ms → af: migrare con `/prd` se serve living AF completo
