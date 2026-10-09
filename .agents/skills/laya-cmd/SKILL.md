---
name: laya-cmd
version: 1.1.0
description: Command laya-cmd for HAL workspace.
---

# /laya — Invocazione Laya System 1

## Obiettivo

Consultare **Laya** (System 1 di HAL) per eseguire valutazioni veloci, instradamento, classificazione e scelte discrete a basso costo cognitivo prima di passare al ragionamento approfondito di System 2.

## Esecuzione

Tramite terminale:
```bash
python3 /var/www/HAL/router.py routing "<testo o problema>" --routes "<rotta1>, <rotta2>, <rotta3>"
python3 /var/www/HAL/router.py choice "<prompt di decisione>" --options "<opzioneA>, <opzioneB>"
python3 /var/www/HAL/router.py score "<testo da valutare>" --criteria "<criterio>"
python3 /var/www/HAL/router.py confidence "<domanda o testo>"
python3 /var/www/HAL/router.py context "<testo da valutare>"
```

Oppure in Python:
```python
from router import handle_choice, handle_routing, handle_score, handle_confidence, handle_context
```
