# Toth — indice del canone (v0)

Regola d'ingaggio: **Toth registra, non decide.** In v0 l'unica voce
deterministica è `toth_index.py`: gemello meccanico del catalogo
«hal-contract» (stesse liste L1/BUNDLED/PROJECT_SKILLS/COMMANDS, stesso
parser `fm_field`/`shorten` di `agents/scripts/hal-contract.py`), senza
regole proprie e senza toccare il traffico.

## Artefatto

- File: `references/toth-index.json` (`schema: 1`).
- Una voce per fonte del canone: `name`, `kind` (agent|bundled|project|command),
  `path` (relativo alla radice, pronto per `read`), `host` (owner dei bundled),
  `parent` (`extends:` per gli L1), `version`, `description` (shorten ≤150),
  `present`.
- `metadata.drift` = `kind:token` delle voci listate la cui sorgente non
  esiste: è il valore di v0 (il fence le salta in silenzio). Se
  `present: false`, o la lista del contratto è stale o manca il bundle.

## Uso

```
python3 agents/a-agentzero/scripts/toth_index.py            # rigenera
python3 agents/a-agentzero/scripts/toth_index.py --check    # exit 1 su drift
```

- L'artefatto si rigenera, **non si edita a mano** (sort_keys + liste
  d'ordine = byte-deterministico).
- Guardie: `tests/test_toth_index.py` (fake tree + canone reale +
  freshness); `--check` pronto per il gate CI (slice successivo).
- Il gate del canone (check-registry) pretende la transazione
  versione+CHANGELOG di `a-agentzero` quando cambia questo bundle.

## v1 (non ancora attiva)

Il dispatcher System 1 su richieste in entrata NON esiste: nessuna
deviazione del traffico, nessun `hint` per uso. La regola di ammissione
resta quella della tabella di delega Laya (verde = esecuzione diretta solo
se margin alto e k≤3; giallo/rosso = sempre System 2). Prima di scrivere
regole di dispatch servono dati: l'indice è il prerequisito, non la
promessa.

## Manutenzione (imparato alla prima settimana di vita)

- Ogni transazione che tocca liste-fonte o versioni delle skill rigenera
  l'artefatto nello stesso commit: un derivato committato marcisce in ore
  (evidenza: `737d776` bump learn senza rigenerazione → `--check` rosso su
  master, assorbito in `a11571c`). Il binding `--check` al gate è il passo
  successivo (`HT-018`).
- Le invarianti cross-file (es. `COMMAND_SOURCE_OVERRIDES` ↔ `LAYASRC` del
  publisher) vivono come test che legge l'altro file, non come commento
  (`test_override_tied_to_publisher`, `a11571c`).
- Un drift segnalato può essere difetto della guardia, non del canone:
  prima di cancellare/ripristinare una fonte, verificare cosa controlla
  l'indice (caso laya: falso negativo, l'indice guardava la directory
  sbagliata).
