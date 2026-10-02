# Workflow /add

## Input

`/add` + descrizione NL. Opzionali: role secondary|edge (default non primary).

## Esempi

```
/add Chi gestisce il portafoglio per un familiare, poco rischio, vuole solo riepilogo chiaro.
/add Persona edge: consulente in call col cliente.
```

## Progress

1. Load `personas.md` (se assente → `/create`)
2. Parse NL → segnali
3. Overlap / anti-persona clash
4. Nuovo id; hypothesis; `origin: add_nl`
5. Schema completo; evidence `po_nl`
6. open_questions; 1–2 Q PO
7. Max 4 active
8. Conferma → `/export` → escalate `a-jtbd`

## Regole

- No primary senza conferma esplicita + demote precedente
- Collasso su esistente → `/update`
- Hypothesis fino a ratifica
