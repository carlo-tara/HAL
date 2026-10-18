# Inventory classi — SurferDark

Snapshot inventory (2026-09-16, post Wave3 E34–E43 + Fine deferred). Runtime CSS SoT: `src/auth/css/surferdark.css`.

**Status:** Wave3 **E34–E43** + Fine **E44–E45** in HEAD. `:root` = canone-only `--surferdark-*` (no short shim). `b2b_explorer.html` gitignored. This file is a **class map**, not the live residual scorecard — for open work see `ToDo.md`.

## 1. `surferdark.css` — classi presenti

### Token `:root`

**Canone:** `--surferdark-color-*`, `--surferdark-radius-sm` (6px), `--surferdark-radius-md` (8px).
**Shim legacy:** `--bg`, `--panel`, `--elevated`, `--accent`, `--accent-dark`, `--text`, `--muted`, `--divider`, `--hover`, `--selected`, `--error`, `--success`.

### Layout / auth / suite shell

| Classe | Ruolo |
|--------|--------|
| `.appbar*` / `.appbar-menubar` / `.appbar-end` | Header suite |
| `.auth-main` / `.auth-card` / `.auth-field` / `.auth-actions` | Login/verify |
| `.wtp-layout` / `.wtp-content` / `.back-link` | Shell Liste |
| `.spinner` / `.auth-loading` / `.auth-lang-bar` | Auth util |

### Azioni / feedback

| Classe | Ruolo |
|--------|--------|
| `.btn` / `.btn-primary` / `.btn-secondary` / `.btn-outline` / `.btn-sm` | CTA (radius sm, min-height 44) |
| `.alert*` | Banner |
| `.empty-state` / `.error-message` | Stati strutturali (`--error`) |

### Form / tabs / panel / progress / table / chip

| Classe | Ruolo |
|--------|--------|
| `.field` (+ `.field-row` / hint / error) | Form Liste |
| `.tabs` / `.tab` | Canone tab |
| `.main-tab` / `.sub-tab` / `.output-tab` / `.output-subtab` | Alias dialetti |
| `.panel` / `.customer-shell` | Section shell |
| `.progress-dialog*` / `.progress-message` / `.progress-bar*` | Job lightbox |
| `.user-table` / `.customer-table` / `.user-table-wrap` | Table densità |
| `.gauges-grid` / `.gauge-card` / `.gauge-title` | Metric cards |
| `.chip` / `.filter-chip` / `.strategy-chip` | Chip generico + Explorer |

### Menubar / chrome

| Classe | Ruolo |
|--------|--------|
| `.menu-*` | File / Preferiti / Prodotti (touch ≥44, panel radius 8, z≈200) |
| `.chrome-session` / `.chrome-profile-link` / `.chrome-lang-*` | End AppBar |

### Ancora TARGET / Explorer-only

Dialog generico `.dialog*` (job usa `.progress-dialog*`); Explorer densità catalogata → SoT Wave3 D0–E7 (score3 senza `<style>` page-local).

---

## 2. Liste WTP — `<style>` page-local (post step 4)

Sorgenti: `index.html`, `customer.html`, `artifacts.html`. Caricano `surferdark.css`; inline = **solo** densità pagina.

| File | Inline tipico (ok) | Vietato in inline |
|------|--------------------|-------------------|
| `index.html` | owner-menu, advanced-panel, summary/chart Output, list-editorial, favorites | `.field` / `.btn-primary` / `.main-tab` / `.progress-bar-fill` con `#ffd400` |
| `customer.html` | sezioni scheda (meta/B2B/reading/stat), print | `.sub-tab` / `.empty-state` / `.error-message` con hex |
| `artifacts.html` | search list densità | `.btn-primary` / `.empty-state` hex |

Gate: `src/auth/js/surferdarkPrimitivesCss.test.js`.

---

## 3. Explorer B2B

Prodotto live: `b2b-score3-clusters.html` — densità + chart chrome interamente in `surferdark.css` (nessun `<style>` page-local). CTA = `.btn.btn-secondary`.
`b2b_explorer.html` = artefatto locale gitignored (può ancora avere `:root` alias).

Residuo soft: nessuno su token corti in SoT (E45). Token opt-in E19–E23 + Wave3 E34–E43 + Fine **E44–E45**. Emotion SX pruned E8–E11; densità product HTML zero `<style>` (E13–E18).

---

## 4. Drift noto

| Issue | Nota |
|-------|------|
| Print / PDF hex | LOCK light — ok; PDF CSS SurferDark/vanilla (no Mui*) |
| Token shim `--bg`/`--accent` | **Removed** from `:root` (E45); use `--surferdark-*` only |
| Inventory menubar min-height 28 / z=40 | **Stale** — runtime ≥44 / z≈200 |
| Class map vs residual | Prefer `ToDo.md` / work-graph for open Act; inventory = SoT class roles |
