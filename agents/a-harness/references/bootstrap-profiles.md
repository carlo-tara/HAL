# Bootstrap profiles — Plugin vs Preset

**Plugin** = capacità atomica (una competenza, un template, un target Make).  
**Preset** = composizione task-ready (`/bootstrap` profile).

## Profiles

| Profile | Contenuto | Quando |
|---------|-----------|--------|
| **minimal** | Makefile gate (`test-unit`, `pre-commit`, `ready-for-review`) + progress file | Eval fairness, greenfield snello, scaffolding minimo |
| **standard** | minimal + glossary + bounded-contexts + L2 skill + permission modes + learnings | Default produzione |
| **creator** (via `/steward`) | Evoluzione preset L2, freeze, hooks recipe, scorecard | Dopo che standard funziona |

## Flusso

1. Scegli profile in `/bootstrap`
2. Non scalare autonomia (multi-slice / parallel) senza `make test` reale
3. Creator: solo steward; non reinventare agent loop (anti self-harness)

Pin: [deepseek-harness-source.md](deepseek-harness-source.md) · [madebywild-agent-harness-source.md](madebywild-agent-harness-source.md)
