---
name: hreflang-i18n
kind: competency
version: 1.0.0
description: >-
  Hreflang e SEO internazionale lean: validazione cluster, parity contenuti,
  freschezza traduzioni. Solo L1 (no baseline L0).
---

# Competenza L1 — hreflang-i18n (a-seozoom)

Canone multi-locale. Distillato da claude-seo `seo-hreflang` (MIT) — senza encyclopedia cultural-profiles.  
Pin: [claude-seo-source.md](../../references/claude-seo-source.md).  
Dettaglio checklist: [references/hreflang-checklist.md](references/hreflang-checklist.md).

---

## Quando applicare

Sito con 2+ lingue/regioni, errori hreflang, “Google mostra la lingua sbagliata”, audit i18n.  
Audit generico → `seo-audit`. Copy localizzato → **a-copywriter**. Redirect/plugin WP → **a-wordpress**.

---

## Validazione hreflang (sintesi)

1. **Self-reference** su ogni URL del set (URL = canonical)
2. **Return tags** bidirezionali (mesh completa)
3. **`x-default`** se c’è selector/fallback (uno solo)
4. Codici **ISO 639-1** (+ regione ISO 3166-1); errori tipici: `en-UK`→`en-GB`, `jp`→`ja`
5. Solo su URL **canonical** 200; coerenza protocollo/host/slash
6. Implementazione: HTML e/o XML sitemap — non in conflitto tra loro
7. Preferire subdirectory `/it/`, `/en/`; evitare `?lang=`

hreflang è un **hint**, non una direttiva. Non raccomandare country targeting GSC (rimosso).

---

## Content parity / MT QA

Per ogni pagina dichiarata multi-lingua: esistenza equivalente, title/meta localizzati, schema localizzato (tipi ancora supportati), sezioni confrontabili, freschezza vs lingua source.  
Ratio word-count per lingua: orientativo (±30%), non score obbligatorio. Dettaglio → ref.

---

## Output atteso

- Finding P1–P5 (formato `seo-audit`) su cluster invalidi
- Checklist parity/freschezza per sample URL
- Proposta fix (tag / sitemap) senza inventare locale non in brief
