# Pin — ashmht/cursor-harness (MIT)

**URL:** https://github.com/ashmht/cursor-harness  
**Licenza:** MIT · **Ruolo AF:** pattern session/progress, non dipendenza runtime

## Adottato in a-harness

| Pattern | Dove |
|---------|------|
| Progress file di sessione | `session-progress`, template `agent-progress.md` |
| When stuck (3 fail → stop/escalate) | `when-stuck` |
| FCIS / functional core | `functional-core` |
| PR budget (&lt;400 LOC) | `sustainable-pace` |
| Session learnings + eviction | template `session-learnings.md` |
| Harness changelog | template `harness-changelog.md` |

## Non adottato

- Clone del repo come tool obbligatorio
- Regole monolitiche senza Makefile gate
