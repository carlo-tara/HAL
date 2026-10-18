# Piano migrazione CSS — SurferDark

Doc di piano **solo**. Implementazione produzione = ciclo **RED → GREEN → REFACTOR** (rule repo). Non eseguire gli step da questo file senza mandato utente + test.

SoT runtime: `src/auth/css/surferdark.css` (shim `enrico.css` rimosso in wave2).
Catalogo: [componenti.md](componenti.md) · foundation: [foundation.md](foundation.md) · MD3: [material3.md](material3.md) · inventory: [inventory-classi.md](inventory-classi.md).

## Principi

1. Un solo foundation per auth + Liste + Explorer.
2. Token `--surferdark-*` prima; rename file CSS **ultimo**. Commenti/doc possono citare ruoli MD3 (`primary`→accent, `surface`, `outline`).
3. Classi: promuovere esistenti (no big-bang `.sd-*`). **No** step che introducono `@mui` / Material Web.
4. Ogni step piccolo, reversible, con criterio “done” falsificabile.
5. Dove si tocca CSS/HTML/JS eseguibile → TDD (test che fissano comportamento token/classi/a11y dove già coperto; altrimenti smoke + assert CSS vars in test unitari se esistono harness). Gate skin: `node --test src/auth/js/surferdarkAppbarCss.test.js src/auth/js/surferdarkPrimitivesCss.test.js` (inclusi in `make test-unit`).

---

## Step 1 — Token `--surferdark-*` + shim

| | |
|--|--|
| **Cosa** | In `enrico.css` `:root`: definire `--surferdark-color-*` (e space/radius se già decisi) con valori **uguali** a oggi; alias `--bg`, `--panel`, `--accent`, … = `var(--surferdark-…)` |
| **File** | `src/auth/css/enrico.css` (+ test se presenti su CSS/theme; altrimenti assert documentati / snapshot visuale manuale) |
| **Rischio** | Basso se valori identici; regressione solo se typo nei nomi |
| **Gate** | `make test-unit`; smoke auth login + `/wtp/` + Explorer (hard refresh) |
| **Done** | Tutti i token OGGI hanno equivalente `--surferdark-*`; shim corti funzionano; nessun cambio visivo intenzionale |

**RED suggerito:** test che `getComputedStyle` / parser CSS (o fixture che legge `:root`) espone `--surferdark-color-bg` === `#0e0e0e` e `--bg` risolto allo stesso valore.

---

## Step 2 — Radius canone 6–8px

| | |
|--|--|
| **Cosa** | btn/input/menu-item/menu-trigger: **6px**; panel/auth-card/menu-panel: **8px**; vars `--surferdark-radius-sm/md` |
| **File** | `enrico.css`; verificare che override Liste non contrastino |
| **Rischio** | Medio — look chrome/auth cambia (da 0 → arrotondato) |
| **Gate** | `make test-unit`; review visuale auth + menubar + form Liste |
| **Done** | Nessun `border-radius: 0` su btn/input/menu (salvo spinner 50%); panel 8px |

**RED suggerito:** assert CSS (o contract test) su regole `.btn` / `.auth-field input` radius ≥ 6px.

---

## Step 3 — Menubar hit-area ≥ 44px

| | |
|--|--|
| **Cosa** | `.menu-trigger` (e idealmente `.menu-item`, `.chrome-lang-btn`) min-height/pad → **≥ 44px** touch target |
| **File** | `enrico.css`; eventualmente `src/auth/js/chrome.js` se markup richiede wrapper |
| **Rischio** | Medio — AppBar più alta; layout title/session |
| **Gate** | `make test-unit`; test chrome se esistono; verifica keyboard menubar |
| **Done** | Trigger misurabile ≥ 44×44; focus-visible integro; File/Preferiti/Prodotti ok |

**RED suggerito:** test DOM/chrome su `min-height` calcolato del trigger ≥ 44, o test a11y esistente esteso.

---

## Step 4 — Primitives Liste in CSS condiviso; spegnere inline

| | |
|--|--|
| **Cosa** | Promuovere in `enrico.css`: `.field`, `.btn-secondary`, `.tabs`/`.tab` (+ alias `.main-tab`…), `.panel`, `.progress*`, `.empty-state`, `.error-message`, table densità. Rimuovere/ridurre hex e duplicati da `<style>` in `index.html` / `customer.html` / `artifacts.html` (restano solo layout max-width se serve) |
| **File** | `enrico.css`; `src/wtp/frontend/*.html`; eventuali JS che iniettano style |
| **Rischio** | Alto — regressioni layout Liste; print customer |
| **Gate** | `make test-unit`; `npm run lint` in `src/wtp/frontend` se tocca JS; smoke Input/Output/scheda/artifacts + print |
| **Done** | Pagine Liste senza ridichiarare `--bg`/`#ffd400` per componenti catalogati; usano classi SoT |

**RED suggerito:** test FE che markup atteso espone classi canoniche; o snapshot HTML fixture; regressione route smoke.

---

## Step 5 — Explorer sullo stesso foundation

| | |
|--|--|
| **Cosa** | Rimuovere `:root` duplicato in `b2b-score3-clusters.html` (e simili); usare token SurferDark/shim; mappare `--paper`/`--primary` → shim o sostituire con canone; allineare radius/chip/tab agli alias SoT |
| **File** | `src/explorer/b2b/*.html` (almeno score3); no seconda palette |
| **Rischio** | Alto — file grande, molte classi locali |
| **Gate** | `make test-unit`; smoke `/explorer/b2b/`; non rompere menubar condiviso |
| **Done** | Nessuna palette parallela; hex solo dove eccezione documentata (chart stroke ok via token; D3 `COLORS` in JS resta eccezione) |

**RED suggerito:** assert assenza di `--primary:` locale o test che computed accent === SurferDark gold.

---

## Step 6 (opzionale, ultimo) — Rename file CSS

| | |
|--|--|
| **Cosa** | `enrico.css` → `surferdark.css`; aggiornare tutti i `<link>`; redirect/alias opzionale |
| **File** | CSS path; HTML auth/wtp/explorer; Docker/nginx se path statici; doc L2 |
| **Rischio** | Breaking path; cache CDN/browser |
| **Gate** | `make test-unit`; `make ready-for-review` prima di review; smoke suite |
| **Done** | Nessun link a `/auth/css/enrico.css`; SoT solo `surferdark.css`; L2 aggiornato |

**Post-step 6 (wave2):** shim `enrico.css` **rimosso** — non reintrodurre. Gate: `existsSync(enrico.css) === false`.

**Anti-pattern (appreso):** non fare replace globale stringa `enrico.css` → `surferdark.css` su test/doc senza review — può corrompere `assert.doesNotMatch(…/enrico.css)`. Dopo rename/delete: verificare a mano HTML `href` SoT e assert pos/neg nei contract.

**Non fare** prima che step 1–5 siano stabili.

---

## Fuori scope di questo piano

- Microcopy / `.po`
- Encoding D3 (`a-charts`)
- Theme UI light
- Prefisso obbligatorio `.sd-*` su tutte le classi

## Ordine vincolato

`1 → 2 → 3` (foundation chrome) poi `4 → 5` (app) poi `6` (rename).
Non saltare 1: gli step successivi devono già scrivere contro `--surferdark-*` dove toccano valori nuovi.

## Stato (runtime)

| Step | Stato |
|------|--------|
| 1 Token `--surferdark-*` + shim | **Done** → Fine **E45** rimosse anche le alias corte da `:root` (gate AppBar: no `--bg`/…) |
| 2 Radius 6–8 | **Done** su `.btn` / `.auth-field input` / `.auth-card` (+ menubar già 6/8) |
| 3 Menubar ≥44px | **Done** (preesistente; contract test) |
| 4 Primitives Liste | **Done** — SoT in `surferdark.css`; inline ridotto a layout/chart page-local (`index`/`customer`/`artifacts`) |
| 5 Explorer foundation | **Done** — `b2b-score3-clusters.html` `:root` = solo alias `--paper`/`--primary`/… → `--surferdark-*`; gate `surferdarkPrimitivesCss.test.js` |
| 6 Rename `enrico.css` | **Done** — SoT `surferdark.css`; shim rimosso (wave2); HTML suite → `/auth/css/surferdark.css` |
