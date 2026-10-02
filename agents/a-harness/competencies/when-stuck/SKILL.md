---
name: when-stuck
kind: competency
version: 1.0.1
description: >-
  Hard stop dopo 3 fallimenti sullo stesso approccio; timeout/iterazioni;
  escalate o fork checkpoint. Anti chat-infinita.
---

# Competenza L1 — when-stuck

## Contatore

Stesso approccio (stesso test/fix/ipotesi) fallisce **3 volte** → stop.

## Hard exit

Uscire anche se:

- Timeout sessione (L2 o utente; default ragionevole ~45–90 min Act continuo)
- Iterazioni GREEN senza progresso su stesso errore
- Policy On Green/Ready = fail non recuperabile nello slice

Flush progress (`exit` / `stuck`) via `session-progress`.

## Dopo stop

1. Append evento stuck con ipotesi fallite
2. Opzioni: (a) chiedere umano, (b) fork nuovo slice da checkpoint, (c) `/steward` se gate rotto
3. **Non** riprovare lo stesso edit cieco

## Anti-pattern

- «Ancora una volta» oltre il 3° fail
- Cambiare 10 file per sbloccare un test
- Ignorare freeze / permission Plan
- **`pkill -f` / `pgrep -f` su pattern presenti nella cmdline dell’agent shell** (il match uccide o confonde la sessione Cursor): filtra PID con `ps -eo pid,cmd | awk` sul binario/script reale (`rclone`, `python3 …/sync_parallel.py`), mai sul testo del wrapper bash
