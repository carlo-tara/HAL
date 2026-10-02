# Permission modes — Plan vs Act + policy points

| Mode | Fasi | Write filesystem | Shell mutante |
|------|------|------------------|---------------|
| **Plan / ReadOnly** | `/slice`, analisi pre-RED, `/progress` read | No (solo note progress se già aperto) | Solo read/`make` dry se documentato |
| **Act / Write** | `/red`, `/green`, `/refactor`, `/steward` infra | Sì, nel perimetro slice | Sì, via Makefile |

## Stati del ciclo (HFDP State / Strategy)

| Stato | Significato | Owner tipico |
|-------|-------------|--------------|
| **Plan** | Slice/acceptance; no write di produzione | `/slice`, permission Plan |
| **Act** | RED→GREEN→REFACTOR nel perimetro | `/red` `/green` `/refactor` |
| **Stuck** | Hard stop dopo 3 fallimenti stesso approccio | `when-stuck` (`stuck@3`) |
| **Ready** | Gate sustainable-pace; review umana di intent | `/ready`, `ready-for-review` |

**Strategy** (senso harness, non polymorphism OO) = competenza di **fase** caricata on-demand (`tdd-red` / `tdd-green` / `tdd-refactor` / `steward`…), non una hierarchy di Strategy classes.

## Regole

1. **Plan→Act handoff:** niente GREEN finché `/slice` ha acceptance criteria e file ≤4 accettati
2. **Accept + clarify defaults:** se l’umano fa `/accept` (o accept 1–N) **senza** rispondere ai clarify, ma il Plan elenca **default consigliati** espliciti per ciascun clarify → lockarli e procedere Act. Se manca un default nel Plan → chiedere prima di `/red` (non indovinare)
3. **`/cycle` ≠ accept:** con Plan aperto, un nuovo `/cycle` ripete le opzioni; Act solo dopo `accept` esplicito
4. **Accept multi-opzione (A+B):** se le lettere sembrano alternative, trattale come **ibrido/composizione** quando compatibili (es. keep name + fail chiaro); se incompatibili → chiedere prima di Act
5. **No force default** — non forzare permessi elevati; chiedi conferma per azioni irreversibili
6. Anti-yolo: niente edit massivi fuori slice
7. Freeze L2: file in freeze list → read-only anche in Act (vedi template freeze)

## Policy evaluation points (warn | fail)

Analogia Harness.io — **senza** OPA/SaaS.

| Point | Quando | warn | fail |
|-------|--------|------|------|
| **On Slice** | Fine `/slice` | Slice ampio ma &lt;6 file | &gt;4 file senza waiver; no acceptance; no Makefile |
| **On Green** | Fine `/green` | Test flaky | `make test-unit`/`pre-commit` ≠ 0 |
| **On Ready** | `/ready` | PR vicino a budget LOC | `ready-for-review` ≠ 0; lazy-delete; shadow intent |
| **On Steward** | `/steward` | Regola morta | Gate make rotto; freeze violato |

Severity default: **fail** su gate Make; **warn** su sizing/effort.

Pin: [harness-lol-source.md](harness-lol-source.md) · [cursor-cloud-harness-source.md](cursor-cloud-harness-source.md) · [harness-io-source.md](harness-io-source.md)
