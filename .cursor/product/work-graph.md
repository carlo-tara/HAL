# Work Graph — Multi-Cycle Backlog (`ToDo.md`)

- **Source:** file (`ToDo.md`)
- **Goal:** Esecuzione strutturata dei task P0 (Cache L1 e Retention/Redaction) e P1 (Circuit Breaker & Session)
- **Auto-accept:** true
- **Multi-cycle:** true

## Nodi

1. **node-07-1**: 07 — Cache L1 (Parte 1): Normalizzazione prompt e hashing canonico (SHA-256) per chiavi Redis composte.
   - **Slash**: `/slice` -> `/red` -> `/green` -> `/refactor`
   - **Next**: `node-07-2`

2. **node-07-2**: 07 — Cache L1 (Parte 2): Integrazione TTL per classe di use-case (`use-cases/*.yaml`) e invalidazione basata su hash dei file di contesto.
   - **Slash**: `/slice` -> `/red` -> `/green` -> `/refactor`
   - **Next**: `node-07-3`

3. **node-07-3**: 07 — Cache L1 (Parte 3): Re-streaming SSE delle risposte cachate e test di hit rate / assenza di risposte stale.
   - **Slash**: `/slice` -> `/red` -> `/green` -> `/refactor`
   - **Next**: `node-05-1`

4. **node-05-1**: 05 — Retention & Redaction (Parte 1): Denylist regex in `event_writer` per API key, Bearer token, blocchi PEM e password con placeholder tipizzati.
   - **Slash**: `/slice` -> `/red` -> `/green` -> `/refactor`
   - **Next**: `node-05-2`

5. **node-05-2**: 05 — Retention & Redaction (Parte 2): Integrazione preset Laya `pii_scan` per flag di PII e gestione differenziata/cifrata dei body.
   - **Slash**: `/slice` -> `/red` -> `/green` -> `/refactor`
   - **Next**: `node-05-3`

6. **node-05-3**: 05 — Retention & Redaction (Parte 3): Rotazione giornaliera JSONL, job di purge (body > 30gg, metadata 12m) e cifratura volumi/backup.
   - **Slash**: `/slice` -> `/red` -> `/green` -> `/refactor`
   - **Next**: `node-19-1`

7. **node-19-1**: 19 — Circuit Breaker & Session (Parte 1): Derivazione deterministica del `session_id` (`hash(api_key, workspace_path, conversation)`) con test di non collisione per chat parallele.
   - **Slash**: `/slice` -> `/red` -> `/green` -> `/refactor`
   - **Next**: `node-19-2`

8. **node-19-2**: 19 — Circuit Breaker & Session (Parte 2): Implementazione State Machine del circuit breaker per provider in Redis (`providers.yaml`) con soglie d'errore e finestre di recupero.
   - **Slash**: `/slice` -> `/red` -> `/green` -> `/refactor`
   - **Next**: `—`

```mermaid
graph TD
    n1[07-1: Normalizzazione e Hashing] --> n2[07-2: TTL e Invalidazione Contesto]
    n2 --> n3[07-3: Re-streaming SSE & Test]
    n3 --> n4[05-1: Denylist Regex Redaction]
    n4 --> n5[05-2: Laya PII Scan & Cifratura]
    n5 --> n6[05-3: Rotazione, Purge e Backup]
    n6 --> n7[19-1: Session ID Deterministico]
    n7 --> n8[19-2: Circuit Breaker Redis]
