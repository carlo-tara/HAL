# Cursor hooks recipe (guarantee layer)

Converte «always/never» in enforcement deterministico. Runtime-specific (Cursor); portabilità bassa — ok.

**Prefer Make as the guarantee.** Hooks stay **light** — avoid full `make pre-commit` / `make test-unit` on every edit. See [consumer-platform-hygiene.md](consumer-platform-hygiene.md).

## Eventi tipici

| Event | Azione suggerita |
|-------|------------------|
| Stop | Light gate (es. `make check-cursor-whitelist`) |
| Before PR / review | Agente esegue `make ready-for-review` (non obbligatorio in hook) |
| After edit | Solo se indispensabile (formatter); non batch Make pesanti |

## Setup L2 (esempio leggero)

`.cursor/hooks.json`:

```json
{
  "version": 1,
  "hooks": {
    "stop": [
      {
        "command": "node .cursor/hooks/steward-stop-gate.js",
        "loop_limit": 2,
        "timeout": 60
      }
    ]
  }
}
```

Lo script tipico invoca un target Make documentato in L2 (es. whitelist). `loop_limit` è enforced da Cursor — non duplicarlo nello script.

Se hooks non disponibili: i target Make restano la garanzia (agente **deve** eseguirli; non skip).

Steward: promuovi regole ripetute da skill → hook/Make ([component-decision.md](component-decision.md)).
