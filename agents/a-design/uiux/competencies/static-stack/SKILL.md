---
name: static-stack
kind: competency
version: 1.0.1
description: >-
  Stack UI statico: vanilla CSS + custom properties M3; no Bootstrap/Tailwind;
  no SPA/router per contenuto indicizzabile. Token opt-in: soft dual-alias shim|target.
---

# Competenza — static-stack

## Regole

1. Preferire **vanilla CSS** + custom properties (Material Design 3 mapping ok)
2. **Non** introdurre Bootstrap, Tailwind, o CSS framework pesanti senza waiver L2
3. Contenuto indicizzabile: **no** SPA/client router come unico rendering
4. System font stack accettabile; display brand → L2
5. Bundler non obbligatorio per pagine marketing statiche
6. **Token opt-in / soft dual-alias:** se un batch migra `var(--shim-legacy)` → `var(--token-target)`, aggiornare nello **stesso** slice i soft-assert / contract test che matchano il vecchio token a dual-alias `--(?:shim-legacy|token-target)` (altrimenti GREEN CSS + RED assert). Nomi token e file test = **L2**

## Anti-pattern

- Utility CSS framework “per velocità”
- Hydration completa per articoli/landing SEO
- Migrare solo il CSS senza aggiornare soft-assert legacy nello stesso slice
