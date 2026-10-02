# Drift batch-to-batch (lean)

Distillato da `vendor/claude-seo/skills/seo-drift/references/comparison-rules.md` (MIT) — **senza** SQLite / script drift.  
Confronto tra cartelle `seo/{YYMMDD}` consecutive e/o Spider export datati. Pin: [claude-seo-source.md](../../../references/claude-seo-source.md).

## Quando

Full audit, “cosa è cambiato”, post-deploy, o ≥2 batch disponibili. Se un solo batch: skip drift.

## CRITICAL (agire subito)

| Segnale | Baseline → corrente | Nota |
|---------|---------------------|------|
| Schema supportato azzerato | Aveva JSON-LD rilevante → vuoto | Non contare FAQ/HowTo retired come perdita rich result |
| Canonical cambiato / rimosso | Valore diverso o null | Verificare intenzionalità |
| noindex aggiunto | Prima indexable | Drop indice in giorni |
| Title / H1 rimossi | Presenti → assenti | |
| Status 2xx → 4xx/5xx | Su URL money | |

## WARNING (≤1 settimana)

| Segnale | Nota |
|---------|------|
| Title / meta description cambiati | Monitorare CTR GSC |
| Schema modificato (hash/tipo) | Validare; tipi retired → Info |
| OG rimossi | Social preview |
| CWV / Lighthouse | Solo se L2 ha misurato — altrimenti “non verificabile” |

## INFO

Nuovo schema aggiunto; H2 ristrutturati; content hash cambiato (atteso post-edit).

## Output

Finding con formato `audit-framework.md`, dimensione SEO, evidenza = path batch A vs B + URL.
