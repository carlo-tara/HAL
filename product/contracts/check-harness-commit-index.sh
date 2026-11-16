#!/usr/bin/env bash
# RED contract (RGR) — isolamento index anti-gara per il comando L0 /commit.
# Origine: brainbeez release 0.14.0 (2026-11-16): il mirror commit «docs(release)» ha
# assorbito 9 file stageati dalla sessione parallela sull'index CONDIVISO — `git commit`
# legge l'index, non «ciò che ho aggiunto io». Recidiva AGG-10 in direzione simmetrica
# (la prima era «l'altrui reset azzecca il mio add»). Regola: commit a index privato
# (GIT_INDEX_FILE seminato da HEAD) + allow-list esplicita + guardie pre/post + push
# verificato via ls-remote. Il contratto è anchesso funzionale (dogfood in repo usa-e-getti).
# Exit 0 = GREEN.
set -euo pipefail
HAL="$(cd "$(dirname "$0")/../.." && pwd)"
CMD="$HAL/agents/a-agentzero/commands/commit.md"
SH="$HAL/agents/a-agentzero/scripts/agent-commit.sh"
fail=0

# 1) Statico: la sezione e i capi saldi del protocollo nel canonico del comando.
grep -q "Isolamento index" "$CMD" \
  || { echo "FAIL: manca la sezione «Isolamento index» in commands/commit.md" >&2; fail=1; }
grep -q "GIT_INDEX_FILE" "$CMD" \
  || { echo "FAIL: il canonico non prescrive l'index privato (GIT_INDEX_FILE)" >&2; fail=1; }
grep -q "ls-remote" "$CMD" \
  || { echo "FAIL: manca la verifica del push (ls-remote) nel canonico" >&2; fail=1; }

# 2) Lo script esiste, è eseguibile e parsato.
[[ -x "$SH" ]] || { echo "FAIL: manca agents/a-agentzero/scripts/agent-commit.sh (o non è eseguibile)" >&2; fail=1; }
if [[ -f "$SH" ]]; then
  bash -n "$SH" || { echo "FAIL: agent-commit.sh non parsato da bash -n" >&2; fail=1; }
fi

# 3) Funzionale (dogfood): la gara sull'index condiviso NON deve contaminare il commit.
if [[ -x "$SH" && $fail -eq 0 ]]; then
  T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
  (
    cd "$T"
    git init -q -b master
    git config user.email test@contract.local
    git config user.name contract
    echo base > base.txt
    git add base.txt
    git commit -qm base
    # la MIA modifica (da committare)
    echo mine > mine.txt
    # la «sessione parallela»: suo file già stageato sull'index condiviso
    echo foreign > foreign.txt
    git add foreign.txt
    printf 'feat: solo il mio file\n' > msg.txt
    bash "$SH" -m msg.txt -- mine.txt
    committed="$(git show --name-only --format= HEAD | sed '/^$/d')"
    echo "$committed" | grep -qx "mine.txt" \
      || { echo "FAIL: il commit non contiene mine.txt" >&2; exit 1; }
    if echo "$committed" | grep -qx "foreign.txt"; then
      echo "FAIL: sweep — il file altrui stageato è finito nel MIO commit" >&2
      exit 1
    fi
    staged="$(git diff --cached --name-only)"
    echo "$staged" | grep -qx "foreign.txt" \
      || { echo "FAIL: index condiviso manomesso (foreign non più stageato)" >&2; exit 1; }
  ) || fail=1
fi

if [[ $fail -ne 0 ]]; then
  echo "check-harness-commit-index: RED" >&2
  exit 1
fi
echo "check-harness-commit-index: GREEN"
