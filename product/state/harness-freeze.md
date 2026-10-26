# Freeze — HAL Gateway (L2)

File stabili: Act mode non li modifica senza conferma umana. Seed del bootstrap 2026-10-25.

| path | since | reason |
|------|-------|--------|
| `global_config.py` (`SystemTwoEngine.ACTIVE_MODEL_NAME`, flag `LLM_EXTERNAL_*`) | 2026-10-25 | AGENTS.md: modello predefinito unico, mai riassignare ai subagent |
| `agents/Makefile` | 2026-10-25 | Platform API del bundle: solo steward del flusso `agents/` |
| `.github/workflows/ready-for-review.yml` | 2026-10-25 | contratto gate CI: va modificato solo nello stesso slice del Makefile root |
