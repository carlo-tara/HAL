# 24 — Trasporto HTTP Laya: pooling, timeout, retry, teardown, TLS

**Priorità:** P1 · **Fonte:** doc QwenCloud «Connection reuse and pooling» + production checklist (backlog 2026-10-28) · **Modulo:** `laya_service.py`

---

## Perché

`_session` Laya usava i default urllib3 (10 connessioni per host) senza adapter
montato, un solo `LAYA_TIMEOUT` per l'intera operazione, retry `continue` senza
attesa e nessuna chiusura. Sotto picco o con Laya degradata il gateway
martellava il servizio e perdeva il reuse ratio (>95% target).

## Come

| Parametro          | Env                                      | Default                | Note                                                                                                   |
| ------------------ | ---------------------------------------- | ---------------------- | ------------------------------------------------------------------------------------------------------ |
| `pool_connections` | `LAYA_POOL_CONNECTIONS`                  | 10                     | hostpool aperti                                                                                        |
| `pool_maxsize`     | `LAYA_POOL_MAXSIZE`                      | 32                     | ≥ massimo chiamate batch concorrenti (`len(texts)`)                                                    |
| `pool_timeout`     | `LAYA_POOL_TIMEOUT`                      | 2.0 s                  | attesa esplicita di una connessione libera (via `connection_pool_kw["timeout"]` urllib3)               |
| `connect_timeout`  | `LAYA_CONNECT_TIMEOUT`                   | 2.0 s                  | corto: servizio locale                                                                                 |
| `read_timeout`     | `LAYA_READ_TIMEOUT`                      | `LAYA_TIMEOUT` (5.0 s) | disaccoppiato dal connect                                                                              |
| retry applicativo  | `LAYA_RETRY_BASE_S` / `LAYA_RETRY_MAX_S` | 0.3 s / 4.0 s          | esponenziale `base * 2^attempt` con jitter ±50%, **solo entro `LayaCallBudget`** (max 1 retry per run) |

Retry di trasporto urllib3 disattivato (`max_retries=0` nell'`HTTPAdapter`):
la forma di retry ammessa è quella applicativa, non vanno sommate due forme.

### TLS verify — `verify=False` solo come fallback esplicito

`get_tls_verify()` risolve in ordine:

1. `LAYA_CA_BUNDLE` = percorso di una CA (es. self-signed di `laya.local`) →
   passato come `verify` a `Session.post`;
2. `LAYA_TLS_VERIFY=1|true|yes` → verifica con CA di sistema;
3. fallback `verify=False`, scelta esplicita **di sola development/retro-compat**:
   va disattivata in produzione montando la CA bundle (punto 1).
   `urllib3.disable_warnings(InsecureRequestWarning)` resta in import per non
   rumorare i log finché il fallback è attivo.

### Teardown

`LayaSystemOneService.close()` rilascia adapter e pool; i runner batch
(`batch_score`, `batch_routing`) lo invocano nel `finally`; per altri run
bulk usare il context manager `LayaSystemOneService.run()`. La sessione
ricostruisce i pool lazy se riusata dopo il teardown.

### Connection reuse (spike N26, 2026-10-29)

Telemetria locale: `python3 scripts/bench_hot_paths.py --reuse` conteggia
richieste vs connessioni nuove dai pool stats urllib3 (`num_requests` /
`num_connections`, deduplicando l'adapter montato su http e https) e calcola
il reuse ratio come `1 - conn_nuove/richieste`.

- **Soglia di attenzione: reuse ratio < 0.95** (target doc QwenCloud
  §Performance monitoring). Misura locale: 24 richieste / 1 connessione =
  0.958 → sopra soglia.
- **Decisione gate: NON portare la metrica nei gate di
  `SystemEvaluationEngine`** (spike N26): sotto carico reale il numero di
  richieste per finestra è troppo basso perché il rapporto sia statisticamente
  significativo, e la soglia perde senso fuori dal batch; resta tool di bench
  on-demand. Da rivedere se i runner batch diventano continuativi.

## Verifica

`tests/test_laya_http_pool.py` (pool + timeout tuple),
`tests/test_laya_retry_backoff.py` (distanza tentativi, nessun retry oltre
budget), `tests/test_laya_teardown_tls.py` (close nel finally, CA bundle).
