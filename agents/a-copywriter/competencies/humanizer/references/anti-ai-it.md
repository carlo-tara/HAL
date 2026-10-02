# Anti-AI — copy italiano web

Merge di regole base + GuideStile (Humanizer, Emulazione 2026).  
Ispirazione processo/triage: [avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing) (EN; adattato IT).  
Catalogo IT / leak / Trova: [italiano-scrittura-anti-ai](https://github.com/mario-montanari/italiano-scrittura-anti-ai) (adattato; **senza** iniezione di anima).  
Processo dettagliato in [humanizer-loop.md](humanizer-loop.md).

Segnali di qualità, non prova di authorship. Bias verso **falsi negativi**: un singolo tropo non basta.  
Word-list = preferenza di gusto; segnali strutturali: [segnali-misurabili.md](segnali-misurabili.md).

---

## Processo (ogni output)

1. **Scrivi** draft (voce brand + struttura tipo contenuto) — o salta se input già scritto
2. **Audita** — elenca pattern con severità P0–P2 (formato sotto)
3. **Scegli strategia** — patch vs rewrite-from-scratch ([humanizer-loop.md](humanizer-loop.md))
4. **Loop avversariale** — interno; **second-pass** obbligatorio prima della consegna
5. **Riscrivi** final: stesso significato, lunghezza ±10%, zero P0, P1/P2 risolti secondo tolerance
6. **Verifica** ad alta voce + test Never inject

Modalità `detect` / `edit`: [humanizer-loop.md](humanizer-loop.md) § Modalità.

---

## Never inject (rewrite guardrails)

Umanizzare = **togliere e affilare**. Vietato aggiungere ciò che non era nel source / brief / brand:

| Vietato iniettare | Esempi da non inventare |
|-------------------|-------------------------|
| First person finto | *«L'ho visto mille volte»*, *«Nella mia esperienza»* se non nel source |
| Candore narrato / hook | *«Voglio essere sincero:»*, *«Ecco il punto»*, *«Il trucco?»* |
| Stakes / drama | urgenza o conflitto assenti dal brief |
| Dettagli inventati | cifre, nomi, date, texture «per concretezza» |
| Contrarianism forzato | opinione opposta solo per «suonare umani» |
| Oralità digitata stock | parentesi riflessive / fallibilità da template se il brand è formale |
| Em-dash theatrics / staccato | convertire prosa in drama a frammenti |

**Test:** ogni frase aggiunta in rewrite risponde a «era nel source o nel brand file?» — se no, taglia.

Carve-out: calibrazione su **campione utente** o esempi brand (allora la voce è autorizzata).  
Dettaglio oralità: [scrittura-umana.md](scrittura-umana.md) § Never inject.

---

## Severità P0 / P1 / P2

| Tier | Cosa | Azione |
|------|------|--------|
| **P0** | Chatbot opener/closer, attribution vaga, knowledge cutoff, filler preambolo, em/en dash, title case IT, Never-inject violation, errori grammatica LLM | Rimuovere sempre |
| **P1** | Vocabolario Tier A in cluster, promo/inflation, parallelismo negativo / leak, liste `**Header:**`, bullet wall, gap-filling, header-rincalzo, false range, metafora-viaggio >1 | Fix in rewrite; in detect: problema chiaro |
| **P2** | Rule of three, copula evasion, transizioni a catena, synonym cycling, hedge-stack, Tier B/C densità, participio parassita, frasi acefale | Fix se supera tolerance del tipo pubblicazione |

In audit elenca la severità accanto a ogni hit.

---

## Tier lessico IT

Non trattare wordiness come prova di AI. Tre bande:

| Banda | Ruolo | Quando flaggare |
|-------|-------|-----------------|
| **A — marker** | Frequenti in output LLM / brochure | Sempre in cluster (≥2 per testo o ≥2 stesso paragrafo); idealmente zero |
| **B — clarity** | Formalità gonfiata / wordiness | Sostituisci per leggibilità; **non** contano come authorship |
| **C — densità** | Parole comuni sovra-usate | Solo se densità alta (~3%+ o ripetizione ossessiva) |

### Banda A (marker) — evita in cluster

`cruciale`, `fondamentale`, `pivotale`, `paesaggio` (astratto), `panorama` (astratto), `ecosistema` (astratto), `testimonianza` / `testamento` (figurato), `faro`, `catalizzatore`, `vibrante`, `ricco tessuto` / *tapestry*-calco, `senza soluzione di continuità` (*seamless*), `navigare le sfide`, `sfruttare` / *leverage* gonfiato, `immergersi` / *delve* figurato, `incredibile`, `unico nel suo genere`, `rivoluzionario`, `innovativo` (senza prova), `soluzione completa`, `esperienza unica`, `connessione profonda`, `elemento distintivo`, `empowerment`, `unlock`, `level up`, `game-changer`, `must-have`, famiglia **metafora-viaggio** (*percorso, viaggio, bussola, mappa, tappa, orizzonte* figurati).

### Banda B (clarity) — preferisci semplice; non = AI

| ❌ | ✅ |
|----|-----|
| utilizzare | usare |
| al fine di / allo scopo di | per |
| effettuare una X | verbo diretto (*valutare*, *controllare*) |
| offrire la possibilità di | permette / puoi |
| in grado di | può |
| dare avvio / dare inizio | iniziare / partire |
| mettere in risalto / evidenziare / sottolineare (ripetuti) | mostra / dice / conta |

### Banda C (densità)

`profondo` (figurato), `sostanzialmente`, `decisamente`, `assolutamente`, `ricco di`, `si distingue per` (una volta OK), `robusto` (in tech spesso legittimo: non flaggare isolato).

### Soglie di densità (gusto, non authorship)

| Famiglia | Soglia |
|----------|--------|
| Aggettivi bandiera (banda A intensificatori) | max **1 / 500 parole** |
| Connettivi (*inoltre, tuttavia, pertanto, infatti…*) | max **1 / 3–4 frasi** |
| Metafora-viaggio | **0–1 / testo** |
| Formule «è importante sottolineare» | **zero** |
| Hit banda A totali | max **1–2 / testo** (idealmente zero) |

**Preferisci:** verbi semplici, nomi concreti, numeri e misure **già nel source** (se manca il numero → taglia l'aggettivo, non inventare).  
Banda B: taglia liberamente; banda C: solo densità.

---

## Vietato — frasi filler (IT)

| ❌ | ✅ | Sev. |
|----|-----|------|
| È importante notare che… | (elimina, vai al fatto) | P0 |
| In conclusione… / Per concludere… | (elimina o chiudi con pattern brand) | P0 |
| Inoltre… / In aggiunta… (a catena) | Una transizione o frase nuova | P2 |
| Vale la pena sottolineare che… | Dillo direttamente | P0 |
| Non solo X, ma anche Y (ripetuto) | Una sola costruzione per testo | P1 |
| Scopri / Esplora / Immergiti in… | Entra nel beneficio o nel prodotto | P0 |
| Se stai cercando di… / Esploriamo insieme… | (finto entusiasmo — elimina) | P0 |
| Perfetto per ogni occasione | Occasioni specifiche | P1 |
| Imperdibile / must-have / game-changer | Dettaglio concreto del perché | P1 |
| In un mondo in cui… / In un'epoca in cui… | (elimina) | P0 |
| Che tu sia un principiante o un esperto… | Scegli un livello o esempi concreti | P1 |
| Come abbiamo visto precedentemente… | (elimina preambolo) | P0 |
| In questo paragrafo esploreremo… | (elimina preambolo) | P0 |
| Voglio essere sincero: / Ecco il punto / Il trucco? / Qui sta il punto | Fatto diretto (senza hook) | P1 |
| Gli esperti dicono / Molti ritengono (senza fonte) | Fonte o taglia | P0 |
| Sulla base delle informazioni disponibili / Fino al mio ultimo aggiornamento | (knowledge cutoff — elimina) | P0 |
| Nel mondo di oggi / Nell'era digitale / Nel panorama attuale | (elimina) | P0 |
| Andiamo a vedere / Scopriamo insieme / Senza ulteriori indugi | Entra nel contenuto | P0 |

---

## Leak conversazionale (famiglia)

Radice: il testo risponde a una chat che il lettore non ha vissuto.  
**Test:** «Questo documento trovato online tra sei mesi tiene, senza il prompt?»

| Pattern | Esempio | Fix | Sev. |
|---------|---------|-----|------|
| Negazione che pianta un equivoco | *La SEO non è una formula magica, è…* | Afferma diretto; nega solo credenze reali e nominate | P1 |
| Suspense inutile | *Ecco la cosa: / Qui sta il punto: / La verità è che* | Vai al fatto | P1 |
| Riassunti frattali | *Come abbiamo visto… Ora vedremo…* | Attacca il contenuto | P0 |
| Domande in bocca al lettore | *Ti starai chiedendo… Andiamo a scoprirlo* | Domanda reale del titolo o elimina | P1 |

---

## Vietato — pattern strutturali e retorici

| Pattern | Fix | Sev. |
|---------|-----|------|
| **Rule of three** forzato | Max 2 elementi o uno specifico | P2 |
| **Sycophantic openers/closers** | *«Un viaggio che promette…»*, *«memorie indelebili»* → elimina | P0 |
| **Significance inflation** vaga | Solo se legato a dato/storia reale | P1 |
| **Inflated symbolism** | *testamento*, *faro*, *catalizzatore* → concreto | P1 |
| **Participio/gerundio parassita** | Test: cancella la coda (*evidenziando…*); se il senso resta → elimina | P2 |
| **Synonym cycling** | *cliente / utente / persona / soggetto* nello stesso paragrafo → ripeti il termine chiave | P2 |
| **Hedge-stack** | *potrebbe eventualmente*, *può potenzialmente* → una sola modalità o claim diretto | P2 |
| **Real/actual inflation** | *vera innovazione*, *reale valore aggiunto* senza contrasto → taglia o nomina il contrasto | P2 |
| **Gap-filling speculativo** | *probabilmente nacque…* inventati → solo fatti source | P1 |
| **Falsa concessione** | *Sebbene X abbia limiti, resta straordinario* → concessione onesta o claim proporzionato | P2 |
| **Evasione della copula** | *si configura come*, *funge da*, *vanta* → *è* / *ha* / *resta* | P2 |
| **Em dash / en dash** (`—`, `–`, ` -- `) | Punto, virgola, due punti, parentesi | P0 |
| **Liste con header bold** | Prosa continua o heading separati | P1 |
| **Header + frase di rincalzo** | Dopo H2 la prima frase non glossa il titolo | P1 |
| **Title case italiano** | *Come Ottimizzare la SEO* → *Come ottimizzare la SEO* | P0 |
| **False range** | *Dalla X alla Y* senza scala reale → elenca o taglia | P1 |
| **Esibizione di notabilità** | Elenco testate/follower → episodio source con data/fonte | P1 |
| **Schema sfide/prospettive** | *Nonostante le sfide… continua a crescere* → fatto o taglia | P1 |
| **Knowledge cutoff** | Dichiarazioni di aggiornamento modello → elimina | P0 |
| **Frase acefala** | *Importante anche il ruolo di X* → soggetto + verbo | P2 |
| **Box In sintesi ridondante** | Se ripete il corpo → taglia o un punto nuovo | P2 |
| **Conclusioni generiche** | Fatto o promessa brand misurata | P1 |
| **Aforismi formula** | Claim concreto sul beneficio | P1 |
| **Staccato drama** (4+ frasi brevi) | Una corta per enfasi, poi una lunga | P1 |
| **Promo da brochure** | Dati: materiale, misura, procedura | P1 |
| **Bullet wall** (5+ bullet) | Max 3 bullet o paragrafo narrativo | P1 |
| **Domande retoriche a catena** | Una sola, o elimina | P2 |
| **Connettivi iper-coesi** | *tuttavia* + *inoltre* stesso paragrafo → taglia | P2 |
| **Elenco simmetrico 3–5 voci** | Asimmetria, prosa mista | P2 |
| **Parallelismo negativo / leak** | *Non è X. È Y.* senza equivoco reale → claim positivo | P1 |

---

## Trova rapido (20 stringhe)

Scan meccanico pre-consegna (gusto + P0 evidenti). Hit → valuta contesto; non = prova di AI.

1. `Nel mondo di oggi`
2. `Nell'era digitale`
3. `Nel panorama attuale`
4. `È importante sottolineare`
5. `Vale la pena notare`
6. `si configura come`
7. `In conclusione`
8. `Per tirare le somme`
9. `Andiamo a vedere`
10. `Scopriamo insieme`
11. `Ti sei mai chiesto`
12. `Ti starai chiedendo`
13. `Come abbiamo visto`
14. `Ecco la cosa`
15. `Qui sta il punto`
16. `Sulla base delle informazioni disponibili`
17. `Fino al mio ultimo aggiornamento`
18. `nonostante le sfide`
19. `connubio tra`
20. `a 360 gradi`

Grammatica Trova: [grammatica-llm.md](../../italiano-locale/references/grammatica-llm.md).

---

## Cosa NON è AI (preserva)

- Metafora ancorata a materiale, colore, sapore, texture + dettaglio tecnico
- Storytelling con date, nomi, procedure verificabili **già nel source**
- Chiusura identitaria da brand file
- Registro poetico/evocativo **se** brand file lo prevede
- Fallibilità / oralità **solo** se coerente con brand o campione (altrimenti Never inject)
- Liste vere: changelog, ingredienti, parametri API, confrontature feature
- Contrasto onesto nominato (*reale X, non Y* con Y esplicito)
- Citazioni ed esempi in documentazione skill (self-reference: non auto-flaggare il corpus)
- *Inoltre* / *si distingue per* isolati (non a catena)
- Dislocazioni / frase scissa ([scrittura-umana.md](scrittura-umana.md))

**Segnale AI = cluster di pattern**, non una singola metafora calibrata.

---

## Audit — formato output

```markdown
### Audit anti-AI
- Mode: rewrite | detect | edit
- Severity: P0 […] | P1 […] | P2 […]
- Tier lessico: A […] | B […] | C densità […]
- Leak conversazionale: [negazione finta / suspense / frattale / domande in bocca — o nessuno]
- Struttura / retorica: [es. header-rincalzo, false range, title case]
- Trova: [stringhe hit]
- Never inject risk: [frasi che aggiungerebbero fatti/voce assenti — o nessuno]
- Strategia: patch | rewrite-from-scratch (motivo)
- Criptoinglese / falsi amici: […]
- Fix applicati: [1 riga per categoria]   ← ometti in mode detect
- Second-pass: [residui trovati / clean]
```

In **detect**: dopo l'audit, sezione *Assessment* (problema chiaro vs judgment call). Nessun rewrite.  
Poi, in **rewrite**/**edit**, consegna la **versione finale** senza ripetere l'audit nel corpo del copy (salvo richiesta utente).

---

## Checklist rapida

- [ ] Zero em/en dash (P0)
- [ ] Zero filler P0 / finto entusiasmo / knowledge cutoff / title case
- [ ] Trova 20 stringhe eseguito
- [ ] Zero leak conversazionale non giustificato
- [ ] Max densità banda A / metafora-viaggio / connettivi
- [ ] Banda B ridotta dove gonfia senza bisogno
- [ ] Zero corporate slop / falsi amici (italiano-locale)
- [ ] Grammatica LLM OK (italiano-locale / grammatica-llm)
- [ ] Nessuna violazione Never inject
- [ ] P0 risolti; P1/P2 entro tolerance del tipo pubblicazione
- [ ] Almeno 2 dettagli concreti **già verificabili nel source** (non inventati)
- [ ] Frasi di lunghezza variata (burstiness)
- [ ] Chiusura coerente con brand file
- [ ] Second-pass eseguito
- [ ] Suona naturale ad alta voce
