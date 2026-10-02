# Agent progress (append-only)

Path suggerito: `.cursor/product/agent-progress.md` (o `docs/harness/agent-progress.md`).

```markdown
# Agent progress

- session_id: {uuid-or-timestamp}
- started: {ISO-8601}
- slice: {nome-slice}
- effort: fast | thorough
- profile: minimal | standard
- ownership: {agente/sessione}
- forked_from: {session_id|none}

## Events (append-only — non riscrivere history)

| ts | phase | event | detail | make_exit |
|----|-------|-------|--------|-----------|
| … | slice | accepted | files: a,b,c | — |
| … | red | attempt | test X failing as expected | 1 |
| … | green | attempt | … | 0 |
| … | stuck | fail_3 | see when-stuck | — |
| … | ready | gate | ready-for-review | 0 |
| … | exit | flush | reason: done|timeout|stuck | — |
```

## Regole

1. Solo **append** su Events
2. Flush on exit / hard exit / timeout
3. Fork = nuovo file o nuova sezione session_id; non mutare history precedente
4. Offload output grandi qui o in file dedicati (context-budget)
