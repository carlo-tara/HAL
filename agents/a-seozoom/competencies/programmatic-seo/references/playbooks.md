# pSEO playbooks — sintesi operativa

Distillato da marketingskills. Per procedure lunghe: upstream `programmatic-seo/references/playbooks.md`.

## Scelta rapida

| Hai… | Considera |
|------|-----------|
| Dati proprietari | Directory, Profiles |
| Integrazioni prodotto | Integrations |
| Design/creative | Templates, Examples |
| Segmenti audience | Personas |
| Presenza locale | Locations |
| Utility/tool | Conversions |
| Expertise editoriale | Glossary, Curation |
| Landscape competitor | Comparisons |

Si possono comporre (es. “best coworking in [city]”).

## Regole anti-thin

- Ogni spoke: almeno una sezione che cambia con dati non banali (non solo nome città)
- Conditional blocks se dato assente (non stampare “N/A” ovunque)
- Soglia minima domanda o valore brand documentata in L2 / brief
- Monitor cannibalizzazione tra spoke simili

## Hub-spoke

```
/hub-category/          ← hub (curation + link a tutti gli spoke)
  /hub-category/item-a/ ← spoke
  /hub-category/item-b/
```

Cross-link spoke correlati; breadcrumb coerente con `site-architecture`.

## Post-launch

Traccia da export successivi: indexation rate (GSC), ranking/traffic CSV, engagement se GA4 in batch. Segnali thin/manual action → riduci cardinalità o arricchisci dati, non “aggiungere keyword”.
