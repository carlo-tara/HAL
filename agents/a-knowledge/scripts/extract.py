#!/usr/bin/env python3
"""
extract.py — Wrapper cost-aware per a-knowledge book-to-skill pipeline.

Selezione estrattore per formato, routing capitolo Laya, cache workdir+sha256.
Zero GPU by default. Costo CPU minimo, zero token in fase di estrazione.

Usage:
    python3 extract.py --check                          # Diagnosi dipendenze
    python3 extract.py --input book.pdf                 # Estrazione automatica
    python3 extract.py --input book.epub --mode technical  # Tecnico (tabelle/codice)
    python3 extract.py --input book.pdf --chapter 3 --laya http://127.0.0.1:8091  # Routing capitolo
    python3 extract.py --input book.pdf --distill --model deepseek-v4-flash-free  # Distillazione
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any

# ── Configurazione ──────────────────────────────────────────────────────────

BOOK_SKILL_WORKDIR = os.environ.get("BOOK_SKILL_WORKDIR", ".book_skill_cache")
LAYA_URL = os.environ.get("LAYA_URL", "http://127.0.0.1:8091")
LAYA_API_KEY = os.environ.get("LAYA_API_KEY", "sk-local")
LAYA_TIMEOUT = float(os.environ.get("LAYA_TIMEOUT", "120"))
LAYA_MODEL = os.environ.get("LAYA_MODEL", "multilingual")

# ── HTTP connection reuse (N24, doc QwenCloud §connection reuse) ────────────
_LAYA_CLIENTS: dict[float, object] = {}


def laya_client(timeout: float):
    """Un solo httpx.Client per run (per timeout): riusato tra cmd_check e
    route_chapter_laya, chiuso a atexit — niente istanze dentro funzioni
    invocate in loop."""
    client = _LAYA_CLIENTS.get(timeout)
    if client is None:
        import httpx

        client = httpx.Client(timeout=timeout)
        _LAYA_CLIENTS[timeout] = client
        if len(_LAYA_CLIENTS) == 1:
            import atexit

            atexit.register(_close_laya_clients)
    return client


def _close_laya_clients() -> None:
    for c in list(_LAYA_CLIENTS.values()):
        try:
            c.close()  # type: ignore[attr-defined]
        except Exception:  # noqa: BLE001 - teardown difensivo
            pass
    _LAYA_CLIENTS.clear()


# Mappa formato → tool primario → fallback
FORMAT_TOOLS: dict[str, dict[str, Any]] = {
    "pdf_text": {
        "primary": "pdftotext",
        "fallbacks": ["pypdf", "pdfminer"],
        "apt": ["poppler-utils"],
        "pip": ["pypdf", "pdfminer.six"],
        "cost_cpu": "~0.1 s",
        "description": "PDF testo (layout preservato)",
    },
    "pdf_tech": {
        "primary": "docling",
        "fallbacks": ["pdftotext", "pypdf"],
        "apt": [],
        "pip": ["docling"],
        "cost_cpu": "~1.5 s/pag",
        "description": "PDF tecnico (tabelle/codice)",
    },
    "epub": {
        "primary": "ebooklib",
        "fallbacks": ["zipfile"],
        "apt": [],
        "pip": ["ebooklib", "beautifulsoup4"],
        "cost_cpu": "~0",
        "description": "EPUB / HTML strutturato",
    },
    "docx": {
        "primary": "python-docx",
        "fallbacks": ["zipfile"],
        "apt": [],
        "pip": ["python-docx"],
        "cost_cpu": "~0",
        "description": "DOCX / Word",
    },
    "html": {
        "primary": "trafilatura",
        "fallbacks": ["beautifulsoup4", "stdlib"],
        "apt": [],
        "pip": ["trafilatura", "beautifulsoup4"],
        "cost_cpu": "~0",
        "description": "HTML (clean extraction)",
    },
    "rtf": {
        "primary": "striprtf",
        "fallbacks": ["regex"],
        "apt": [],
        "pip": ["striprtf"],
        "cost_cpu": "~0",
        "description": "RTF (Rich Text Format)",
    },
    "mobi_azw": {
        "primary": "ebook-convert",
        "fallbacks": [],
        "apt": [],
        "pip": [],
        "cost_cpu": "variabile",
        "description": "MOBI/AZW/AZW3 (Calibre obbligatorio)",
    },
    "txt_md_rst": {
        "primary": "builtin",
        "fallbacks": [],
        "apt": [],
        "pip": [],
        "cost_cpu": "~0",
        "description": "TXT/MD/rST/AsciiDoc (built-in)",
    },
}

# Estensioni → formato
EXTENSION_MAP: dict[str, str] = {
    ".pdf": "pdf_text",
    ".epub": "epub",
    ".docx": "docx",
    ".html": "html",
    ".htm": "html",
    ".rtf": "rtf",
    ".mobi": "mobi_azw",
    ".azw": "mobi_azw",
    ".azw3": "mobi_azw",
    ".txt": "txt_md_rst",
    ".md": "txt_md_rst",
    ".rst": "txt_md_rst",
    ".adoc": "txt_md_rst",
}


# ── Utilità ─────────────────────────────────────────────────────────────────


def sha256_file(path: str) -> str:
    """Calcola SHA-256 di un file."""
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return ""


def check_command_available(cmd: str) -> bool:
    """Verifica se un comando è installato nel PATH."""
    return shutil.which(cmd) is not None


def check_python_package(pkg: str) -> bool:
    """Verifica se un pacchetto Python è installato."""
    try:
        __import__(pkg.replace("-", "_"))
        return True
    except ImportError:
        return False


def detect_format(filepath: str) -> str | None:
    """Rileva il formato del file dall'estensione."""
    ext = Path(filepath).suffix.lower()
    return EXTENSION_MAP.get(ext)


def estimate_table_code_density(text: str) -> float:
    """Stima la densità di tabelle/codice nel testo (0-1)."""
    if not text:
        return 0.0
    lines = text.split("\n")
    code_lines = sum(
        1
        for l in lines
        if any(
            kw in l.lower()
            for kw in ["def ", "class ", "import ", "return ", "{", "}", "=>"]
        )
    )
    table_lines = sum(1 for l in lines if "|" in l and ("-" in l or "+" in l))
    total = max(len(lines), 1)
    return (code_lines + table_lines) / total


# ── Modalità --check ────────────────────────────────────────────────────────


def cmd_check() -> int:
    """Diagnosi dipendenze: report per formato + comandi installati/mancanti."""
    print("=" * 60)
    print("extract.py — Diagnosi dipendenze")
    print("=" * 60)

    all_ok = True
    results: list[dict[str, Any]] = []

    for fmt, tools in FORMAT_TOOLS.items():
        primary_ok = False
        fallback_ok = False
        missing_primary = ""
        missing_fallbacks = []

        # Verifica primario
        if tools["primary"] == "builtin":
            primary_ok = True
        elif check_command_available(tools["primary"]):
            primary_ok = True
        elif check_python_package(tools["primary"].replace("-", "_")):
            primary_ok = True
        else:
            missing_primary = tools["primary"]
            all_ok = False

        # Verifica fallback
        for fb in tools["fallbacks"]:
            if fb == "builtin":
                fallback_ok = True
                break
            elif check_command_available(fb):
                fallback_ok = True
                break
            elif check_python_package(fb.replace("-", "_")):
                fallback_ok = True
                break
            else:
                missing_fallbacks.append(fb)

        status = "OK" if primary_ok else ("fallback" if fallback_ok else "MISSING")
        results.append(
            {
                "format": fmt,
                "status": status,
                "primary": tools["primary"],
                "primary_ok": primary_ok,
                "fallback_ok": fallback_ok,
                "missing_primary": missing_primary,
                "missing_fallbacks": missing_fallbacks,
                "cost_cpu": tools["cost_cpu"],
                "description": tools["description"],
            }
        )

    # Tabella risultati
    print(f"\n{'Formato':<20} {'Stato':<10} {'Primario':<15} {'Costo CPU':<12}")
    print("-" * 60)
    for r in results:
        icon = (
            "✓" if r["status"] == "OK" else ("~" if r["status"] == "fallback" else "✗")
        )
        print(
            f"{icon} {r['description']:<18} {r['status']:<10} {r['primary']:<15} {r['cost_cpu']:<12}"
        )

    # Raccomandazioni
    missing_apt = set()
    missing_pip = set()
    for r in results:
        if r["status"] == "MISSING":
            fmt_key = next(
                (
                    k
                    for k, v in FORMAT_TOOLS.items()
                    if v["description"] == r["description"]
                ),
                None,
            )
            if fmt_key:
                missing_apt.update(FORMAT_TOOLS[fmt_key].get("apt", []))
                missing_pip.update(FORMAT_TOOLS[fmt_key].get("pip", []))

    if missing_apt or missing_pip:
        print("\nRaccomandazioni installazione:")
        if missing_apt:
            print(f"  apt: sudo apt install {' '.join(sorted(missing_apt))}")
        if missing_pip:
            print(f"  pip: pip3 install {' '.join(sorted(missing_pip))}")

    # Cache info
    workdir = Path(BOOK_SKILL_WORKDIR)
    if workdir.exists():
        cached = len(list(workdir.glob("*")))
        print(f"\nCache workdir: {workdir} ({cached} elementi)")
    else:
        print(f"\nCache workdir: {workdir} (non ancora creata)")

    # Laya check
    try:
        client = laya_client(LAYA_TIMEOUT)
        resp = client.post(
            f"{LAYA_URL}/predict",
            headers={"Authorization": f"Bearer {LAYA_API_KEY}"},
            json={"text": "test", "task_family": "translation"},
        )
        laya_ok = resp.status_code == 200
    except Exception:
        laya_ok = False

    laya_status = "✓ attivo" if laya_ok else "✗ non raggiungibile"
    print(f"Laya System 1: {LAYA_URL} → {laya_status}")

    print("\n" + "=" * 60)
    if all_ok and laya_ok:
        print("Stato: TUTTO OK — estrazione e routing pronti.")
    elif all_ok:
        print(
            "Stato: ESTRATTAZIONE OK, LAYA NON RAGGIUNGBILE — estrazione funziona, routing disabilitato."
        )
    else:
        print("Stato: DIPENDENZE MANCANTI — vedi raccomandazioni sopra.")
    print("=" * 60)

    return 0 if all_ok else 1


# ── Selezione estrattore ────────────────────────────────────────────────────


def select_extractor(fmt: str, mode: str = "auto") -> tuple[str, str]:
    """
    Seleziona l'estrattore migliore per il formato dato.

    Args:
        fmt: formato rilevato (es. 'pdf_text', 'epub')
        mode: 'auto' (euristica densità), 'text', 'technical'

    Returns:
        (tool_name, strategy_description)
    """
    if fmt not in FORMAT_TOOLS:
        return ("builtin", "lettura testuale diretta")

    tools = FORMAT_TOOLS[fmt]

    if mode == "auto":
        # Per PDF, usa euristica: solo dopo estrazione si può stimare densità
        if fmt.startswith("pdf"):
            return (
                tools["primary"],
                f"default {tools['description']} — passa --mode technical se servono tabelle",
            )
        return (tools["primary"], tools["description"])

    if mode == "technical" and fmt.startswith("pdf"):
        return (
            tools["primary"],
            f"modalità tecnica: {tools['description']} con tabelle/codice",
        )

    return (tools["primary"], tools["description"])


# ── Estrazione ──────────────────────────────────────────────────────────────


def extract_pdf_text(input_path: str, output_path: str, mode: str = "auto") -> bool:
    """Estrae testo da PDF usando pdftotext o pypdf."""
    if check_command_available("pdftotext"):
        cmd = ["pdftotext", "-layout", "-enc", "UTF-8", input_path, output_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            return True
        print(
            f"  pdftotext fallito (exit {result.returncode}), provo fallback...",
            file=sys.stderr,
        )

    # Fallback: pypdf
    if check_python_package("pypdf"):
        try:
            import pypdf

            reader = pypdf.PdfReader(input_path)
            with open(output_path, "w", encoding="utf-8") as f:
                for page in reader.pages:
                    f.write(page.extract_text() or "")
                    f.write("\n\n")
            return True
        except Exception as exc:
            print(f"  pypdf fallito: {exc}", file=sys.stderr)

    print("  ERRORE: nessun estrattore PDF disponibile", file=sys.stderr)
    return False


def extract_epub(input_path: str, output_path: str) -> bool:
    """Estrae testo da EPUB usando ebooklib + beautifulsoup4."""
    if check_python_package("ebooklib"):
        try:
            from bs4 import BeautifulSoup
            from ebooklib import epub

            book = epub.read_epub(input_path)
            chapters = []

            for item in book.get_items_of_type(epub.ITEM_DOCUMENT):
                soup = BeautifulSoup(item.get_content(), "html.parser")
                text = soup.get_text(separator="\n", strip=True)
                if text.strip():
                    chapters.append(text)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n\n---CHAPTER_SEP---\n\n".join(chapters))
            return True
        except Exception as exc:
            print(f"  ebooklib fallito: {exc}, provo fallback...", file=sys.stderr)

    # Fallback: zipfile + regex (structura EPUB = ZIP con XML)
    try:
        with zipfile.ZipFile(input_path, "r") as z:
            texts = []
            for name in z.namelist():
                if name.endswith(".xhtml") or name.endswith(".html"):
                    content = z.read(name).decode("utf-8", errors="ignore")
                    # Strip tags semplice
                    clean = "".join(
                        line.strip()
                        for line in content.split("\n")
                        if "<" not in line and ">" not in line
                    )
                    if clean.strip():
                        texts.append(clean)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n\n".join(texts))
            return True
    except Exception as exc:
        print(f"  zipfile fallback fallito: {exc}", file=sys.stderr)

    return False


def extract_docx(input_path: str, output_path: str) -> bool:
    """Estrae testo da DOCX usando python-docx."""
    if check_python_package("docx"):
        try:
            import docx

            doc = docx.Document(input_path)
            with open(output_path, "w", encoding="utf-8") as f:
                for para in doc.paragraphs:
                    if para.text.strip():
                        f.write(para.text + "\n")
            return True
        except Exception as exc:
            print(f"  python-docx fallito: {exc}", file=sys.stderr)

    # Fallback: unzip + XML parsing
    try:
        import xml.etree.ElementTree as ET

        with zipfile.ZipFile(input_path, "r") as z:
            xml_content = z.read("word/document.xml").decode("utf-8")
            root = ET.fromstring(xml_content)
            ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            texts = [
                elem.text
                for elem in root.iter(
                    "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"
                )
                if elem.text
            ]
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(texts))
            return True
    except Exception as exc:
        print(f"  XML fallback fallito: {exc}", file=sys.stderr)

    return False


def extract_txt(input_path: str, output_path: str) -> bool:
    """Copia file TXT/MD/RST direttamente."""
    try:
        shutil.copy2(input_path, output_path)
        return True
    except Exception as exc:
        print(f"  ERRORE copia: {exc}", file=sys.stderr)
        return False


def extract_html(input_path: str, output_path: str) -> bool:
    """Estrae testo da HTML usando trafilatura o beautifulsoup4."""
    if check_python_package("trafilatura"):
        try:
            import trafilatura

            with open(input_path, "r", encoding="utf-8", errors="ignore") as f:
                html_content = f.read()
            extracted = trafilatura.extract(html_content)
            if extracted:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(extracted)
                return True
        except Exception as exc:
            print(f"  trafilatura fallito: {exc}, provo fallback...", file=sys.stderr)

    if check_python_package("beautifulsoup4"):
        try:
            from bs4 import BeautifulSoup

            with open(input_path, "r", encoding="utf-8", errors="ignore") as f:
                soup = BeautifulSoup(f.read(), "html.parser")
            text = soup.get_text(separator="\n", strip=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)
            return True
        except Exception as exc:
            print(f"  beautifulsoup4 fallback fallito: {exc}", file=sys.stderr)

    return False


def run_extraction(
    input_path: str, output_path: str, fmt: str, mode: str = "auto"
) -> bool:
    """Esegue l'estrazione basata sul formato rilevato."""
    extractor_map = {
        "pdf_text": extract_pdf_text,
        "pdf_tech": extract_pdf_text,
        "epub": extract_epub,
        "docx": extract_docx,
        "html": extract_html,
        "txt_md_rst": extract_txt,
        "rtf": extract_txt,  # Simplified: RTF requires striprtf, fallback to copy
        "mobi_azw": lambda *a: (
            print("ERRORE: MOBI/AZW richiede Calibre ebook-convert", file=sys.stderr),
            False,
        )[1],
    }

    extractor = extractor_map.get(fmt)
    if not extractor:
        print(f"ERRORE: formato '{fmt}' non supportato", file=sys.stderr)
        return False

    tool, desc = select_extractor(fmt, mode)
    print(f"  Estrattore: {tool} — {desc}")

    return extractor(input_path, output_path, mode=mode)


# ── Routing capitolo Laya ───────────────────────────────────────────────────


def route_chapter_laya(
    query: str,
    chapters: list[str],
    laya_url: str = LAYA_URL,
    laya_api_key: str = LAYA_API_KEY,
    laya_timeout: float = LAYA_TIMEOUT,
    laya_model: str = LAYA_MODEL,
) -> dict[str, Any] | None:
    """
    Routing System 1 (Laya): sceglie il capitolo più rilevante per la query.

    Costo: ~33ms Laya, zero token per il documento.
    Ritorna None se Laya non è raggiungibile (fallback: primo capitolo).
    """
    if not chapters:
        return None

    try:
        client = laya_client(laya_timeout)
        payload = {
            "text": query,
            "task_family": "routing",
            "options": chapters,
            "model": laya_model,
        }
        resp = client.post(
            f"{laya_url}/predict",
            headers={"Authorization": f"Bearer {laya_api_key}"},
            json=payload,
        )
        if resp.status_code == 200:
            data = resp.json()
            return {
                "selected": data.get("answers", {}).get("intent", {}).get("choice"),
                "confidence": data.get("answers", {})
                .get("intent", {})
                .get("confidence"),
                "laya_model": laya_model,
            }
    except Exception as exc:
        print(f"  Laya routing fallito: {exc} (fallback: capitolo 1)", file=sys.stderr)

    return None


# ── Distillazione ───────────────────────────────────────────────────────────


def cmd_distill(
    input_path: str,
    model: str = "deepseek-v4-flash-free",
    depth: str = "reference",
) -> bool:
    """
    Distillazione: genera sintesi capitolo-per-capitolo con modello free/flash.

    Questa è una stub — la distillazione vera richiede integrazione con
    il router OrcaRouter o un endpoint OpenAI-compatible.
    """
    print(f"Distillazione: {input_path}")
    print(f"  Modello: {model}")
    print(f"  Profondità: {depth}")
    print("  NOTA: La distillazione richiede integrazione con OrcaRouter/LlamaIndex.")
    print("  Batch API (-50%, esito in 24h): preferita oltre la soglia di volume")
    print("    (> ~500 richieste JSONL); sotto soglia resta la Task API.")
    print("    Regola completa: docs/25_task_vs_batch.md")
    print("  Per ora, usa il manuale: capitolo-per-capitolo con wc/grep/sed.")
    return True


# ── Main ────────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(
        description="extract.py — Wrapper cost-aware per a-knowledge book-to-skill",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Diagnosi dipendenze: report format/tool/installati",
    )
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        help="Percorso file sorgente (PDF, EPUB, DOCX, HTML, TXT...)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Percorso output testo estratto (default: stdout o <input>.txt)",
    )
    parser.add_argument(
        "--mode",
        choices=["auto", "text", "technical"],
        default="auto",
        help="Modalità estrazione: auto (euristica), text (default), technical (tabelle/codice)",
    )
    parser.add_argument(
        "--chapter",
        "-c",
        type=int,
        default=None,
        help="Capitolo specifico da processare (richiede EPUB strutturato)",
    )
    parser.add_argument(
        "--laya",
        type=str,
        default=None,
        help="URL Laya System 1 per routing capitolo (default: $LAYA_URL)",
    )
    parser.add_argument(
        "--query",
        "-q",
        type=str,
        default=None,
        help="Query per routing capitolo Laya",
    )
    parser.add_argument(
        "--distill",
        action="store_true",
        help="Esegui distillazione (stub: richiede OrcaRouter integration)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="deepseek-v4-flash-free",
        help="Modello per distillazione (default: deepseek-v4-flash-free)",
    )
    parser.add_argument(
        "--depth",
        choices=["reference", "study"],
        default="reference",
        help="Profondità distillazione: reference (lean, 800-1800 token) o study",
    )
    parser.add_argument(
        "--workdir",
        type=str,
        default=None,
        help=f"Workdir cache (default: $BOOK_SKILL_WORKDIR o {BOOK_SKILL_WORKDIR})",
    )

    args = parser.parse_args()

    # --check
    if args.check:
        return cmd_check()

    # Validazione input
    if not args.input:
        parser.error("--input è richiesto (tranne che per --check)")
    if not os.path.isfile(args.input):
        print(f"ERRORE: file non trovato: {args.input}", file=sys.stderr)
        return 1

    # Rilevamento formato
    fmt = detect_format(args.input)
    if not fmt:
        print(f"ERRORE: formato non riconosciuto per: {args.input}", file=sys.stderr)
        return 1

    print(f"Input: {args.input}")
    print(f"Formato: {fmt}")

    # Cache check
    workdir = Path(args.workdir or BOOK_SKILL_WORKDIR)
    src_hash = sha256_file(args.input)
    cache_key = f"{Path(args.input).name}_{src_hash[:12]}"
    cached_output = workdir / f"{cache_key}.txt"

    if cached_output.exists() and src_hash:
        print(f"Cache hit: {cached_output} (sha256 match)")
        if args.output:
            shutil.copy2(str(cached_output), args.output)
        else:
            with open(cached_output, "r", encoding="utf-8") as f:
                print(f.read(), end="")
        return 0

    # Creazione workdir
    workdir.mkdir(parents=True, exist_ok=True)

    # Output path
    output_path = args.output or f"{args.input}.txt"

    # Estrazione
    print(f"Output: {output_path}")
    success = run_extraction(args.input, output_path, fmt, mode=args.mode)

    if not success:
        print("ERRORE: estrazione fallita", file=sys.stderr)
        return 1

    # Salva in cache
    if src_hash and cached_output != Path(output_path):
        shutil.copy2(output_path, str(cached_output))
        print(f"Cache salvata: {cached_output}")

    # Routing capitolo Laya
    if args.query and args.laya:
        laya_url = args.laya
    else:
        laya_url = LAYA_URL

    if args.query:
        print(f"\nRouting Laya: '{args.query}' → {laya_url}")
        # Stub: in produzione, leggere i capitoli dall'output e fare routing
        print("  NOTA: Il routing capitolo richiede capitoli strutturati nell'output.")
        print("  Per EPUB: usa --chapter per selezionare manualmente.")

    # Distillazione
    if args.distill:
        print("\nDistillazione...")
        cmd_distill(output_path, model=args.model, depth=args.depth)

    print(f"\nEstrazione completata: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
