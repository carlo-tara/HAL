---
name: italiano-locale
kind: competency
version: 1.2.0
extends-version: 1.1.0
description: >-
  Italiano locale per copy web: costruzione frasi, densità sintattica (forbici
  strutturali), grammatica LLM-tipica, falsi amici, inflessioni regionali
  calibrate, idiomi, purismo, tempi e clitici. Estende L0 italiano-locale.
---

# Competenza L1 — italiano-locale (a-copywriter)

Estende [a-agentzero/competencies/italiano-locale](../../../a-agentzero/competencies/italiano-locale/SKILL.md).

Grammatica normativa LLM: ispirata a [italiano-scrittura-anti-ai](https://github.com/mario-montanari/italiano-scrittura-anti-ai).

---

## Reference

| File | Contenuto |
|------|-----------|
| [purismo-italiano.md](references/purismo-italiano.md) | Anti-criptoinglese, corporate slop, falsi amici, verbi ibridi |
| [italiano-vivo.md](references/italiano-vivo.md) | Tempi verbali, reggenze, clitici |
| [forbici-strutturali.md](references/forbici-strutturali.md) | Densità sintattica target (pro-drop, clitici, *si*, …) da corpus Strega |
| [grammatica-llm.md](references/grammatica-llm.md) | Errori ortografici/morfologici tipici LLM + Trova |

---

## Costruzione frasi naturali

Regole operative:

1. **Soggetto chiaro, verbo vicino** — evita catene di subordinate all'inglese (*«il fatto che… è che…»*)
2. **Informazione nuova a destra** — metti il carico utile dopo il tema noto
3. **Una idea per periodo** — periodi lunghi ok se respirano; spezza se servi tre concetti
4. **Preferisci attivo** — passivo solo per focus sull'oggetto o registro formale brand
5. **Congiunzioni sobrie** — *e*, *ma*, *però*, *quindi*; evita *Inoltre* / *In aggiunta* a catena (anche competenza humanizer)
6. **Articoli e preposizioni articolate** — controlla *di/da/in* + articolo; errori tipici da calco EN; vedi [grammatica-llm.md](references/grammatica-llm.md)

### Densità sintattica (forbici)

Su **copy lungo** (blog, landing body, email narrative, case study, ~≥40–50 frasi), usa le forbici in [forbici-strutturali.md](references/forbici-strutturali.md) come **target di densità** dei tratti strutturali italiani (pro-drop, clitici, *si*, congiuntivo, …). Su meta/FAQ/microcopy: solo orientamento qualitativo, senza conteggio %.

Esempio calibrazione lessicale-sintattica:

| Calco / piatto | Più naturale |
|----------------|--------------|
| *Questo prodotto è progettato per aiutarti a…* | *Ti serve a…* / *Lo usi quando…* |
| *Ci sono tre cose da considerare* | *Tre punti contano:* / *Guarda tre cose:* |
| *Al fine di* | *Per* |

---

## Inflessioni regionali (uso calibrato)

- **Default copy web:** italiano standard neutro, comprensibile in tutta Italia
- **Tratti ammessi** solo se brand/pubblico li usano già (esempi nel brand file): *mica*, *piuttosto*, *un po'*, *roba*, *ci* attualizzante
- **Mai** stereotipo folklore (fonetica da cartolina, dialetto inventato, battute su regioni)
- Se il brand è radicato in un'area, usa **1-2 tratti lessicali** tipici e riconoscibili, non un pastiche

---

## Modi di dire e idiomi

### Diffusi (ok se chiari)

Esempi: *fare il punto*, *mettere le mani avanti*, *essere sulla stessa lunghezza d'onda*, *tagliare corto*, *andare liscio*. Preferisci versioni italiane a calchi EN (*on the same page* → vedi purismo).

### Quando evitarli in copy web

- Meta, title, FAQ: no idiomi opachi o regionali stretti
- Pubblico internazionale / B2B formale: idiomi colloquiali solo se brand file li ammette
- Traduzioni letterali di idiomi EN: riscrivi il senso, non calca

---

## Registro parlato vs scritto

| Contesto | Registro |
|----------|----------|
| Scheda prodotto, categoria, landing | Scritto curato, vicino al parlato medio se brand è *tu* |
| Blog narrativo, email | Può avvicinarsi al parlato; tempi vivi (vedi italiano-vivo) |
| Meta SEO, FAQ tecniche | Scritto chiaro, niente slang |
| Microcopy UI | Parlato breve, imperativo o infinito coerente col brand |

Non mescolare *Lei* formale e *tu* nello stesso pezzo.  
Matrice registro × tic AI (humanizer): [registri-canali.md](../humanizer/references/registri-canali.md).

---

## Purismo e morfologia

- Purismo attivo: [purismo-italiano.md](references/purismo-italiano.md)
- Tempi, reggenze, clitici: [italiano-vivo.md](references/italiano-vivo.md)
- Densità strutturale: [forbici-strutturali.md](references/forbici-strutturali.md)
- Errori LLM (apostrofi, accenti, articoli, *piuttosto che*): [grammatica-llm.md](references/grammatica-llm.md)
- Eccezioni: glossario brand o termini tecnici consolidati (*SEO*, *CMS*, *software*, …)

---

## Checklist consegna (italiano-locale)

- [ ] Purismo: niente corporate slop / falsi amici / verbi ibridi sostituibili
- [ ] Grammatica LLM: Trova + congiuntivo/articoli ([grammatica-llm.md](references/grammatica-llm.md))
- [ ] Tempi/clitici vivi dove il registro lo ammette
- [ ] Pezzi lunghi: autoverifica forbici (pro-drop, clitici, *si*, congiuntivo presenti a densità plausibile; *ne*/climbing non forzati)
- [ ] Meta/FAQ/microcopy: tratti italiani qualitativi, senza conteggio %
