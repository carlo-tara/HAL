# Design System SurferDark

Design system **vanilla** (HTML/CSS, no MUI/Tailwind/Bootstrap) per la suite Sales Coach / WTP App: **auth + Liste WTP + Explorer B2B**.

Nome del DS: **SurferDark** (ex “Enrico” / skin dark). SoT CSS: `src/auth/css/surferdark.css`.

## Decisioni LOCK (2026-09-13)

| Decisione         | Valore                                                                                                                                                                                                       |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Scope             | Un solo DS per auth + Liste + Explorer                                                                                                                                                                       |
| Radius            | Canone **Liste 6–8px**; chrome squadrato `0` da allineare                                                                                                                                                    |
| Token naming      | Target `--surferdark-*` only (`:root` short shims removed Fine E45)                                                                                                                                          |
| Light mode        | **Solo** print / PDF                                                                                                                                                                                         |
| Menubar           | Hit-area **touch-first ≥ 44px**                                                                                                                                                                              |
| Material Design 3 | **Mapping** di ruoli/pattern (color, shape, type, state layers) → [material3.md](material3.md). Runtime resta vanilla. Conflitto MD3 vs LOCK → **vince SurferDark**. **No** MUI / Material Web / seed purple |

## Albero

```
SurferDark
├── Foundation     → foundation.md (+ tokens-dark.md)
├── Material 3 map → material3.md
├── Components     → componenti.md
├── Patterns       → patterns.md
├── Migration CSS  → migration-css.md
└── Usage rules    → SKILL.md (checklist) + sezioni qui sotto
```

## SoT path

| Layer                             | Runtime (oggi)                         | Doc L2                                            |
| --------------------------------- | -------------------------------------- | ------------------------------------------------- |
| Token + primitives chrome/auth    | `src/auth/css/surferdark.css`          | `foundation.md`, `tokens-dark.md`, `material3.md` |
| Classi / drift                    | HTML inline Liste + Explorer           | `inventory-classi.md`                             |
| Primitives (btn, field, panel, …) | `surferdark.css` (+ inline page-local) | `componenti.md`                                   |
| Layout / dense UI / print         | —                                      | `patterns.md`                                     |
| Piano migrazione runtime          | —                                      | `migration-css.md`                                |
| Activation + gate pre-commit      | —                                      | `SKILL.md`                                        |
| Brand voice / microcopy           | —                                      | `brands/`, `a-copywriter-wtp` (**fuori scope**)   |
| Grafici D3                        | CDN + JS charts                        | `a-charts` (**fuori scope** encoding)             |

## Boundary

**Vive nel DS (questo L2 + CSS runtime):**

- Colore, type, space, radius, elevation/border, motion, z-index, focus, touch target
- Primitives UI (button, field, panel, alert, menubar, tabs, table densità, progress, empty/error _strutturali_)
- Pattern di composizione (section shell, dialog densità, AppBar, print invert)

**Non vive qui:**

- Stringhe UI / empty copy → `a-copywriter` + `a-copywriter-wtp` + `src/auth/locales/`
- Encoding grafici → `a-charts` (usa solo palette SurferDark referenziata)
- Brand corpus narrativo → `brands/wtp-app.md`
- Microcopy Explorer → `b2b-explorer-ui-ux` (deve **consumare** foundation SurferDark, non inventare palette)

## Anti-MUI / anti-framework

- Nessun `sx`, `variant="contained"`, `TextField`, `Card` MUI, `colorSchemes`, theme JS.
- Nessun Material Web Components / `@material/*` / dynamic color OS.
- Nessun Bootstrap / Tailwind / utility framework.
- Classi BEM-light + stati `.is-*` / `.is-active` / `.is-disabled`.
- **MD3 sì come vocabolario** ([material3.md](material3.md)); **MD3-as-library no**.
- Doc legacy che citava MUI è obsoleto: verità = CSS vars + classi vanilla.

## Usage rules (sintesi)

1. **Dark default** — superfici su `#0e0e0e` / paper `#181818`; niente bianco fuori print/PDF.
2. **Una CTA primaria** per vista (`.btn-primary` gold); secondarie quieter.
3. **No card-in-card** — un solo section shell per pannello.
4. **Token, non hex** — in CSS nuovo usare `--surferdark-*`; hex solo D3 serie / print.
5. **Radius 6–8** — input/btn/panel; eccezioni: spinner 50%, progress track ≤2px, pill chip solo se documentato.
6. **Touch ≥ 44px** — menubar trigger, tab, bottoni primari.
7. **Print invert** — `@media print` / export PDF: sfondo chiaro; chrome nascosto.
8. **A11y** — contrasto AA; `focus-visible` 2px accent; stato non solo a colore.
9. **Sentence case** su CTA (no UPPERCASE marketing Tara).

## Stato migrazione (doc vs codice)

| Stato                 | Cosa                                                                                                |
| --------------------- | --------------------------------------------------------------------------------------------------- |
| **Oggi in CSS**       | `:root { --surferdark-*; }` canone-only (Fine **E45** — short shim `--bg`/`--accent`/… **rimossi**) |
| **Target**            | Stesso: solo `--surferdark-*` (+ radius); non reintrodurre alias corti nel SoT                      |
| **Doc L2**            | Foundation + componenti + piano migrazione (`componenti.md`, `migration-css.md`)                    |
| **Prossimo (codice)** | Step 1–6 + Fine E44–E45 **Done** — evoluzioni future = TDD su token/primitives in `surferdark.css`  |
