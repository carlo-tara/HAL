# Work Graph — Gating System 1/System 2

- **Source:** file (`ToDo.md`, P1 `#system1-gating`)
- **Goal:** rafforzare i gate S1/S2 in HAL Gateway usando le evidenze di `hal_system2`, senza copiarne il runtime.
- **BC:** routing ed esecuzione HAL Gateway
- **Auto-accept:** true (`-y`)
- **Multi-cycle:** true, sequenziale
- **Mode:** loop
- **Why mode:** un solo P1, un bounded context e un owner; le attività condividono il percorso Laya e vanno validate in sequenza. Un DAG aggiungerebbe graph-trap.
- **Next:** `cycle-baseline`

## Loop Spec

1. **`cycle-baseline` — `/cycle`**
   - Input: middleware, configurazione, test nativi gateway, dati benchmark.
   - Output: mappa dei punti d'integrazione e baseline tecnica/qualità per coppia modello-task; misurare separatamente overhead Laya, stato tecnico e rubriche euristiche.
   - Stop: baseline riproducibile e path di implementazione entro 4 file per slice.
   - Next: `cycle-preflight`.
2. **`cycle-preflight` — `/slice`**
   - Output: preflight locale sul contratto task; skip remoto per richieste atomiche semplici; invio a Laya del solo contesto essenziale.
   - Stop: test dimostrano skip, payload compatto e rispetto di fonte/formato.
   - Next: `cycle-coherence`.
3. **`cycle-coherence` — `/slice`**
   - Output: gate di coerenza famiglia/strategia/modalità; single-pass predefinito; plan-then-solve soltanto con scomponibilità esplicita e confidenza sufficiente.
   - Stop: incoerenze e bassa confidenza degradano in modo conservativo, senza perdere o scartare segmenti.
   - Next: `cycle-budget`.
4. **`cycle-budget` — `/slice`**
   - Output: limite alle chiamate Laya, decisioni intermedie solo se cambiano il flusso, retry limitati e motivati.
   - Stop: test verificano budget chiamate/retry e preservazione dei segmenti.
   - Next: `cycle-telemetry`.
5. **`cycle-telemetry` — `/slice`**
   - Output: eventi SQLite per run/fase/sistema/modello/task con latenza, caratteri, token se disponibili, decisione/confidenza, fallback ed errori; niente prompt o risposte.
   - Stop: test verificano aggregazione, token mancanti e assenza di contenuti sensibili.
   - Next: `cycle-compare`.
6. **`cycle-compare` — `/cycle`**
   - Output: test pertinenti e confronto baseline/candidato per modello-task, includendo overhead Laya e rubriche euristiche separate dallo stato tecnico.
   - Stop: acceptance del P1 soddisfatta o hard stop documentato; quindi chiudere ToDo.
   - Next: `—`.

**Hard stop:** `stuck@3`, test/gate non recuperabile, dipendenza da scelta umana o path consumer non determinabile. Ogni slice resta entro 4 file salvo waiver esplicito.
