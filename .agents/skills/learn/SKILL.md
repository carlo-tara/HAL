---
name: learn
version: 1.0.0
description: Command learn for HAL workspace.
---

# /learn — apprendimento da sessione (L0)

## Objective

Esporre `/learn` come comando L0: catturare ciò che emerge dalla sessione corrente e consolidarlo dove sopravvive (skill del progetto, `./ToDo.md`, `docs/`, changelog). Il canone operativo — regole su cosa apprendere, ambiti, formato di scrittura, target di consolidamento e pitfall tool — resta la skill utility `a-agentzero/learn/` con versione e CHANGELOG proprî.

## Process

1. **Carica il canone:** `read /var/www/hal_gateway/agents/a-agentzero/learn/SKILL.md` (il deep skill nel bundle; `.agents/skills/learn/` e la skill globale sono ora wrapper generati da questo file).
2. **Instrada l'argomento (tabella canone):**
   - `?` → **Riflessione** — report apprendimenti dalla conversazione/sessione, nessuna scrittura su file.
   - `!` → **Consolidamento** — scrive nei target attivi (skill L2, brand, rules) e, se necessario, apre Attività in `./ToDo.md` e/o apprendimenti in `docs/` locali; changelog + `/version patch` sulle skill toccate.
   - `! redigi <file> per <target>` → **Redazione** — riscrittura comunicativa per destinatario dichiarato; non è apprendimento (regole non negoziabili nel canone).
   - altro → mostra questa invocazione.
3. **Regole, ambiti e formati di scrittura:** `references/learn-guidelines.md`, `references/consolidation-targets.md`, `references/tool-pitfalls.md` dentro la skill canone.
4. Non duplicare qui le regole del canone.

## Expected output

- `?`: elenco apprendimenti senza tocchi; `!`: file scritti + bump + changelog, con sweep CJK/mojibake a chiusura; `! redigi`: il documento redatto, mai i costi/fornitore interni nel testo verso l'esterno.

## Usage

```
/learn ? | ! | ! redigi <file> per <target>
```

## Notes

- Baseline L0: `a-agentzero/commands/learn.md`. Canone operativo: skill utility `a-agentzero/learn/SKILL.md` (che mantiene `disable-model-invocation: true` per sé: il wrapper generato dal comando non la porta, quindi `/learn` diventa invocabile anche dal modello come gli altri L0).
- Override progetto: `{repo}/.agents/commands/learn.md` se presente (skill locale omonima ha priorità sulla globale).
