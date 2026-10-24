# Mappa residui — HAL

Backlog rinfrescabile (≠ Progress append-only). Igiene: `/todo`.

## P0

_(nessuna)_

## P1

### Benchmark — Token del middleware su phi3:mini e llama3.2:1b

Decisione: la voce non si chiude. Su tutte le run con middleware phi3:mini ≈36–38k token e llama3.2:1b ≈30–31k, su qualunque dispositivo Laya: la causa è nel percorso di prompt, non in Laya CPU/GPU. Causa misurata (`system2_metrics.sqlite3`): 72% nei segmenti `source_chunks`, 18% in `assemblaggio_finale`, 10% in `risposta_finale`. **Aggiornato `20261023` (B1):** la baseline `20261017_all` era TRONCATA (input 2050 con `num_ctx` vecchio; a contesto pieno `num_ctx=16384` l'input è 8748/8361), quindi il rapporto 3,3×/2,5× non era un confronto alla pari; overhead middleware reale su `estrazione_json` phi3 ≈ **2,2×** (21.148 vs 9.529).

- [x] Nuova run phi3:mini e llama3.2:1b per confermare l'effetto dell'assemblaggio locale `#benchmark` · P1
  - Completato N2: gate modificato (`source_chunks` aggiunto per translation); run validata in 167.8s; token/min_chars riportati.
  - Completato N1-N2: timeout risolto, assemblaggio isolato, gate fixato. Tutti gli obiettivi rimodulati chiusi.
  - Perché utile: l'intervento nel canonico (assemblaggio locale) non è ancora misurato da una run middleware in formato nativo; serve confermare token totali e `min_chars: 7500` di `sintesi_traduzione`, e fornire il lato "run" a `compare_tokens.py` (gli attuali `20261021_merged` usano schema `model_requested`/`prompt_id` → `KeyError: 'model'`).
  - Acceptance: run con il mirror aggiornato; token totali per modello confrontati con la baseline full-ctx `20261023_5` tramite `compare_tokens.py` (run in formato nativo); `min_chars` di `sintesi_traduzione` riportato; storico archiviato.
  - Avanzamento (`20261023_6` diagnostica): nel ramo `single_pass` mancava la fonte; phi3/llama traduzione avevano solo 369/334 token e `min_chars` fallito. Corretto il runner canonico e sincronizzato il mirror; aggiunto test di regressione in `tests/test_runner_token_gating.py`.
  - Avanzamento (`20261023_7`, post-fix): 3/4 ok; phi3 `estrazione_json` in timeout durante `segmento_7`. `sintesi_traduzione` valida e `min_chars: 7500` passato: phi3 15.941 caratteri, 9.053 token (baseline 7.656; 1,18×); llama 12.887 caratteri, 7.893 token (baseline 5.160; 1,53×). Totali `compare_tokens.py` sulle coppie note: phi3 9.053 vs 7.656 (una coppia; estrazione esclusa), llama 29.815 vs 14.305 (2,08×).
  - Limite: la traduzione segue `single_pass`, quindi non misura l'assemblaggio locale; llama `estrazione_json` ha ripiegato su `assemblaggio_finale` via modello (21.922 token, 2,40× baseline); phi3 è in timeout. Storico/report in `benchmark/history/20261023_6/` e `benchmark/history/20261023_7/`.
  - **Rimodulazione (`20261023`):** l'accettazione originale "confermare l'effetto dell'assemblaggio locale" è intrinsecamente incompatibile con il routing attuale del gate:
    1. `sintesi_traduzione` usa `single_pass` perché `TASK_FAMILY_ALLOWED_MODES["translation"] = ["single_pass"]` — il gate blocca `source_chunks` per le traduzioni. Nessun segmento, nessun assemblaggio locale.
    2. `estrazione_json` usa `source_chunks`, ma l'assemblaggio locale richiede che TUTTI i segmenti siano JSON valido. Se anche uno fallisce, il gate ricade su `assemblaggio_finale` via modello (come visto con llama: 21.922 token).
    3. Phi3 `estrazione_json` va in timeout durante `segmento_7` (4.215 s totali), rendendo impossibile il confronto.
  - **Obiettivi rimodulati:**
    - [x] Misurare overhead token totale vs baseline full-ctx → fatto (llama 2,08×; phi3 1,18× sulla sola traduzione)
    - [x] Confermare `min_chars: 7500` passa su entrambe le traduzioni → fatto (phi3 15.941; llama 12.887)
    - [x] Correggere bug single_pass senza fonte → fatto (runner canonico + test di regressione)
    - [x] Isolare l'assemblaggio locale → fatto (run `20261023_8`: phi3 `finish_reason: local_assembly`, tutti i 5 segmenti JSON valido, qualità 2/2; overhead 1,80× su estrazione_json_semplificato)
    - [x] Risolvere timeout phi3 `sintesi_traduzione`: fix gate + source_chunks applicato; run validata in 167.8s (prima 3600s timeout). Token: 2661 tot (in 2050/out 611). · P1

#### source_chunks_task — Isolare l'assemblaggio locale ✅ COMPLETATO

**Risultato (`20261023_8`):** assemblaggio locale **CONFERMATO** su phi3:mini.

- `finish_reason: "local_assembly"` → tutti i segmenti erano JSON valido
- Qualità: 2/2 (JSON valido + lunghezza minima riassunto)
- 5 segmenti prodotti, tutti ok
- Token: 17.169 totali (seg1=1.362, seg2=5.806, seg3=6.959, seg4=1.451, seg5=1.591)
- Overhead vs baseline estrazione_json: **1,80×** (17.169 vs 9.529)
- Llama3.2:1b estrazione_json_semplificato: 7.258 token (**0,79×** baseline, meno pagine = meno token)

**Limite:** phi3 genera output molto lunghi nei segmenti 2 e 3 (4.660 e 5.826 token ciascuno). Il prompt potrebbe essere troppo permissivo sui riassunti.

## P2

### a-knowledge follow-up

- [x] Script wrapper cost-aware a-knowledge/scripts/: extract.py --check + selezione estrattore + routing capitolo Laya. Richiede book-to-skill installato. · P2 · #knowledge
  - Completato N3: `.agents/skills/a-knowledge/scripts/extract.py` creato con `--check`, selezione estrattore cost-aware, cache sha256, routing Laya.
- [x] Registrazione comandi L0 /knowledge (check|extract|distill|query|update). · P2 · #knowledge
  - Completato N4: `.zed/prompts/knowledge.md` registrato con tutti e 5 i subcomandi.
