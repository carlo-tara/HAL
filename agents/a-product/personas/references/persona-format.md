# Formato persona

## Campi obbligatori

| Campo | Note |
|-------|------|
| `id` | `P-01` stabile → tag `@persona-p01` |
| `role` | `primary` \| `secondary` \| `edge` |
| `status` | `active` \| `hypothesis` \| `deprecated` |
| `archetype` | Titolo corto, non biografia |
| `profile` | 2–3 righe contesto d'uso |
| `digital_skill` | `low` \| `mid` \| `high` + note abitudini |
| `primary_goal_in_product` | Outcome, non feature |
| `triggers` | Cosa fa partire l'uso |
| `frustrations` | Pain tool/processi attuali |
| `current_workarounds` | Come se la cava oggi |
| `success_signal` | Come sa di aver fatto bene |
| `constraints` | Tempo, capitale, risk, broker/legal… |
| `interaction_style` | wizard / search / dashboard / shortcuts |
| `ui_bindings` | Schermate/flussi mockup |
| `flow_expectations` | Continuità journey pre/next |
| `jtbd_hints` | 1–3 indizi job (non job stories complete) |
| `evidence` | `source` + nota |
| `open_questions` | Gap aperti |

Opzionali: display name, quote PO, frequency, `origin: add_nl`.

## digital_skill

| Livello | Significato operativo |
|---------|----------------------|
| low | Preferisce guida/wizard; evita densità |
| mid | Mix guida e controllo; tollera qualche scelta |
| high | Shortcuts, dashboard, densità informativa ok |
