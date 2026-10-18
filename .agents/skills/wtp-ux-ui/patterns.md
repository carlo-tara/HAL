# Pattern UX/UI — SurferDark (vanilla)

Stack: HTML statico + CSS custom properties + JS ES modules. **Niente MUI / Material Web / Tailwind / Bootstrap.**
DS: [design-system.md](design-system.md) · foundation: [foundation.md](foundation.md) · MD3: [material3.md](material3.md).

## Layout pagina

- Root: `min-height: 100dvh` (o `100vh`), background token bg (`#0e0e0e`).
- **Product homes** (Customer / Company / Profile / Risk): shell SoT `.product-layout` + `.product-content` (+ `--narrow` / `.product-lede` se serve) in `surferdark.css` — **no** cloni page-local `*-layout`.
- Contenuto Liste: padding orizzontale 16px; max-width ~960–1100px — densità pagina può restare locale.
- Chat Company: classi e ID page-local prefisso `co-*` (es. `.co-chat`, `id="co-chat-form"`).
- Landmark: un `main`; un solo `h1` visibile (titolo appbar o pagina).

## Section shell

Pannello dati / blocco:

- background surface `#181818`
- border `1px solid` divider
- **radius 8px** (canone Liste)
- padding 16–20px
- **niente card-in-card**: sotto-blocchi borderless o soft tint senza secondo outline pieno

Canone classe TARGET (migrazione): es. `.sd-panel` o promozione di un nome unico in CSS SoT. Oggi: mix `.auth-card`, `.gauge-card`, `.suggestion-item`, Explorer `.card` / `.kpi-card`.

## Schermate dense (Output, lista, scheda, dialog)

- Un shell; overline / label uppercase tracking stretto + accent o muted.
- Contenuti lunghi → **tab secondarie** (es. Sintesi | Liste; Panoramica | …).
- Tab: `text-transform: none`, `font-weight: 600`, hit-area **≥ 44px**, indicatore 2–3px accent sul selezionato (`.is-active`).
- Dialog / sheet (Profilo): stesso linguaggio — soft surface, chip stato, form a shell unico; no lista flat card-in-card.

## Tipografia

- Family: system UI (vedi foundation).
- Titoli: weight 700, letter-spacing ~`-0.01em`.
- Meta: color muted.
- CTA: **sentence case** (no UPPERCASE marketing).

## AppBar e navigazione

- Surface paper, bordo inferiore divider, **no** ombra pesante.
- **Gerarchia titolo:** `.appbar-title` in colonna con barra accent 3px a sinistra; `.appbar-brand` (1.25rem / 700) sopra `.appbar-version` (overline muted, non inline col brand).
- **Brand suite (LOCK):** in ogni prodotto (`/wtp/`, `/explorer/b2b/`, …) `.appbar-brand` = **Sales Coach** (`ListsWtpTitle`); `.appbar-version` = semver UI (es. `v 1.24.0`). Non mettere nome prodotto («Explorer B2B», «Liste WTP») né etichette vista («Cluster») nello slot brand/version — il prodotto si distingue da menu Prodotti / body.
- Menubar desktop stile app: **File → Preferiti → Prodotti** (`role="menubar"`), titoli flat, highlight aperto, hover-switch tra menu; separatore divider tra brand e menubar.
- **Touch-first (LOCK):** AppBar `min-height` ≥ 64px; `.menu-trigger`, `.menu-item`, `.chrome-lang-btn`, `.chrome-profile-link` hit-area **≥ 44×44px**; radius trigger/utilità **6px**, pannello **8px**.
- Utilities destra (`.appbar-end`, separate da divider): segmento Lingua **IT/EN** glyph fissi (non full “Italiano”/msgid) + Profilo quiet su surface elevated; sessione email in `title` / sr-only (no chip email in chrome).
- **i18n (chrome + body Liste + customer/`data-i18n`):** se `WtpI18n.t(key)` restituisce la key (msgid assente), usare `uiT` / fallback; **mai** renderizzare msgid in UI (es. `LanguageItShort`, `OutputTabSummary`, `CustomerNotFound`). AppBar: preferire testo fisso IT/EN + `aria-label` da `LanguageIt`/`LanguageEn`. Chiavi HTML: solo msgid già in `src/auth/locales/*.po` (scheda cliente → `CustomerSheet*`, non inventare `CustomerTab*` / `BackToApp`).
- **i18n DOM DRY (product homes):** usare `src/wtp/frontend/js/core/applyDomI18n.js` (`applyDomI18n` + `formatAcquiredDate(lang)`) — non duplicare loop `data-i18n` / formattazione date tra Customer e Company.
- DevTools che etichetta la toolbar come `MuiAppBar` **non** implica MUI nel monorepo — verità = `header.appbar` + SurferDark.
- Pannello menu: bordo divider, radius canone 6–8, z-index menu.
- **File → Salva / Esporta PDF:** voci contestuali (JSON / PDF / ZIP); niente bottoni export duplicati nel body se già in menubar. Schede **Customer / Company 360:** `hooks.exportPdf` → PDF **continuo** (una pagina scroll-alta, non A4 paginato / non dialog stampa). Company multi-sezione: concatenare tutte le tab in un solo capture (reveal pannelli + titoli sezione `h2.wtp-pdf-export-section-title`, restore dopo). Classic-script Company → vendor `/wtp/vendor/html2canvas|jspdf` + `WtpDomToPdfBlob` (vedi `harness-wtp` § FE PDF continuo). Superficie export = **carta light intenzionale** (`pdfExportSurface`) — vedi § Print / PDF / ZIP.
- Prodotti = catalogo suite; Preferiti = IndexedDB locale.

Classi OGGI: `.appbar`, `.appbar-brand`, `.appbar-version`, `.menu-*`, `.chrome-*`. Shell unica suite (`header.appbar`); meta pagina (dataset, contatori) **fuori** dall’AppBar.

## Bottoni e chip

| Variante | Canone |
|----------|--------|
| Primary | bg accent, testo on-accent, radius **6px**, altezza utile ≥ 44px |
| Secondary / quiet | bg soft white alpha o outline divider |
| Outline featured | bordo accent, testo accent |
| Chip stato | surface + bordo; non comunicare solo a colore |

OGGI: `.btn` / `.btn-primary` / `.btn-secondary` / `.btn-outline` / `.btn-sm` in `surferdark.css` (SoT).

## Form e input

- Label sopra o `.field-row` per checkbox.
- **Checkbox in `.field`:** non applicare `display:block` / `text-transform:uppercase` / `width:100%` della label overline al `.field-row`; `input[type=checkbox]` resta `width:auto` in riga col testo.
- Input/select/textarea: surface o bg, bordo divider, **radius 6px**, focus-visible 2px accent.
- Helper / error: testo + colore semantico (non solo bordo).
- OGGI: `.auth-field` (enrico, radius 0) vs `.field` (Liste, radius 6) — unificare al canone Liste.

## Liste Input (vanilla)

- SoT: `src/wtp/frontend/index.html` + `js/app.js` + futuri `js/input/*` + `lib/{launch,list,core}`.
- **Non** reintrodurre React/MUI/`dist/` Vite (`layoutHygiene.test.js`).
- IA canone (ex App React): primary = Contact Owner raggruppato, Formula, Launch price, Users to analyze, CTA; **Avanzate** collassabile = data, lookback, cohort, ignore double-paid.
- Se mancano slider/avanzate/owner ricco: scaffold migrazione incompleto — ripristinare wiring, non dichiarare “JS rotto” senza verifica `import`/console.
- Start job: body allineato a `listsInputSchema` (`launchPriceEur`, `contactOwnerHubspotIds`, `usersToAnalyze`, …).
- **Progress job:** lightbox bloccante (`.progress-dialog` + scrim; `inert` sul layout) — non barra inline sotto il form. Escape/Chiudi solo in errore. Dettaglio classi → [componenti.md](componenti.md) § Progress.

## Liste Output (vanilla)

- **Sintesi:** doc `kind: 'summary'` (`segmentSizes`, `segmentAvgWtp`, `executiveSummary`) — metric strip + pie / barre WTP / owner×segment + narrativa sanitizzata. **Non** stub gauge “N utenti / max 1000”. Palette charts SurferDark (`SUMMARY_CHART_COLORS`).
- **Scheda lista:** sub-tab Panoramica | Grafici | Suggerimenti | Dettaglio utenti. Tabella utenti: campi snake_case SoT (`user_id`, `WTP`, `first_name`/`last_name`, `contact_owner`, `ltv`) — non camelCase inventato (`wtpScore`, `fullName`, …).
- **Scheda cliente:** SoT = Customer 360 `/customer/<userId>` (`src/customer/frontend/`); API `GET /api/customer/:userId`; msgid `CustomerSheet*`. Liste WTP = solo link (e export via API) con query contesto (`jobId`/`listId`/`returnUrl`). Legacy `src/wtp/frontend/customer.html` → redirect HTTP a `/customer/` (non reintrodurre scheda job-scoped sotto `/wtp/`). Back-link contestuale (lista/sintesi vs home Customer 360). Tab Integrazioni = card status+CTA; Profilo/Altro = valori nested tipizzati (`formatCustomerProfileValue` / peer).
- Artefatti: `fetchWtpViewJson` / `resolve*FromView` (harness-wtp § Steward notes).
- **CSS:** primitives catalogate in `surferdark.css`; `<style>` pagina solo page-local (owner-menu, chart Output, sezioni scheda). Hex catalogati (`#ffd400` su `.btn-primary`/`.main-tab`/…) = regressione.

## Company 360 (scheda)

- Tab SoT: **Azienda | Dettaglio | Clienti MS | Rischi** — **niente** tab Persone / IT-advanced / IT-stakeholders separate.
- **Dettaglio** = pack advanced (+ report coalesced) **e** sezioni stakeholders (gruppo, dipendenti, filiali, amministratori, soci); dedupe identity già in advanced (Ragione sociale↔Organizzazione, P.IVA, CF, REA, CCIAA); resta Tipo sede se presente.
- Toolbar OpenAPI = strip status+CTA **dentro** Dettaglio (non chrome globale sulle altre tab); shell unica come Customer — **no card-in-card** sui sotto-pannelli stacked.
- Importi economici OpenAPI → locale it-IT + ` €` in coda (`formatOpenApiMoneyEur` / metric); date → `dd/mm/yyyy`.
- **Azienda / Identità — dominio + P.IVA:** se manca VAT, CTA `#company-vat-from-domain` = `.btn-icon` (lente) **in riga** col dominio (`aria-label`/`title` i18n `CompanyVatSearchFromDomain`); status/errore `.company-domain-vat-status` **sotto** la cella, non inline. Form VAT mancante resta nella chip row (input touch ≥44).

## Tabelle e liste

- Densità: font ~0.875rem; th muted; td bordo inferiore soft.
- Hover riga: token hover; selezione: selected.
- Wrap overflow-x su mobile.

## Responsive

- Mobile-first; test ~390px.
- Header: flex wrap; titolo ellipsis.
- Griglie gauge: `auto-fit` / stack su stretto.

## Accessibilità

- Contrasto AA; focus-visible sempre.
- Keyboard su menubar e tab.
- Live region per stati rilevanti (`role="status"`).
- Stato non solo a colore.
- `prefers-reduced-motion` (TARGET in CSS).

## Print / PDF / ZIP

- **Light only** (LOCK): `@media print` e surface html2canvas (`pdfExportSurface`) → bg bianco, testo scuro; **non** ereditare dark (gold muted / divider invisibili).
- Nascondere chrome / tab UI (classe tipo `*-no-print`).
- Pannelli `hidden` / `display:none`: in print/export forzare visibilità dei blocchi contenuto se servono al foglio.
- Export raster/ZIP: layout **flat** nel DOM; non affidarsi solo a `@media print`.
- **Carta intenzionale (Company/Customer continuous):** titoli sezione H2 + hairline; KV `dt` muted / `dd` forte; card/chip overview light; tabelle header statico + zebra (no sticky/hover dark); link scuri sottolineati; risk print-safe (verde/ambra/rosso) — **senza** spezzare in A4 (`break-inside` continuo).

## Cosa evitare

- Hex fuori token (salvo serie D3 e print).
- Radius 0 su btn/input (legacy chrome) e pill `999px` non documentati.
- Sfondo bianco fuori print/PDF.
- `text-transform: uppercase` su button.
- Ombre pesanti in dark.
- Palette teal/mauve marketing Tara in runtime.
- Nuove API stile MUI (`sx`, `variant="contained"`, ecc.).
