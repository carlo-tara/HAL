---
name: harness-hal-seo
extends: a-harness
version: 0.1.2
extends-version: 1.10.2
description: >-
  Reason why: senza Platform API e gate, il progetto delegato resterebbe uno script privo di uscita verificabile.
  Delta harness per hal_mcp_seo (MCP QA deterministica copywriting & SEO): Makefile Platform API, path artefatti, N/A documentati, safety note e conflitti di sessione parallela.
---

# harness-hal-seo — delta L2

Skill figlia (L2). All'avvio: L0 `a-agentzero` → L1 `a-harness` → **questo file**. Solo override di path, stack e gate — non rieseguire il workflow L1 nel body.

## Progetto

| Campo             | Valore                                                            |
| ----------------- | ----------------------------------------------------------------- |
| Nome              | hal_mcp_seo (MCP QA Copywriting & SEO)                            |
| Working directory | `/var/www/hal_seo`                                                |
| Stack             | Python 3.12, core stdlib; `pyphen` opzionale (fallback euristica) |
| Bootstrap profile | **standard** (2026-11-01)                                         |
| Effort default    | thorough                                                          |

## Path locali

| Artefatto        | Path                                   |
| ---------------- | -------------------------------------- |
| Platform API     | `Makefile` (root)                      |
| Glossario        | `docs/glossary.md`                     |
| Bounded contexts | `docs/bounded-contexts.md`             |
| PRD              | `docs/PRD.md`                          |
| Progress         | `docs/product/agent-progress.md`       |
| Residui          | `./ToDo.md`                            |
| Changelog        | `CHANGELOG.md` (Keep a Changelog)      |
| Shared kernel    | `app/rules.py` (soglie), `app/util.py` |

## Target Makefile

| Target             | Comando                                                      |
| ------------------ | ------------------------------------------------------------ |
| `test-unit`        | `pytest -q -m "not integration"`                             |
| `test-int`         | `pytest -q -m integration` (contratto stdio su `app.server`) |
| `pre-commit`       | `check-static-diff`                                          |
| `ready-for-review` | come L1 (gate Make)                                          |

## N/A documentati (L1)

- `test-e2e`: N/A — nessun runtime browser; il contratto stdio di `test_int.py` copre l'interfaccia esterna.
- `check-parity`: N/A — nessun dual-canon canone→runtime.

## Bounded context attivi

Vedi `docs/bounded-contexts.md`: QA Testo (`readability`, `keyterm`, `dedup`), SEO Meta (`meta`), MCP Protocol (`protocol`/`server`), Rules & Config (`rules`/`util`). Ogni `/slice` dichiara il context toccato.

## Safety note specifiche

- **grammar_check = ACL opt-in (M3-LT)**: senza `HAL_LT_URL` valorizzato il tool risponde `skipped/lt_disabled` senza costruire transport (zero rete garantita negli unit, transport iniettata). Fail-open: `OSError/URLError/HTTPError/Timeout` → `lt_unreachable`, non-JSON → `lt_bad_response`; mai raise al protocollo, mai verdetti inventati. Categorie regole: GRAMMAR/TYPO/SPELLING → `fail`, altre → `warn`, 0 match → `pass`.
- **Marker additivi**: `app/server.py` contiene il blocco marcato `hal-seo-M3LT` (handler + registrazioni `_TOOLS`/`_REQUIRED`/`TOOL_SCHEMAS`); patch futuri sul server partono dallo stato on-disk e non sovrascrivono i blocchi Seozoom.

- **Manifest-only**: i tool rispondono SOLO verdict+metriche compatti (≤`MAX_OUTPUT_CHARS`=4000); mai il corpo del testo/corpus in risposta. Test di guardia in `test_meta.py::test_output_json_compatto_manifest_only` e `test_dedup.py::test_output_non_echeggia_input`.
- **Niente LLM nel perimetro**: questo MCP è il gate deterministico del caso `harness-copywriting`; la generazione resta al System 2. Eventuali adapter LanguageTool/GSC/SerpApi solo in slice M3, opt-in via env.
- **Degradazione esplicita**: pyphen assente → euristica `heur-<lang>` dichiarata nel campo output `syllable_engine`; stesso input → output bit-identico (determinismo = requisito di test).
- **Soglie centrali**: `app/rules.py` = unica sede delle soglie (glossario); i moduli QA non duplicano costanti.
- **API pyphen**: `inserted()` nelle versioni moderne (≥0.17), `insert()` legacy — `app/readability.py::_pyphen_total` gestisce entrambe.
- **Guard import server**: `test_server_contract.py` importa `app.server` nei test unit — un SyntaxError nel server non deve più passare inosservato (evidenza: 2026-11-01, bracket mismatch in `_tools_list` intercettato solo da `test-int`).

## Conflitto sessioni parallele (2026-11-01)

- M3-LT: i pin sul tool list in `tests/test_protocol.py` (set `==`) e `tests/test_server_int.py` (`len==6`) erano scritti dalla sessione parallela; estesi minimamente a `grammar_check` (6→7) preservando la semantica strict. Se la sessione parallela ri-pinna, il conflitto si risolve lì.

Una sessione parallela ha scritto nello stesso tree uno scope **Seozoom imports** (default env `HAL_SEOZOOM_*`, `BATCH_SUBDIRS`, `SHA_PREFIX` in `rules.py`; `SERVER_VERSION` 0.2.0 atteso). Regola applicata da AGENTS.md: merge **additivo** — lo shared kernel attuale contiene sia le soglie QA (blocco "Soglie QA copy/SEO") sia le costanti import. Ogni futuro `/slice` deve ripartire dalla versione corrente di HEAD e non sovrascrivere l'altro cluster.
- `/version patch` 2026-11-01: release iniziale del progetto — `SERVER_VERSION` 0.2.0 → 0.2.1 (in `rules.py` e `server.py`); le regole di merge di cui sopra restano invariate.


## Ref cross-progetto

- Telemetria origine: `hal_system2/events/events-*.jsonl` use case `harness-copywriting`/`harness-analyze` (4 occ. ciascuna).
- Dipendenza segnalata: `laya_intake_class` mai `writing` in telemetria (bug da aprire in `hal_system2`).
- Installazione Zed (post-M1, a richiesta utente): `context_servers.hal-mcp-seo` come `hal-mcp-docs`.
