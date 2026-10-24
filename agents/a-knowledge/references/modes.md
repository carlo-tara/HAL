# Modalità operative

| Modalità | Invocazione | Fasi | Costo |
| -------- | ----------- | ---- | ----- |
| **check** | `/knowledge check` | 0 (diagnosi) | ~0 |
| **extract** | `/knowledge extract <path>` | 1 | CPU, 0 token |
| **analyze** | `/knowledge analyze <path>` | 1 + report | CPU + lettura parziale |
| **distill** | `/knowledge distill <path> [slug]` | 1 → 2 | free/flash, 1× |
| **query** | `/knowledge query <slug> "<domanda>"` | 3 | ~5k token |
| **update** | `/knowledge update <slug> <nuove sorgenti>` | 1 → 2 (delta) | solo input nuovo |

Mappa ai modi book-to-skill:

| book-to-skill | a-knowledge |
| ------------- | ----------- |
| Full Conversion | `distill` |
| Analyze Only | `analyze` |
| Generate from Prior Analysis | `distill` su analisi esistente |
| Update / Fold-in | `update` |
| Publish to GitHub | fuori scope (privacy: non pubblicare skill di terzi) |

## Flusso consigliato

```text
check → extract (CPU) → distill (free, 1×) → query (Laya + 1 capitolo)
```

## Privacy

- Estrazione **locale**, nessun upload.
- Se il modello è cloud, il testo inviato segue i termini del provider (come ogni prompt).
- Skill generate da opere di terzi: **private**. Documentazione propria/open-license: condivisibile nei limiti della licenza.
