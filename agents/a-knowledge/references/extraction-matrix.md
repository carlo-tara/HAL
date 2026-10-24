# Matrice di estrazione — formato → tool → costo

Estrazione **locale e deterministica**: 0 GPU, 0 token. Ordine di tentativo = primo tool disponibile.

| Formato | Tool primario | Fallback | Costo CPU | GPU |
| ------- | ------------- | -------- | --------- | --- |
| PDF testo | `pdftotext -layout` | `pypdf`, `pdfminer.six` | ~0.1 s | 0 |
| PDF tecnico (tabelle/codice) | `docling` | catena testo | ~1.5 s/pag | 0 |
| EPUB | `ebooklib` + `beautifulsoup4` | stdlib `zipfile` | ~0 | 0 |
| DOCX | `python-docx` | stdlib ZIP/XML | ~0 | 0 |
| HTML | `trafilatura` | `beautifulsoup4`, stdlib | ~0 | 0 |
| RTF | `striprtf` | regex | ~0 | 0 |
| MOBI/AZW/AZW3 | Calibre `ebook-convert` | — (obbligatorio) | variabile | 0 |
| TXT/MD/rST/AsciiDoc | built-in | — | ~0 | 0 |
| PDF scansionato | `ocrmypdf` (**opt-in**) | — | alto | 0 |

## Install (Ubuntu/Debian)

```bash
sudo apt install poppler-utils        # pdftotext
pip3 install pypdf pdfminer.six       # fallback PDF
pip3 install docling                  # PDF tecnico (tabelle/codice)
pip3 install ebooklib beautifulsoup4  # EPUB / HTML
pip3 install python-docx trafilatura striprtf
```

## Diagnosi

```bash
python3 scripts/extract.py --check    # report per formato + comandi install mancanti (exit 0)
```

## Regole

- **Mai GPU**: `marker`, `mineru`, `nougat` sono GPU-heavy e restano **fuori default**.
- **Mai OCR automatico**: PDF di immagini → stop + `ocrmypdf input.pdf output.pdf` manuale.
- **Cache**: `BOOK_SKILL_WORKDIR` riusato se workdir intatto + `sha256` combaciano → 0 ri-estrazione.
- **Scelta modo**: euristica su densità tabelle/codice → `text` (default) vs `technical`.
