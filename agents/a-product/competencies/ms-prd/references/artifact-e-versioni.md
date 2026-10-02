# Sezione 8 — Artifact e Versioni

Da aggiungere in coda al PRD **solo se il PO chiede esplicitamente** di tracciare artifact digitali (dashboard, tracker, mockup, script, ecc.).

## Struttura

### 8.1 Artifact attivo (corrente)

Solo la versione più recente di ciascun artifact:

| Artifact | Tipo | Versione | Data | Descrizione | Path / link | Stato |
|----------|------|----------|------|-------------|-------------|-------|
| {nome} | HTML / Doc / Script / altro | v1.x | YYYY-MM-DD | Delta vs precedente | | attivo |

### 8.2 Storico versioni artifact

Append-only — non cancellare righe storiche:

| Artifact | Versione | Data | Principali modifiche |
|----------|----------|------|----------------------|
| {nome} | v1.0 | | Prima release |
| {nome} | v1.1 | | |

### 8.3 Storico versioni del documento PRD

| Versione documento | Data | Changelog |
|--------------------|------|-----------|
| 1.0 | | Prima stesura |
| 1.1 | | |

## Convenzione di versioning (artifact)

- **Major (X.0)** — Nuova Epic completata o cambio architetturale significativo
- **Minor (x.Y)** — Nuove User Story o feature rilevanti sull'artifact
- **Patch (x.y.Z)** — Aggiornamenti dati / fix (tipico su artifact con dati frequenti)

Il link in "Artifact attivo" punta sempre alla versione corrente. Se manca un path, chiedilo al PO — non inventare.
