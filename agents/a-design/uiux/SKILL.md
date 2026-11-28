---
name: uiux
parent: a-design
version: 1.2.1
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
- **Slot brand vs meta di pagina:** lo slot brand dell'AppBar porta identità del prodotto e versione; i metadati di pagina (contatori, "generato…") stanno sotto l'header, mai dentro il titolo brand.
- **Azioni di output nel menu File della suite:** stampa/export sono voci del menu File e operano sulla vista corrente filtrata; niente pulsanti di export inventati per singola pagina.
- **Copy UI da origine i18n:** le stringhe a schermo derivano da un'unica origine i18n (msgid SoT) con fallback per chiave mancante; nessun msgid grezzo a schermo.
- **State layer M3 solo in `opacity:` (classe IACVT):** i token di stato di opacità (`--bb-state-*` ed equivalenti) si usano **solo** in `opacity:`, mai in `background:`/`outline:`/`color:`; hover canonico = state layer condiviso, non cambio di superficie. Insidia IACVT (invalid at computed-value time): il fallback `var(--token, fallback)` **non scatta** se il token è definito ma il suo valore è invalido per la proprietà — la dichiarazione viene scartata in silenzio, senza console error. Evidenza: brainbeez /improve ui/ux M3 (2026-11-07, /learn ! #23; **soglia ≥2 forzata su indicazione owner**, AGG-07).
