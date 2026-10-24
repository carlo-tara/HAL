# Mappa residui — HAL

Backlog rinfrescabile (≠ Progress append-only). Igiene: `/todo`.

## P0

_(nessuna)_

## P1

- [ ] Handoff da hal_system2: rafforzare il gating System1/System2 in HAL Gateway #system1-gating · P1
  - Avanzamento: gate 1 implementato in `system1_preflight.is_atomic_short_low_risk` (soglia `PREFLIGHT_SHORT_MAX_CHARS = 400`, `complexity=atomic`, `risk_level=low`) e `LayaSystemOneService.preflight` (`abstain` / `preflight_skipped_atomic`, nessun consumo di budget); coperto da test. Il gate equivalente `laya_recommended` in `benchmark/runner/benchmark_models.py` (copia di `hal_system2/app/`) non è stato toccato. Restano aperti i gate successivi.
  - Perché utile: mantenere le decisioni System 1 pertinenti al task, ridurre latenza/token del coordinamento e impedire che classificazioni incerte scartino contenuto o generino retry inutili.
  - Gate proposti:
    1. Eseguire un preflight locale sul prompt e sui metadati disponibili (famiglia task, complessità, fonte/lunghezza, formato e vincoli) prima di chiamare Laya; saltare il preflight remoto per richieste atomiche, brevi e a basso rischio.
    2. Passare a Laya un contratto compatto del task e contesto essenziale; non inviare l’intera fonte o l’intero artefatto quando bastano metadati/estratti.
    3. Verificare la coerenza tra famiglia prevista, strategia e modalità scelte da Laya (es. traduzione ≠ estrazione); il gate locale prevale su scelte incompatibili.
    4. Usare single-pass come default; consentire plan-then-solve solo per richieste esplicitamente decomponibili e con confidenza sopra soglia; segmentare solo fonti lunghe e rispettare i limiti di pagina/intervallo.
    5. Applicare fallback conservativi a ogni decisione sotto soglia: mai scartare una fonte, ripetere una fase o attivare una pianificazione solo per una decisione Laya incerta. Retry limitati e ammessi solo quando una decisione sufficientemente confidente può cambiare il flusso.
    6. Ridurre le chiamate Laya a un preflight utile e a sole decisioni intermedie capaci di cambiare il flusso; eliminare classificazioni generiche per segmento e verifiche/ripetizioni ridondanti del single-pass.
    7. Registrare in SQLite eventi per run/fase/sistema/modello/task: modalità, stato, latenza, caratteri, token disponibili, scelta, confidenza, fallback ed errori; aggregare per run/task/modello. Non salvare contenuti di prompt o risposte; distinguere token misurati da quelli non disponibili.
  - Acceptance: ispezionare prima middleware, configurazione e test nativi di hal_gateway; implementare i gate applicabili senza copiare il runtime di hal_system2 né crearne uno alternativo; aggiungere test per coerenza task-strategia, skip del preflight semplice, fallback low-confidence, preservazione dei segmenti e limite chiamate/retry; confrontare baseline e nuova run per coppia (modello, test), includendo overhead Laya in latenza/token e separando status tecnico, rubriche euristiche e validazione semantica indipendente; richiedere latenza serving comparabile, distinguere la durata end-to-end che include il caricamento modello e bloccare la promozione con output troncati o evidenza mancante; eseguire i test pertinenti.

- [x] Correggere i passi di test in `.github/workflows/ready-for-review.yml`: i file `test_*.py` sono in `tests/`, quindi `python3 test_gateway_core.py` fallisce con `No such file or directory`; usare `PYTHONPATH=. python3 tests/test_*.py` #infra · P1
  - Perché utile: tutti gli step di test del workflow puntano alla root, ma i file sono in `tests/`; in locale il comando corretto è `PYTHONPATH=. python3 tests/test_gateway_core.py` (eseguito con successo, 11 test).
  - Acceptance: tutti gli step test del workflow passano in CI; verificare lanciando i comandi del workflow dalla root del repo.
  - Fatto: step riscritti con `python3 -m unittest tests.<modulo>` (`PYTHONPATH=.` a livello di job), installazione di `requirements-dev.txt`, aggiunti `test_router_score`, `test_runner_token_gating`, `test_benchmarks`. Tutti i 18 comandi `run:` lanciati dalla root escono 0; l'esito su GitHub Actions non è verificato.

- [x] Aggiungere un cooldown configurabile tra i modelli nel runner benchmark, o rendere il generatore ricorsivo #benchmark · P1
  - Perché utile: il runner non ha pause tra run; la run 20261019_3 è stata fatta con una run per modello e uno script con `sleep 180`. Il generatore legge solo i JSON nella cartella indicata, quindi le sottocartelle vanno aggregate a mano.
  - Acceptance: `--cooldown` (o equivalente) nel runner canonico di hal_system2, con un'unica cartella di run; oppure `generate_benchmark_report.py` legge le sottocartelle; test di regressione.
  - Fatto: `--cooldown SECONDI` nel runner canonico `hal_system2/app/benchmark_models.py` (pausa solo tra modelli, validazione finita ≥ 0), mirror nel gateway con `diff` vuoto; 3 test in `hal_system2/tests/` (suite completa 190 verdi, non committata) e 2 nel gateway. Il generatore resta non ricorsivo.

- [ ] Verificare i timeout di `qwen2.5:1.5b` su prompt lunghi (`estrazione_json`, `sintesi_traduzione`) #benchmark · P1
  - Perché utile: la run 20261019_3 ha 2 timeout a 600 s su questi test; i risultati non sono confrontabili su quei test.
  - Acceptance: determinare se il problema è il timeout o il modello (rilanciare con `--timeout` più alto e `--prompt` mirati); documentare la causa.
  - Progresso: nella run `20261020_2` phi3:mini va in timeout su `estrazione_json` (1172 s registrati, limite 600 s). Anche run precedenti superano 600 s su timeout (qwen 694,9 s; phi3 `sintesi_traduzione` 1102 s in `20261020_1`): verificare se il limite si applica per tentativo (retry) prima di cambiare il valore.
  - Causa del tempo >600 s (verificata su telemetria, 9 workflow con stage in errore): il limite di 600 s è `httpx.Client(timeout=...)`, quindi vale **per singola chiamata**, mentre `seconds` nel report è la durata dell'intero workflow (somma degli stage). Es. phi3:mini `estrazione_json` 1172,0 s = 571,9 s di stage riusciti + 600,1 s dello stage in timeout; ogni stage in errore dura esattamente 600 s. Non ci sono retry. Gli stage in errore non registrano token (nessun dato sul costo del tentativo).
  - **Ancora aperto**: se i timeout siano limite o modello (serve rilanciare con `--timeout` più alto e `--prompt` mirati sullo stage fallito: 7 dei 9 errori sono in `segmento_N`/`assemblaggio_finale`); i risultati su quei test restano non confrontabili.

- [ ] Isolare l'effetto di Laya su CPU vs GPU sul tempo per chiamata #benchmark · P1
  - Perché utile: nella run 20261019_3 tre variazioni sono avvenute insieme (Laya su CPU, middleware nuovo, cooldown); la mediana del tempo per chiamata è salita su phi3 (87→169 s), llama3.2:3b (45→126 s) e qwen (27→91 s).
  - Acceptance: run con middleware nuovo e Laya su GPU, stesse condizioni; confronto per coppia (modello, test) nel report.
  - Progresso: run `20261020_1` eseguita (Laya su GPU, pausa 300 s invece di 180 s, quindi condizioni non identiche). Tempi misti, token invariati: Laya CPU/GPU non spiega il tetto dei token. Ripetizione `20261020_2` (phi3:mini e llama3.2:3b, stesse condizioni, pausa 300 s): tempi ancora misti (phi3 141→197 s, llama3.2:3b 172→152 s), nessun effetto stabile di Laya GPU. Serve almeno un confronto con Laya CPU alla stessa pausa per chiudere il punto.

- [ ] Verificare l'aumento dei token del middleware nuovo su phi3:mini e llama3.2:1b #benchmark · P1
  - Perché utile: i token totali sono circa 3 volte quelli della baseline 20261017_all (≈34k contro ≈11k); i dati non spiegano il motivo.
  - Acceptance: identificare il percorso di prompt che genera i token in più (misurati vs non disponibili in SQLite) e documentare la causa.
  - Progresso: la run `20261020_1` conferma ≈31–38k token su phi3:mini e llama3.2:1b anche con Laya su GPU, quindi la causa è nel middleware, non nel dispositivo di Laya. Ripetizione `20261020_2`: su phi3:mini l'eccesso resta sui test con input lungo (`sintesi_traduzione` 12,1k token; `estrazione_json` in timeout); su llama3.2:3b `estrazione_json` 19,4k e `sintesi_traduzione` 13,4k.
    - Causa misurata (`system2_metrics.sqlite3`, 430,8k token su 11 run, 256 stage System 2 ok): il 72% è nei segmenti `source_chunks` (~1,1k token in per segmento da ~3,4k caratteri), il 18% nell'`assemblaggio_finale` (78,5k; 37,8k solo per la traduzione), il 10% in `risposta_finale`. Nella traduzione l'assemblaggio con modello restituisce in mediana ~25% del testo dei segmenti (solo 1 caso su 12 ≥ 100%), il che spiega anche `min_chars: 7500` a 0/2 in `sintesi_traduzione`.
    - Intervento: `hal_system2/app/` (canonico, commit `9a2ff01`/`c9b7cbb`) ha già assemblaggio locale (traduzione, segmento unico, JSON valido), `--segment-max-tokens` e stop su troncamento; la copia del gateway è stata riallineata (`diff` vuoto). Non ancora misurato da una run: serve una nuova run per confermare token e `min_chars` di `sintesi_traduzione`. Misura attuale (`get_token_breakdown`): 51,9k token (12%) sono sprecati in workflow poi falliti. Candidato non implementato: ridurre il blocco `<strategia_system1_laya>` ripetuto in ogni stage (stima ~3%, non misurata, rischio qualità non verificato).

- [ ] Riallineare `extends-version` dei sette L1 e di `harness-agentfactory` dopo il bump di `a-agentzero` a 1.8.6 #version-sync · P1
  - Perché utile: `make -C agents version-chains` (quindi `ready-for-review`) fallisce con `STALE` su tutti i L1 (`extends: a-agentzero @ 1.8.5` contro padre 1.8.6); il fallimento è preesistente (stesso esito sullo stato committato, introdotto da `a65bdba`).
  - Acceptance: `make -C agents ready-for-review` esce 0; ogni L1 bumpato con voce CHANGELOG pertinente (verificare prima in `a-agentzero/CHANGELOG.md` se i cambi 1.8.6 richiedono adeguamenti agli L1 o solo il pin).

## P2

- [x] Sincronizzare automaticamente `generate_benchmark_report.py` tra `hal_gateway/benchmark/scripts/` e `hal_system2/scripts/` #benchmark · P2
  - Perché utile: oggi la copia è manuale; i due file sono identici solo dopo `cp`.
  - Acceptance: una sola sorgente, o uno script di sync con verifica `diff`.
  - Fatto: `benchmark/scripts/sync_hal_system2.sh check|apply` (canonico `hal_system2` → mirror) copre generatore, runner e metriche; 6 test in `tests/test_sync_hal_system2.py` su cartelle temporanee, inclusi in CI. `check` sulle copie reali esce 0. Lo script non è agganciato a un hook: va lanciato a mano o da CI con `hal_system2` presente.

- [x] Allineare la versione dei wrapper CLI generati con la sorgente canonica #version-sync · P2
  - Perché utile: `link-workspace-skills.sh` imposta `version: 1.0.0` nei wrapper `SKILL.md`, quindi una versione bumpata sul wrapper generato può essere persa al sync successivo.
  - Acceptance: definire una sola sorgente della versione; il bump seguito da due sync mantiene versione e contenuto idempotenti; aggiungere test di regressione.
  - Fatto: sorgente unica = `version:` nel frontmatter del comando canonico (`agents/a-agentzero/commands/<cmd>.md`, default `1.0.0`); `link_zed_skill` la legge (`command_version`, formato semver validato) e lo script è *sourceable* per i test. `version.md` porta ora `version:` (1.2.1, poi bump minor a 1.3.0). Due sync consecutivi: hash identici per i 10 wrapper e i prompt Zed. 6 test in `tests/test_link_workspace_skills.py`, in CI. Il bump va fatto sul canonico, non sul wrapper.

## Già fatto

_(nessuna)_

## P2

### a-knowledge follow-up

- [ ] Script wrapper cost-aware a-knowledge/scripts/: extract.py --check + selezione estrattore + routing capitolo Laya. Richiede book-to-skill installato. · P2 · #knowledge
- [ ] Registrazione comandi L0 /knowledge (check|extract|distill|query|update). · P2 · #knowledge
