# PR / Ready proof checklist

Usare in `/ready` prima di handoff umano. Human review = **intent**, non «funziona?».

## Obbligatorio

- [ ] `make ready-for-review` exit **0** (incolla log sintetico)
- [ ] Scope file entro budget (≤4) o waiver documentato
- [ ] Acceptance criteria dello `/slice` soddisfatti
- [ ] Nessun placeholder lazy-delete (`// ... existing code ...`, `...` che cancella codice)
- [ ] Commit con **perché** architetturale
- [ ] PR / diff budget: preferire **&lt;400 LOC** netti; altrimenti spezza

## Proof del gate (exit fresco)

- [ ] Exit **0** da un run **fresco** post-diff dello slice corrente — non citare log «Gate OK» / `ready=0` di uno slice precedente
- [ ] Non pipe-are `make` su `| tail` (o altro sink) senza `pipefail`: altrimenti l’exit del Make è mascherato. Preferire `bash -c 'make ready-for-review; echo MAKE_EXIT:$?'` (o equivalente L2 con flock)
- [ ] Progress `ready … | 0` / `exit flush` solo se `MAKE_EXIT:0` (o banner Gate OK) è **osservato** nel log di quel run — non su gate running/killed/parziale

## Intent (umano)

- [ ] Un umano può spiegare cosa fa lo slice in 2 frasi (anti shadow-code)
- [ ] Allineato a glossario / bounded context

## Opzionale L2 UI

- [ ] Screenshot / note computer-use se progetto UI
- [ ] Video demo — solo se pipeline progetto lo supporta (non richiesto da a-harness)

Pin: [cursor-cloud-harness-source.md](cursor-cloud-harness-source.md)
