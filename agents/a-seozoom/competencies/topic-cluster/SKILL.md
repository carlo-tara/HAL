---
name: topic-cluster
kind: competency
version: 1.0.0
description: >-
  Clustering topico SERP-overlap allineato a CSV SeoZoom: owner URL, hub-spoke,
  anti-cannibalizzazione. Solo L1 (no baseline L0).
---

# Competenza L1 — topic-cluster (a-seozoom)

Architettura contenuti da overlap SERP + export SeoZoom. Distillato da claude-seo `seo-cluster` (MIT), riallineato ad AF.  
Pin: [claude-seo-source.md](../../references/claude-seo-source.md).  
Metodo: [references/serp-overlap.md](references/serp-overlap.md).

**Non** inventare volumi. **Non** duplicare playbook `programmatic-seo`.

---

## Quando applicare

Mappa cluster, “una pagina o due?”, pillar/spoke, fan-out GEO, priorità hub dopo cannibalizzazione.  
Selezione keyword money → spesso con `metriche-analisi`. Link interni → `site-architecture`.

---

## Fonti preferite (ordine)

1. `seo/{YYMMDD}/seozoom/clusters_keyword.csv`, `keywords_cluster.csv`
2. Cannibalizzazione / `monitored.csv` (owner URL)
3. SERP live / WebSearch **solo** se batch assente e utente lo chiede (soglie in ref)

---

## Principio

Stessi risultati organici top-10 → stessa pagina o stesso cluster. Overlap basso → pagine/cluster separati + interlink se adiacenti.

Output tipico: cluster → **primary keyword** (volume da `seo/`) → **owner URL** → hub/spoke → azioni (`onpage-seo` / nuova URL solo se gap confermato).

---

## Output atteso

- Tabella cluster | keyword | owner URL | relazione (same post / same cluster / interlink / separate)
- Gap strutturali verso `site-architecture` / `programmatic-seo`
- Nessun volume senza file+data
