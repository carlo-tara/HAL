---
name: onpage-seo
kind: competency
version: 1.0.3
description: >-
  Ottimizzazione on-page SEO: title, meta, H1, FAQ, sanity check keyword driver,
  tier impatto, audit Spider, pattern AEO. Riusa tono-di-voce in scrittura. Solo L1.
---

# Competenza L1 — onpage-seo (a-seozoom)

Pattern on-page generici + ponte verso copy inclusivo. Path contenuti, build e tono brand: skill L2. Corpo lungo / humanize: **delega a-copywriter**.

---

## Quando applicare

Ottimizzazione title/meta/H1/FAQ, batch PagesWithPotential (fase scrittura), audit Screaming Frog mirato, conflitto keyword CSV vs linguaggio inclusivo / voice di progetto.

---

## Pattern on-page

Canone dettagliato: [metriche-seozoom.md](../metriche-analisi/references/metriche-seozoom.md) § Pattern ottimizzazione on-page, § Workflow batch PagesWithPotential.

Regole sintetiche:

1. **Sanity check** keyword driver prima di ogni intervento (scarta typo brand, query generiche, intent mismatch, keyword **fuori perimetro** senza richiesta esplicita — canone `metriche-seozoom.md` § PagesWithPotential)
2. **Tier impatto:** driver valido + GSC CTR basso + (opzionale) PagesWithTrafficDown
3. Interventi tipici: title, meta description, H2, FAQ on-page (copy), link interni — su URL esistenti con owner confermato
4. **AEO surfaces (diagnosi/scrittura corta):** H2 question-shaped, answer block 40–60 sotto la domanda, pattern “X è…”, liste/tabelle — dettaglio `geo-citabilita`. JSON-LD FAQ/HowTo **non** leva SERP Google → `schema-markup`
5. **Immagini (corto):** alt descrittivi; flag LCP candidate ovvio (hero enorme senza dimensioni) — CWV soglie → L2; asset → **a-illustrator**
6. Max 3–5 azioni consigliate per URL; chiusura batch: build/test + tracker L2; **guardrail** post-lag (→ `metriche-analisi` § Validazione)
7. Screaming Frog (`*_SEO-Spider.csv`): audit title/meta/H1/canonical/alt prima o dopo rewrite

---

## Keyword CSV ≠ copy letterale

**Regola ferrea:** il termine nel CSV SeoZoom/GSC è un *driver di intent*, non obbligatoriamente la stringa da stampare in title/meta/H1/FAQ/corpo.

| Situazione | Azione |
|------------|--------|
| Driver valido, forma inclusiva/brand diversa | Usa sinonimo o parafrasi naturale; conserva intent |
| Volume alto ma forma esclusiva / jargon consulente | **Vince voice/brand** (tono-di-voce L2 + brand); cerca long-tail naturale |
| Stuffing o CTA invasiva vs tono progetto | **Vince voice/brand** — non forzare keyword |
| Driver = typo / brand errato | Scarta nel sanity check; non pubblicare |

Esempio: CSV «certificazione facilitatore» → testo «chi facilita» se brand/L2 lo richiedono.

Dopo ottimizzazione: audit diff title/preview/FAQ contro pattern esclusivi del brand (grep se utile).

---

## Copy in title / meta / FAQ

Quando **scrivi** (non su puro import/analisi CSV):

1. Carica competenza **`tono-di-voce`** (L0 + L1 a-copywriter) — inclusività e brand
2. Se riscrittura ampia: anche `humanizer` / `italiano-locale` via a-copywriter, o **delega** all'agente a-copywriter
3. Applica § Keyword CSV ≠ copy letterale sopra
4. Non caricare le competenze copy su task solo import/metriche

---

## Output atteso

- Diff o testo title/meta/FAQ allineati a driver + inclusività / voice
- Citazione CSV/GSC usati per la priorità
- Note su keyword scartate dal sanity check o riformulate per tono
