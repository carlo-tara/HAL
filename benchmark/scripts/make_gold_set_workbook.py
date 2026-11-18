"""HT-005 — generatore del workbook di etichettatura gold set System 1.

Il workbook e' lo strumento per il residuo umano di HT-005: ~200 casi etichettati
per famiglia (choice/routing/score/noul). Questo script rigenera il file in modo
deterministico: header + righe seed (contenuto reale ancorato alla pratica HAL:
agenti primari, comandi, bivia documentati in CHANGELOG/ToDo) + righe vuote
autore per arrivare a TARGET_PER_FAMILY per famiglia. La colonna ``label`` e'
SEMPRE vuota nei seed: l'etichetta deve essere umana (HT-005 #human).

Uso:
    python3 benchmark/scripts/make_gold_set_workbook.py [out.xlsx]

Export delle etichette in JSONL: benchmark/scripts/gold_set_xlsx_to_jsonl.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

TARGET_PER_FAMILY = 200
FAMILIES = ("choice", "routing", "score", "noul")
PREFIX = {"choice": "c", "routing": "r", "score": "s", "noul": "n"}
DEFAULT_OUT = (
    Path(__file__).resolve().parent.parent / "gold_set" / "HT-005_labeling.xlsx"
)

HEADERS = (
    "id",
    "family",
    "instruction",
    "candidates (pipe |)",
    "criteria",
    "label (UMANA)",
    "fonte/note",
)

# --- seed: contenuto reale, etichetta lasciata vuota (giudizio umano) -------
# I candidati rispettano il canone Laya: label corta <30 char; k>=4 => System 1
# produce solo shortlist (T-73140), la label gold rimane una sola opzione.

Seed = tuple[str, list[str] | str, str]
ROUTING_SEEDS: list[Seed] = [
    (
        "Il cliente vuole impostare un pilota B2B con ICP 6-50 dipendenti nel bacino di Chiasso",
        ["a-b2b", "a-product", "a-seozoom"],
        "agenti primari HAL",
    ),
    (
        "Serve il copy SEO per la scheda prodotto della categoria casco da ciclismo",
        ["a-copywriter", "a-seozoom", "a-wordpress"],
        "agenti primari HAL",
    ),
    (
        "Audit di accessibilita WCAG della landing page del sito statico",
        ["a-design", "a-copywriter", "a-wordpress"],
        "agenti primari HAL",
    ),
    (
        "Trasformare un PDF tecnico in una skill interrogabile on-demand",
        ["a-knowledge", "a-agentzero", "a-product"],
        "agenti primari HAL",
    ),
    (
        "Coordinare discovery, PRD e priorita del roadmap del prodotto",
        ["a-product", "a-b2b", "a-knowledge"],
        "agenti primari HAL",
    ),
    (
        "Sviluppare e revisionare un plugin WordPress per la migrazione dati",
        ["a-wordpress", "a-design", "a-harness"],
        "agenti primari HAL",
    ),
    (
        "Analizzare le metriche SeoZoom e costruire topic cluster",
        ["a-seozoom", "a-copywriter", "a-product"],
        "agenti primari HAL",
    ),
    (
        "Aprire uno slice TDD con gate Make e ciclo red-green-refactor",
        ["a-harness", "a-agentzero", "a-design"],
        "agenti primari HAL",
    ),
    (
        "Generare un'illustrazione hero coerente con lo stile del brand",
        ["a-design", "a-copywriter", "a-knowledge"],
        "agenti primari HAL",
    ),
    (
        "Verificare la sincronizzazione dei bundle agenti L0/L1 del workspace",
        ["a-agentzero", "a-harness", "a-seozoom"],
        "sync HAL",
    ),
    (
        "L'utente digita /sync ? per controllare gli agenti fuori fase",
        ["sync", "version", "todo"],
        "comandi workspace",
    ),
    (
        "L'utente digita /cycle chiudendo una voce ToDo marcate #cycle",
        ["cycle", "todo", "graph"],
        "comandi workspace",
    ),
    (
        "L'utente digita /graph -y per rigenerare il work graph",
        ["graph", "cycle", "slice"],
        "comandi workspace",
    ),
    (
        "L'utente digita /impersonate karpathy sul gateway",
        ["impersonate", "review", "improve"],
        "comandi workspace",
    ),
    (
        "L'utente digita /flush per spostare le voci chiuse nel CHANGELOG",
        ["todo", "commit", "cycle"],
        "comandi workspace",
    ),
    (
        "Commit che aggiunge una nuova skill L2 al bundle",
        ["feat", "fix", "docs", "chore"],
        "commit-type (canone blind-set)",
    ),
    (
        "Commit che corregge un parsing errato nel router",
        ["fix", "feat", "refactor", "test"],
        "commit-type (canone blind-set)",
    ),
    (
        "Commit che riallinea un changelog mirror senza toccare codice",
        ["docs", "chore", "fix", "refactor"],
        "commit-type (canone blind-set)",
    ),
    (
        "Commit che rinomina una funzione interna senza cambiare comportamento",
        ["refactor", "chore", "feat", "fix"],
        "commit-type (canone blind-set)",
    ),
    (
        "Commit che aggiunge unittest al gate pre-commit",
        ["test", "feat", "chore", "fix"],
        "commit-type (canone blind-set)",
    ),
    (
        "Un file in benchmark/runner/ della mappa residui va a quale bounded context?",
        ["Benchmark", "Observability & Retention", "System 1 (Laya)"],
        "bounded contexts HAL",
    ),
    (
        "Una modifica a laya_gate.py appartiene a quale contesto?",
        ["System 1 (Laya)", "Benchmark", "Observability & Retention"],
        "bounded contexts HAL",
    ),
    (
        "Un aggiornamento a docs/28_laya_model_card.md e' di quale dominio?",
        ["System 1 (Laya)", "Product docs", "Benchmark"],
        "HT-006/007",
    ),
    (
        "La richiesta e' triage di lead HubSpot con gate ICP: quale skill?",
        ["enrichment", "a-b2b", "a-product"],
        "skill integrate",
    ),
    (
        "Bisogna scrivere scenari Gherkin da JTBD seeds per l'handoff",
        ["gherkin", "jtbd", "a-product"],
        "skill integrate",
    ),
    (
        "Mappare unmet needs con intervista timeline e Four Forces",
        ["jtbd", "personas", "gherkin"],
        "skill integrate",
    ),
    (
        "Definire personas da PRD e verificare journey coherence",
        ["personas", "jtbd", "a-design"],
        "skill integrate",
    ),
    (
        "Scegliere il tipo di grafico per una serie temporale KPI",
        ["charts", "a-design", "uiux"],
        "skill integrate",
    ),
    (
        "Microcopy dell'explorer B2B score3 con pattern STRATEGY_GUIDE",
        ["b2b-explorer-ui-ux", "uiux", "a-copywriter"],
        "skill L2",
    ),
    (
        "Un task e' preliminare euristico: System 1 o System 2?",
        ["laya", "a-harness", "a-agentzero"],
        "architettura cognitiva AGENTS.md",
    ),
    (
        "Il PDF della liberatoria cliente va archiviato: che tipo di richiesta?",
        ["document", "todo", "review"],
        "comandi workspace",
    ),
    (
        "Revisionare il diff di una PR prima del merge",
        ["review", "improve", "commit"],
        "comandi workspace",
    ),
]

CHOICE_SEEDS: list[Seed] = [
    (
        "Prima del deploy degli agenti: dry-run di verifica o deploy diretto",
        ["report_prima", "deploy_diretto"],
        "/sync ? poi /sync !",
    ),
    (
        "Nuova feature AI senza set di valutazione: shippare o attendere baseline",
        ["attendere_baseline", "ship_subito"],
        "reject /impersonate karpathy (HT-005)",
    ),
    (
        "Il gate A/B mostra +85% token contro baseline: dismettere o ottimizzare",
        ["dismissione", "ottimizzare"],
        "HT-003/HT-009, run 20261109b",
    ),
    (
        "Slice con RED per modulo mancante: implementare il modulo o mockare il test",
        ["implementare", "mockare"],
        "RED HT-008 gold_set_scoring",
    ),
    (
        "Drift su file generato (changelog mirror): pin manuale o rigenerare",
        ["pin_manuale", "rigenerare"],
        "collaterale HT-008 (2f37faf)",
    ),
    (
        "Il task richiede due edit in aree non sovrapposte: un solo agente o delega parallela",
        ["unico_agente", "delega_parallela"],
        "multi-agent delegation",
    ),
    (
        "Laya chiede escalate_system2 su una decisione banale: deferire a System 2 o accettare il top",
        ["deferire_S2", "accettare_top"],
        "laya_gate recommendation",
    ),
    (
        "Un verdetto S1 era sbagliato: recordare outcome incorrect o ignorare",
        ["registrare_voto", "ignorare"],
        "laya_outcome calibration loop",
    ),
    (
        "Preparare un benchmark con GPU occupata: rimandare o run su CPU",
        ["rimandare", "run_cpu"],
        "laya_health VRAM",
    ),
    (
        "Il gold set ha label ambigua tra due opzioni: scegliere o astenersi",
        ["forzare_scelta", "astensione_documentata"],
        "noul abstain by design",
    ),
    (
        "Aggiungere una soglia duplicata in uno script o importare da laya_gate",
        ["importare_gate", "duplicare"],
        "fonte unica soglie HT-008",
    ),
    (
        "Il ToDo e' #human ma con estratto ciclabile: /cycle l'estratto o bloccare tutto",
        ["ciclo_extract", "blocco_umano"],
        "HT-008 estratto di HT-005",
    ),
    (
        "Serve un subagent per leggere 3 file indipendenti: spawn parallelo o lettura seriale",
        ["spawn_parallelo", "lettura_seriale"],
        "sub-agent design",
    ),
    (
        "Il file grande va letto tutto o solo la sezione con start/end line",
        ["lettura_targeted", "lettura_integra"],
        "regola tool read_file",
    ),
    (
        "La modifica tocca 5 file e il vincolo di slice e' 4: WAIVER o spezzare lo slice",
        ["waiver", "spezzare"],
        "work-graph rule (<=4 file o WAIVER)",
    ),
    (
        "Il prompt engine del benchmark va cambiato con la run in corso: in coda o subito",
        ["in_coda", "subito"],
        "sessioni parallele HT-004/HT-007",
    ),
    (
        "Il test esterno preesistente e' rosso: chiuderlo come collaterale o ignoralo",
        ["chiudere_collaterale", "ignorare"],
        "collaterale documentato HT-008",
    ),
    (
        "Nella scelta tra bracci con token zero su entrambi: dichiarare N/A o misurare comunque",
        ["dichiarare_NA", "misurare_comunque"],
        "kill criterion HT-003",
    ),
    (
        "Il commit contiene solo mirror rigenerati: commitato separato o insieme",
        ["separato", "insieme"],
        "convenzione CHANGELOG mirror",
    ),
    (
        "Il subagent deve solo leggere o anche scrivere file: lettura o lettura+edit",
        ["solo_lettura", "lettura_edit"],
        "disjoint write set",
    ),
    (
        "Il seed del gold set e reale o sintetico: ancorare al CHANGELOG o inventare",
        ["ancorare_reale", "sintetico"],
        "questo workbook",
    ),
    (
        "Con k>=4 Laya shortlist solo top-2: usare la shortlist o richiedere scelta piena",
        ["usa_shortlist", "richiedi_scelta"],
        "T-73140",
    ),
    (
        "Il margine e basso ma la scelta e banale: comunque S2 o diretta con cautela",
        ["comunque_S2", "diretta_cautela"],
        "laya_gate bands",
    ),
    (
        "Il ToDo HT-005 e umano: fare solo lo strumento o anche etichettare",
        ["solo_strumento", "etichetta_agent"],
        "HT-005 #human",
    ),
    (
        "La telemetria mostra 39% unclear zone: abbassare soglia o piu dati",
        ["abbassare_soglia", "piu_dati"],
        "laya_gate telemetry note",
    ),
    (
        "Il mirror symlink non risolve su CI: copia tracciata con guardia drift o niente mirror",
        ["copia_guardata", "niente_mirror"],
        "laya_gate mirror",
    ),
    (
        "Il refusal di un tool MCP per missing duckdb: degradare a stderr o errore duro",
        ["degradare", "errore_duro"],
        "events_parquet READ-ONLY",
    ),
    (
        "Il fixture sintetico basta per il contratto o serve traffico reale",
        ["fixture_ok", "traffico_reale"],
        "HT-008 vs HT-005",
    ),
    (
        "Il gate e pronto ma il dataset no: gate NOT-MEASURED o green silenzioso",
        ["not_measured", "green_silenzioso"],
        "blind-eval honesty",
    ),
    (
        "La label deve essere della singola opzione o della shortlist ordinata",
        ["opzione_unica", "shortlist"],
        "schema gold vs T-73140",
    ),
    (
        "Serve il voto di calibrazione per un verdetto cache-hit: votare o saltare",
        ["saltare_cache", "votare"],
        "laya_outcome cache skip",
    ),
]

SCORE_SEEDS: list[Seed] = [
    (
        "refactor del parser choice in router.py che tocca il fallback legacy",
        "rischio_regressione",
        "score 0-1 vs soglia gate",
    ),
    ("modifica puramente doc nel CHANGELOG mirror", "rischio_regressione", ""),
    ("cambio di threshold in laya_gate.py senza nuovi test", "rischio_regressione", ""),
    (
        "nuovo test file che aggiunge coperture senza toccare codice",
        "rischio_regressione",
        "",
    ),
    (
        "switch BENCHMARK_LOCAL_ASSEMBLY=0 nel workflow di run",
        "rischio_regressione",
        "HT-007 step-0",
    ),
    (
        "fix del bug di serializzazione LayaOutcome in router.py --json",
        "rischio_regressione",
        "",
    ),
    (
        "duplicazione di soglie di banda in uno script nuovo",
        "aderenza_architettura",
        "fonte unica soglie",
    ),
    (
        "uso di laya_choice per decidere un commit type",
        "aderenza_architettura",
        "regola S1 preliminare",
    ),
    (
        "il agente System 2 che decide senza consultare Laya su scelta discreta",
        "aderenza_architettura",
        "",
    ),
    (
        "etichette gold set generate da modello senza verifica umana",
        "validita_metodo",
        "HT-005 #human",
    ),
    ("run di regressione agganciata a make target esistente", "validita_metodo", ""),
    ("kill criterion dichiarato nel report history", "validita_metodo", ""),
    (
        "ricalibrazione soglie su traffico prod anziche oro etichettato",
        "validita_metodo",
        "",
    ),
    (
        "casi gold sintetici al posto di casi reali HAL",
        "rappresentativita_campione",
        "",
    ),
    ("200 casi per famiglia con label per 4 famiglie", "completezza_target", ""),
    ("gold set da 30 casi x famiglia", "completezza_target", ""),
    ("l'utente chiede fix the bug senza contesto", "chiarezza_contesto", ""),
    (
        "il task e' chiudere HT-005 con lo strumento e i seed documentati",
        "chiarezza_contesto",
        "",
    ),
    (
        "richiesta: prepara spreadsheet per HT-005 con schema gia pronto",
        "chiarezza_contesto",
        "",
    ),
    (
        "azienda IT di Lugano 18 dipendenti senza budget dichiarato",
        "aderenza_ICP",
        "b2b-explorer pilota",
    ),
    (
        "software house 40 dipendenti nel bacino Chiasso con budget attivo",
        "aderenza_ICP",
        "",
    ),
    ("agenzia marketing Milano 5 dipendenti fuori raggio 3h", "aderenza_ICP", ""),
    ("startup fintech Zurigo 60 dipendenti fuori ICP 6-50", "aderenza_ICP", ""),
    ("il diff aggiunge 2 righe e toglie un test", "prontezza_merge", ""),
    ("PR verde con CHANGELOG e ToDo aggiornati e gate a 0", "prontezza_merge", ""),
    ("run gated che vince 4/16 coppie con rubrica tie", "convinzione_esito", "HT-003"),
    (
        "esito negativo ex kill criterion con causa ereditata riverificata",
        "convinzione_esito",
        "",
    ),
    ("il report non contiene i numeri della run", "completezza_artefatto", ""),
    (
        "workbook con istruzioni, seed, copertura e label vuota",
        "completezza_artefatto",
        "",
    ),
    (
        "n=94 voti insufficiente per revocare eccezione top1",
        "sufficienza_dati",
        "telemetria gate",
    ),
]

NOUL_SEEDS: list[tuple[str, str]] = [
    (
        "il cliente vuole capire se il pilota B2B funziona ma non sa confrontare i dati",
        "pre-filtro: analisi vs enrichment",
    ),
    (
        "sincronizza gli agenti e poi controlla le versioni",
        "sequenza: deploy poi verify",
    ),
    (
        "il cliente vuole piu visibilita sul sito senza budget ne scadenze",
        "richiesta vaga: espandi o astieniti",
    ),
    ("normalizza: sistemiamo le robe del gateway", "normalizzazione richiesta vaga"),
    ("il cliente vuole che il copy suoni meno robotico", "pre-filtro: humanize"),
    ("aggiungi test al gold set scoring", "pre-filtro: QA/TDD"),
    (
        "il agente sbaglia sempre la scelta del modello, rivedi tutto",
        "richiesta con giudizio assoluto",
    ),
    ("esporta i lead da Apollo e filtrali per ICP", "pre-filtro: enrichment"),
    (
        "voglio sapere perche il benchmark e andato male ieri",
        "pre-filtro: analisi telemetria",
    ),
    ("crea un grafico delle conversioni settimanali", "pre-filtro: chart"),
    ("il cliente vuole vendere di piu con l AI", "vago: espandi"),
    ("dammi una mano col sito", "vago: astensione"),
    ("verifica se la soglia del gate va cambiata", "pre-filtro: calibration"),
    ("scrivi le FAQ della categoria caschi mtb", "pre-filtro: copy"),
    (
        "il agente product deve parlare con quello design, decidi tu",
        "handoff multi-agente",
    ),
    ("sistemiamo il deploy: prima la verifica o direttamente?", "decisione sequenza"),
    ("il run non parte, capisci", "errore vago"),
    ("ho un pdf di 300 pagine e mille domande", "pre-filtro: book-to-skill"),
    ("il lead non risponde da 3 settimane, va tenuto?", "pre-filtro: lead validation"),
    ("controlla se i mirror degli agenti puntano a posto", "pre-filtro: sync"),
    ("il cliente chiede una landing + blog + ads insieme", "scope detection"),
    ("devo capire se Laya e accesa o spenta", "health check"),
    ("il grafico e confuso, rifallo", "qualita visiva vaga"),
    ("l eval del gate e una sensazione o un numero?", "pre-filtro: eval rigor"),
    ("fai tutto tu e non rompermi niente", "vago + vincolo"),
    ("il run A e B dicono due cose opposte, quale credo", "decisione appaiata"),
    ("abbiamo 8000 chiamate ma non so cosa misurano", "telemetria vaga"),
    ("il cliente vuole il plugin wordpress ma anche l SEO e non so", "triage agente"),
    ("normalizza: fix the thing nel parser", "vago EN"),
    ("il prompt di scelta ha opzioni quasi uguali, quale?", "ambiguita S1"),
]

SEEDS: dict[str, list[Seed]] = {
    "routing": ROUTING_SEEDS,
    "choice": CHOICE_SEEDS,
    "score": SCORE_SEEDS,
    "noul": [(instruction, "", fonte) for instruction, fonte in NOUL_SEEDS],
}


def build_workbook(out_path: Path) -> dict[str, int]:
    wb = Workbook()

    # --- foglio Istruzioni ---------------------------------------------------
    ws = wb.active
    if (
        ws is None
    ):  # Workbook() nasce sempre con un foglio attivo; guardia per il tipe checker
        ws = wb.create_sheet()
    ws.title = "Istruzioni"
    header_font = Font(bold=True)
    wrap = Alignment(wrap_text=True, vertical="top")
    rows = [
        ("HT-005 — Etichettatura gold set System 1 (strumento umano)", True),
        ("", False),
        (
            "Obiettivo: ~200 casi per famiglia (choice/routing/score/noul) con LABEL UMANA, validati",
            False,
        ),
        (
            "da benchmark/config/gold_set.schema.json e misurati da scripts/gold_set_scoring.py (HT-008).",
            False,
        ),
        ("", False),
        ("REGOLE DEL FOGLIO 'GoldSet':", True),
        (
            "1. Ogni riga e un caso. id (già assegnati: c###/r###/s###/n###) e family NON si cambiano",
            False,
        ),
        (
            "   liberamente: se il caso reale non torna, correggere instruction/candidates, non l'id.",
            False,
        ),
        (
            "2. instruction: il testo passato a Laya (prompt/questo testo e la valutazione System 1).",
            False,
        ),
        (
            "3. candidates: opzioni separate da pipe |. Obbligatorio per choice/routing (>=2 opzioni);",
            False,
        ),
        (
            "   label DEVE essere una delle candidate. Sotto la soglia k>=4 System 1 shortlist solo",
            False,
        ),
        ("   top-2 (T-73140) ma la gold label resta una singola opzione.", False),
        (
            "4. criteria: obbligatorio per score. label = banda attesa {alto, medio, basso} (vedi sotto).",
            False,
        ),
        (
            "5. label: COLONNA UMANA. Compilarla solo per casi a cui si sicuri. La label e una stringa",
            False,
        ),
        ("   esatta dei candidates (o banda per score, o intent per noul).", False),
        (
            "6. fonte/note: da dove arriva il caso (CHANGELOG, ToDo, pratica reale). Rende l'oro difendibile.",
            False,
        ),
        ("", False),
        ("VOCABOLARIO PER FAMILIA:", True),
        (
            "- choice: label = una delle opzioni (es. report_prima). Prompt di decisione discreta.",
            False,
        ),
        (
            "- routing: label = una rotta (es. a-b2b, /sync, fix). Classificazione/instradamento.",
            False,
        ),
        (
            "- score: label = banda attesa {alto, medio, basso} rispetto a criteria; in pred.jsonl il",
            False,
        ),
        (
            "  punteggio numerico di Laya va mappato alla stessa banda (bucket dichiarato qui, non nel gate).",
            False,
        ),
        (
            "- noul: label = esito atteso del pre-filtro (intent-choice, routing, score, astensione...).",
            False,
        ),
        (
            "  Convenzione HAL: astensione documentata quando il testo non discriminante.",
            False,
        ),
        ("", False),
        ("PIPELINE DOPO L'ETICHETTATURA:", True),
        (
            "1. python3 benchmark/scripts/gold_set_xlsx_to_jsonl.py   # XLSX -> benchmark/gold_set/gold_set.jsonl",
            False,
        ),
        (
            "   (righe senza label saltate; ogni item validato con scripts/gold_set_scoring.py; exit 2 se oro invalido)",
            False,
        ),
        (
            '2. pred.jsonl: chiamare Laya per ogni caso (python3 /var/www/hal_system1/router.py <famiglia> "<instruction>"',
            False,
        ),
        (
            '   --options/--routes/--criteria --json) e scrivere righe {"id":..., "choice":..., "margin":...}.',
            False,
        ),
        (
            "3. python3 scripts/gold_set_scoring.py benchmark/gold_set/gold_set.jsonl benchmark/gold_set/pred.jsonl",
            False,
        ),
        (
            "   -> hit-rate + accuracy per fascia (direct>=0.5, caution>=0.15, escalate <0.15, soglie da laya_gate).",
            False,
        ),
        (
            "4. Acceptance HT-005: ricalibrare le soglie di laya_gate.py sul set e agganciare la regressione a una",
            False,
        ),
        ("   make target esistente (gate make test-unit).", False),
        ("", False),
        (
            "RIGENERARE QUESTO WORKBOOK (i seed restano, le label umane si perdono: esportare prima):",
            True,
        ),
        ("python3 benchmark/scripts/make_gold_set_workbook.py", False),
    ]
    for i, (text, bold) in enumerate(rows, start=1):
        cell = ws.cell(row=i, column=1, value=text)
        if bold:
            cell.font = header_font
        cell.alignment = wrap
    ws.column_dimensions["A"].width = 110

    # --- foglio GoldSet ------------------------------------------------------
    ws = wb.create_sheet("GoldSet")
    bold_fill = PatternFill("solid", fgColor="DDDDDD")
    label_fill = PatternFill("solid", fgColor="FFF2CC")
    for col, title in enumerate(HEADERS, start=1):
        cell = ws.cell(row=1, column=col, value=title)
        cell.font = Font(bold=True)
        cell.fill = bold_fill
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:G{TARGET_PER_FAMILY * len(FAMILIES) + 1}"

    dv_family = DataValidation(
        type="list", formula1='"' + ",".join(FAMILIES) + '"', allow_blank=False
    )
    ws.add_data_validation(dv_family)

    row = 2
    counts: dict[str, int] = {}
    for family in FAMILIES:
        seeds = SEEDS[family]
        for i in range(TARGET_PER_FAMILY):
            case_id = f"{PREFIX[family]}{i + 1:03d}"
            ws.cell(row=row, column=1, value=case_id)
            fam_cell = ws.cell(row=row, column=2, value=family)
            dv_family.add(fam_cell)
            if i < len(seeds):
                instruction, second, fonte = seeds[i]
                ws.cell(row=row, column=3, value=instruction).alignment = wrap
                if family in ("choice", "routing"):
                    candidates = second if isinstance(second, list) else []
                    ws.cell(
                        row=row, column=4, value=" | ".join(candidates)
                    ).alignment = wrap
                if family == "score":
                    ws.cell(
                        row=row,
                        column=5,
                        value=second if isinstance(second, str) else "",
                    )
                ws.cell(row=row, column=7, value=fonte).alignment = wrap
            lc = ws.cell(row=row, column=6)
            lc.fill = label_fill
            counts[family] = counts.get(family, 0) + 1
            row += 1

    widths = {1: 10, 2: 10, 3: 60, 4: 40, 5: 22, 6: 16, 7: 30}
    for col, width in widths.items():
        ws.column_dimensions[get_column_letter(col)].width = width

    # --- foglio Copertura ----------------------------------------------------
    ws = wb.create_sheet("Copertura")
    ws.cell(row=1, column=1, value="famiglia").font = Font(bold=True)
    ws.cell(row=1, column=2, value="casi").font = Font(bold=True)
    ws.cell(row=1, column=3, value="label complete").font = Font(bold=True)
    ws.cell(row=1, column=4, value="target").font = Font(bold=True)
    ws.cell(row=1, column=5, value="gap").font = Font(bold=True)
    total_seed = 0
    for r, family in enumerate(FAMILIES, start=2):
        ws.cell(row=r, column=1, value=family)
        ws.cell(row=r, column=2, value=f"=COUNTIF(GoldSet!$B:$B,A{r})")
        ws.cell(
            row=r, column=3, value=f'=COUNTIFS(GoldSet!$B:$B,A{r},GoldSet!$F:$F,"<>")'
        )
        ws.cell(row=r, column=4, value=TARGET_PER_FAMILY)
        ws.cell(row=r, column=5, value=f"=D{r}-C{r}")
        total_seed += len(SEEDS[family])
    ws.cell(row=6, column=1, value="totale").font = Font(bold=True)
    ws.cell(row=6, column=2, value="=SUM(B2:B5)")
    ws.cell(row=6, column=3, value="=SUM(C2:C5)")
    ws.cell(row=6, column=4, value=f"={TARGET_PER_FAMILY * len(FAMILIES)}")
    ws.cell(row=7, column=1, value="seed con contenuto")
    ws.cell(row=7, column=2, value=total_seed)
    ws.cell(
        row=8,
        column=1,
        value="NB: una label conta solo se la riga e completa (instruction, candidati, eventuale criteria);",
    )
    ws.cell(
        row=9,
        column=1,
        value="   il controllo duro e comunque gold_set_xlsx_to_jsonl.py con validate_gold_item.",
    )
    for col, width in {1: 22, 2: 10, 3: 16, 4: 10, 5: 8}.items():
        ws.column_dimensions[get_column_letter(col)].width = width

    out_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out_path)
    return counts


def main(argv: list[str]) -> int:
    out = Path(argv[0]) if argv else DEFAULT_OUT
    counts = build_workbook(out)
    print(f"scritto: {out}")
    print("righe per famiglia:", counts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
