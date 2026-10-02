# Pin — harness.lol Cursor adapter — omonimo

**URL:** https://www.harness.lol/docs/agents/cursor  
**Ruolo AF:** permission modes + resume; **non** CLI multi-agent

## Adottato

| Idea | Dove |
|------|------|
| Plan/ReadOnly vs FullAccess | `permission-modes.md` |
| Resume `session_id` | `session-progress` |
| Timeout + flush progress on exit | `when-stuck` / session-progress |
| Anti-force default | permission-modes |

## Non adottato

- harness.lol CLI, full-access default, dipendenza prodotto
