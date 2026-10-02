---
name: tono-di-voce
kind: competency
version: 1.0.2
extends-version: 1.0.2
description: >-
  Tono di voce per copy web: brand file .cursor/brands/, gerarchia voce, calibrazione
  registro/lessico/chiusure, scrittura inclusiva. Estende L0 tono-di-voce.
---

# Competenza L1 — tono-di-voce (a-copywriter)

Estende [a-agentzero/competencies/tono-di-voce](../../../a-agentzero/competencies/tono-di-voce/SKILL.md).  
Aggiunge regole copy web e reference di dominio.

---

## Fonti voce (ordine)

| Priorità | Fonte | Cosa governa |
|----------|-------|--------------|
| 1 | Override L2 `competencies/tono-di-voce/` | Delta vocale progetto |
| 2 | Skill voice dedicata (`*-voice`, `*-tone-of-voice`) se presente | Registri, struttura, writing-rules; se voice-as-brand anche lessico/inclusivo |
| 3 | Skill figlia L2 (`extends: a-copywriter`) | Voce breve, path, workflow |
| 4 | `.cursor/brands/{sito}.md` | Identità, lessico, inclusività, PS (se presente) |
| 5 | Questa competenza L1 | Calibrazione e inclusività generiche |
| 6 | L0 tono-di-voce | Principi voce locale |

**Brand vs voice skill:** canone in L0 `tono-di-voce` § Brand file vs skill voice (incl. voice-as-brand).  
Inclusività / lessico vietato esplicito nel brand → **vince il brand**; se nessun brand → **vince la voice skill**.

Template brand (root agente): [brand-brief-template.md](../../brand-brief-template.md).

---

## Calibrazione (copy)

Prima del draft:

1. Leggi brand file se presente (o campione utente se fornito)
2. Se esiste skill voice L2, caricala (dopo il brand se c'è; altrimenti è la fonte primaria — voice-as-brand)
3. Estrai: registro (tu/Lei/neutro), parole preferite/vietate, pattern di chiusura CTA
4. Allinea burstiness al campione se presente (dettaglio ritmo: competenza `humanizer`)
5. Se 0 brand **e** 0 voice skill: ferma e proponi da `brand-brief-template.md` (discovery a-agentzero). Se c'è voice skill senza brand: procedi (voice-as-brand)

---

## Scrittura inclusiva

Reference: [references/scrittura-inclusiva.md](references/scrittura-inclusiva.md).

- Audit abilismo e linguaggio escludente sul copy pubblico
- In conflitto con keyword SEO: preferisci formulazione inclusiva equivalente; non inventare ranking (anche L1 `onpage-seo`)

---

## Output atteso dalla competenza

- Draft e rewrite coerenti con esempi del brand file
- Chiusure CTA allineate al pattern brand (non slogan generici)
- Checklist inclusiva passata o eccezioni documentate dal brand
