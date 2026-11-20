#!/usr/bin/env bash
# RED contract (RGR) — confine bounded context del side-car Auto Ontology (Livello C, HT-013).
# Origine: analisi 2026-11-20 su gogoymh/auto-ontology-mcp @ 0fb5ecf. Il suo knowledge store
# (records/concepts/passages + FTS5 + vault) si sovrappone al retrieval documentale di
# a-knowledge/hal_mcp_docs. Senza un confine canonico, l'agente invia le domande al tool sbagliato.
# Verifica che il confine sia promosso nella context map (docs/bounded-contexts.md), non solo nel PRD:
#   (1) riga BC «Knowledge & Ontology (side-car)» nella context map;
#   (2) tabella «Routing delle domande» con i 4 ancoraggi di strumento (un solo destinatario per riga);
#   (3) PRD referenziato (docs/29_auto_ontology_semantic_layer.md);
#   (4) la slice AO-1 esiste e referenzia questo contratto (invariante stabile, backlog-indipendente:
#       in plan l'assert era sul ref di HT-013 in ToDo.md, ma HT-013 è stato flushato in CHANGELOG
#       il 2026-11-20 → il ref nel backlog non è un invariant, la sede della slice sì);
#   (5) AO-1.1: la delega è PROMOSSA in agents/a-knowledge/SKILL.md §Deleghe — linka il canone
#       §«Routing delle domande», non ne duplica le righe.
# Exit 0 = GREEN (confine documentato nel canonico). RED = la context map non ha ancora il confine.
set -euo pipefail
HAL="$(cd "$(dirname "$0")/../.." && pwd)"
BC="$HAL/docs/bounded-contexts.md"
PRD="$HAL/docs/29_auto_ontology_semantic_layer.md"
fail=0

[[ -f "$PRD" ]] || { echo "FAIL: manca il PRD $PRD" >&2; fail=1; }

grep -q "Knowledge & Ontology (side-car)" "$BC" \
  || { echo "FAIL: manca la riga BC «Knowledge & Ontology (side-car)» in bounded-contexts.md (Act non fatto)" >&2; fail=1; }

if grep -q "Routing delle domande" "$BC"; then
  for anchor in "chapter_route" "validate_sql" "find_join_path" "get_source"; do
    grep -q "$anchor" "$BC" \
      || { echo "FAIL: tabella routing in bounded-contexts.md senza ancoraggio '$anchor'" >&2; fail=1; }
  done
else
  echo "FAIL: manca la tabella «Routing delle domande» in bounded-contexts.md (Act non fatto)" >&2; fail=1;
fi

SLICE="$HAL/docs/slices/AO1-sidecar-boundary.md"
[[ -f "$SLICE" ]] && grep -q "check-ontology-bc-boundary.sh" "$SLICE" \
  || { echo "FAIL: la slice AO-1 non esiste o non referenzia questo contratto" >&2; fail=1; }

grep -q "Routing delle domande" "$HAL/agents/a-knowledge/SKILL.md" \
  || { echo "FAIL: a-knowledge/SKILL.md non linka il canone §«Routing delle domande» (AO-1.1 non fatto)" >&2; fail=1; }

if [[ "$fail" -ne 0 ]]; then
  echo "check-ontology-bc-boundary: RED" >&2
  exit 1
fi
echo "check-ontology-bc-boundary: GREEN"
