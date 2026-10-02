---
name: switch-interview
kind: competency
version: 1.0.0
description: >-
  Switch interview JTBD (Moesta): timeline First Thought→Purchase, Four Forces,
  recruit/prep/guide/synth. Solo L1 (a-jtbd). Non è intervista al PO.
---

# Competenza L1 — switch-interview (a-jtbd)

Ricostruisce **perché** un cliente ha *assunto* (hired) un prodotto: storia di switch reale, non preferenze astratte né feature request.

**Non confondere** con `po-interviewer` (intervista al Product Owner) né con colloqui HR.

**Reference:** [timeline-markers.md](references/timeline-markers.md) · [four-forces.md](references/four-forces.md) · [interview-protocol.md](references/interview-protocol.md) · [synthesis-template.md](references/synthesis-template.md)

---

## Quando applicare

- `/interview prep|guide|synth`
- Manca evidenza di hire/switch per job, positioning, unmet
- Validare ipotesi Lean Canvas (Problem/Segment/UVP/Channels) con storie reali
- Pattern da 5–10 interviste prima di roadmap/messaging

## Quando NON applicare

- Intervista al PO → `po-interviewer`
- Gift / impulse buy (timeline JTBD non affidabile)
- Solo “cosa vorresti nel prodotto?” (non è switch interview)
- Scrivere `.feature` → `a-gherkin` dopo seeds
- Inventare quote o timeline

---

## Slash `/interview`

| Arg | Ruolo |
|-----|--------|
| `prep` | Screening, recency, pair roles, practice, checklist |
| `guide` | Facilitazione live: bounce timeline, dig, unpack adjectives |
| `synth` | Timeline + Four Forces da note/transcript; pattern cross-set |

Default se omesso: chiedi `prep` | `guide` | `synth` (1 Q).

---

## Workflow

### prep

1. Definisci chi: recent switchers (preferisci &lt;6 mesi se novice; evita &gt;1.5 anni)
2. Mix utile: recent buyers, long-time, **lost deals** (perché non hanno scelto te)
3. Escludi gift/impulse
4. Practice interview (amico/familiare, purchase non-gift recente) se il team è rusty
5. Pair: interviewer lead + note-taker/second brain
6. Prepara data di purchase se disponibile (niente lookup mid-call)

### guide (live, 45–90 min)

Segui [interview-protocol.md](references/interview-protocol.md).  
Organizza in tempo reale sul [timeline](references/timeline-markers.md) (**bounce**, non solo ordine lineare).  
Alla fine mappa [Four Forces](references/four-forces.md).

### synth

1. Compila template per intervista; se timeline/forces incompleti → intervista scarsa (non “salvabile” con ipotesi inventate)
2. Dopo 5–10: pattern Push/Pull/Anxiety/Habit; linguaggio cliente
3. Handoff: aggiorna `jtbd.md` (stories/unmet) o seeds; messaging → `a-po` → `a-copywriter`; validate → `a-po` `/validate`

Path: `.cursor/product/interviews/` (o path L2).

---

## Regole ferree

1. Eventi concreti, non opinioni generiche — *name of the dog*, where/when
2. First thought quasi sempre **più indietro** — probe backward
3. Non chiedere “quali erano le four forces?” — emergono dagli eventi
4. Anti-invention: no quote/timeline fabbricati
5. Tag `evidence` vs `hypothesis` nella sintesi
6. Piano interview col PO: 1–2 Q/turno (`po-interviewer`); live guide: protocollo denso ok

---

## Anti-pattern

- Intervistare chi ha comprato “anni fa” da novice
- Feature wishlist al posto della storia di switch
- Un’intervista sola = “verità”
- Hard sell framing durante passive looking phase (nel racconto)
- Confondere Mom Test generico con switch interview (qui: purchase timeline + forces)

---

## Output

- `prep`: lista candidati filtrata + checklist + pair roles
- `guide`: note strutturate (timeline markers + open digs)
- `synth`: file per intervista + pattern sheet; next actions su jtbd/messaging/validate
