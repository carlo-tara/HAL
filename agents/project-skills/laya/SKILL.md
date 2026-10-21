---
name: laya
version: 1.4.1
description: >-
  Reason why: senza un modello System 1 veloce e a basso costo per routing, scelte discrete, scoring euristico, stima di confidenza e chiarezza del contesto, l'agente spreca ragionamento su decisioni preliminari. Interfaccia per Laya System 1: routing di categorie, choice tra opzioni, score euristico di rischio o aderenza, confidence 0-100%, context 0-100%, noul. Invocabile via CLI python3 router.py o modulo Python router.
---

# Laya — System 1 Service

Skill per l'interazione con **Laya**, il modello **System 1** integrato in HAL.

## Architettura Cognitiva HAL

HAL adotta una separazione rigorosa a due livelli:

1. **System 1 (Laya)**:
   - Modello veloce, reattivo, a basso costo e ad alta efficienza.
   - Compiti: categorizzazione iniziale, instradamento (routing), scelta discreta tra percorsi equivalenti (choice), attribuzione di punteggio euristico (score), pre-elaborazione (noul).
   - Invocazione: via CLI (`python3 router.py ...` o `HAL/router.py`) o importando `router` in Python.

2. **System 2 (Agente / Active Reasoning Model)**:
   - Modello di ragionamento ad alta capacità (es. Gemini / Claude / GPT) attivo in Zed / Cursor.
   - Compiti: pianificazione strategica, comprensione profonda del codice, scrittura e modifica file, refactoring, esecuzione test, verifica semantica.

---

## Quando consultare Laya (System 1)

L'agente deve consultare Laya ogni volta che si presenta un compito preliminare di:

- **Triage e Routing**: assegnare un file, una richiesta o un problema a una categoria/rotta (`python3 router.py routing "..." --routes ...`).
- **Scelta discreta**: scegliere tra un set definito di opzioni o strategie operative (`python3 router.py choice "..." --options ...`).
- **Valutazione di rischio o aderenza**: ottenere uno score 0-1 rispetto a un criterio specifico (`python3 router.py score "..." --criteria ...`).
- **Valutazione di confidenza**: stimare la confidenza (0-100%) di una risposta a un quesito o dato (`python3 router.py confidence "..."`).
- **Valutazione del contesto**: stimare la chiarezza e completezza (0-100%) del contesto fornito (`python3 router.py context "..."`).
- **Pre-filtro**: ridurre opzioni prima di una pianificazione approfondita di System 2.

## Quando NON usare Laya (riservato a System 2)

- Modifica, generazione o refactoring del codice.
- Creazione o manipolazione di file nel workspace.
- Esecuzione ed interpretazione di test suite o verifiche deterministiche (`make test-unit`, `check-parity`, ecc.).
- Decisioni architetturali vincolanti che richiedono piena coerenza di contesto.

---

## Interfaccia CLI

L'interfaccia principale da terminale è `python3 router.py`:

```bash
# 1. Routing
python3 router.py routing "<testo>" --routes "<rotta1>, <rotta2>, <rotta3>"
# con output JSON:
python3 router.py routing "<testo>" --routes "<rotta1>, <rotta2>" --json

# 2. Scelta discreta (Choice)
python3 router.py choice "<prompt o domanda>" --options "<opzione1>, <opzione2>"
python3 router.py choice "<prompt>" --options "<opzione1>, <opzione2>" --json

# 3. Score euristico
python3 router.py score "<testo da valutare>" --criteria "<criterio>"
python3 router.py score "<testo>" --criteria "<criterio>" --json

# 4. Confidenza (0-100%)
python3 router.py confidence "<testo o domanda>"
python3 router.py confidence "<testo o domanda>" --json

# 5. Contesto (0-100%)
python3 router.py context "<testo o contesto>"
python3 router.py context "<testo o contesto>" --json

# 6. Noul
python3 router.py noul "<testo>"
```

## Best Practices per Agenti (Ottimizzazione L1)

Per massimizzare la confidenza e l'efficacia di Laya, la skill `smart_choice` implementa automaticamente le seguenti strategie:

### Strategy A — Multi-question Anchoring

Le decisioni complesse vengono ancorate a una domanda di categorizzazione preliminare nello stesso payload.

**Pattern:**

```bash
python3 router.py routing "<testo>" --routes "<rotta1>, <rotta2>"
# Prima di System 2, verificare:
python3 router.py confidence "<testo categorizzato>"
```

**Telemetria:** `python3 scripts/token_budget.py log s1_call` dopo ogni routing.

### Strategy B — Semantic Pacing

Evitare più di 5 opzioni e usare descrizioni di criteri con alta distanza semantica.

**Regole:**

- Max 5 opzioni per chiamata `choice` / `routing`.
- Se le opzioni sono > 5, raggrupparle semanticamente prima di chiamare Laya.
- Usare etichette brevi (< 30 caratteri) per ogni opzione.

**Telemetria:** `python3 scripts/token_budget.py log attachment_filter <original_count> <summary_length>` quando si troncano liste.

### Strategy C — Confidence-Based Routing

- `Confidence > 0.8`: Esecuzione veloce (System 1 diretto).
- `Confidence 0.3-0.8`: Retry automatico con istruzioni di sfida.
- `Confidence < 0.3`: Escalation automatica a System 2 (LLM).

**Pattern:**

```bash
conf=$(python3 router.py confidence "<testo>" | grep -oP '"confidence":\s*\K[0-9.]+')
if (( $(echo "$conf > 0.8" | bc -l) )); then
    # Esecuzione veloce
elif (( $(echo "$conf > 0.3" | bc -l) )); then
    # Retry con sfida
else
    # Escalation System 2
fi
```

**Telemetria:** `python3 scripts/token_budget.py log s1_call` o `s2_call` in base al branch.

### Strategy D — Attachment Filtering

Liste lunghe di allegati o file vengono riassunte (es. "15x .JPG") per ridurre il rumore testuale.

**Regole:**

- Non elencare mai più di 5 elementi nello stesso payload.
- Riassumere: "N x .estensione" per gruppi omogenei.
- Mantenire solo i nomi rilevanti per la decisione corrente.

**Telemetria:** `python3 scripts/token_budget.py log attachment_filter <original_count> <summary_length>`.

---

### Middleware di sistema

Laya include middleware che:

- **Validano il payload** segnalando pattern a bassa confidenza (troppe opzioni).
- **Migliorano il prompt** chiamando System 2 se l'input è ambiguo, troppo corto o "caricato".

Se eseguito all'interno di script o runtime Python in HAL:

```python
from router import handle_choice, handle_routing, handle_score, handle_confidence, handle_context, handle_noul

scelta = handle_choice("strategia", ["opt1", "opt2"])
rotta = handle_routing("richiesta", ["docs", "agents", "infra"])
punteggio = handle_score("snippet", "rischio_regressione")
conf = handle_confidence("quanti abitanti ha Milano?")
ctx = handle_context("richiesta utente con dettagli...")
```
