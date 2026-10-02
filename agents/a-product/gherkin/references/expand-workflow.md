# Expand workflow (`/expand` e `/cover`)

## `/cover` — completezza inventory

1. Costruisci/aggiorna inventory UI + IO su tutto il prodotto (o slice PO)
2. Diff vs Scenario esistenti in `features/*.feature`
3. Proponi Scenario mancanti (cluster nei file flusso giusti)
4. Documenta waiver espliciti (controllo non testabile / out of scope)
5. Draft → conferma PO → `/export`

## `/expand` — edge su happy esistenti

1. Seleziona happy path / journey di partenza
2. Scegli famiglie da [expand-catalog.md](expand-catalog.md) rilevanti all'inventory
3. Aggiungi Scenario/Outline nel **file del flusso** (non nuovi file inutili)
4. Evita duplicare `/secure`/`/perf`
5. Draft → conferma → export

## Ordine consigliato suite nuova

`/create` (seeds + inventory baseline) → `/cover` (chiude UI/IO) → `/expand` (edge) → `/secure` `/perf` se needs → `/validate`
