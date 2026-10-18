# Componenti — SurferDark

Catalogo primitives. **No microcopy** (slot vuoti / chiavi i18n solo placeholder strutturali). **No D3.**

Drift e inventario: [inventory-classi.md](inventory-classi.md). Foundation: [foundation.md](foundation.md). MD3 map: [material3.md](material3.md). Migrazione: [migration-css.md](migration-css.md).

Stati hover/focus/pressed: trattare come **MD3 state layers** + `focus-visible` obbligatorio (non sostituire il focus ring con solo tint).

## Scelta naming classi (LOCK pragmatico)

**Promuovere le classi già usate** come API pubblica; **niente big-bang** verso `.sd-*`.

| Regola | Dettaglio |
|--------|-----------|
| Esistenti | `.btn`, `.btn-primary`, `.btn-outline`, `.alert*`, `.menu-*`, `.appbar`, `.field` (Liste), `.auth-field` (auth) restano canoniche |
| Mancanti / nuovi | Nomi corti neutri: `.panel`, `.tab` / `.tabs`, `.chip`, `.dialog`, `.progress`, `.empty-state`, `.error-message`, `.btn-secondary` |
| Prefisso `.sd-*` | **Opzionale** dual-class solo se serve disambiguare durante migrazione (es. `.panel.sd-panel`); non è l’API target |
| Stati | Sempre `.is-active`, `.is-disabled`, `.is-open`, `.is-featured`, `.is-error` |

Perché: HTML Liste/auth/Explorer già usano `.btn` / `.menu-*` / `.field`; un rename a `.sd-btn` moltiplicherebbe il rischio senza guadagno UX. Token sì `--surferdark-*`; classi no.

---

## 1. Button

**Purpose:** azioni primarie/secondarie; una CTA primary per vista.

**Classi canoniche**

| Classe | Ruolo |
|--------|--------|
| `.btn` | Base (reset + densità) |
| `.btn-primary` | CTA gold |
| `.btn-outline` | Secondario bordo |
| `.btn-outline.is-featured` | Outline accent |
| `.btn-secondary` | Quiet (oggi solo Liste → promuovere in SoT) |
| `.btn-sm` | Compatto (oggi artifacts; hit-area resta ≥44 o padding touch wrapper) |
| `.btn-icon` | CTA grafica quadrata ≥44×44 (`padding: 0`); nome accessibile via `aria-label` / `title` |

**Anatomia:** `<button type="button|submit" class="btn btn-primary">…</button>`
Link-as-button: stesso set classi su `<a>` solo se navigazione; preferire `<button>` per azioni.

**Stati**

| Stato | Comportamento |
|-------|----------------|
| default | primary: bg accent, color on-accent; outline: transparent + divider; secondary: soft alpha |
| hover | primary → accent-pressed; secondary → alpha più alto; outline → bordo accent se featured |
| focus-visible | outline 2px accent, offset 2px |
| disabled | opacity ~0.5–0.6, `cursor: not-allowed`, no hover |
| active/pressed | primary: accent-pressed |

**Do:** sentence case; min altezza utile **≥ 44px** (pad o min-height).
**Don’t:** UPPERCASE; hex fuori token; radius 0 (canone **6px**); due `.btn-primary` competenti nella stessa vista.

**A11y:** contrasto on-accent su gold; focus-visible; `disabled` nativo o `aria-disabled` + no pointer; touch ≥44.

**Drift:** `.btn` triplicato (enrico radius 0 vs Liste 6); allineare a Liste in step migrazione 2/4.

---

## 2. Field (label + input / select / textarea)

**Purpose:** input form densità app.

**Classi canoniche**

| Classe | Ruolo |
|--------|--------|
| `.field` | Stack label + controllo (canone Liste → SoT) |
| `.field label` | Label (overline-like ok) |
| `.field input` / `select` / `textarea` | Controlli |
| `.field-row` | Label+checkbox in riga |
| `.auth-field` | Specializzazione auth (stesso look post-migrazione; può diventare alias di `.field`) |

**Anatomia:**
```html
<div class="field">
  <label for="id">…</label>
  <input id="id" />
  <!-- opz. helper / error slot -->
</div>
```

**Stati:** default | hover (bordo soft) | focus-visible (2px accent) | disabled | error (bordo/testo error token + messaggio non solo colore).

**Do:** radius **6px**; bg surface o bg; bordo divider.
**Don’t:** card annidata intorno al field; radius 0 legacy auth dopo step 2.

**A11y:** `label` associato; errore con `aria-invalid` + testo; touch su checkbox ≥44 (area `.field-row`).

**Drift:** `.auth-field` radius 0 vs `.field` 6 — unificare.

---

## 3. Surface / Panel

**Purpose:** section shell dati; un solo livello di outline.

**Classi canoniche**

| Classe | Ruolo |
|--------|--------|
| `.panel` | **Nuovo canone SoT** (TARGET) — surface + divider + radius 8 + pad 16–20 |
| `.auth-card` | Alias/specializzazione auth → stesso skin di `.panel` |
| `.gauge-card`, `.suggestion-item`, `.kpi-card`, `.card` | Drift locale → migrare a `.panel` (+ modificatori se serve) |

**Stati:** default only (no elevazione hover obbligatoria). Nested: soft tint **senza** secondo bordo pieno.

**Do:** no card-in-card.
**Don’t:** ombre pesanti; bg bianco fuori print.

**A11y:** non richiedere role speciale; heading dentro il panel nella hierarchy corretta.

---

## 4. Alert

**Purpose:** feedback inline non-modale.

**Classi:** `.alert`, `.alert-success`, `.alert-error` (già in enrico).

**Stati:** success | error (default = neutro `.alert`).

**Do:** testo + colore bordo/bg soft.
**Don’t:** solo colore; sostituire dialog per errori bloccanti.

**A11y:** `role="status"` o `role="alert"` se urgente; contrasto testo su tint.

**Copy:** slot strutturale — stringhe da i18n / copywriter.

---

## 5. Menubar

**Purpose:** AppBar File / Preferiti / Prodotti (chrome suite).

**Classi:** `.menu-root`, `.menu-trigger`, `.menu-panel`, `.menu-item`, `.menu-sep`, `.is-open`, `.is-disabled`, `.is-featured` + `.chrome-session`, `.chrome-profile-link`, `.chrome-lang-*`.

**Anatomia:** `role="menubar"` → trigger `role="menuitem"` / button → panel con items.

**Stati:** default | hover (token hover) | open (`.is-open` / selected) | focus-visible | disabled item.

**Do:** ordine File → Preferiti → Prodotti; hover-switch; pannello denso; **hit-area trigger ≥ 44×44** (LOCK).
**Don’t:** pill toolbar; export duplicati nel body se già in File→Salva; MUI OutlinedSelect / AppBar patterns.

**A11y:** keyboard (Arrow/Escape — responsabilità `chrome.js`); focus-visible 2px; touch ≥44 su trigger e item (pad verticale adeguato).

**Stato:** step 2–3 migrazione applicati su AppBar (radius 6/8 + touch ≥44); brand/version split `.appbar-brand` / `.appbar-version`.

---

## 6. Tabs (main / sub)

**Purpose:** switch vista primaria (Input|Output) o secondaria (scheda / Explorer).

**Classi canoniche (TARGET unificato)**

| Classe | Ruolo |
|--------|--------|
| `.tabs` | Tablist container |
| `.tab` | Tab button |
| `.tab.is-active` | Selezionato (indicatore accent) |

**Alias di migrazione (mantenere finché HTML non aggiornato):** `.main-tabs`/`.main-tab`, `.sub-tabs`/`.sub-tab`, `.output-tabs`, `.secondary-tabs`/`.secondary-tab` → stesso CSS via selettori multipli.

**Stati:** default (muted) | hover (text) | active (accent + underline) | focus-visible | disabled.

**Do:** `role="tablist"|"tab"|"tabpanel"`; `text-transform: none`; font-weight 600; hit ≥44.
**Don’t:** tre skin diverse (gold vs neutro inconsistenti).

**A11y:** keyboard tabs; `aria-selected`; pannelli `hidden` / `aria-hidden`.

---

## 7. Chip

**Purpose:** stato / filtro / meta compatta (non CTA primaria).

**Classi canoniche**

| Classe | Ruolo |
|--------|--------|
| `.chip` | Base Liste / editoriale (radius sm) |
| `.chip.is-selected` / `.is-active` | Selezionato |
| `.strategy-chip` | Explorer filtro strategia (SoT) |
| `.filter-chip` | Explorer filtro attivo rimovibile (pill 999 documentata) |

**Stati:** default | hover | selected | disabled.

**Do:** surface + bordo; radius 6 (o 8); se clickable → ≥44 altezza.
**Don’t:** `border-radius: 999px` salvo eccezione documentata; chip come unico segnale ok/errore.

**A11y:** se toggle, `aria-pressed`; contrasto testo; non solo colore.

**Copy:** slot — no stringhe nel DS.

---

## 8. Dialog / sheet

**Purpose:** overlay denso (Profilo, config); stesso linguaggio section shell.

**Classi canoniche (TARGET — oggi poco in enrico)**

| Classe | Ruolo |
|--------|--------|
| `.dialog` | Overlay + surface |
| `.dialog-backdrop` | Scrim |
| `.dialog-body` | Contenuto scrollabile |
| `.dialog-actions` | Zona CTA |

**Stati:** open (nel DOM / `.is-open`) | focus trap (JS) | closing.

**Do:** un shell; soft surface sotto-blocchi; chip stato; z-index dialog **sopra AppBar** (runtime progress/job ≥250 se AppBar ~200; foundation TARGET generico 50 = sotto-menu — non usare 50 per overlay job).
**Don’t:** card-in-card; light theme.

**A11y:** `role="dialog"`, `aria-modal="true"`, focus iniziale, Escape, ripristino focus; CTA ≥44.

---

## 9. Table (densità)

**Purpose:** dati tabulari densi (utenti, customer, Explorer).

**Classi:** `.table-wrap` (overflow-x) + `.table` canone; alias `.user-table`, `.customer-table` finché migrati.

**Stati:** row hover (token hover); row selected (selected); th muted.

**Do:** font ~0.875rem; pad cella ~8–12px; th uppercase tracking ok.
**Don’t:** padding da marketing; zebra obbligatoria.

**A11y:** `<table>` semantica; header scope; non affidare sort solo al colore.

---

## 10. Progress

**Purpose:** avanzamento job / caricamento lineare.

**Classi:** barra `.progress`, `.progress-message`, `.progress-bar`, `.progress-bar-fill`, `.progress-bar.is-error`. **Job Liste:** montare in lightbox `.progress-dialog` (+ scrim) — non inline sotto Input.

**Stati:** indeterminate / determinate (width %); error; hidden (`[hidden]`). Job: Escape / Chiudi **solo** in errore; durante run layout `inert`.

**Do:** track soft; fill accent; radius track ≤2px; z-index overlay ≥ AppBar.
**Don’t:** solo colore per errore (messaggio + `.is-error`); progress job non-modale nel form.

**A11y:** `role="dialog"` + `aria-modal` sul lightbox; `role="progressbar"`, `aria-valuenow` / `aria-valuetext` sulla barra; messaggio in live region se aggiornato.

**Copy:** `.progress-message` = slot (`WtpProg_*` — copywriter-wtp).

---

## 11. Empty / Error strutturali

**Purpose:** stati vuoto e errore di pagina/sezione — **struttura**, non testo.

**Classi canoniche**

| Classe | Ruolo |
|--------|--------|
| `.empty-state` | Contenitore vuoto (Liste) |
| `.error-message` | Errore sezione/pagina (Liste) |
| `.loading` | Alias Explorer loading → allineare a pattern spinner + testo |
| `.error` | Alias Explorer → preferire `.error-message` o dual-class |

**Anatomia:**
```html
<p class="empty-state" data-i18n="…"><!-- copywriter / i18n --></p>
<p class="error-message" role="alert" data-i18n="…"><!-- … --></p>
```

**Do:** muted per empty; error token + testo per error; opz. CTA secondary.
**Don’t:** inventare copy nel DS; empty solo con icona colorata senza testo.

**A11y:** error → `role="alert"` o status; contrasto AA.

---

## Matrice promozione SoT (riepilogo)

| Primitive | Già in `surferdark.css` | Da promuovere / aggiungere |
|-----------|---------------------|----------------------------|
| Button | `.btn*` (outline/primary) | `.btn-secondary`, radius/touch |
| Field | `.auth-field` | `.field`, unificazione radius |
| Panel | — | `.panel` (+ skin `.auth-card`) |
| Alert | sì | — |
| Menubar | sì | touch ≥44 |
| Tabs | — | `.tabs`/`.tab` + alias legacy |
| Chip | — | `.chip` |
| Dialog | — | `.dialog*` |
| Table | — | `.table` + wrap |
| Progress | — | famiglia `.progress*` |
| Empty/Error | — | `.empty-state`, `.error-message` |
