# Token colore — SurferDark (dark default)

Design system **SurferDark**. Runtime CSS SoT: `src/auth/css/surferdark.css`.

Niente MUI / theme JS. Valori = hex reali già usati in suite.
Ruoli semantici allineati a **Material Design 3** (primary ≈ accent, surface, outline, …) — tabella MD3 → SurferDark in [material3.md](material3.md).

## Palette dark (default app)

| Ruolo | Hex | Alias corto | Canone `--surferdark-*` |
|-------|-----|---------------------|--------|
| bg | `#0e0e0e` | `--bg` | `--surferdark-color-bg` |
| surface / paper | `#181818` | `--panel` | `--surferdark-color-surface` |
| elevated | `#222222` | `--elevated` | `--surferdark-color-surface-elevated` |
| accent | `#ffd400` | `--accent` | `--surferdark-color-accent` |
| accent pressed | `#e6bf00` | `--accent-dark` | `--surferdark-color-accent-pressed` |
| text | `#f4f4f0` | `--text` | `--surferdark-color-text` |
| text muted | `#9a9a92` | `--muted` | `--surferdark-color-text-muted` |
| divider | `rgba(244, 244, 240, 0.12)` | `--divider` | `--surferdark-color-divider` |
| hover | `rgba(255, 212, 0, 0.08)` | `--hover` | `--surferdark-color-hover` |
| selected | `rgba(255, 212, 0, 0.14)` | `--selected` | `--surferdark-color-selected` |
| error | `#ff6b6b` | `--error` | `--surferdark-color-error` |
| success | `#6bcf7f` | `--success` | `--surferdark-color-success` |
| on-accent | `#0e0e0e` | hardcode `.btn-primary` | `--surferdark-color-on-accent` (**TARGET**) |
| accent soft | `#ffe566` | non in `:root` | `--surferdark-color-accent-soft` (**TARGET**) |

## Shim deprecati

Alias corti (`--bg`, `--panel`, `--accent`, …) restano **solo** come:

```css
--bg: var(--surferdark-color-bg);
```

fino a fine migrazione auth + Liste + Explorer. Nuovo CSS: preferire `--surferdark-*`.

**Token opt-in (Wave3):** batch E19–E43 + Fine **E44** opt-in + **E45** `:root` alias **deleted**. Runtime `:root` = solo `--surferdark-*` (+ radius). `b2b_explorer.html` resta gitignored locale (può ancora usare alias locali).

Sinonimi Explorer da eliminare in migrazione: `--paper` → surface, `--primary` → accent.

## Light — solo print / PDF

| Ruolo | Hex |
|-------|-----|
| bg foglio | `#ffffff` |
| paper / th | `#f5f5f5` |
| text | `#0e0e0e` |
| text muted | `#5c5c56` |
| accent su light | `#c9a600` |

Niente theme UI light.

## Tipografia

System UI: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif`.
Dettaglio scale → [foundation.md](foundation.md).

## Radius / space / focus / touch

Vedi [foundation.md](foundation.md). Lock: radius **6–8px**, menubar hit-area **≥ 44px**, focus `2px` accent.

## Grafici D3 (riferimento)

| Uso | Hex |
|-----|-----|
| Serie | `#ffd400`, `#e6bf00`, `#9a9a92`, `#ffe566`, `#6e6e68`, `#c9a600` |
| Assi / empty | `#9a9a92` |
| Stroke fette (dark) | `#181818` |

Encoding → `a-charts`.

## Accessibilità colore

- `#f4f4f0` su `#0e0e0e` / `#181818`: ≥ 4.5:1.
- CTA: `#0e0e0e` su `#ffd400`.
- Non usare solo colore per ok/errore (testo/icona).
- Drift da chiudere: Liste `#e05252` vs `--error` `#ff6b6b` → un solo error token.
