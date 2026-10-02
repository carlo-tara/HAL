# Sezione 9 — Artifact e Versioni

Da aggiungere in coda al PRD **solo se il PO chiede esplicitamente** di tracciare gli artifact digitali collegati al prodotto (dashboard, tracker, mockup, script, export, ecc.). Non di default: appesantisce documenti senza artifact da versionare.

## Struttura

### 9.1 Artifact attivo (corrente)

Solo la versione più recente di ciascun artifact:

| Artifact | Tipo | Versione | Data | Descrizione | Path / link | Stato |
|----------|------|----------|------|-------------|-------------|-------|
| {nome} | HTML / Doc / Script / altro | v1.x | YYYY-MM-DD | Cosa contiene / delta vs precedente | | attivo |

### 9.2 Storico versioni artifact

Append-only — non cancellare righe storiche anche se il link non è più raggiungibile:

| Artifact | Versione | Data | Principali modifiche |
|----------|----------|------|----------------------|
| {nome} | v1.0 | | Prima release |
| {nome} | v1.1 | | |

### 9.3 Storico versioni del documento PRD

| Versione documento | Data | Changelog |
|--------------------|------|-----------|
| 1.0 | | Prima stesura |
| 1.1 | | |

## Convenzione di versioning (artifact)

SemVer semplificato:

- **Major (X.0)** — Nuova Epic completata o cambio architetturale significativo
- **Minor (x.Y)** — Nuove User Story o feature rilevanti sull'artifact
- **Patch (x.y.Z)** — Aggiornamenti dati / fix (tipico su artifact con dati frequenti; raro sul solo testo PRD)

## Regola pratica

Il link in "Artifact attivo" punta **sempre** alla versione corrente; lo storico tiene i link precedenti. Se manca un path/UUID, chiedilo al PO — non inventare placeholder.
