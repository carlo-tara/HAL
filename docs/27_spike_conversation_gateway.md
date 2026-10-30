# 27 — Spike: astrazione conversation lato gateway (N25, 2026-10-30)

Domanda (ToDo P2, doc QwenCloud «Multi-turn conversations»): HAL necessita un
`conversation_id` con message array session-scoped server-side (Responses
`previous_response_id` / Conversations API), oltre al `derive_session_id` attuale?

## Mappatura delle tre lezioni

| Lezione QwenCloud                                                      | Stato HAL                                                                                                                                                                                                                                          |
| ---------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Parametri di richiesta mutuamente esclusivi da validare alla frontiera | già consegnato: `validate_chat_payload` + resolver capability per-modelli (N14, CHANGELOG `flag streaming_only` con validazione alla frontiera)                                                                                                    |
| Item server-side con scadenza 7 giorni                                 | non applicabile come fonte di verità: il vincolo ZDR del gateway impone la copia locale (ContextManager `context_manager.py`: troncamento, rolling summary, retrieval — N5); mai conservare solo l'ID del provider (regola protocollo § retention) |
| `instructions` separate dalla history                                  | già consegnato: `split_instructions` (N3) + system prompt fuori dal transcript append-only                                                                                                                                                         |

## Evidenze aggiuntive dallo spike N28 (docs/26)

OrcaRouter non inoltra semantica di sessione lato provider (header e marker
inertenti, `cached_tokens=0` anche a caldo): un `conversation_id` server-side
non avrebbe comunque controparte misurabile sull'aggregatore.

## Decisione: RIFIUTATO

Nessun `conversation_id` session-scoped nuovo. L'astrazione locale esiste già:
`derive_session_id` deterministico + ContextManager (gestione window) +
ToolSessionRegistry append-only (carry-forward). Nessuna apertura feature
connessa. Rivalutare solo se HAL esponesse backend DashScope diretti (non via
aggregatore) con retention server-side ≥ sessioni tipiche.

## Riprodurre

Decisione documentale su evidenze `docs/26_spike_session_cache_orcarouter.md`
e voce multi-turn del delta 2026-10-28.

System 1 (Laya) conferma la decisione con `choice` → `skip` (status ok).
