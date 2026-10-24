#!/usr/bin/env bash
# Baseline a contesto pieno: stessi test della baseline, senza middleware (--system1)
# e con num_ctx esplicito e registrato, per verificare se la fonte era tagliata.
#
# Uso:
#   run_baseline_fullctx.sh [--dry-run] RUN_ID        (RUN_ID = yyyymmdd_id)
#
# Parametri (variabili d'ambiente, default tra parentesi):
#   NUM_CTX (16384)  MODELS ("phi3:mini llama3.2:1b")
#   PROMPTS ("estrazione_json sintesi_traduzione")  TIMEOUT (1800)  COOLDOWN (60)
#   HISTORY_DIR (benchmark/history)  RUNNER_CMD ("python3 -m runner.benchmark_models")
#   RUNNER_DIR (benchmark/)  cartella da cui parte il runner: i percorsi di config e fonte
#     (es. docs/*.epub) sono relativi ad essa. Per il canonico:
#     RUNNER_DIR=/var/www/hal_system2 RUNNER_CMD="python3 -m app.benchmark_models"
#
# --dry-run stampa comando e run_config.json senza chiamare il runner né Ollama.
# Scrive `run_config.json` nella cartella di run (anche se il runner fallisce) e
# restituisce il codice di uscita del runner.
set -euo pipefail

BENCH_DIR="$(cd "$(dirname "$0")/.." && pwd)"

die() {
  echo "run_baseline_fullctx: $*" >&2
  exit 2
}

DRY_RUN=0
RUN_ID=""
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    -*) die "opzione sconosciuta: $arg" ;;
    *) RUN_ID="$arg" ;;
  esac
done

[[ "$RUN_ID" =~ ^[0-9]{8}_[0-9]+$ ]] || die "RUN_ID obbligatorio nel formato yyyymmdd_id (ricevuto: '${RUN_ID}')"

NUM_CTX="${NUM_CTX-16384}"
[[ "$NUM_CTX" =~ ^[0-9]+$ ]] && (( NUM_CTX >= 4096 )) \
  || die "NUM_CTX deve essere un intero >= 4096 (ricevuto: '${NUM_CTX}')"

MODELS="${MODELS-phi3:mini llama3.2:1b}"
PROMPTS="${PROMPTS-estrazione_json sintesi_traduzione}"
TIMEOUT="${TIMEOUT-1800}"
COOLDOWN="${COOLDOWN-60}"
HISTORY_DIR="${HISTORY_DIR-$BENCH_DIR/history}"
RUNNER_CMD="${RUNNER_CMD-python3 -m runner.benchmark_models}"
RUNNER_DIR="${RUNNER_DIR-$BENCH_DIR}"
[[ -d "$RUNNER_DIR" ]] || die "RUNNER_DIR non è una cartella: $RUNNER_DIR"

read -r -a MODEL_LIST <<< "$MODELS"
read -r -a PROMPT_LIST <<< "$PROMPTS"
read -r -a RUNNER <<< "$RUNNER_CMD"
(( ${#MODEL_LIST[@]} > 0 )) || die "MODELS vuoto"
(( ${#PROMPT_LIST[@]} > 0 )) || die "PROMPTS vuoto"

RUN_DIR="$HISTORY_DIR/$RUN_ID"
[[ -e "$RUN_DIR" ]] && die "la cartella di run esiste già: $RUN_DIR"

ARGS=(
  --models config/benchmark-models.json
  --prompts config/benchmark-prompts.json
  --run-dir "$RUN_DIR"
  --output "$RUN_DIR/results.json"
  --provider ollama
)
for model in "${MODEL_LIST[@]}"; do ARGS+=(--model "$model"); done
for prompt in "${PROMPT_LIST[@]}"; do ARGS+=(--prompt "$prompt"); done
ARGS+=(--timeout "$TIMEOUT" --cooldown "$COOLDOWN")

config_json() {
  RUN_ID="$RUN_ID" NUM_CTX="$NUM_CTX" MODELS="$MODELS" PROMPTS="$PROMPTS" \
    TIMEOUT="$TIMEOUT" COOLDOWN="$COOLDOWN" RUNNER_DIR="$RUNNER_DIR" python3 - <<'PY'
import json
import os

env = os.environ


def number(value: str) -> int | float:
    return int(value) if value.isdigit() else float(value)


print(
    json.dumps(
        {
            "run_id": env["RUN_ID"],
            "num_ctx": int(env["NUM_CTX"]),
            "models": env["MODELS"].split(),
            "prompts": env["PROMPTS"].split(),
            "timeout": number(env["TIMEOUT"]),
            "cooldown": number(env["COOLDOWN"]),
            "runner_dir": env["RUNNER_DIR"],
            "system1": False,
        },
        indent=2,
    )
)
PY
}

if (( DRY_RUN )); then
  echo "# dry-run: nessuna chiamata a Ollama né al runner"
  printf '(cd %q && ' "$RUNNER_DIR"
  printf 'OLLAMA_NUM_CTX=%s' "$NUM_CTX"
  printf ' %q' "${RUNNER[@]}" "${ARGS[@]}"
  printf ')\n# run_config.json\n'
  config_json
  exit 0
fi

status=0
(cd "$RUNNER_DIR" && OLLAMA_NUM_CTX="$NUM_CTX" "${RUNNER[@]}" "${ARGS[@]}") || status=$?
if [[ -d "$RUN_DIR" ]]; then
  config_json > "$RUN_DIR/run_config.json"
fi
exit "$status"
