# Mappa residui — HAL

Backlog rinfrescabile (≠ Progress append-only). Igiene: `/todo`.

## P0

_(nessuna)_

## P1

- [ ] Handoff da hal_system2: rafforzare il gating System1/System2 in HAL Gateway #system1-gating · P1
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

- [ ] Correggere i passi di test in `.github/workflows/ready-for-review.yml`: i file `test_*.py` sono in `tests/`, quindi `python3 test_gateway_core.py` fallisce con `No such file or directory`; usare `PYTHONPATH=. python3 tests/test_*.py` #infra · P1
  - Perché utile: tutti gli step di test del workflow puntano alla root, ma i file sono in `tests/`; in locale il comando corretto è `PYTHONPATH=. python3 tests/test_gateway_core.py` (eseguito con successo, 11 test).
  - Acceptance: tutti gli step test del workflow passano in CI; verificare lanciando i comandi del workflow dalla root del repo.

- [ ] Aggiungere un cooldown configurabile tra i modelli nel runner benchmark, o rendere il generatore ricorsivo #benchmark · P1
  - Perché utile: il runner non ha pause tra run; la run 20261019_3 è stata fatta con una run per modello e uno script con `sleep 180`. Il generatore legge solo i JSON nella cartella indicata, quindi le sottocartelle vanno aggregate a mano.
  - Acceptance: `--cooldown` (o equivalente) nel runner canonico di hal_system2, con un'unica cartella di run; oppure `generate_benchmark_report.py` legge le sottocartelle; test di regressione.

- [ ] Verificare i timeout di `qwen2.5:1.5b` su prompt lunghi (`estrazione_json`, `sintesi_traduzione`) #benchmark · P1
  - Perché utile: la run 20261019_3 ha 2 timeout a 600 s su questi test; i risultati non sono confrontabili su quei test.
  - Acceptance: determinare se il problema è il timeout o il modello (rilanciare con `--timeout` più alto e `--prompt` mirati); documentare la causa.

- [ ] Isolare l'effetto di Laya su CPU vs GPU sul tempo per chiamata #benchmark · P1
  - Perché utile: nella run 20261019_3 tre variazioni sono avvenute insieme (Laya su CPU, middleware nuovo, cooldown); la mediana del tempo per chiamata è salita su phi3 (87→169 s), llama3.2:3b (45→126 s) e qwen (27→91 s).
  - Acceptance: run con middleware nuovo e Laya su GPU, stesse condizioni; confronto per coppia (modello, test) nel report.

- [ ] Verificare l'aumento dei token del middleware nuovo su phi3:mini e llama3.2:1b #benchmark · P1
  - Perché utile: i token totali sono circa 3 volte quelli della baseline 20261017_all (≈34k contro ≈11k); i dati non spiegano il motivo.
  - Acceptance: identificare il percorso di prompt che genera i token in più (misurati vs non disponibili in SQLite) e documentare la causa.

## P2

- [ ] Sincronizzare automaticamente `generate_benchmark_report.py` tra `hal_gateway/benchmark/scripts/` e `hal_system2/scripts/` #benchmark · P2
  - Perché utile: oggi la copia è manuale; i due file sono identici solo dopo `cp`.
  - Acceptance: una sola sorgente, o uno script di sync con verifica `diff`.

- [ ] Allineare la versione dei wrapper CLI generati con la sorgente canonica #version-sync · P2
  - Perché utile: `link-workspace-skills.sh` imposta `version: 1.0.0` nei wrapper `SKILL.md`, quindi una versione bumpata sul wrapper generato può essere persa al sync successivo.
  - Acceptance: definire una sola sorgente della versione; il bump seguito da due sync mantiene versione e contenuto idempotenti; aggiungere test di regressione.

## Già fatto

_(nessuna)_
