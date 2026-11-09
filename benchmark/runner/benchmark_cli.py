"""Entry point CLI del benchmark (T2-09, rv7 N28).

Spostamento meccanico di codice da `app/benchmark_models.py` (nessun
riscrittura).
"""

from __future__ import annotations

import argparse
import math
import os
import sys
from dataclasses import replace
from pathlib import Path

import httpx

from . import benchmark_parsing as parsing
from .benchmark_calls import discover_models
from .benchmark_parsing import load_inputs
from .benchmark_report import apply_llm_model_override, log
from .benchmark_runner import filter_models, filter_prompts, run_benchmark
from .benchmark_settings import ROOT, Settings, write_json
from .benchmark_workflow import system1_guide
from .system2_metrics import DEFAULT_METRICS_DB


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--models", type=Path, default=ROOT / "config/benchmark-models.json"
    )
    parser.add_argument(
        "--prompts", type=Path, default=ROOT / "config/benchmark-prompts.json"
    )
    parser.add_argument(
        "--output", type=Path, default=ROOT / "events/benchmarks/results.json"
    )
    parser.add_argument(
        "--run-dir",
        type=Path,
        help="Cartella dedicata a tutti i risultati dei modelli della run; deve non esistere",
    )
    parser.add_argument(
        "--system1",
        action="store_true",
        help="Usa il gate task-aware Laya/System 2 (le metriche SQLite si registrano anche senza)",
    )
    parser.add_argument(
        "--metrics-db",
        type=Path,
        default=Path(os.getenv("SYSTEM2_METRICS_DB_PATH", DEFAULT_METRICS_DB)),
        help="File SQLite per telemetria System 1/System 2 (default: events/benchmarks/system2_metrics.sqlite3)",
    )
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    parser.add_argument(
        "--provider",
        choices=("ollama", "google"),
        help="Esegue solo i modelli del provider indicato",
    )
    parser.add_argument(
        "--model",
        action="append",
        dest="model_names",
        help="Esegue solo il modello indicato (ripetibile)",
    )
    parser.add_argument(
        "--prompt",
        "--only-id",
        action="append",
        dest="prompt_ids",
        help=(
            "Esegue solo il test indicato per id (ripetibile; --only-id e alias di "
            "--prompt). Il filtro e applicato dopo il caricamento della suite"
        ),
    )
    parser.add_argument(
        "--timeout",
        type=float,
        help="Timeout HTTP per operazione in secondi (default: 600)",
    )
    parser.add_argument(
        "--cooldown",
        type=float,
        default=0.0,
        help="Pausa in secondi tra un modello e il successivo (default: 0)",
    )
    parser.add_argument(
        "--segment-max-tokens",
        type=int,
        help=(
            "Tetto opzionale di token in uscita per ogni segmento delle fonti lunghe "
            "(default: nessun limite; env BENCHMARK_SEGMENT_MAX_TOKENS)"
        ),
    )
    parser.add_argument(
        "--refresh-models",
        action="store_true",
        help="Aggiorna solo il catalogo, senza generazione",
    )
    parser.add_argument(
        "--providers",
        nargs="+",
        choices=("ollama", "google"),
        default=["ollama", "google"],
        help="Provider da interrogare durante --refresh-models",
    )
    args = parser.parse_args(argv)
    try:
        config = Settings.from_env(args.env_file)
        timeout = config.timeout if args.timeout is None else args.timeout
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("Il timeout deve essere un numero positivo finito")
        if not math.isfinite(args.cooldown) or args.cooldown < 0:
            raise ValueError("Il cooldown deve essere un numero finito non negativo")
        segment_cap = (
            config.segment_max_output_tokens
            if args.segment_max_tokens is None
            else args.segment_max_tokens
        )
        if segment_cap is not None and segment_cap < 1:
            raise ValueError("Il tetto di token per segmento deve essere positivo")
        config = replace(config, timeout=timeout, segment_max_output_tokens=segment_cap)
        if args.system1 and (
            not math.isfinite(config.laya_timeout)
            or config.laya_timeout <= 0
            or not math.isfinite(config.laya_min_confidence)
            or not 0 <= config.laya_min_confidence <= 1
        ):
            raise ValueError("Configurazione timeout/confidenza Laya non valida")
        if args.refresh_models:
            if args.models.resolve() in {
                args.env_file.resolve(),
                args.prompts.resolve(),
            }:
                raise ValueError("Il catalogo non può sovrascrivere prompt o .env")
            with httpx.Client(timeout=timeout) as client:
                catalog = discover_models(
                    config, client=client, providers=args.providers
                )
            write_json(args.models, catalog)
            print(
                f"Catalogo aggiornato: {len(catalog['models'])} modelli in {args.models}"
            )
            return 0
        if args.output.resolve() in {
            args.models.resolve(),
            args.prompts.resolve(),
            args.env_file.resolve(),
        }:
            raise ValueError("L'output non può sovrascrivere input o .env")
        models, prompts = load_inputs(args.models, args.prompts)
        prompts = filter_prompts(prompts, args.prompt_ids)
        for prompt in prompts:
            if "source" in prompt:
                log(
                    f"Fonte per {prompt['id']}: {prompt['source']} "
                    f"({len(parsing.epub_text(ROOT / prompt['source'])):,} caratteri)"
                )
        models = filter_models(
            apply_llm_model_override(models, config), args.provider, args.model_names
        )
        if args.run_dir is not None:
            if args.run_dir.exists():
                raise ValueError(f"La cartella di run esiste già: {args.run_dir}")
            if args.output.resolve().parent != args.run_dir.resolve():
                raise ValueError("--output deve essere direttamente dentro --run-dir")
        elif args.output.exists():
            raise ValueError(
                f"L'output esiste già; specificare --run-dir: {args.output}"
            )
        with httpx.Client(timeout=timeout) as client:
            guides = None
            if args.system1:
                log(
                    f"System 1 Laya: preflight su {len(prompts)} prompt "
                    f"({config.laya_base_url}, modello {config.laya_model})"
                )
                guides = {}
                for prompt in prompts:
                    log(f"  → classificazione Laya: {prompt['id']}")
                    guides[prompt["id"]] = system1_guide(prompt, config, client)
            report = run_benchmark(
                models,
                prompts,
                config,
                args.output,
                client=client,
                run_dir=args.run_dir,
                system1_guides=guides,
                metrics_db=args.metrics_db,
                cooldown=args.cooldown,
            )
        print(
            f"Risultati: {args.output}; successi: {report['summary']['successful']}; errori: {report['summary']['failed']}"
        )
        return 1 if report["summary"]["failed"] else 0
    except httpx.HTTPStatusError as exc:
        print(
            f"Errore HTTP {exc.response.status_code} durante discovery o System 1 Laya",
            file=sys.stderr,
        )
    except httpx.RequestError:
        print(
            "Errore di rete/timeout durante discovery o inferenza System 1 Laya",
            file=sys.stderr,
        )
    except FileNotFoundError as exc:
        print(f"File non trovato: {exc.filename}", file=sys.stderr)
        return 2
    except (OSError, ValueError, KeyError, TypeError):
        print(
            "Configurazione/input non validi o file non accessibile: verificare JSON, percorsi, chiave Google e timeout",
            file=sys.stderr,
        )
    except KeyboardInterrupt:
        print(
            "Interrotto: i risultati già completati restano nel checkpoint JSON",
            file=sys.stderr,
        )
        return 130
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
