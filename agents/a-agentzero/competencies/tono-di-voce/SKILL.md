---
name: tono-di-voce
kind: competency
version: 1.0.2
description: >-
  Scrivere nella voce definita localmente: file brand/dati di progetto, override L2,
  calibrazione di registro, lessico e chiusure. Principi cross-dominio (L0).
---

# Competenza L0 — tono-di-voce

Principi generici. Le regole di dominio (copy web, brand file `.cursor/brands/`) vivono nel L1 del dominio che dichiara questa competenza.

---

## Principi

1. **Voce locale prima** — non inventare tono: usa file dati di progetto, skill L2 o campione fornito
2. **Calibrazione** — allinea registro (tu/Lei/neutro), lessico preferito/vietato e pattern di chiusura alle fonti locali
3. **Gerarchia** — in conflitto: override L2 > file dati > regole L1 della competenza > questo L0
4. **Coerenza** — stesso pezzo = stessa voce; non mescolare registri senza motivo documentato
5. **Inclusività di base** — evita abilismo e linguaggio escludente salvo diversa indicazione esplicita del brand

---

## Brand file vs skill voice (quando usare cosa)

| Contenuto | Dove | Esempio |
|-----------|------|---------|
| Identità, audience, Usa/Evita, PS, inclusività lessicale | `.cursor/brands/{slug}.md` | tabelle lessico, anti-pattern |
| Override breve (1–5 bullet) | Sezione delta in `copywriter-{progetto}/SKILL.md` o `competencies/tono-di-voce/` | registro tu, 2 parole vietate |
| Voice **pesante** (registri per tipo, struttura post, writing-rules, anti-AI locale) | Skill L2 dedicata `*-voice` / `*-tone-of-voice` con `extends: a-copywriter` (o legacy naming) | newsletter long-form |

**Regole:**

1. **Preferisci brand file** (`.cursor/brands/`) per identità + lessico + inclusività. Non è obbligatorio se il progetto documenta **voice-as-brand**: skill L2 `*-voice` / `*-tone-of-voice` è l’unica fonte vocale (nessun brand file).
2. Skill voice dedicata se il corpus supera ciò che sta comodo in brand + delta copywriter breve; oppure se voice-as-brand (punto 1).
3. **Una idea, un posto:** lessico inclusivo nel brand **se esiste**; altrimenti nella voice skill. Registri/struttura nella voice skill. Non duplicare paragrafi verso L1.
4. In conflitto esplicito su inclusività/lessico vietato → **vince il brand file** se presente; altrimenti **vince la voice skill** L2.
5. Naming discovery: vedi AGENT-PROTOCOL fallback `*-tone-of-voice` / `*-voice`

---

## Cosa non fa questo L0

- Non definisce template di pubblicazione o SEO
- Non sostituisce brand brief o skill figlia di progetto
- Non impone un tono "HAL" ai consumer
