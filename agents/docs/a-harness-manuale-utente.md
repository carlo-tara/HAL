# Manuale utente — agente **a-harness** (per sviluppatori)

Guida pratica per **sviluppatori umani** che usano `@a-harness` in Cursor (o Claude) per implementare codice dietro un contratto (Gherkin/PRD), con ciclo TDD e gate Makefile.

Versione agente: **1.1.4** · Specifica interna: [`harness-engineering.md`](harness-engineering.md) · Skill: [`a-harness/SKILL.md`](../a-harness/SKILL.md)

---

## 1. Cos’è (in una frase)

**a-harness** è un agente di *processo*: ti fa implementare **un pezzo piccolo alla volta** (slice), con **test prima**, codice minimo, gate automatici (`make`), e ti chiama **solo** quando il lavoro è meccanicamente pronto — così tu giudichi se è **quello che volevi**, non se “compila”.

Non sostituisce Cursor/Claude, non è un prodotto CI/CD cloud, non scrive PRD né file `.feature` (per quelli: `a-po` / `a-gherkin`).

```
Tu (intent + design)  →  a-harness (TDD + Make)  →  Tu (review intent su PR)
         ↑                        │
    contratto .feature / US       └─ stop se stuck o gate rosso
```

---

## 2. Prima di iniziare (checklist repo)

Sul **repository del prodotto** (non su HAL):

| Serve | Perché |
|-------|--------|
| Contratto: `.feature` **oppure** US/AC chiari **oppure** task con perimetro file | L’agente non inventa il comportamento |
| `Makefile` con almeno `test-unit`, `pre-commit`, `ready-for-review` | Platform API: verità deterministica |
| `docs/glossary.md` (consigliato) | Nomi allineati al dominio |
| `docs/bounded-contexts.md` (consigliato) | Dove può toccare i file |
| Skill L2 opzionale `.cursor/skills/harness-{progetto}/` | Path/stack specifici del progetto |

Se il repo è greenfield:

```
@a-harness /bootstrap profile standard
```

(Profile `minimal` = solo Makefile/gate; `standard` = + glossario, bounded context, progress.)

**CI-first:** senza `make test` / `ready-for-review` reali non ha senso dare autonomia multi-slice.

Deploy agenti sul tuo Cursor (una tantum, da HAL):

```bash
bash /var/www/HAL/agents/deploy-all.sh
# oppure solo:
bash /var/www/HAL/agents/a-harness/deploy.sh
```

Poi in chat: `@a-harness` o subagent `a-harness`.

---

## 3. Il tuo ruolo vs quello dell’agente

| Tu (umano) | a-harness |
|------------|-----------|
| Scegli *cosa* vale la pena costruire (intent) | Esegue Red → Green → Refactor sullo slice |
| Accetti o rifiuti lo **slice** proposto in Plan | Non scrive codice finché lo slice non è accettato |
| Non micro-gestisci lint/test “rossi” a metà | Autocorregge fino a `make ready-for-review` = 0 |
| Review PR: «è quello che volevamo?» | Fornisce diff + prove Make (PR-as-proof) |
| Decidi architettura di alto livello | Steward può proporre Makefile/CI/hooks, non riscrivere il business a caso |

**Regola d’oro:** non chiedere all’agente «apri la PR» o «è finito?» finché non ha fatto `/ready` con gate verde. Se lo fa prima, sta violando `sustainable-pace`.

---

## 4. Flusso quotidiano consigliato

### 4.1 Un feature / bug ben delimitato

1. Assicurati che esista lo scenario (o US) e il modulo (bounded context).
2. Incolla un prompt tipo:

```
@a-harness /cycle

Slice: aggiungere rate limiting a POST /api/auth/login
usando il middleware già in /api/users.
Contratto: .cursor/product/features/auth-login.feature — scenario "…"
Bounded context: Auth (src/modules/auth/)
File max 4. Effort: thorough.
Non chiedermi attenzione finché make ready-for-review non è verde.
```

3. L’agente in **Plan** (`/slice`) elenca file, acceptance criteria, termini glossario → **conferma o correggi** prima che scriva codice.
4. Poi in **Act** fa `/red` → `/green` → `/refactor` → `/ready`.
5. Tu: leggi il riepilogo + log Make + diff; approva intent; apri/merge PR se ha senso.

### 4.2 Solo una fase (controllo fine)

| Comando | Quando usarlo |
|---------|----------------|
| `/slice` | Definire/accettare perimetro (≤4 file, acceptance) |
| `/red` | Solo test che devono fallire |
| `/green` | Solo implementazione minima |
| `/refactor` | Solo pulizia sotto test verdi |
| `/cycle` | Sequenza completa sullo slice |
| `/ready` | Gate finale + checklist proof |
| `/progress` | Dove siamo (session_id, eventi, stuck) |
| `/steward` | Audit Makefile/CI/hooks/freeze (non feature) |
| `/bootstrap` | Scaffold harness su repo nuovo |

Dettaglio completo di ogni comando → [§13](#13-riferimento-comandi-man).

### 4.3 Handoff da Gherkin

Se vieni da `a-gherkin`, usa il template in [`handoff-from-gherkin.md`](../a-harness/references/handoff-from-gherkin.md).

---

## 5. Come scrivere uno slice “buono”

Lo slice è la skill più importante **tua**.

| Evita | Preferisci |
|-------|------------|
| «Refactora tutto auth» | «Aggiungi X su `/api/…` con pattern già in Y» |
| «Rinomina questa variabile» (troppo stretto per un cycle) | Task medium: 1 comportamento osservabile, 1–4 file |
| «Sistema i test» senza acceptance | Acceptance verificabili + riferimento a `.feature` o US |

Budget tipico: **&lt;400 LOC** netti per handoff; oltre → spezza.

---

## 6. Cosa succede quando si blocca

Dopo **3 fallimenti** sullo stesso approccio (`when-stuck`), l’agente deve:

1. Fermarsi e aggiornare il progress file  
2. Chiedere a te, **oppure** proporre uno slice nuovo (fork), **oppure** `/steward` se è rotto il gate Make  

Non lasciare girare «ancora una volta» all’infinito: è anti-pattern.

Comando utile:

```
@a-harness /progress
```

---

## 7. Review umana (dopo `/ready` verde)

Checklist minima (allineata a [`pr-proof-checklist.md`](../a-harness/references/pr-proof-checklist.md)):

- [ ] `make ready-for-review` è uscito 0 (log in chat o CI)
- [ ] Scope file coerente con lo slice accettato
- [ ] Nessun placeholder tipo `// ... existing code ...` che ha cancellato codice
- [ ] Commit con **perché** architetturale (non solo «fix»)
- [ ] Riesci a spiegare l’intent in due frasi (anti “shadow code”)

Tu **non** sei il linter: se il gate è verde e dubiti del design, chiedi refactor o un nuovo slice — non “sistema anche il formatting”.

---

## 8. Bootstrap e manutenzione fabbrica

| Bisogno | Comando / azione |
|---------|------------------|
| Repo senza Makefile | `/bootstrap` `minimal` o `standard` |
| Regole always/never ripetute | Chiedi `/steward` di promuoverle a hook/`make` |
| File che l’agente non deve toccare | Freeze list (template freeze) + conferma in L2 |
| Audit periodico | `/steward` → scorecard gate/hooks/freeze |

Template Makefile: [`makefile-template.mk`](../a-harness/references/makefile-template.mk)  
Scaffold: [`harness-scaffold.md`](../a-harness/references/harness-scaffold.md)

---

## 9. Prompt pronti all’uso

**Cycle standard**

```
@a-harness /cycle per {nome}.
Bounded context: {Context} ({path}/).
Contratto: {path/.feature o US}.
Non chiedermi attenzione finché make ready-for-review non è verde.
```

**Solo pianificazione**

```
@a-harness /slice
Proponi slice medium per: {obiettivo}.
Elenca ≤4 file, acceptance criteria, termini glossario. Non scrivere codice.
```

**Ripresa sessione**

```
@a-harness /progress
Poi continua da dove eravamo in Act, senza rifare lo slice se già accettato.
```

**Infra**

```
@a-harness /steward
Verifica make ready-for-review, freeze, e se ci sono always/never da promuovere a Make/hooks.
```

---

## 10. Errori frequenti (umani)

| Errore | Meglio |
|--------|--------|
| Interrompere a metà GREEN per “vedere se funziona” | Aspettare `/ready` o chiedere `/progress` |
| Slice vago → PR enorme | Rifare `/slice` più stretto |
| Chiedere discovery prodotto a a-harness | `@a-po` / `@a-gherkin` |
| Scalare 5 agent in parallelo su monolite legacy | Un cycle alla volta; CI solida prima |
| Merge senza capire l’intent | Fallisce il DoD “human can explain” |

---

## 11. Dove approfondire

| Documento | Contenuto |
|-----------|-----------|
| [harness-engineering.md](harness-engineering.md) | Meta: omonimi, maturity, evoluzione |
| [harness-architecture.md](../a-harness/references/harness-architecture.md) | Five-layer + seven-stack |
| [discovery-pipeline.md](discovery-pipeline.md) | Pipeline po → gherkin → harness |
| [permission-modes.md](../a-harness/references/permission-modes.md) | Plan vs Act |
| [bootstrap-profiles.md](../a-harness/references/bootstrap-profiles.md) | minimal \| standard |
| [extension-template.md](../a-harness/extension-template.md) | Skill L2 di progetto |
| [§13 Riferimento comandi](#13-riferimento-comandi-man) | Pagine man: slash, L0, Makefile |
| [discovery-pipeline.md](discovery-pipeline.md) § Slash di dominio | Comandi upstream (`a-personas`, `a-jtbd`, `a-gherkin`) |

---

## 13. Riferimento comandi (man)

Indice: [bootstrap(1)](#bootstrap1) · [cycle(1)](#cycle1) · [green(1)](#green1) · [learn(1)](#learn1) · [makefile-targets(7)](#makefile-targets7) · [progress(1)](#progress1) · [ready(1)](#ready1) · [red(1)](#red1) · [refactor(1)](#refactor1) · [slice(1)](#slice1) · [steward(1)](#steward1) · [sync(1)](#sync1)

Convenzione: `(1)` = comandi utente/slash; `(7)` = target Makefile Platform API. Formato ispirato a `man(1)` Linux.

---

<a id="bootstrap1"></a>

```text
BOOTSTRAP(1)                    a-harness                    BOOTSTRAP(1)

NOME
       bootstrap — scaffold harness su repository greenfield o senza gate

SINTASSI
       @a-harness /bootstrap [profile]

DESCRIZIONE
       Crea o adatta l'infrastruttura minima di harness nel repo target:
       Makefile (Platform API), file progress, e — con profile standard —
       glossario, bounded-context map, skill L2 e template learnings.

       Non implementa feature di prodotto. Non sostituisce `/steward` per
       evoluzione post-bootstrap (profile creator).

MODALITÀ
       minimal    Makefile gate (test-unit, pre-commit, ready-for-review)
                  + progress file. Per eval fairness o greenfield snello.

       standard   minimal + docs/glossary.md + docs/bounded-contexts.md
                  + skill L2 + permission modes + session learnings.
                  Default produzione.

       creator    Evoluzione preset L2, freeze, hooks, scorecard.
                  Solo via /steward, non in bootstrap iniziale.

PERMISSION MODE
       Act — scrive file scaffold nel repo target.

CONDIZIONI DI USCITA
       make ready-for-review raggiungibile (adapter stack compilati in Makefile).
       Senza make test reali non scalare autonomia multi-slice.

ESEMPI
       @a-harness /bootstrap profile standard

       @a-harness /bootstrap minimal
       Repo nuovo: solo gate Make + progress, niente glossario.

VEDI ANCHE
       bootstrap-profiles.md, harness-scaffold.md, makefile-template.mk,
       platform-api(7), steward(1)
```

---

<a id="cycle1"></a>

```text
CYCLE(1)                        a-harness                        CYCLE(1)

NOME
       cycle — sequenza TDD completa su uno slice medium

SINTASSI
       @a-harness /cycle [descrizione slice]

DESCRIZIONE
       Esegue in sequenza: /slice → handoff Act → /red → /green → /refactor
       → /ready. Registra eventi nel file progress append-only.

       In /slice (Plan): clarify ambiguità e analyze allineamento
       contratto ↔ glossario ↔ BC ↔ file. Dopo /ready, residui → nuovo
       /slice (converge Spec Kit) — non silent expand.

       Loop lieve verify/retry/stop — non un agent loop autonomo multi-slice.
       Non saltare fasi. Non richiedere review umana prima di /ready verde.

PERMISSION MODE
       Plan in /slice; Act nelle fasi R/G/Rf/ready.

CONDIZIONI DI USCITA
       /ready completato con make ready-for-review = 0, oppure hard exit
       (stuck@3, timeout) con flush progress.

ESEMPI
       @a-harness /cycle

       Slice: aggiungere rate limiting a POST /api/auth/login
       usando il middleware già in /api/users.
       Contratto: .cursor/product/features/auth-login.feature
       Bounded context: Auth (src/modules/auth/)
       Non chiedermi attenzione finché make ready-for-review non è verde.

       @a-harness /cycle per validazione InvoiceLine.
       Bounded context: Billing (src/modules/billing/).

VEDI ANCHE
       slice(1), red(1), green(1), refactor(1), ready(1), progress(1),
       when-stuck, handoff-from-gherkin.md, github-spec-kit-source.md
```

---

<a id="green1"></a>

```text
GREEN(1)                        a-harness                        GREEN(1)

NOME
       green — implementazione produzione minima (fase GREEN TDD)

SINTASSI
       @a-harness /green

DESCRIZIONE
       Persona Driver: scrive il codice produzione minimo YAGNI per far
       passare i test creati in RED. Vietate astrazioni premature, refactoring
       e nuove feature. Dati esterni solo tramite adapter (ACL).

       Autocorregge errori meccanici (lint, type) senza disturbare l'umano.

PERMISSION MODE
       Act — scrive codice produzione nel perimetro slice (≤4 file).

CONDIZIONI DI USCITA
       make test-unit && make pre-commit
       Exit code 0.

       Dopo 3 fallimenti sullo stesso approccio → when-stuck: stop, flush
       progress, chiedi umano o fork slice.

ESEMPI
       @a-harness /green
       Slice già accettato; test RED falliscono per logica mancante.

       @a-harness /green
       Continua da /progress — fase GREEN, test auth-login.feature.

VEDI ANCHE
       red(1), refactor(1), tdd-green, anti-corruption-layer,
       functional-core, when-stuck
```

---

<a id="learn1"></a>

```text
LEARN(1)                        a-agentzero                      LEARN(1)

NOME
       learn — cattura e consolida apprendimenti da sessione chat

SINTASSI
       @a-harness /learn
       @a-harness /learn ?
       @a-harness /learn ! [filtro]

DESCRIZIONE
       Utility L0 ereditata da a-agentzero. Estrae preferenze, convenzioni
       e pattern stabili emersi in chat. Non sovrascrive sicurezza L0.
       Non consolidare credenziali o task one-off.

MODALITÀ
       (nessun suffisso)
                  Mostra sintassi; chiede ? o !.

       ?            Riflessione — report apprendimenti, zero scrittura su disco.

       ! [filtro]   Consolidamento — persiste in skill L2, brand, rules;
                  se necessario Attività in ./ToDo.md e/o docs locali.
                  Diff minimo; bump patch + CHANGELOG delle skill toccate.
                  Filtro opzionale limita le voci consolidate.

PERMISSION MODE
       ? = read-only; ! = Act (scrive file target del repo).

ESEMPI
       @a-harness /learn ?
       Report: cosa è emerso in questa sessione, target proposti per !.

       @a-harness /learn !
       Consolida convenzioni progetto in .cursor/skills/harness-progetto/.

       @a-harness /learn ! solo notazione minuti

VEDI ANCHE
       a-agentzero/learn/SKILL.md, consolidation-targets.md, sync(1)
```

---

<a id="makefile-targets7"></a>

```text
MAKEFILE-TARGETS(7)             a-harness             MAKEFILE-TARGETS(7)

NOME
       makefile-targets — Platform API deterministica del repo target

SINTASSI
       make test-unit
       make pre-commit
       make check-standards
       make test-int
       make test-e2e
       make ready-for-review
       make db-up          (opzionale)
       make seed-data      (opzionale)

DESCRIZIONE
       Il Makefile root è l'unica verità meccanica per l'agente. Non usare
       script ad hoc non documentati. Solo steward (o /bootstrap) modifica
       questi target in routine.

TARGET
       test-unit
              Test unitari dello slice corrente.
              Gate RED (exit ≠ 0) e GREEN/REFACTOR (exit = 0).

       pre-commit
              Lint, format, typecheck. Gate GREEN (exit = 0).

       check-standards
              Alias o wrapper di pre-commit.

       test-int
              Test integrazione. Opzionale: @true + doc L2 se N/A.

       test-e2e
              Test end-to-end. Opzionale: @true + doc L2 se N/A.

       ready-for-review
              Gate finale sustainable-pace: check-standards + test-unit +
              test-int + test-e2e. Exit 0 = autorizzazione a /ready e review
              intent umana.

       db-up, seed-data
              Ambiente DB effimero e seed dati test, se applicabile.

CONDIZIONI DI USCITA
       Ogni target restituisce exit code shell standard (0 = successo).
       ready-for-review = 0 è prerequisito per dichiarare lavoro finito.

ESEMPI
       make test-unit
       Verifica fase RED: deve fallire per logica mancante.

       make ready-for-review
       Gate pre-review: lint + tutti i test configurati.

VEDI ANCHE
       makefile-template.mk, platform-api, sustainable-pace, ready(1),
       steward(1)
```

---

<a id="progress1"></a>

```text
PROGRESS(1)                     a-harness                     PROGRESS(1)

NOME
       progress — stato sessione append-only e ripresa lavoro

SINTASSI
       @a-harness /progress

DESCRIZIONE
       Legge (e riassume) il file .cursor/product/agent-progress.md:
       session_id, fase corrente, ultimi eventi, exit code make, stuck count.

       History append-only — non riscrive eventi passati. Fork = nuovo
       session_id da checkpoint. Se file assente, crea da template e segnala
       fresh session.

PERMISSION MODE
       Plan / read-only (lettura e riassunto; append solo se sessione attiva).

ESEMPI
       @a-harness /progress

       @a-harness /progress
       Poi continua da dove eravamo in Act, senza rifare lo slice se già accettato.

VEDI ANCHE
       session-progress, agent-progress-template.md, cycle(1), when-stuck
```

---

<a id="ready1"></a>

```text
READY(1)                        a-harness                        READY(1)

NOME
       ready — gate finale e checklist proof pre-review umana

SINTASSI
       @a-harness /ready

DESCRIZIONE
       Esegue make ready-for-review. Se exit 0, emette checklist PR-as-proof
       (scope file, commit message, assenza placeholder lazy-delete).

       Autorizza la review umana su **intent** («è quello che volevamo?»),
       non su lint/test (già coperti dal gate).

       Vietato richiedere review, aprire PR o dichiarare finito prima di
       ready-for-review = 0.

PERMISSION MODE
       Act — esegue make; può appendere evento exit al progress file.

CONDIZIONI DI USCITA
       make ready-for-review exit 0 → handoff umano per review intent.
       Exit ≠ 0 → autocorreggi o esci con when-stuck/steward.

ESEMPI
       @a-harness /ready
       Dopo /refactor completato; verifica gate e checklist.

VEDI ANCHE
       sustainable-pace, pr-proof-checklist.md, makefile-targets(7), cycle(1)
```

---

<a id="red1"></a>

```text
RED(1)                          a-harness                          RED(1)

NOME
       red — scrittura test che falliscono (fase RED TDD)

SINTASSI
       @a-harness /red

DESCRIZIONE
       Persona Navigator: scrive SOLO test (unit o integration) per lo slice
       corrente. Divieto assoluto di modificare codice produzione.

       Il test deve fallire dimostrando logica mancante, non errore di
       sintassi o setup. Se passa senza implementazione → test insufficiente.

PERMISSION MODE
       Act — scrive file test nel perimetro slice (≤4 file).

CONDIZIONI DI USCITA
       make test-unit
       Exit code ≠ 0 (fallimento per logica mancante).

ESEMPI
       @a-harness /red
       Slice accettato: scenario auth-login.feature → test Go/TS/Python.

       @a-harness /red
       Bounded context Billing; termini da docs/glossary.md.

VEDI ANCHE
       green(1), slice(1), tdd-red, aggregate-root, ubiquitous-language,
       bounded-context
```

---

<a id="refactor1"></a>

```text
REFACTOR(1)                     a-harness                     REFACTOR(1)

NOME
       refactor — pulizia sotto rete di test verdi (fase REFACTOR TDD)

SINTASSI
       @a-harness /refactor

DESCRIZIONE
       Elimina duplicazioni reali, zavorra (codice morto, import inutili),
       allinea nomi a docs/glossary.md. Comportamento invariato.

       Non introdurre nuove feature né astrazioni non motivate da duplicazione
       misurabile. Se test rossi → torna a green o red.

PERMISSION MODE
       Act — modifica codice nel perimetro slice.

CONDIZIONI DI USCITA
       make test-unit (o suite L2) exit 0; comportamento invariato.

ESEMPI
       @a-harness /refactor
       GREEN completato; rimuovi duplicazione handler e allinea glossario.

VEDI ANCHE
       green(1), ready(1), tdd-refactor, ubiquitous-language
```

---

<a id="slice1"></a>

```text
SLICE(1)                        a-harness                        SLICE(1)

NOME
       slice — definisce e accetta perimetro medium di implementazione

SINTASSI
       @a-harness /slice [obiettivo]

DESCRIZIONE
       Fase Plan/read-only: propone slice medium con ≤4 file, acceptance
       criteria verificabili, termini glossario, bounded context, effort
       (fast|thorough), pattern di riferimento esistente nel repo.

       Apre o aggiorna progress file con session_id. Non scrive codice
       produzione finché lo slice non è accettato dall'umano (handoff Act).

PERMISSION MODE
       Plan — no write filesystem (eccetto note progress se sessione aperta).

CONDIZIONI DI USCITA
       Slice accettato esplicitamente → autorizzazione a /red o /cycle Act.
       Slice rifiutato → ripianifica con perimetro più stretto.

ESEMPI
       @a-harness /slice
       Proponi slice medium per: rate limit su POST /api/auth/login.
       Elenca ≤4 file, acceptance criteria, termini glossario.
       Non scrivere codice.

       @a-harness /slice
       Bug: doppio addebito su InvoiceLine duplicata.
       Contratto: billing-invoice.feature scenario "…"

VEDI ANCHE
       permission-modes.md, context-budget, sustainable-pace, cycle(1),
       handoff-from-gherkin.md
```

---

<a id="steward1"></a>

```text
STEWARD(1)                      a-harness                      STEWARD(1)

NOME
       steward — audit e evoluzione infrastruttura harness (fabbrica)

SINTASSI
       @a-harness /steward [focus]

DESCRIZIONE
       Persona Platform Engineer AI: custode Makefile, CI, hooks, freeze,
       scorecard gate/hooks/freeze. Promuove regole always/never ripetute
       a hook o target Make.

       Non implementa feature di prodotto. Non inventa secondo agent loop.
       Profile creator (preset L2, hooks recipe) solo via steward.

PERMISSION MODE
       Act — modifica infra (Makefile, CI, rules, L2 harness skill).

ESEMPI
       @a-harness /steward
       Verifica make ready-for-review, freeze, always/never da promuovere.

       @a-harness /steward
       Audit pre-merge main: ciclo R/G/R rispettato, commit con perché.

VEDI ANCHE
       steward competency, steward-audit-checklist.md, cursor-hooks-recipe.md,
       component-decision.md, bootstrap-profiles.md (creator), freeze-template.md
```

---

<a id="sync1"></a>

```text
SYNC(1)                         a-agentzero                       SYNC(1)

NOME
       sync — deploy agenti L0/L1 e verifica allineamento versioni

SINTASSI
       @a-harness /sync
       @a-harness /sync ?
       @a-harness /sync !
       @a-harness /sync < [path-progetto ...]

DESCRIZIONE
       Utility L0 ereditata da a-agentzero. Pubblica skill/agents/comandi
       in ~/.cursor (e ~/.claude). Verifica extends-version STALE. Analizza
       skill L2 per candidati promozione L1/L0.

MODALITÀ
       (nessun suffisso)
                  Mostra sintassi; chiede ?, ! o <.

       ?            Report catene versioni + stato comandi L0; zero deploy.

       ! [path...]  Esegue deploy-all.sh + report. Path opzionali per scan L2.

       < [path...]  Analisi generalizzazione L2→L1/L0; zero scrittura.
                  Report DUP | L1 | L0 | NEED-N; conferma utente prima di edit.

ESEMPI
       @a-harness /sync ?
       Report: a-harness 1.1.1 OK, comandi L0 MISSING?

       @a-harness /sync !
       Deploy HAL → ~/.cursor/skills e ~/.cursor/commands.

       @a-harness /sync < /var/www/mio-progetto
       Candidati promozione da skill L2 copywriter-mio-progetto.

VEDI ANCHE
       a-agentzero/sync/SKILL.md, deploy-all.sh, agent-versioning.md,
       l2-generalization.md, learn(1)
```

---

## 14. TL;DR

1. Contratto + Makefile + (meglio) glossario.  
2. `@a-harness /cycle` con slice **medium** e «non disturbarmi fino a ready verde».  
3. Conferma lo **slice** (Plan: clarify + analyze) prima del codice.  
4. Review **intent** dopo `/ready`, non la meccanica; residui → nuovo `/slice` (converge).  
5. Se stuck@3 o gate rotto → tu decidi; `/steward` per la fabbrica.  
6. Spec Kit / SDD: mapping in `a-harness/references/github-spec-kit-source.md` (no CLI obbligatoria).
