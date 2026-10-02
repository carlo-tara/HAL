---
name: accessibility
kind: competency
version: 1.0.0
description: >-
  Checklist WCAG 2.1 AA per shell UI: contrasto, focus, keyboard, touch, semantic HTML.
---

# Competenza — accessibility

## Checklist minima

- [ ] Contrasto testo/sfondo ≥ 4.5:1 (normale)
- [ ] `:focus-visible` visibile
- [ ] Navigazione keyboard completa
- [ ] Target tocco ≥ 44×44px
- [ ] Un solo `h1`; landmark `main`
- [ ] Skip link se header lungo
- [ ] `prefers-reduced-motion` rispettato
- [ ] `aria-*` solo dove la semantica nativa non basta

## Conflict

**accessibilità e leggibilità > decorazione** (anche vs brand UI).
