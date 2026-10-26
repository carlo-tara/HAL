---
name: a-agentzero
version: 1.12.0
description: >-
  Reason why: senza L0 comune ogni dominio reinventa protocollo, sync e sicurezza.
  Agente radice HAL: ereditarietà a 3 livelli, competenze modulari,
  avvio multiprogetto, workflow generici, checklist e scaffold L2.
  Tutti gli L1 estendono a-agentzero.
---

# a-agentzero — agente radice (L0)

Radice dell'ecosistema agenti HAL. Fornisce funzionalità generiche condivise; gli agenti di dominio (L1) e le skill figlie di progetto (L2) ereditano via `extends:`.

**Sorgente canonica:** `agents/a-agentzero/`
**Protocollo formale:** [AGENT-PROTOCOL.md](AGENT-PROTOCOL.md).
**Coding Standards:** [references/coding-standards.md](references/coding-standards.md).

---

## Gerarchia a 3 livelli

| Livello | Esempi                                                                                    | Ruolo                                                      |
| ------- | ----------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| **L0**  | `a-agentzero`                                                                             | Protocollo, workflow comuni, scaffold, competenze baseline |
| **L1**  | `a-b2b`, `a-copywriter`, `a-design`, `a-harness`, `a-product`, `a-seozoom`, `a-wordpress` | Competenza di dominio + moduli dominio                     |
| **L2**  | `.agents/skills/{dominio}-{progetto}/`                                                    | Delta progetto                                             |

**Ordine di caricamento:** L0 → L1 → L2. Le regole di sicurezza L0 non sono mai sovrascrivibili.

---

## Token Budget (Regole globali)

**Riferimento completo:** [references/token-budget.md](references/token-budget.md)

### Output compatto (Contratto)

- **Nessun testo narrativo, saluti o "Reason why" auto-evidenti.**
- Output stringato, tabellare o liste. Solo script/codice dove applicabile.
- Usa `router.py` prima di stampare conclusioni discrete.
- **Max 500 token output per sessione.** Se il ragionamento richiede più spazio, usa file esterni (`events/`, `product/`).

### Lazy-load (mai leggere file interi se > 100 righe)

- Prima di `read_file`: stimare la dimensione del file.
- Se > 100 righe, usare `start_line` / `end_line` per leggere solo le sezioni rilevanti.
- Mai riversare l'intero contenuto di un file grande nel contesto.
- Tracciare in telemetria: `python3 scripts/token_budget.py log lazy_load <path> <lines_read> <total_lines>`.

### Attachment filtering (Strategy D)

- Liste lunghe di allegati/file vengono riassunte (es. "15x .JPG", "3x .md") per ridurre il rumore testuale.
- Non elencare mai più di 5 elementi nello stesso payload.
- Tracciare: `python3 scripts/token_budget.py log attachment_filter <original_count> <summary_length>`.

### System 1 (Laya) Cognitive Layer

`a-agentzero` stabilisce l'architettura cognitiva a due livelli per HAL:

1. **System 1 (Laya)**: Obbligatorio per compiti preliminari, tramite `router.py`:
   - `router.py triage` / `routing` per smistamento richieste a L1/competenza.
   - `router.py score` per valutazione rapida rischio/aderenza.
2. **System 2 (Reasoning)**: Riservato esclusivamente a pianificazione complessa e codice.

---

## Note

Per regole avanzate (conflitti, checklist estese, deleghe L1 specifiche e discovery):
Leggi `references/agentzero-extended-rules.md`.

Per il protocollo token budget e telemetria:
Leggi `references/token-budget.md`.
