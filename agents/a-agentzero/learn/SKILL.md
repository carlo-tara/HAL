---
name: learn
parent: a-agentzero
version: 1.2.1
model: orcarouter/openai/gpt-4o-mini
model-fallback: cursor-default
description: >-
  Slash /learn con doppia modalità: /learn ? illustra gli apprendimenti dalla
  conversazione o sessione corrente; /learn ! consolida nelle skill attive del
  progetto (L2, brand, rules), e — se necessario — Attività in ./ToDo.md e/o
  apprendimenti in docs locali; scrive changelog Progetto|HAL e bump
  patch (/version patch) sulle skill toccate. Usare quando l'utente invoca
  /learn, /learn ?, /learn ! o chiede di memorizzare preferenze e residui.
disable-model-invocation: true
---

# /learn — apprendimento da sessione (L0)

Skill utility di **a-agentzero**. Cattura ciò che emerge dalla chat corrente e, su richiesta, lo persiste nelle skill del progetto senza duplicare L0/L1. **Se necessario**, registra anche Attività residue in `./ToDo.md` e/o aggiorna documentazione locale (non solo skill).

**Reference:** [consolidation-targets.md](references/consolidation-targets.md)

---

## Invocazione

| Input utente | Modalità |
|--------------|----------|
| `/learn ?` | **Riflessione** — solo report, nessuna scrittura |
| `/learn !` | **Consolidamento** — scrive nei target (skill / brand / rules / **ToDo** / **docs**) + changelog Progetto\|HAL + `/version patch` sulle skill |
| `/learn` senza suffisso | Mostra sintassi e chiedi `?` o `!` |

Il suffisso (`?` o `!`) ha priorità su eventuale testo aggiuntivo. Se l'utente scrive `/learn ! solo la notazione minuti`, applica il filtro al consolidamento.

---

## Cosa conta come «appreso»

Includi solo elementi **stabili e riutilizzabili**, oppure **residui actionable** da tracciare:

- Preferenze esplicite dell'utente (formato, tono, vincoli, «sempre», «mai»)
- Correzioni ripetute o correzioni puntuali con intento permanente
- Convenzioni progetto scoperte o confermate (path, workflow, naming)
- Pattern validati in questa sessione (es. notazione `60'`, JSON-first PED)
- Invarianti o failure condition emersi da debug
- Follow-up / debito / «da fare dopo» confermati (→ candidati `./ToDo.md`)
- Lacune di glossario / BC / howto locali (→ candidati docs)

**Escludi:**

- Task già completati in sessione («fixa questo bug» fatto e chiuso)
- Dati sensibili, credenziali, token, path a `.env`
- Metriche SEO/traffico non verificate
- Ipotesi non confermate dall'utente
- Contenuto già presente identico nelle skill/docs (segnala «già consolidato»)

---

## Destinazione (routing)

Ogni voce ha **una** destinazione primaria. Scegli con questa regola:

| Destinazione | Quando (necessario) | Esempi |
|--------------|---------------------|--------|
| **Skill / brand / rules** | Preferenza o convenzione **permanente** che l'agente deve riapplicare | notazione `60'`, no commit senza richiesta, path L2 |
| **`./ToDo.md` (Attività)** | Residuo **actionable** non ancora slice: follow-up, techdebt, bug aperto, wave successiva | «allineare L2 consumer», «documentare X», «fix flake CI» |
| **Doc locale** | Spiegazione / naming / confini / howto che non è regola agente | glossario UL, BC map, `docs/operativo.md`, README path |
| **Escludi** | Ephemeral, fatto, sensibile, non confermato | patch one-shot già mergeata |

**Anti-pattern:** non mettere preferenze stabili solo in ToDo; non gonfiare skill con todo operativi; non duplicare la stessa voce in skill **e** ToDo senza motivo (ToDo punta al lavoro; skill alla regola).

Se la voce è mista (regola + lavoro residuo): skill/docs per la regola **e**, se necessario, Attività ToDo per il lavoro rimanente — due righe distinte nel report.

---

## Modalità `?` — Riflessione

**Obiettivo:** illustrare cosa l'agente ha imparato dalla conversazione/sessione corrente **senza modificare file**.

### Workflow

```
Task Progress:
- [ ] 1. Ricostruisci sessione — messaggi utente, correzioni, decisioni, file toccati
- [ ] 2. Classifica ogni apprendimento (categorie + destinazione)
- [ ] 3. Verifica duplicati — grep in skill/brand/rules/docs/ToDo già in contesto
- [ ] 4. Escludi voce ephemeral o sensibile
- [ ] 5. Proponi target per eventuale `!` (skill | ./ToDo.md | docs/…)
- [ ] 6. Emetti report nel formato sotto
```

### Formato output obbligatorio

```markdown
# /learn ? — Apprendimenti da questa sessione

## Sintesi
[1–2 frasi: cosa è cambiato nel modello operativo per questo progetto]

## Apprendimenti

### 1. [Titolo breve]
- **Cosa:** [enunciato operativo, una riga]
- **Evidenza:** [citazione o parafisi fedele da chat / file modificati]
- **Stato:** nuovo | già in skill/docs/ToDo | da confermare
- **Ambito:** Progetto | HAL
- **Destinazione:** skill \| ToDo \| docs \| escludi
- **Target proposto (per !):** `path/file.md` § sezione  (o `./ToDo.md` · P1 · #tag)

[Ripeti per ogni voce]

## Escluso da consolidamento
- [voce + motivo breve]

## Prossimo passo
Esegui `/learn !` per consolidare, oppure `/learn ! [filtro]` per un sottoinsieme.
```

### Categorie (per classificazione interna)

| Categoria | Esempi |
|-----------|--------|
| Preferenza utente | notazione `60'`, no commit senza richiesta |
| Convenzione progetto | JSON-first PED, render script |
| Tono / brand | lessico inclusivo, no PMI |
| Workflow | checklist publish, path asset |
| Tecnica / tool | flag script, formato MD |
| Anti-pattern | cosa evitare emerso da correzione |
| Residuo / Attività | follow-up, techdebt, bug aperto |
| Doc / semantic layer | glossario, BC, howto locale |

---

## Modalità `!` — Consolidamento

**Obiettivo:** scrivere gli apprendimenti approvati nei target del contesto attivo (priorità L2). **Se necessario**, anche Attività in `./ToDo.md` e/o docs locali.

### Workflow

```
Task Progress:
- [ ] 1. Esegui estrazione come `?` (se non già fatta nel turno)
- [ ] 2. Filtra: solo voci con stato nuovo o da confermare esplicitamente accettate da `!`
- [ ] 3. Classifica ogni voce: **Progetto** | **HAL** + destinazione (skill|ToDo|docs)
- [ ] 4. Risolvi catena attiva — L0 → L1 → L2 + file dati (brand, rules, docs, ToDo)
- [ ] 5. Mappa ogni voce al target (tabella in consolidation-targets.md)
- [ ] 6. Leggi file target; evita duplicazione con padre L0/L1 / voci ToDo esistenti
- [ ] 7. Applica diff minimo — skill/docs: una regola per bullet; ToDo: Attività nel formato Mappa residui
- [ ] 8. Scrivi **Changelog apprendimenti** in `.cursor/product/session-learnings.md` (obbligatorio se ≥1 voce)
- [ ] 9. `/version patch` su ogni `SKILL.md` modificato (+ CHANGELOG skill)
- [ ] 10. Rigenera derivati se il progetto lo prevede (es. render script)
- [ ] 11. Emetti report consolidamento
```

### Ambito: Progetto vs HAL

| Ambito | Criterio | Esempi di target |
|--------|----------|------------------|
| **Progetto** | Convenzione/preferenza del repo consumer (o delta L2 locale) | `.cursor/skills/{dominio}-{progetto}/`, brands, rules, CONTRIBUTING, `./ToDo.md`, `docs/` consumer |
| **HAL** | Protocollo / L0 / L1 canonici / harness meta-repo | `a-*/`, `a-agentzero/learn|sync|commands`, `harness-agentfactory`, docs AF, `./ToDo.md` AF |

Se il workspace attivo è HAL e la voce riguarda solo questo meta-repo come prodotto operativo (gate Make, RGR hooks), classifica **HAL**. Se riguarda un sito consumer citato in chat, classifica **Progetto** anche se stai editando da AF.

### `./ToDo.md` — quando necessario

Scrivi o aggiorna **`./ToDo.md`** (root del repo attivo) **solo se** almeno una voce è destinazione **ToDo** e:

1. Il lavoro **non** è già chiuso in sessione / già in HEAD come fatto
2. Non è già uno `/slice` accettato in progress (quello resta in `agent-progress.md`)
3. L'Attività è verificabile (titolo + acceptance minima)

Formato Attività (allineato a competenza `a-harness` / `todo`):

```markdown
- [ ] Titolo chiaro `#tag` · P0|P1|P2 · BC opz.
  - Perché utile: …
  - Acceptance: …
```

Crea scheletro minimo del file se assente (sezioni P0/P1/P2). **Non** sostituire un pass `/todo` completo: append/merge mirato; se il file è disordinato, proponi `/todo` dopo. Dettaglio igiene → `/todo`.

### Docs locali — quando necessario

Aggiorna documentazione **locale al repo** (non skill) **solo se** la voce è destinazione **docs** e il file è il posto canonico (vedi consolidation-targets). Esempi tipici: `docs/glossary.md`, `docs/bounded-contexts.md`, `docs/operativo.md`, `README.md`, `.cursor/product/README.md`, `CONTRIBUTING.md`.

Diff minimo; stesso lessico del file; niente narrativa di chat. Se manca il file e serve davvero, crealo solo con scheletro utile — altrimenti segnala gap nel report senza inventare alberi docs.

### Changelog apprendimenti (obbligatorio su `!`)

Ogni `/learn !` che consolida almeno una voce **deve** appendere a `.cursor/product/session-learnings.md` un blocco con entrambe le sezioni (vuota → `- (nessuno)`):

```markdown
## [YYYY-MM-DD] {session_id} — /learn !

### Progetto
- [apprendimento] → `path` § sezione
- [Attività] → `./ToDo.md` · P1 · #tag

### HAL
- [apprendimento] → `path` § sezione
```

Crea il file se manca (template minimo: titolo + questa entry). Non sostituire lo storico: solo append.

### `/version patch` (obbligatorio su `!`)

Dopo i diff di consolidamento, esegui il bump **patch** come `/version patch` su ogni skill toccata:

1. `version` frontmatter: patch +1
2. Voce in `CHANGELOG.md` della skill (o agente) sotto `## [Unreleased]` → `### Added` / `### Changed`
3. Testo voce: `Appreso da sessione: [sintesi breve]` + `[sync:safe]` se L2

Se nessuna `SKILL.md` è stata modificata (solo brand/rules/session-learnings/**ToDo**/docs), non inventare bump: aggiorna solo i file pertinenti + Changelog apprendimenti e segnalalo nel report.

Non bumpare **a-agentzero** L0 per apprendimenti di progetto consolidati solo in L2 / ToDo / docs consumer.

### Regole di scrittura

1. **Delta only** — nel L2 non copiare intere sezioni già in L0/L1; aggiungi o precisa
2. **Una idea, un posto canonico** — se esiste già, integra la voce esistente invece di creare sezione parallela
3. **Stesso lessico del file target** — allineati a brand/skill/docs ospite
4. **Mai** scrivere segreti o placeholder credenziali
5. **L1 globale** (`~/.agents/skills/a-*`) — modifica solo se l'utente chiede esplicitamente regola cross-progetto **oppure** il pattern è già validato su ≥2 progetti e il filtro `!` lo indica; altrimenti resta nel L2 del repo
6. **`.cursorrules` / `.cursor/rules/`** — solo per vincoli sempre-on o scope file; preferisci skill per workflow
7. **Anti-grasso** — se l'apprendimento è già coperto da L1/L0, in `!` segnala «già in padre» e **non** gonfiare il L2; proponi promozione solo se manca nei padri e serve cross-repo
8. **Voice** — lessico/inclusività → brand; registri/struttura pesanti → skill `*-voice` se esiste, altrimenti delta copywriter (vedi consolidation-targets + L0 tono-di-voce)
9. **ToDo / docs solo se necessario** — nessuna Attività decorativa; nessun doc senza gap reale

### Dove scrivere (priorità)

| Priorità | Target | Quando |
|----------|--------|--------|
| 1 | `.cursor/skills/{dominio}-{progetto}/SKILL.md` | workflow, delta dominio |
| 2 | `.cursor/skills/{dominio}-{progetto}/writing-rules.md` o skill `*-voice` | regole copy/formato / voice pesante |
| 3 | `.cursor/brands/*.md` | tono, lessico, PS, inclusività |
| 4 | `.cursor/rules/*.mdc` | vincolo automatico su glob |
| 5 | `./ToDo.md` | Attività residue (quando necessario) |
| 6 | `docs/**`, `README`, `CONTRIBUTING`, `.cursor/product/README.md` | doc locale (quando necessario) |
| 7 | L1 / L0 globale | solo su richiesta esplicita cross-repo o pattern ≥2 progetti |

Dettaglio per dominio: [consolidation-targets.md](references/consolidation-targets.md).

### Formato output obbligatorio

```markdown
# /learn ! — Consolidamento completato

## Scritto
| Apprendimento | Ambito | Destinazione | File | Sezione |
|---------------|--------|--------------|------|---------|
| … | Progetto \| HAL | skill \| ToDo \| docs | `path` | … |

## Changelog apprendimenti
Appended: `.cursor/product/session-learnings.md` — `## [YYYY-MM-DD] … — /learn !`
### Progetto
- …
### HAL
- …

## Già presente (nessuna modifica)
- …

## Escluso
- … — motivo

## Versioni (/version patch)
- `copywriter-giocostrategico` 1.0.0 → 1.0.1
- (nessun bump — solo ToDo/docs/brand)

## Verifica suggerita
- [ ] Prossima sessione: l'agente applica la regola senza re-prompt
- [ ] Se ToDo aggiornato: eventuale `/todo` per igiene priorità
```

Se nessuna voce è consolidabile, dilo esplicitamente e restituisci il report `?` al posto di modificare file (nessun changelog, nessun bump).

---

## Integrazione con catena agenti

All'invocazione `/learn`:

1. Carica `a-agentzero/SKILL.md` (già in contesto se L0 attivo)
2. Identifica L1/L2 attivi dal repo corrente (`extends:` in `.cursor/skills/*/SKILL.md`)
3. Per `?`: usa trascrizione/chat + diff/file tocchi nella sessione
4. Per `!`: rispetta gerarchia conflitti L2 > dati > L1 > L0; ToDo/docs non sovrascrivono sicurezza L0
5. Per Attività ToDo: allinea al formato competenza `todo` (`a-harness`); igiene ampia → suggerisci `/todo`

---

## Esempi

### Esempio `?`

Utente: `/learn ?`

Agente: report con voce «Durate in minuti: notazione `60'`» → destinazione **skill**, target brand + `writing-rules.md`; voce «allineare pin L2 consumer X» → destinazione **ToDo**, `./ToDo.md` · P1 · `#infra`.

### Esempio `!`

Utente: `/learn !`

Agente: integra la regola in `writing-rules.md` e brand; appende Attività in `./ToDo.md` se necessario; aggiorna docs solo se gap; appende Changelog apprendimenti; `/version patch` sulle skill toccate; report tabella «Scritto».

### Esempio filtrato

Utente: `/learn ! solo notazione minuti`

Agente: consolida solo le voci il cui titolo o target riguarda durate/minuti; changelog e patch solo per quel sottoinsieme.

---

## Checklist qualità

- [ ] `?` non ha modificato alcun file
- [ ] `!` ha diff minimo e nessun segreto
- [ ] Nessuna duplicazione con L0/L1
- [ ] Ogni voce consolidata tracciabile a evidenza in chat
- [ ] Destinazione corretta: skill vs ToDo vs docs (solo se necessario)
- [ ] Changelog apprendimenti appendato con `### Progetto` e `### HAL`
- [ ] `/version patch` eseguito su ogni `SKILL.md` modificato (non per solo ToDo/docs)
- [ ] Utente sa cosa è stato scritto e dove
