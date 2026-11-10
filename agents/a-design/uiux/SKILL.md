---
name: uiux
parent: a-design
version: 1.1.0
competencies:
  - static-stack
  - accessibility
  - editorial-layout
description: >-
  Reason why: senza regole comuni di layout e accessibilità, le pagine risultano confuse, incoerenti e difficili da usare per tutti. UI/UX per siti statici e shell pagina integrato in a-design: stack M3/vanilla CSS, accessibilità WCAG, layout editoriale, pattern guida/chrome comuni, scaffold L2. Non sostituisce charts (encoding dati) né a-copywriter (microcopy).
---

# uiux — UI/UX Shell & Accessibility

Skill di UI/UX per **shell pagina**, navigazione, tipografia, accessibilità WCAG e layout editoriale. Competenza integrata di **a-design**.

---

## Competenze integrate

- `static-stack`: No framework pesanti per contenuto indicizzabile; M3 vanilla CSS vars
- `accessibility`: Checklist WCAG 2.1 AA (focus, contrasto, touch targets, HTML semantico)
- `editorial-layout`: Mobile-first, rhythm tipografico, layout pulito

---

## Pattern guida & chrome comuni (shell)

Pattern tema-indipendenti della shell pagina, validati su due consumer (WTP App: Liste + Explorer B2B, dedup `/sync <` 2026-11-09). Le classi di implementazione restano nel design system L2 di progetto.

- **Guide collassabili (performance percepita):** sezioni di guida lunghe chiuse di default con `<details>`/`<summary>`; il trigger dichiara l'azione («Mostra guida / Nascondi guida»), mai contenuto aperto sulla prima vista.
- **Empty state con azione:** pannello senza selezione → heading + istruzione operativa su cosa cliccare per popolarlo; mai sola descrizione passiva.
- **«Come leggere», una riga:** ogni aiuto grafico è 1 riga (2 max) con l'interazione chiave; la legenda dice cosa rappresenta la vista e come si filtra (hover/click → risultato).
- **Click → risultato:** un'interazione che applica un filtro porta l'utente dove il risultato è visibile; nessun filtro «silenzioso».
