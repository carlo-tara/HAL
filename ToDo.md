# Mappa residui — HAL

Backlog rinfrescabile (≠ Progress append-only). Igiene: `/todo`.

## P0

- [ ] Riallineare le catene `extends-version` che bloccano il gate Make `#infra` · P0
  - Perché utile: `make -C agents test-unit` si ferma prima dei test gateway perché sette L1 e L2 `harness-agentfactory` risultano STALE.
  - Acceptance: il report `make -C agents version-chains` non contiene `STALE` e `make -C agents test-unit` termina con codice 0; riallineamenti e changelog seguono il flusso sync selettivo.
- [ ] Rendere obbligatori in CI i test del gateway `#infra` · P0
  - Perché utile: il workflow esistente è in `agents/.github/workflows/ready-for-review.yml`, ascolta `main` ed esegue il gate degli agenti; non copre i test Python del gateway nel repository root.
  - Acceptance: `ready-for-review` esegue `test_gateway_core.py` e `test_agent_llm_config.py`; la workflow è in `.github/workflows/` alla root e attiva su push e pull request del branch predefinito; un test fallito rende CI non verde.

## P1

- [ ] Distinguere astensione e fallback Laya da una decisione valida `#bug` · P1
  - Perché utile: in caso di indisponibilità Laya restituisce il primo candidato o score `0.95`, che il chiamante può scambiare per una decisione affidabile.
  - Acceptance: indisponibilità o risposta non valida produce uno stato esplicito `fallback`/`abstain`, non un punteggio di alta confidenza; il risultato degradato non viene memorizzato come decisione valida e il chiamante applica una policy prudente.
- [ ] Integrare redaction e scansione PII prima della persistenza degli eventi `#infra` · P1
  - Perché utile: le primitive di redaction non proteggono i dati finché non sono collegate al punto di scrittura; il fallimento della scansione non deve essere interpretato come assenza di PII.
  - Acceptance: test d’integrazione invia segreti e PII sintetici e verifica che non siano persistiti in chiaro; un errore della scansione è rappresentato come esito incerto e non come controllo superato.
- [ ] Applicare retention, cifratura e accesso controllato ai log eventi `#infra` · P1
  - Perché utile: redaction da sola non limita conservazione e accesso a prompt, codice e dati personali.
  - Acceptance: purge automatico applica le retention documentate (body 30 giorni, metadati 12 mesi); volume e backup sono cifrati e l’accesso ai dati grezzi è limitato e verificabile.
- [ ] Collegare `SystemTwoEngine` a un provider reale e verificare il modello servito `#feature` · P1
  - Perché utile: `execute()` restituisce attualmente una stringa dimostrativa, quindi la selezione del modello non corrisponde a un’inferenza verificabile.
  - Acceptance: `execute()` invoca il backend configurato e restituisce la risposta con il modello effettivamente servito; un test con backend mock verifica invocazione e fallback.
- [ ] Selezionare il provider System 2 per profilo d’uso, capability e modello condiviso `#feature` · P1
  - Perché utile: l’attuale mappa per agente può assegnare modelli diversi ai subagent e non considera capability, contesto, budget o salute del provider.
  - Acceptance: la selezione dipende dal profilo d’uso, non dall’identità dell’agente; filtra per capability e vincoli del profilo, mantiene `ACTIVE_MODEL_NAME` come fallback condiviso e non accetta da Laya un nome modello arbitrario.
- [ ] Definire la policy di instradamento System 1/System 2 e la riduzione del budget System 2 `#feature` · P1
  - Perché utile: il dispatcher attuale sceglie solo in base al nome del task e non considera rischio, complessità, tool o affidabilità della decisione Laya.
  - Acceptance: tabella e test distinguono decisioni chiuse risolvibili da System 1, generazione semplice a basso rischio e richieste complesse/ambigue/con side-effect; System 2 si riduce tramite contesto, token e tool budget mantenendo lo stesso modello; astensione, errore o rischio elevato impediscono la riduzione.
- [ ] Validare policy e selezione modello con replay, shadow e metriche `#infra` · P1
  - Perché utile: il risparmio di chiamate o token non dimostra qualità e non basta per promuovere una nuova configurazione.
  - Acceptance: replay offline e shadow su richieste sicure misurano qualità/outcome, errori, correzioni utente, latenza e costo; la promozione richiede un gate positivo e dispone di rollback.
- [ ] Integrare la cache L1 Redis oltre il calcolo della chiave `#feature` · P1
  - Perché utile: il codice calcola una chiave ma non serve né invalida risposte tramite cache runtime; chiavi basate solo sui path possono non rilevare modifiche ai contenuti.
  - Acceptance: lettura/scrittura Redis applica TTL per profilo e hash del contenuto dei file rilevanti; una modifica causa miss; risposte con tool rispettano i limiti di cache documentati; hit/miss hanno provenance negli eventi.
- [ ] Integrare il circuit breaker nella risoluzione e nel fallback dei provider `#feature` · P1
  - Perché utile: la state machine isolata non evita richieste a provider degradati e lo stato half-open attuale consente più probe concorrenti.
  - Acceptance: errori e timeout nella finestra configurata aprono il breaker, il resolver salta il provider aperto e ammette un solo probe half-open; test coprono recupero e fallback.
- [ ] Aggiungere un controllo segreti low-noise al gate CI `#infra` · P1
  - Perché utile: riduce il rischio di committare credenziali nel codice o nella configurazione.
  - Acceptance: un segreto sintetico in fixture viene rilevato senza stamparne il valore; repository pulito passa e le eccezioni sono esplicite.
- [ ] Dichiarare e sottoporre ad audit le dipendenze runtime del gateway `#infra` · P1
  - Perché utile: senza inventario delle dipendenze dirette non si possono rilevare vulnerabilità note o drift in modo riproducibile.
  - Acceptance: un manifest elenca le dipendenze runtime effettive e il gate CI esegue l’audit; un advisory di test fa fallire il controllo.
- [ ] Aggiungere SAST Python a basso rumore per il codice gateway `#infra` · P1
  - Perché utile: la scansione segreti e l’audit dipendenze non intercettano difetti nel codice applicativo.
  - Acceptance: lo scanner gira in CI sul perimetro gateway; il baseline è pulito oppure le eccezioni sono motivate e tracciate.
- [ ] Ripristinare il comando Laya `score` `#bug` · P1
  - Perché utile: `router.py score` termina con `NameError` e blocca i controlli euristici dei workflow Harness e Product.
  - Acceptance: un test CLI copre la risposta numerica; `python3 router.py score "test" --criteria "relevance"` termina con codice 0.
- [ ] Allineare stato delle funzionalità e indice della documentazione `#docs` · P1
  - Perché utile: README/changelog presentano primitive non integrate come complete e l’indice elenca schede non presenti; entrambe le discrepanze possono generare assunzioni operative errate.
  - Acceptance: cache, redaction e circuit breaker sono etichettati come prototipo, integrati o verificati; ogni voce dell’indice punta a un file esistente o è marcata come pianificata, con conteggio coerente.

## P2

- [ ] Allineare i riferimenti agli hook Cursor ai file mantenuti `#infra` · P2
  - Perché utile: il Makefile dichiara percorsi di hook assenti e può saltarli silenziosamente.
  - Acceptance: ogni hook dichiarato esiste ed è verificato oppure il riferimento è rimosso con motivazione; nessun hook richiesto viene saltato.
- [ ] Misurare i percorsi caldi prima di introdurre ottimizzazioni `#spike` · P2
  - Perché utile: batch Laya seriali, scansioni regex della redaction e allocazioni nella normalizzazione sono possibili costi, ma non ci sono benchmark che ne provino l’impatto.
  - Acceptance: benchmark ripetibile misura batch Laya per dimensione, redaction e normalizzazione su input rappresentativi; registra round trip, tempo e memoria senza soglie temporali instabili in CI; si apre un’ottimizzazione solo se il costo è materiale.

## Già fatto

_(nessuno)_
