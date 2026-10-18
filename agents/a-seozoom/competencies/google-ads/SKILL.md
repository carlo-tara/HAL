---
name: google-ads
kind: competency
version: 1.0.1
model: orcarouter/deepseek/deepseek-v4-flash-free
description: >-
  Strutturazione e ottimizzazione campagne Google Ads (Search, PMax, Shopping)
  basate su dati SEO/intento. Gestione SKAG, copy persuasivo per Ads, asset
  PMax (testi/immagini), e mapping feed Shopping. Usa regole di WTP (Winner
  Takes All) e segmentazione ROAS.
---

# Competenza L1 — google-ads

Ponte operativo tra SEO/intento (organico) e Google Ads (PPC).

## Pre-filtro (System 1)
- Usa `router.py score` per un quick check di aderenza dell'ad-copy ai vincoli di lunghezza Google Ads senza consumare token di Reasoning per il conteggio caratteri.

## Output (Contratto)
- **Niente boilerplate testuale o strategie descrittive.** Restituisci template CSV (per bulk upload Google Ads Editor) o tabelle markdown compatte:
  `| Campagna | AdGroup | Keyword | Match | Headline | Desc |`

Per i dettagli su SKAG/STAG, Performance Max asset spec, e Shopping feed mapping:
Leggi `references/google-ads-extended.md`.
