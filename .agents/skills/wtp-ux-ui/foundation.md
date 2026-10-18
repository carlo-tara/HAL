# Foundation — SurferDark

Valori allineati a `src/auth/css/surferdark.css`, con naming `--surferdark-*`.
Legenda: **OGGI** = presente nel CSS runtime; **TARGET** = da introdurre in migrazione CSS (non ancora nel file).

**Material Design 3:** i ruoli sotto (surface / primary / outline / …) seguono la semantica MD3; mappatura completa e limiti (no MUI, shape 6–8) → [material3.md](material3.md).

## 1. Color

### Palette dark (default app) — OGGI

| Ruolo | Hex | Alias corto | Canone `--surferdark-*` |
|-------|-----|-------------------------|------------|
| Bg pagina | `#0e0e0e` | `--bg` | `--surferdark-color-bg` |
| Surface / paper | `#181818` | `--panel` | `--surferdark-color-surface` |
| Elevated | `#222222` | `--elevated` | `--surferdark-color-surface-elevated` |
| Accent (CTA, link, focus) | `#ffd400` | `--accent` | `--surferdark-color-accent` |
| Accent pressed | `#e6bf00` | `--accent-dark` | `--surferdark-color-accent-pressed` |
| Accent soft (hover tint) | — | — | `--surferdark-color-accent-soft` `#ffe566` (**TARGET**, usato in doc/chart, non in `:root` oggi) |
| Text primary | `#f4f4f0` | `--text` | `--surferdark-color-text` |
| Text muted / secondary | `#9a9a92` | `--muted` | `--surferdark-color-text-muted` |
| Divider | `rgba(244, 244, 240, 0.12)` | `--divider` | `--surferdark-color-divider` |
| Hover | `rgba(255, 212, 0, 0.08)` | `--hover` | `--surferdark-color-hover` |
| Selected | `rgba(255, 212, 0, 0.14)` | `--selected` | `--surferdark-color-selected` |
| Error | `#ff6b6b` | `--error` | `--surferdark-color-error` |
| Success | `#6bcf7f` | `--success` | `--surferdark-color-success` |
| Accent contrast (testo su gold) | `#0e0e0e` | hardcode in `.btn-primary` | `--surferdark-color-on-accent` (**TARGET**) |

### Shim corti — **rimossi** (Fine E45)

`:root` espone solo `--surferdark-*` (+ radius). Non reintrodurre `--bg` / `--accent` / … nel SoT. Codice nuovo e legacy tracked devono usare canone.

### Light — solo print / PDF (LOCK)

Non è un theme switch UI. Valori di riferimento export:

| Ruolo | Hex |
|-------|-----|
| Bg foglio | `#ffffff` |
| Paper / th | `#f5f5f5` / `#f4f4f0` |
| Text | `#0e0e0e` / `#000` |
| Text muted | `#5c5c56` |
| Accent stampa | `#c9a600` (se serve CTA su light) |

**TARGET** (opzionale in `@media print`): `--surferdark-print-bg`, `--surferdark-print-text`, … — oggi hex inline in `customer.html`.

### Drift hex noto (non canone)

| Hex | Dove | Nota |
|-----|------|------|
| `#e05252` | Liste artifacts/customer | Error UI diverso da `--error` `#ff6b6b` |
| `rgba(255,255,255,0.12)` bordi | Liste inline | Vicino a `--divider` ma canale bianco vs `244,244,240` |
| Explorer `--paper` / `--primary` | `b2b-score3-clusters.html` | Alias → `--surferdark-*` (stessi hex) |

## 2. Typography

| Token | OGGI | TARGET |
|-------|------|--------|
| Family | system UI stack in `body` | `--surferdark-font-sans` (stesso stack) |
| Size base | `16px` | `--surferdark-font-size-body` |
| Line height | `1.55` | `--surferdark-font-line-body` |
| Title weight | `700`, `letter-spacing: -0.01em` / `-0.02em` | documentare scale sotto |

**Scale (canone doc — parte OGGI implicita, parte TARGET):**

| Ruolo | Size | Weight | Tracking |
|-------|------|--------|----------|
| App title (`.appbar-title`) | ~1.1–1.25rem | 700 | -0.02em |
| Section h1/h2 | 1–1.35rem | 700 | -0.01em |
| Body | 1rem / 0.95rem | 400 | 0 |
| Label / overline | 0.75–0.875rem | 600–700 | 0.04–0.06em |
| Meta muted | 0.8–0.875rem | 400 | 0 |

Niente Montserrat/Nunito/Inter come font runtime suite.

## 3. Space

**TARGET** scale 4-based (oggi padding sparsi, non vars):

| Step | px | Uso tipico |
|------|-----|------------|
| 1 | 4 | gap chip, lang toggle |
| 2 | 8 | gap field interno, menu item pad-y |
| 3 | 12 | padding cella tabella, gap chrome |
| 4 | 16 | padding contenuto, margin field |
| 5 | 20 | — |
| 6 | 24 | padding appbar / auth-card |
| 8 | 32 | — |
| 12 | 48 | margin auth-main, loading |

Vars TARGET es.: `--surferdark-space-4: 16px`.

## 4. Radius (LOCK: 6–8px canone Liste)

MD3 shape scale: usare solo **small→6px** e **medium→8px**. Non adottare large/XL MD3 su shell — [material3.md](material3.md) § Shape.

| Uso | Canone | SoT `surferdark.css` | OGGI Liste | OGGI Explorer |
|-----|--------|-------------------|------------|--------------|
| Input / button | **6px** | `0` (da allineare) | `6px` | misto `0` e `6px` |
| Panel / card / gauge | **8px** | n/a (auth-card senza radius) | `8px` | `8px` kpi/card |
| Progress track | 2px | — | 2px | — |
| Spinner | 50% | 50% | — | — |
| Pill | evitare `999px` salvo chip documentato | — | — | `999px` su un controllo |

**TARGET vars:** `--surferdark-radius-sm: 6px`, `--surferdark-radius-md: 8px`.

## 5. Border / elevation

Allineato a MD3 dark: preferire **surface tint** (bg → surface → elevated) rispetto a ombre pesanti.

| Token | OGGI | Note |
|-------|------|------|
| Border default | `1px solid var(--divider)` | Section shell (= outline) |
| Shadow menu | `0 4px 12px rgba(0,0,0,0.35)` / Liste `0 10px 28px` | Unificare in migrazione |
| Card shadow | nessuno in dark | Non aggiungere ombre Material 24dp |

**TARGET:** `--surferdark-elevation-menu` (valore unificato).

## 6. Motion

| OGGI | TARGET |
|------|--------|
| `@keyframes spin` 0.8s linear; progress width `.2s ease` (Liste) | `--surferdark-motion-fast: 150ms`, `--surferdark-motion-base: 200ms` |
| — | `@media (prefers-reduced-motion: reduce)` → spegnere spin / transition non essenziali (**TARGET**, non in CSS oggi) |

## 7. Z-index

| Layer | OGGI | TARGET |
|-------|------|--------|
| Menu panel | `z-index: 40` | `--surferdark-z-menu: 40` |
| Dialog / sheet | progress job Liste ~`250` (sopra AppBar ~200) | `--surferdark-z-dialog` ≥ AppBar (**TARGET**; non restare a 50 se AppBar sale) |
| Toast | — | `--surferdark-z-toast` sopra dialog (**TARGET**) |

## 8. Focus

| Regola | OGGI |
|--------|------|
| Outline | `2px solid var(--accent)` |
| Offset | `1px` (input auth) / `2px` (menu-trigger) — **unificare a 2px** in migrazione (**TARGET**) |
| Contrasti | testo `#f4f4f0` su `#0e0e0e`/`#181818` ≥ 4.5:1; CTA testo `#0e0e0e` su `#ffd400` |

## 9. Touch (LOCK ≥ 44px)

| Controllo | OGGI (AppBar post step 2–3) | Canone |
|-----------|----------------------------|--------|
| `.menu-trigger` | `min-height`/`min-width` **44px**, radius 6 | **min 44×44** |
| `.chrome-lang-btn` / `.chrome-profile-link` | **44px**, radius 6, quiet outline | ≥ 44px |
| `.btn` | pad ~10×16 → ~altezza 40px | portare a ≥ 44px altezza utile |
| Tab Liste `.main-tab` | pad `8px 16px` | ≥ 44px |

Desktop “app chrome” non è eccezione: **touch-first**.

## 10. Grafici (solo riferimento colore)

Serie D3 (consumo `a-charts`): `#ffd400`, `#e6bf00`, `#9a9a92`, `#ffe566`, `#6e6e68`, `#c9a600`; assi/empty `#9a9a92`; stroke fette su dark ≈ surface `#181818`.
