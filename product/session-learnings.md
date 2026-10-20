# Changelog apprendimenti (/learn)

## 2026-10-20

### Progetto

- Benchmark (`benchmark/README.md`): il runner ha due copie (gateway e `hal_system2/app/`) con test solo in `hal_system2/tests/`; modifiche da portare in entrambe. Appreso da sessione [sync:safe]
- Benchmark (`benchmark/README.md`): sezione "Telemetria" (DB vivo in `hal_system2/events/benchmarks/`, sola lettura, `run_id` UUID, token solo negli stage `system2`, errori senza token). Appreso da sessione [sync:safe]
- Benchmark: prima di modificare il runner nel gateway confrontare con `hal_system2/app/` (`git log`, `diff`): la canonica può già contenere la modifica; il gateway è un mirror, non va divergere. Appreso da sessione [sync:safe]
- Benchmark (`benchmark/README.md`): `wasted_tokens` (12% dei token) = stage riusciti di workflow poi falliti; misurato da `get_token_breakdown`. Appreso da sessione [sync:safe]
- CI: il gate Make `agents/` non esegue i test del gateway; la sola verifica è `.github/workflows/ready-for-review.yml`, quindi ogni nuovo test va aggiunto lì. Appreso da sessione [sync:safe]
- Benchmark (`benchmark/README.md`): `--output` obbligatorio e dentro `--run-dir`; esempi corretti. Appreso da sessione [sync:safe]
- Benchmark: il runner non ha cooldown tra modelli; una run per modello con `sleep`, poi cartella piatta per il generatore (non ricorsivo). Residuo in `ToDo.md` #benchmark P1 [sync:safe]
- Benchmark: background con `setsid`; `nohup` dalla shell del tool termina con la shell. Appreso da sessione [sync:safe]
- Benchmark: `generate_benchmark_report.py` esiste in due copie identiche (`benchmark/scripts/`, `hal_system2/scripts/`), da sincronizzare a mano. Residuo in `ToDo.md` #benchmark P2 [sync:safe]
- Benchmark: `--sintesi FILE_HTML` aggiunto al generatore per l'executive summary. Appreso da sessione [sync:safe]

### HAL

_(nessuna)_
