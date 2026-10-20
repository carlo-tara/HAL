#!/bin/sh
# Benchmark modalità A (System 1 attivo, Laya su GPU): una run per modello, pausa di 300 s tra una run e l'altra.
set -u
BASE=/var/www/hal_system2/events/benchmarks/20261020_1
BENCH=/var/www/hal_system2/events/benchmarks
export PYTHONPATH=/var/www/hal_system2

mkdir -p "$BASE"
i=0
for MODEL in phi3:mini qwen2.5:1.5b llama3.2:3b llama3.2:1b; do
  SLUG=$(echo "$MODEL" | tr ':.' '__')
  RUN_DIR="$BASE/$SLUG"
  if [ "$i" -gt 0 ]; then
    echo "[$(date '+%H:%M:%S')] pausa 300 s prima di $MODEL" >> "$BASE.log"
    sleep 300
  fi
  echo "[$(date '+%H:%M:%S')] avvio run $MODEL -> $RUN_DIR" >> "$BASE.log"
  (cd /var/www/hal_system2 && python3 -m app.benchmark_models \
    --run-dir "$RUN_DIR" \
    --output "$RUN_DIR/results.json" \
    --system1 \
    --provider ollama \
    --model "$MODEL" \
    --metrics-db "$BENCH/system2_metrics.sqlite3") >> "$BASE.log" 2>&1
  echo "[$(date '+%H:%M:%S')] fine run $MODEL (exit $?)" >> "$BASE.log"
  i=$((i + 1))
done
echo "[$(date '+%H:%M:%S')] benchmark 20261020_1 completato" >> "$BASE.log"
