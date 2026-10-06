# Indice — 23 documenti di dettaglio (perché / cosa / come)

Modello di costo: forward Laya ~33ms CPU · op Redis <1ms · LLM in unità relative (piccolo=1, medio=3, frontier=10).

## P0
- [01_gate_sorpresa.md](01_gate_sorpresa.md) — Gate di sorpresa: OOD detector indipendente come trigger di escalation
- [02_valore_atteso.md](02_valore_atteso.md) — Escalation per valore atteso: P(miglioramento) x value(task) > costo(escalation)
- [03_gruppo_ombra.md](03_gruppo_ombra.md) — Gruppo ombra: 5-10% delle richieste sicure passa per S2 in modalità log-only
- [04_degradazione_graceful.md](04_degradazione_graceful.md) — Degradazione graceful di laya-serve: fail-open verso S2 con policy prudente
- [05_retention_redaction.md](05_retention_redaction.md) — Retention e redaction del volume eventi dal giorno 1
- [06_outcome_rpe.md](06_outcome_rpe.md) — Outcome come errore di predizione (3 gradienti), non booleano
- [07_cache_l1.md](07_cache_l1.md) — Cache L1 esatta: hash normalizzato, invalidazione per file, TTL per classe, prefisso session
- [08_verificatore_esecuzione.md](08_verificatore_esecuzione.md) — Verificatore a prova di esecuzione: bozza piccola → test → verde servi / rosso escala
- [09_replay_strutturato.md](09_replay_strutturato.md) — Replay strutturato pre-fine-tuning: recenti mescolati a campioni del passato

## P1
- [10_cache_l2.md](10_cache_l2.md) — Cache L2 semantica: embedding + similarità + verifica Laya prima di servire
- [11_routing_distillato.md](11_routing_distillato.md) — Routing distillato su Laya: fissare il modello economico dove il log dimostra stabilità
- [12_scoring_pertinenza_laya.md](12_scoring_pertinenza_laya.md) — Scoring pertinenza dello storico via Laya invece che via LLM
- [13_eliminazione_escalation_inefficaci.md](13_eliminazione_escalation_inefficaci.md) — Eliminazione escalation inefficaci: i bucket con P(miglioramento) < 30% smettono di escalare
- [14_guardrail_subcorticale.md](14_guardrail_subcorticale.md) — Guardrail subcorticale: parallelo, prima di tutto, batch unico con intake
- [15_enforcement_budget.md](15_enforcement_budget.md) — Enforcement del budget contestuale: oltre max_context_tokens → compattazione col piccolo
- [16_urgency_signal.md](16_urgency_signal.md) — Urgency signal: sotto deadline si serve la bozza, il grande completa in background
- [17_intake_multilabel.md](17_intake_multilabel.md) — Intake multi-label gerarchico: richieste miste non forzate in una classe
- [18_decorrelazione.md](18_decorrelazione.md) — Decorrelazione S1/S2: chi decide il routing ≠ chi verifica; S1 come ipotesi esplicita
- [19_circuit_breaker.md](19_circuit_breaker.md) — Circuit breaker sui provider + session_id corretto per conversazioni parallele

## P2
- [20_segnale_metabolico.md](20_segnale_metabolico.md) — Segnale metabolico: carico/budget/health modulano le soglie di escalation
- [21_soglie_dinamiche.md](21_soglie_dinamiche.md) — Soglie dinamiche dal log: epsilon-esplorazione e learning rate con deadband
- [22_broadcast_lavagna.md](22_broadcast_lavagna.md) — Broadcast della risposta S2 nella lavagna come fatto con provenance
- [23_serving_speculativo.md](23_serving_speculativo.md) — Serving speculativo: bozza servita mentre il grande completa (estensione di 16)
