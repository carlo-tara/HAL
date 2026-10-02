# Pin — curated lists / HE guides (2026)

Tre fonti omogenee (Top-10 / guide HE). URL e adozioni consolidate.

| Fonte | URL |
|-------|-----|
| explainx Top 10 | https://explainx.ai/blog/top-10-open-closed-source-agent-harnesses-2026 |
| thetoolnerd 10 harnesses | https://www.thetoolnerd.com/p/10-agent-harnesses-every-ai-builder |
| claudeskills HE | https://claudeskills.info/harness/cursor/ · https://claudeskills.info/harness-engineering/ |

## Adottato

| Idea | Dove | Fonte |
|------|------|-------|
| Agent = Model + Harness | SKILL Posizionamento | claudeskills |
| Framework ≠ Harness / Meta-Harness = processo | `docs/harness-engineering.md` | toolnerd |
| Seven-stack / building blocks | [harness-architecture.md](harness-architecture.md) | claudeskills, toolnerd, explainx |
| Skills vs MCP vs Hooks | [component-decision.md](component-decision.md) | claudeskills |
| Verification-first + gate deterministici | `/slice`, `platform-api`, hooks | explainx |
| Hard exit (iterazioni/timeout) | `when-stuck` | explainx |
| Progressive disclosure / tool-call offload | competenze on-demand, `context-budget` | toolnerd |
| Maturity L3 Enforced | docs + SKILL | claudeskills |
| Failure-mode checklist | `steward` + [steward-audit-checklist.md](steward-audit-checklist.md) | claudeskills |
| Anti self-harness | `steward` | explainx |
| Session persistence | `session-progress` | claudeskills |

## Non adottato

- Ranking prodotti / Claude/OpenCode/Mastra/Omnigent come dipendenze
- MCP-first; directory shopping list di runtime
- Superpowers / Everything Claude Code come pacchetto obbligatorio
- Framework agent come stack AF obbligatorio
