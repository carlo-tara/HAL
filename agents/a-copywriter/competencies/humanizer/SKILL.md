---
name: humanizer
kind: competency
version: 1.2.0
extends-version: 1.1.0
description: >-
  Humanizer per copy web IT: anti-AI, loop avversariale, ritmo/burstiness,
  editing solidità/taglio, leak conversazionale, voce misurata. Estende L0 humanizer.
---

# Competenza L1 — humanizer (a-copywriter)

Estende [a-agentzero/competencies/humanizer](../../../a-agentzero/competencies/humanizer/SKILL.md).  
Corpus e processo copy italiano.

Fonti: [blader/humanizer](https://github.com/blader/humanizer); [avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing); [italiano-scrittura-anti-ai](https://github.com/mario-montanari/italiano-scrittura-anti-ai) (IT; senza iniezione di anima).

---

## Vincoli sul copy consegnato

### Punteggiatura

- Zero trattino lungo e lineetta (`—`, `–`, ` -- `)
- Virgolette dritte `"..."` salvo diversa indicazione nel brand file

### Struttura

- Evita «non solo X, ma anche Y» e parallelismi negativi / leak conversazionale
- Rule of three: max 2 elementi o un dettaglio specifico
- Liste con header bold: prosa o heading separati; niente header-rincalzo
- Title case italiano: solo prima parola e nomi propri
- Anafora: max 1 ripetizione stesso incipit ogni 3-4 frasi

### Lessico

- Taglia enfasi sproporzionata e promo da brochure
- Preferisci copula semplice (*è*, *ha*, *resta*)
- Max densità banda A / metafora-viaggio / connettivi ([anti-ai-it.md](references/anti-ai-it.md))
- Word-list = gusto; segnali strutturali: [segnali-misurabili.md](references/segnali-misurabili.md)

### Never inject

- Umanizzare = togliere e affilare: niente voce, fatti, stakes o candore assenti da source/brand/campione

### Iperboli

- Default: prosa concreta
- Max 1 iperbole in scheda prodotto; ogni iperbole ancorata a fatto verificabile **nel source**

---

## Processo

```
Radar stesura → calibrazione (qualitativa | scheda voce) → audit P0–P2 + Trova
→ patch|rewrite → loop + second-pass → Never inject → (opz.) canali lettore
```

Modalità: `rewrite` | `detect` | `edit` — [humanizer-loop.md](references/humanizer-loop.md).

| Fase | Reference |
|------|-----------|
| Pattern, leak, Trova, densità, Never inject | [anti-ai-it.md](references/anti-ai-it.md) |
| Radar, scheda voce, second-pass, tolerance | [humanizer-loop.md](references/humanizer-loop.md) |
| Segnali strutturali vs word-list | [segnali-misurabili.md](references/segnali-misurabili.md) |
| Registri × tic, canali lettore | [registri-canali.md](references/registri-canali.md) |
| Ritmo, sintassi | [scrittura-umana.md](references/scrittura-umana.md) |
| Solidità, taglio -30% | [editing-avanzato.md](references/editing-avanzato.md) |

Purismo, grammatica LLM, tempi/clitici: competenza `italiano-locale`.
