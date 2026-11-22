# Apprendimenti — catena side-car Auto Ontology (2026-11-20)

Estratti dalla sessione `ao-sidecar-governance` (HT-013 → AO-1/AO-1.1/AO-2). Routing `/learn !` con `router.py routing` (skill|ToDo|docs|escludi). Riversamento nei target canonici rinviato a **HT-015** perché `learn/` e `session-learnings` erano sporchi di WIP parallelo (stessa causa di HT-012).

## 1. Il flush ToDo appiattisce le voci chiuse multi-bullet

- **Cosa:** `todo_flush` (→ `agent-todo.py`) sposta in CHANGELOG la sola riga-titolo di una voce `[x]`; il corpo a più bullet (Perché/Acceptance/Esito) **non sopravvive**. L'Esito di una voce destinata a chiudersi va scritto **in riga** (formato HT-010), non in sub-bullet.
- **Evidenza:** voce HT-013 flushata alla riga 108 di `CHANGELOG.md` senza i 4 sub-bullet; Esito re-inlineato manualmente.
- **Ambito:** HAL · **Destinazione:** tool-pitfalls (via HT-015) + qui.

## 2. Un contratto di guardia non deve asserire sul backlog

- **Cosa:** gli assert di una guardia persistente devono puntare a **sedi stabili** (slice, docs, altri contratti), mai a `ToDo.md`: il flush rimuove le voci chiuse e l'assert diventa falso a invariante intatto. Corollario: un assert «la voce X referenzia il contratto» va riscritto come «la slice Y referenzia il contratto» quando la voce si chiude.
- **Evidenza:** `check-ontology-bc-boundary.sh` tornato RED dopo il flush di HT-013 (assert 4 su ToDo), verde solo dopo inasprimento su sede slice.
- **Ambito:** HAL · **Destinazione:** tool-pitfalls/contratti (via HT-015) + qui.

## 3. Smoke di boot MCP: usare comando **e env** esatti della entry

- **Cosa:** verificare un side-car con il solo comando della entry Zed testa il **default** del server, non la configurazione: senza env il server ha esposto 35 tool (set `all`), con l'env della entry 13 (set `answer`, datasource nascosti). Il gate contestuale (KPI-1) va misurato con lo stesso `command`+`args`+`env` che useranno i client.
- **Evidenza:** doppio handshake stdio del 2026-11-20 (`tools/list` 35 vs 13); righe `ao-2-boot-smoke`/`ao-2-env-verify` in `product/state/agent-progress.md`.
- **Ambito:** HAL · **Destinazione:** docs (qui) + rituale bump nel pin file.

## 4. `router.py choice --json` non emette `request_hash`

- **Cosa:** il binding CLI di Laya non espone l'hash della decisione: i **voti di calibrazione** (`laya_outcome`/`chapter_outcome`) non sono esprimibili per decisioni prese via CLI; solo il tool MCP lo restituisce. Se il voto serve, la decisione va presa via MCP (o l'hash va recuperato dal log del servizio).
- **Evidenza:** scelta del bump a-knowledge (override «major»→minor) senza hash → voto non registrato; famiglia del pitfall già notato il 2026-11-17 (`auto_vote_routing`, exit 0 ≠ voto).
- **Ambito:** HAL · **Destinazione:** tool-pitfalls (via HT-015).

## 5. Deviazione di path per sudo non interattivo: registrarla, non subirla

- **Cosa:** quando un path canonico in un piano richiede privilegi non ottenibili in sessione agente (`sudo` con password), non bloccare: deviare su una path user-writable che **conserva le proprietà rilevanti** (pin, isolamento dal workspace, riproducibilità), e registrare deviazione + procedura di ripristino nel registro del componente (pin file) e nei docs.
- **Evidenza:** `/opt/auto-ontology-mcp` → `~/auto-ontology-mcp`; deviazione documentata in `agents/a-knowledge/references/auto-ontology-source.md` e PRD §4/§6.
- **Ambito:** HAL · **Destinazione:** docs (qui).

## 6. Pin di runtime ≠ corpus vendor: due pattern distinti

- **Cosa:** `agents/vendor/` è per **corpus da distillare** (gitignored, mapping in references, `l1-from-proto`). Un **runtime esterno** (MCP side-car) non è un corpus: il clone vive fuori dal bundle, ma il **pin file** (SHA + version + misure + rituale di aggiornamento) vive in `references/` della skill che lo consuma, con blocco `PIN:START/END` riusabile dagli script. Da precisare in `l1-from-proto.md` (oggi dice solo «vendor+pin se aggiornabile»).
- **Evidenza:** `auto-ontology-source.md` creato come primo esemplare; PRD §5 non-goal Livello B.
- **Ambito:** HAL · **Destinazione:** l1-from-proto (via HT-015) + qui.

## 7. Il «success» di edit_file e l'output troncato non sono evidenza di completamento

- **Cosa:** in un turno lungo (catena AO-2.2) ho rivendicato scritture mai avvenute: una sezione in un file **inesistente** (`bootstrap.sh`, con tanto di numeri di riga citati a memoria), un bump harness-hal 1.1.0 mai scritto, e un «link dangling» che dangling non era (il file esiste). Scoperto dall'audit del turno dopo: grep sul file reale → 0 hit. Corollari: (a) ogni affermazione «file X contiene Y» va ri-verificata con read in una chiamata **separata e successiva** alla scrittura; (b) l'output troncato/collassato non è evidenza — se non si vede, non si asserisce; (c) `edit_file` può riportare «success» senza applicare l'edit targeted (caso reale: fix indentazione dichiarato applicato, file invariato) — le modifiche di precisione su testo unicode/whitespace vanno fatte con python ancorato a righe e riverificate con `git diff`.
- **Evidenza:** audit 2026-11-22: `grep -c "Ontology sidecar" harness-hal/SKILL.md` → 0; `find agents -name bootstrap.sh` → assente; poi fix reale (§Bootstrap 17 righe, 1.1.0+CHANGELOG, AO-2.2 nel PRD, `check-registry` che verifica la transazione esistente).
- **Ambito:** HAL · **Destinazione:** tool-pitfalls via HT-015 (estensione §Strumenti replay/stale + nuova regola di chiusura turno).

## Esclusi (anti-grasso)

- «Batch di tool call con dipendenze su file produce esiti falsi» → **già** in `tool-pitfalls.md` § «Tool call paralleli nella stessa risposta: collisione su stato condiviso» (la ricaduta di stasera — guardia GREEN da race — è una conferma, non una voce nuova).
- I task chiusi della sessione (AO-1/1.1/2) → non apprendimento.
