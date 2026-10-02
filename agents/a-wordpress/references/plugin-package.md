# Packaging plugin — artefatto .zip versionato

Ogni plugin custom (stabile o migrate) è **pronto per la consegna** solo quando esiste anche il pacchetto **`.zip` installabile da wp-admin**, con **versione nel nome file**.

---

## Regola obbligatoria

| Elemento | Convenzione |
|----------|-------------|
| Nome file | `{plugin-slug}-{versione}.zip` |
| Esempio | `asso2026-broken-link-0.5.23.zip` |
| Versione | Da header `Version:` del file principale del plugin |
| Allineamento | `Version:` header = costante `*_VERSION` = versione progetto se prevista |
| Struttura zip | Cartella radice = slug plugin (formato upload WordPress) |
| Output | Cartella artefatti del progetto (vedi profilo sito o `CONTRIBUTING.md`) |

**Non considerare completato** un plugin senza zip versionato aggiornato.

---

## Quando creare / aggiornare lo zip

- Nuovo plugin consegnato
- Ogni bump di versione (patch, minor, major)
- Prima di deploy su produzione o consegna al cliente
- Dopo sync source → runtime e test verdi

---

## Struttura zip corretta

WordPress si aspetta:

```
{plugin-slug}-{versione}.zip
└── {plugin-slug}/
    ├── {plugin-slug}.php
    ├── includes/
    └── ...
```

**Errato:** file PHP alla radice dello zip senza cartella slug.

---

## Esclusioni obbligatorie dallo zip

- `.git/`, `.gitignore`
- `node_modules/`
- `vendor/` (solo se non richiesto in runtime — di default escludi dev dependencies)
- `tests/`, `phpunit.xml*`, `.phpunit.*`
- `*.md` di sviluppo (opzionale: tieni `readme.txt` WordPress.org se presente)
- `.DS_Store`, `__MACOSX/`, `*.log`

---

## Workflow packaging

```
Task Progress:
- [ ] 1. Verifica versione allineata (header, costante, README progetto)
- [ ] 2. Test / smoke check passati
- [ ] 3. Genera zip con nome {slug}-{versione}.zip
- [ ] 4. Verifica contenuto zip (cartella radice = slug)
- [ ] 5. Comunica path zip in output / CHANGELOG se richiesto
```

### Comando generico (bash)

Adatta `PLUGIN_SLUG`, `PLUGIN_SOURCE_DIR`, `OUTPUT_DIR` al progetto.

```bash
#!/usr/bin/env bash
set -euo pipefail

PLUGIN_SLUG="my-plugin"
PLUGIN_DIR="/path/to/plugins/${PLUGIN_SLUG}"
MAIN_FILE="${PLUGIN_DIR}/${PLUGIN_SLUG}.php"
OUTPUT_DIR="/path/to/dist"   # oppure plugins/

VERSION="$(grep -m1 '^[[:space:]]*\*[[:space:]]*Version:' "${MAIN_FILE}" \
  | sed -E 's/.*Version:[[:space:]]*([0-9.]+).*/\1/')"

if [[ -z "${VERSION}" ]]; then
  echo "Errore: Version non trovata in ${MAIN_FILE}" >&2
  exit 1
fi

ZIP_NAME="${PLUGIN_SLUG}-${VERSION}.zip"
ZIP_PATH="${OUTPUT_DIR}/${ZIP_NAME}"

mkdir -p "${OUTPUT_DIR}"
rm -f "${ZIP_PATH}"

(
  cd "$(dirname "${PLUGIN_DIR}")"
  zip -r "${ZIP_PATH}" "${PLUGIN_SLUG}" \
    -x "${PLUGIN_SLUG}/.git/*" \
    -x "${PLUGIN_SLUG}/.git" \
    -x "${PLUGIN_SLUG}/node_modules/*" \
    -x "${PLUGIN_SLUG}/tests/*" \
    -x "${PLUGIN_SLUG}/**/.DS_Store"
)

echo "Creato: ${ZIP_PATH}"
```

### Script di progetto

Se il progetto ha già script (es. `scripts/dev/package-{slug}-plugin.sh`), **usalo** e non reinventare il comando.

Pattern comuni:

| Progetto | Output | Script esempio |
|----------|--------|----------------|
| CambiaPasso analytics | `plugins/` | `scripts/dev/package-analytics-plugin.sh` |
| CambiaPasso migrate | `dist/` | `scripts/package-migrate-ga4-form-events.sh` |

Annota path e script nel profilo `.cursor/wordpress/{sito}.md`.

---

## Verifica rapida post-build

```bash
unzip -l path/to/my-plugin-1.2.3.zip | head
```

Controlla che la prima colonna mostri `my-plugin/` come prefisso dei path.

Test installazione (opzionale, ambiente dev):

```bash
wp plugin install /path/to/my-plugin-1.2.3.zip --activate
```

---

## Output atteso dell'agente

Al termine di un plugin stabile o migrate, riporta sempre:

1. Path cartella source del plugin
2. Versione rilasciata
3. **Path completo del file `.zip`** (es. `dist/asso2026-foo-1.0.0.zip`)
4. Eventuale comando/script usato per rigenerarlo

---

## Checklist pre-consegna packaging

- [ ] Header `Version:` presente e valida (semver)
- [ ] Costante versione allineata
- [ ] Zip generato: `{slug}-{versione}.zip`
- [ ] Radice zip = cartella slug
- [ ] Esclusioni dev (.git, node_modules, tests) applicate
- [ ] Path zip comunicato all'utente
- [ ] `.gitignore` del progetto esclude `*.zip` se gli artefatti non vanno versionati
