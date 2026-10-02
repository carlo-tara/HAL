# Cascade triage (pipeline discovery)

Quando un agente in sessione esegue `/triage` e l’impatto esce dal proprio layer, **segnala** il next slash — non modificare in silenzio gli artefatti degli altri agenti.

```
a-personas /triage
  → check | update | create | add  (se persona/flow a rischio)
  → escalate a-jtbd /triage        (se personas stabili ma job/UI binding mossi)

a-jtbd /triage
  → map | refine | unmet | add-story | add-need | prioritize
  → escalate a-gherkin /triage     (se jtbd/seeds cambiano)

a-gherkin /triage
  → validate | refine | expand | add-scenario | secure | perf
  → escalate a-jtbd | a-personas   (se manca upstream)
```

## Regole

- Cascade = **segnalazione + next slash**, non pipeline autonoma senza PO
- Nessun agent fa `/export` sugli artefatti di un altro layer
- Dual-runtime (Cursor/Claude): indica all’utente di invocare l’altro skill/subagent
