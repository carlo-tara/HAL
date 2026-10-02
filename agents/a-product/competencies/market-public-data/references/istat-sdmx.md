# ISTAT SDMX — access playbook

UI: [esploradati.istat.it/databrowser](https://esploradati.istat.it/databrowser/)  
API base: `https://esploradati.istat.it/SDMXWS/rest`

## Discovery

1. Nel databrowser individua tema/dataflow e annota **dataflow id** (es. `IT1,22_289` o id numerico documentato).
2. Metadati: `GET .../dataflow/IT1?detail=allstubs` (Accept structure+json se supportato).
3. Guida comunitaria: [ondata guida-api-istat](https://ondata.github.io/guida-api-istat/).

## Data query

```
GET https://esploradati.istat.it/SDMXWS/rest/data/{flowRef}/{key}?startPeriod=YYYY&endPeriod=YYYY&lastNObservations=N
```

Content negotiation (esempi):

```bash
# CSV
curl -fsSL -H 'Accept: application/vnd.sdmx.data+csv;version=1.0.0' \
  "https://esploradati.istat.it/SDMXWS/rest/data/FLOW_ID?startPeriod=2020&endPeriod=2024&lastNObservations=50"

# JSON data (se accettato dal server)
curl -fsSL -H 'Accept: application/vnd.sdmx.data+json;version=1.0.0' \
  "https://esploradati.istat.it/SDMXWS/rest/data/FLOW_ID?lastNObservations=20"
```

Helper repo: `a-po/scripts/fetch-istat-sdmx.sh FLOW_ID [start] [end]`

## Vincoli

- Rate limit tipico: **~5 query/minuto/IP** — pausa tra chiamate
- Payload grandi: filtra periodo e `lastNObservations` / `firstNObservations`
- Endpoint `/rest/v2` può non essere disponibile; preferisci `/rest/data`
- Se la serie è vuota, verifica key dimensionale e workaround documentati dalla community (filtri temporali)

## Citation

`Fonte: ISTAT — {titolo dataflow/serie}; estratto via SDMX REST da esploradati.istat.it il {YYYY-MM-DD}`
