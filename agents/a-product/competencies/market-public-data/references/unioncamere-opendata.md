# Unioncamere Open Government — access playbook

Portale: [opengovernment.unioncamere.gov.it](https://opengovernment.unioncamere.gov.it/)  
Come fruire: [come-fruire-dei-dati](https://opengovernment.unioncamere.gov.it/come-fruire-dei-dati)

## Cosa trovi

Dataset aperti (tipicamente **CSV**) da Camere di commercio aderenti:

- demografia delle imprese
- start-up (aggregati camerali)
- commercio estero
- imprenditoria femminile / giovanile / straniera
- ambiente (dove pubblicato)

Sono **dati primari amministrativi**, non indici sintetici o indagini.

## Discovery

1. Cerca sul portale per categoria/territorio.
2. Catalogo nazionale federato (CKAN):

```bash
curl -fsSL 'https://dati.gov.it/opendata/api/3/action/package_search?q=unioncamere&rows=10'
# Affina: q=impresa+camera, o fq su organization/holder quando noto
```

3. Dalla scheda dataset scarica la distribuzione CSV e salvala in `.cursor/product/data/`.

## Licenze

Spesso **CC-BY 4.0** o CC BY-SA — verifica il campo Licenze nei metadati di ogni dataset.

## Citation

`Fonte: {Camera / Unioncamere} — {titolo dataset}; {URL scheda}; licenza {X}; scaricato il {YYYY-MM-DD}`

## Limiti

- Copertura a macchia di leopardo (solo camere aderenti)
- Definizioni e annualità variano per dataset — non confrontare province diverse senza leggere metadati
- Portale Drupal: non assumere CKAN API locale su unioncamere.gov.it
