# Material Design 3 ↔ SurferDark

SurferDark **integra i ruoli e i pattern di Material Design 3** (MD3 / Material You) come **linguaggio di mappatura**, non come libreria runtime.

| Cosa | Decisione |
|------|-----------|
| Spec di riferimento | [Material Design 3](https://m3.material.io/) (color roles, shape, type roles, state layers, motion) |
| Runtime suite | **Vanilla CSS** + `--surferdark-*` — **niente** MUI, Material Web Components, `@material/*`, theme JS |
| Brand | Palette Sales Coach (**gold** `#ffd400` su dark `#0e0e0e`) — non la default purple/tonal seed Google |
| Shape | Canone SurferDark **6–8px** (LOCK); non adottare corner “extra-large” 28dp MD3 su shell |
| Touch | SurferDark **≥ 44px** (LOCK); MD3 consiglia 48dp — usare 44 come minimo suite, 48 dove c’è spazio |

Se MD3 e LOCK SurferDark confliggono → **vince SurferDark LOCK**.

---

## 1. Perché MD3 qui

- Vocabolario condiviso (primary / on-primary / surface-container / outline / state layer) per review e migrazione token.
- Allineamento a competenze L1 `a-uiux` / `static-stack` (custom properties M3-ready, no framework).
- Evitare drift “inventiamo un terzo sistema” quando si parla di elevation, shape scale, typography roles.

**Non significa:** reintrodurre React MUI, `sx`, `variant="filled"`, o CSS Material precompilato.

---

## 2. Color roles MD3 → SurferDark

MD3 separa **ruolo** (semantic) da **valore**. SurferDark usa gli stessi ruoli con hex suite.

| Ruolo MD3 | SurferDark TARGET | Hex / valore | Note |
|-----------|-------------------|--------------|------|
| `background` | `--surferdark-color-bg` | `#0e0e0e` | Canvas pagina |
| `surface` | `--surferdark-color-surface` | `#181818` | Paper / section shell |
| `surface-container` / `surface-container-high` | `--surferdark-color-surface-elevated` | `#222222` | Menu, panel elevated |
| `primary` | `--surferdark-color-accent` | `#ffd400` | CTA, focus, link |
| `on-primary` | `--surferdark-color-on-accent` | `#0e0e0e` | Testo su gold |
| `primary-container` | `--surferdark-color-selected` / hover soft | `rgba(255,212,0,0.14)` / `0.08` | Chip selected, row tint |
| `on-surface` | `--surferdark-color-text` | `#f4f4f0` | Body |
| `on-surface-variant` | `--surferdark-color-text-muted` | `#9a9a92` | Meta, label secondaria |
| `outline` / `outline-variant` | `--surferdark-color-divider` | `rgba(244,244,240,0.12)` | Bordi 1px |
| `error` | `--surferdark-color-error` | `#ff6b6b` | |
| `on-error` | (TARGET) | `#0e0e0e` o `#fff` — scegliere in migrazione per contrasto AA | |
| `tertiary` / tonal secondary | **non** introdurre viola MD3 | riusare muted / accent-soft | Suite monocromatica gold |

Shim corti OGGI (`--bg`, `--accent`, …) restano alias verso `--surferdark-*` — vedi [tokens-dark.md](tokens-dark.md).

### Seed / tonal palette

MD3 genera tonalità da un seed. **SurferDark non genera tonalità runtime**: i valori sono **fissi** (tabella sopra). Non aggiungere algoritmo HCT/CAM16 in FE senza mandato + TDD.

---

## 3. State layers (MD3)

MD3 applica un overlay di opacità su surface/primary per hover / focus / pressed / dragged.

| Stato MD3 | SurferDark (canone) |
|-----------|---------------------|
| Hover | `--surferdark-color-hover` (`rgba(255,212,0,0.08)`) o brightness su primary |
| Focus | non solo layer: **`outline 2px` accent** + offset 2px (`focus-visible`) |
| Pressed | `--surferdark-color-accent-pressed` / selected più forte |
| Disabled | opacity ~0.5–0.6 + no pointer; non solo desaturazione |

**Do:** combinare state layer + focus ring (MD3 + a11y).
**Don’t:** hover solo `opacity` sul testo senza change di surface/border.

Implementazione classi: [componenti.md](componenti.md) (`.is-*`, `.btn:hover`, …).

---

## 4. Shape (MD3 shape scale → SurferDark)

| MD3 (indicativo) | SurferDark LOCK | Uso |
|------------------|-----------------|-----|
| none / extra-small | evitare `0` su controlli nuovi | — |
| small ~8–12dp | **6px** (`--surferdark-radius-sm`) | input, button, menu-item, trigger |
| medium ~12–16dp | **8px** (`--surferdark-radius-md`) | panel, menu-panel, gauge, dialog |
| large / extra-large (20–28dp+) | **non usare** su shell suite | fuori brand |

Pill `999px`: solo chip documentato; default no.

---

## 5. Typography roles MD3 → SurferDark

| Ruolo MD3 | SurferDark (scale foundation) | Esempio classe / uso |
|-----------|-------------------------------|----------------------|
| display / headline | App title ~1.1–1.35rem / 700 | `.appbar-brand`, auth `h1` |
| title | Section ~1–1.25rem / 700 | h2 panel, Preferiti |
| body | 1rem / 400, line 1.55 | `body`, field value |
| label | 0.75–0.875rem / 600–700, tracking 0.04–0.06em | overline field, `.owner-section` |
| — | System UI stack (no Roboto obbligatorio) | foundation |

Niente scale MD3 “display-large 57sp” in AppBar: densità suite = **compact desktop + touch**.

---

## 6. Elevation / surface tint

MD3 dark preferisce **surface tint** a ombre pesanti.

| Livello | SurferDark |
|---------|------------|
| 0 — canvas | bg `#0e0e0e` |
| 1 — section | surface `#181818` + border divider |
| 2 — overlay (menu, owner panel) | elevated `#222` + shadow soft menu |
| 3+ | evitare; dialog = elevated + z-dialog |

Shadow canone: `--surferdark-elevation-menu` (oggi `0 10px 28px rgba(0,0,0,0.55)` / legacy `0 4px 12px` — unificare in migrazione).
**No** multi-layer Material drop-shadow da kit MUI.

---

## 7. Motion

| MD3 | SurferDark TARGET |
|-----|-------------------|
| short / standard | `--surferdark-motion-fast: 150ms`, `--surferdark-motion-base: 200ms` |
| emphasized | solo se documentato (es. panel open) — default standard |
| reduced motion | `@media (prefers-reduced-motion: reduce)` spegne spin / transition non essenziali |

---

## 8. Componenti: equivalenze (vanilla)

| MD3 (nome) | SurferDark (classe) | Note |
|------------|---------------------|------|
| Filled button | `.btn.btn-primary` | primary = gold |
| Outlined button | `.btn.btn-outline` | |
| Text button | `.btn.btn-secondary` | quiet |
| Text field | `.field` / `.auth-field` | label overline |
| Menu | `.menu-root` / `.menu-trigger` / `.menu-panel` | AppBar |
| Navigation bar (top) | `.appbar` | non Bottom nav |
| Tabs | `.main-tab` / `.tab` | |
| Snackbar | toast TARGET | non ancora SoT |
| Dialog | `.dialog` TARGET / densità patterns | |
| Checkbox / switch | nativo + accent | no MUI Switch |

Dettaglio anatomia/stati: [componenti.md](componenti.md).

---

## 9. Anti-pattern (MD3 “finto”)

| Vietato | Perché |
|---------|--------|
| `@mui/*`, `ThemeProvider`, `sx={{}}` | Anti-MUI LOCK; layoutHygiene |
| Material Web / `md-filled-button` | Dipendenza e look default Google |
| Seed purple / dynamic color OS | Rompe brand gold |
| Corner 28dp su AppBar/card | Fuori canone 6–8 |
| Elevation 24dp ovunque | Rumore su dark |
| Copiare solo il nome “MD3” senza roles | Doc theater |

---

## 10. Checklist review (MD3-aware)

1. Ruolo colore citato (primary/surface/outline/…) mappa a `--surferdark-*` o shim documentato?
2. Shape 6/8 — non large MD3?
3. State: hover/focus/pressed senza perdere `focus-visible`?
4. Hit ≥ 44px (48 ok)?
5. Nessuna dipendenza Material runtime?
6. Print resta light invert — non “MD3 light theme” UI?

---

## Vedi anche

- [foundation.md](foundation.md) — valori e scale
- [tokens-dark.md](tokens-dark.md) — tabella token
- [design-system.md](design-system.md) — LOCK e boundary
- [migration-css.md](migration-css.md) — step runtime (token prima)
