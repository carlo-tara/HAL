# Changelog apprendimenti (/learn)

## 2026-10-20

### Progetto

- Benchmark (`benchmark/README.md`): `--output` obbligatorio e dentro `--run-dir`; esempi corretti. Appreso da sessione [sync:safe]
- Benchmark: il runner non ha cooldown tra modelli; una run per modello con `sleep`, poi cartella piatta per il generatore (non ricorsivo). Residuo in `ToDo.md` #benchmark P1 [sync:safe]
- Benchmark: background con `setsid`; `nohup` dalla shell del tool termina con la shell. Appreso da sessione [sync:safe]
- Benchmark: `generate_benchmark_report.py` esiste in due copie identiche (`benchmark/scripts/`, `hal_system2/scripts/`), da sincronizzare a mano. Residuo in `ToDo.md` #benchmark P2 [sync:safe]
- Benchmark: `--sintesi FILE_HTML` aggiunto al generatore per l'executive summary. Appreso da sessione [sync:safe]

### HAL

_(nessuna)_
