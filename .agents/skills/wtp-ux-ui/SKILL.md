---
name: wtp-ux-ui
extends: a-uiux
version: 1.3.67
extends-version: 1.0.7
description: >-
  Design System SurferDark (L2) + mapping Material Design 3 per Sales Coach / WTP App:
  foundation, componenti, pattern, MD3 roles, migrazione CSS (auth + Liste + Explorer).
  Runtime CSS surferdark.css; no MUI. Extends a-uiux (a11y/stack editoriale → L1).
disable-model-invocation: true
---

# SurferDark — Design System (L2)

Skill figlia. Eredita `a-agentzero` → `a-uiux` → **questo file**.

Canoni a11y / stack statico M3 / layout editoriale generico → L1 `a-uiux`. Qui solo SurferDark, path WTP e checklist prodotto.

## Quando usarla

Prima di proporre o committare layout, colori, tipografia, chrome, componenti shell o tema in:

- `src/auth/` (shell)
- `src/wtp/frontend/` (Liste)
- `src/explorer/b2b/` (Explorer)

**Non** usarla per microcopy (→ `a-copywriter-wtp`) né encoding grafici (→ `a-charts`).

## Cos’è

**SurferDark** è il design system unico della suite (dark-first, vanilla HTML/CSS).
Ex skin “Enrico”: stesso look (`#0e0e0e` / `#ffd400`), nome e struttura DS aggiornati.

Integra **Material Design 3** come mappatura di ruoli (color / shape / type / state layers) — vedi [material3.md](material3.md). **Non** introduce MUI né Material Web (allinea non-goals L1 `a-uiux`).

Runtime CSS SoT: `src/auth/css/surferdark.css` (shim `enrico.css` **rimosso**). Piano storico: [migration-css.md](migration-css.md) (step 1–6 **Done**).

## File del DS

| File                                       | Contenuto                                                |
| ------------------------------------------ | -------------------------------------------------------- |
| [design-system.md](design-system.md)       | Overview, albero, boundary, decisioni LOCK               |
| [foundation.md](foundation.md)             | Color, type, space, radius, motion, z, focus, touch      |
| [tokens-dark.md](tokens-dark.md)           | Palette + naming target / shim                           |
| [material3.md](material3.md)               | Mapping MD3 ↔ SurferDark (roles, shape, state, anti-MUI) |
| [componenti.md](componenti.md)             | Primitives: classi, stati, a11y, do/don’t                |
| [patterns.md](patterns.md)                 | Layout, shell, menubar, form, print                      |
| [inventory-classi.md](inventory-classi.md) | Classi enrico vs Liste vs Explorer + drift               |
| [migration-css.md](migration-css.md)       | Piano step 1–6 migrazione CSS (TDD-aware)                |
| [CHANGELOG.md](CHANGELOG.md)               | Storia L2                                                |

## Decisioni LOCK (sintesi)

1. Scope: auth + Liste + Explorer
2. Radius canone 6–8px (allineare chrome da 0)
3. Token target `--surferdark-*` only (`:root` short shims removed in Fine E45)
4. Light solo print/PDF
5. Menubar ordine File→Preferiti→Prodotti; touch → L1 `a-uiux` / checklist #6
6. MD3 = mapping/roles only; conflitti → vince SurferDark LOCK; **no** MUI / Material runtime

## Checklist pre-commit UI (slim)

1. Token SurferDark / vars — no hex nuovi salvo D3/print; ruoli MD3 solo via [material3.md](material3.md)
2. Dark default; print invert light
3. Section shell: surface + divider + radius 8; **no card-in-card**
4. CTA SurferDark: primary **gold** + sentence case — classi in [componenti.md](componenti.md); una CTA / hit ≥44px → L1 `a-uiux`
5. Radius input/btn 6; panel 8; no 0 legacy su nuovi controlli; no corner MD3 large/XL
6. Menubar ordine WTP File→Preferiti→Prodotti; touch target → L1 `a-uiux`
7. Nuovi blocchi: preferire `.panel` / `.field` / `.tab` SoT (alias legacy ok in migrazione); product homes = `.product-layout` / `.product-content`
8. Focus-visible SurferDark: **2px accent**; state layers MD3 ok **con** focus ring; contrasto AA → L1 `a-uiux`

9. PDF disabilitato finché contenuto chiave non pronto; export in File→Salva
10. Grafici: palette SurferDark; dettagli → `a-charts`
11. Dopo cambi FE: preview `http://127.0.0.1:8181/wtp/` (o `:3000`) + hard refresh — preferire `127.0.0.1` a `localhost` (IPv4-only + cookie sessione host-bound)
12. Tocchi a `surferdark.css`/HTML skin: RED→GREEN; gate = contract test CSS (`src/auth/js/surferdarkAppbarCss.test.js`, `surferdarkPrimitivesCss.test.js`); rename path CSS = no blanket replace su assert negativi; assert «non ridichiarare» / no-hex: **suite-wide** tollerare assenza `<style>` (`pageCss = style ? style[1] : ''` **oppure** `doesNotMatch(html, /<style/)`); helper `ruleBody` = match standalone/comma-group only — **no** `(?:^|[,\\s])` che cattura discendenti (`.product-content .panel` ≠ `.panel`); **token opt-in GREEN:** dual-alias soft-assert → L1 `a-uiux`/`static-stack` regola 6 — shim WTP `--(?:bg|panel|muted|…|surferdark-*)` nello **stesso** slice

13. i18n UI (chrome + Liste + customer/`data-i18n`): niente msgid a schermo — `uiT` / fallback se `t(key)===key`; IT/EN fissi in AppBar; msgid SoT da `.po`; product homes → `applyDomI18n`
14. Liste Input: primary/advanced come [patterns.md](patterns.md) § Liste Input; payload Zod completo
15. Liste Output: Sintesi = summary doc + charts; scheda lista = sub-tab + campi snake_case; progress job = lightbox bloccante ([patterns.md](patterns.md) § Liste Output, [componenti.md](componenti.md) § Progress)
16. `<style>` pagina = **evitare** su HTML prodotto (densità in SoT); **no** ridichiarare `.field`/`.btn*`/`.tab`/`.progress*`/`.empty-state` con hex — SoT `surferdark.css`. **Zero `<style>` page-local:** Explorer, Profile, Risk, Customer/Company homes+sheets, Liste `index` / `artifacts` / legacy `customer.html` (E13–E18). Print/PDF LOCK light ok; se print CSS entra in SoT → **scope** (es. `body:has(#customer-main-content)`), non regole globali `body`/`.appbar`; export HTML può avere style isolato
17. Scheda cliente SoT = Customer 360 `/customer/<userId>` (`src/customer/`); Liste solo link/API — niente scheda UI interna. Legacy `/wtp/customer.html` può essere redirect 302 (mandato ownership). **Back-link:** da lista/sintesi → «Torna all’analisi» (`/wtp/lista/…` o `/wtp/sintesi/…` via `returnUrl`/query); senza contesto Liste → «← Customer 360» `/customer/`. **Tab Integrazioni:** card stato+CTA (HubSpot / B2B / PBX), non tabella KV email/`ok`. **Tab Altro/Profilo:** formattare nested (`birthParts`, `Set`, `segments`) via formatter FE — no `[object Object]`
18. Nessuna dipendenza `@mui/*` / Material Web / seed purple “dynamic color”; migrazione CSS = skin only (no redesign feature); **wave emotion chiusa** — **no** reintrodurre `*Sx` / `APP_MENU_*_SX` né moduli morti; prunati/deleted: `appMenuBarModel`, `outputResultLayout`, `customerSheetLayout`, `inputPrimaryLayout` (E10), `profileDialogLayout` (E11). Modulo SX senza importer runtime → DELETE + contratto `existsSync===false`, non reinventare UI

19. **URL tab 360** — su Company/Customer usare la mappa condivisa `src/wtp/frontend/lib/core/tabUrlNavigation.js`, non hash derivati dalle label tradotte né router duplicati. Contratto: tab base senza frammento; apertura diretta/refresh/Avanti-Indietro e `hashchange` sincronizzati; query WTP preservata; fallback per frammenti sconosciuti senza riscrivere URL; deduplicare `popstate`/`hashchange` per non riattivare i lazy load. Attivare la tab da URL dopo il render, senza reset successivo alla prima tab. URL pubblici nei README `src/company/` e `src/customer/`; test `tabUrlNavigation.test.js` e limiti della prova browser in `docs/testing.md`.

## Non-goals

| Fuori scope                      | Dove                                               |
| -------------------------------- | -------------------------------------------------- |
| Microcopy / locale / brand voice | `a-copywriter-wtp`, `brands/`, `src/auth/locales/` |
| Encoding D3                      | `a-charts`                                         |
| Microcopy Explorer               | `b2b-explorer-ui-ux` (deve consumare SurferDark)   |

## Marketing vs runtime

|        | tarafacilitazione.com | Suite SurferDark |
| ------ | --------------------- | ---------------- |
| Font   | Inter                 | System UI        |
| Accent | Teal / mauve          | Gold `#ffd400`   |
| Sfondo | Chiaro                | Dark `#0e0e0e`   |
| CTA    | Spesso MAIUSCOLO      | Sentence case    |

## SoT implementazione

| Cosa                 | Dove                          |
| -------------------- | ----------------------------- |
| CSS shell SurferDark | `src/auth/css/surferdark.css` |
| Chrome menubar       | `src/auth/js/chrome.js`       |
| Liste                | `src/wtp/frontend/`           |
| Explorer             | `src/explorer/b2b/`           |
