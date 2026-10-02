# Rich result Google retired vs vocabulary schema.org

Distillato da `vendor/claude-seo/skills/seo-schema/references/deprecated-types-2024-2026.md` (MIT).  
Fonte primaria in conflitto: **Google Search Central**. Pin: [claude-seo-source.md](../../../references/claude-seo-source.md).

**Regola:** vocabulary schema.org ≠ rich result Google. Non raccomandare un tipo per SERP se Google ha ritirato il risultato.

## Tipi critici per a-seozoom

| Type | Rich result Google | Cosa fare in AF |
|------|--------------------|-----------------|
| `HowTo` | Ritirato (set 2023) | Non raccomandare per SERP. Contenuto step con H2 ok; markup solo se richiesto esplicitamente senza claim SERP |
| `FAQPage` | Ritirato per tutti (claim upstream mag 2026; verificare docs Google) | Info se già presente; **non** nuovo FAQPage per rich result. FAQ on-page restano utili a GEO/AEO non-Google. Q&A utente reale → `QAPage` |
| `ClaimReview` | Ritirato (giu 2025) | Non leva SERP; non spingere in audit AEO |
| `SpecialAnnouncement` | Ritirato (lug 2025) | Non usare |
| `VehicleListing` | Ritirato (giu 2025) | Preferire `Product` se vendita online |
| `EstimatedSalary` | Ritirato (giu 2025) | `JobPosting` + `baseSalary` per ruoli specifici |
| Learning Video / Course Info carousel | Ritirati (2025) | `VideoObject` / singolo `Course` ancora live |
| `SpeakableSpecification` | Non prioritario L1 | Non raccomandare come leva AEO Google |

## Severity audit

- Markup retired **già presente** e accurato → finding **Info** (non Critical): non obbligare rimozione
- Richiesta di **aggiungere** FAQ/HowTo/ClaimReview “per ranking Google” → rifiutare e spiegare
- Override vs checklist Labat che spingono FAQ/HowTo/Speakable come leve AEO Google → **questa tabella vince**

## Tipi ancora tipici (leva SERP / entity)

Organization, WebSite, Article/BlogPosting, Product, BreadcrumbList, SoftwareApplication, JobPosting, Event, LocalBusiness (se locale), QAPage (Q&A reale), Course (singolo), VideoObject, Dataset (Dataset Search, non SERP classico).

Last aligned: pin claude-seo in `claude-seo-source.md`.
