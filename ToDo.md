# Mappa residui — HAL

Backlog rinfrescabile (≠ Progress append-only). Igiene: `/todo`.

## P0

_(nessuna)_

## P1

### Benchmark — Token del middleware su phi3:mini e llama3.2:1b

Decisione: la voce non si chiude. Su tutte le run con middleware phi3:mini ≈36–38k token e llama3.2:1b ≈30–31k, su qualunque dispositivo Laya: la causa è nel percorso di prompt, non in Laya CPU/GPU. Causa misurata (`system2_metrics.sqlite3`): 72% nei segmenti `source_chunks`, 18% in `assemblaggio_finale`, 10% in `risposta_finale`. **Aggiornato `20261023` (B1):** la baseline `20261017_all` era TRONCATA (input 2050 con `num_ctx` vecchio; a contesto pieno `num_ctx=16384` l'input è 8748/8361), quindi il rapporto 3,3×/2,5× non era un confronto alla pari; overhead middleware reale su `estrazione_json` phi3 ≈ **2,2×** (21.148 vs 9.529).

#### source_chunks_task — Isolare l'assemblaggio locale ✅ COMPLETATO

**Risultato (`20261023_8`):** assemblaggio locale **CONFERMATO** su phi3:mini.

- `finish_reason: "local_assembly"` → tutti i segmenti erano JSON valido
- Qualità: 2/2 (JSON valido + lunghezza minima riassunto)
- 5 segmenti prodotti, tutti ok
- Token: 17.169 totali (seg1=1.362, seg2=5.806, seg3=6.959, seg4=1.451, seg5=1.591)
- Overhead vs baseline estrazione_json: **1,80×** (17.169 vs 9.529)
- Llama3.2:1b estrazione_json_semplificato: 7.258 token (**0,79×** baseline, meno pagine = meno token)

**Limite:** phi3 genera output molto lunghi nei segmenti 2 e 3 (4.660 e 5.826 token ciascuno). Il prompt potrebbe essere troppo permissivo sui riassunti.
