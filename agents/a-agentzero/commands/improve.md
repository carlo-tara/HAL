---
model: orcarouter/deepseek/deepseek-v4-flash
model-fallback: cursor-default
---

# Miglioramenti (L0)

## Objective

Analizzare e proporre (o applicare con approvazione) miglioramenti mirati al codice o alle skill del **repository corrente**, senza refactor gratuiti.

## Process

1. **Contesto**: identificare file/area in lavorazione dal task o dal diff.
2. **Qualità** (solo ciò che ha senso nel contesto):
   - Duplicazioni evitabili, nomi chiari, percorsi d'errore gestiti
   - Coerenza con convenzioni del repo (`README`, linter, skill L2)
   - Performance o DX solo se evidenti e a basso rischio
3. **Sicurezza**: niente segreti in codice; credenziali solo da `.env` del progetto.
4. Dopo modifiche sostanziali: eseguire le verifiche tipiche del repo (test, build, lint) se disponibili.
5. Evitare di "pulire" file non toccati dal task.
6. Se si modificano skill agenti: bump `version` + CHANGELOG e, se serve, `/sync` / `/version`.

## Checklist

- [ ] Miglioramenti pertinenti al task corrente
- [ ] Nessun refactor di massa non richiesto
- [ ] Verifiche post-edit eseguite o motivate
- [ ] Nessun path hardcoded a progetti non correlati
- [ ] Nessun segreto introdotto

## Expected output

- Elenco suggerimenti prioritizzati
- Se applicati: diff sintetico + esito verifiche

## Usage

```
/improve
```

## Notes

- Baseline L0: `a-agentzero/commands/improve.md` (pubblicata da `/sync !`).
- Override progetto: `{repo}/.cursor/commands/improve.md` se presente.
- Per revisione mirata al diff usare `/review`.
