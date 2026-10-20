#!/usr/bin/env python3
"""Genera report.htm con grafici D3.js dentro una cartella di run di benchmark.

Uso (dalla root di hal_system2):
  python3 scripts/generate_benchmark_report.py events/benchmarks/20261017_all
  python3 scripts/generate_benchmark_report.py events/benchmarks/20261017_2 --confronto events/benchmarks/20261017_all

Legge i *.json prodotti da app/benchmark_models.py e scrive report.htm nella stessa
cartella. I JSON che non sono una singola run (es. results.json) vengono ignorati.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import statistics
import sys
from datetime import UTC, datetime
from pathlib import Path

RUN_KEYS = {"model", "test_id", "status", "quality", "tokens", "seconds"}
OUTPUT_NAME = "report.htm"
D3_URL = "https://d3js.org/d3.v7.min.js"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def fmt_int(value: int | None) -> str:
    if value is None:
        return "n/d"
    return f"{value:,}".replace(",", ".")


def fmt_seconds(value: float) -> str:
    return f"{value:,.1f}".translate(str.maketrans({",": ".", ".": ","}))


def fmt_duration(seconds: float) -> str:
    hours, minutes = divmod(round(seconds / 60), 60)
    return f"{hours} h {minutes} min"


def load_runs(folder: Path) -> list[dict]:
    runs = []
    for path in sorted(folder.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not RUN_KEYS <= data.keys():
            continue
        quality = data["quality"] or {
            "passed": 0,
            "total": 0,
            "score": None,
            "checks": [],
        }
        runs.append(
            {
                "file": path.name,
                "model": data["model"],
                "test_id": data["test_id"],
                "status": data["status"],
                "passed": quality["passed"],
                "total": quality["total"],
                "score": quality["score"],
                "failed_checks": [
                    c["label"] for c in quality["checks"] if not c["passed"]
                ],
                "seconds": data["seconds"],
                "tokens": data["tokens"]["total"],
                "started_at": data.get("started_at"),
            }
        )
    return runs


def summarize_models(runs: list[dict]) -> list[dict]:
    by_model: dict[str, list[dict]] = {}
    for run in runs:
        by_model.setdefault(run["model"], []).append(run)

    models = []
    for model, items in by_model.items():
        scores = [r["score"] for r in items if r["score"] is not None]
        models.append(
            {
                "model": model,
                "runs": len(items),
                "score_mean": statistics.fmean(scores) if scores else None,
                "passed": sum(r["passed"] for r in items),
                "total": sum(r["total"] for r in items),
                "seconds_median": statistics.median([r["seconds"] for r in items]),
                "not_ok": sum(r["status"] != "ok" for r in items),
            }
        )
    return sorted(models, key=lambda m: (-(m["score_mean"] or 0), m["seconds_median"]))


def run_key(run: dict) -> tuple[str, str]:
    return run["model"], run["test_id"]


def mean_score(runs: list[dict]) -> float | None:
    scores = [r["score"] for r in runs if r["score"] is not None]
    return statistics.fmean(scores) if scores else None


def build_comparison(
    runs: list[dict], baseline_name: str, baseline_runs: list[dict]
) -> dict:
    previous = {run_key(r): r for r in baseline_runs}
    current_keys = {run_key(r) for r in runs}
    pairs = []
    for run in runs:
        prev = previous.get(run_key(run))
        if prev is None:
            continue
        delta = None
        if run["score"] is not None and prev["score"] is not None:
            delta = run["score"] - prev["score"]
        pairs.append(
            {
                "file": run["file"],
                "model": run["model"],
                "test_id": run["test_id"],
                "prev_passed": prev["passed"],
                "prev_total": prev["total"],
                "curr_passed": run["passed"],
                "curr_total": run["total"],
                "delta": delta,
                "prev_status": prev["status"],
                "curr_status": run["status"],
                "prev_seconds": prev["seconds"],
                "curr_seconds": run["seconds"],
            }
        )

    previous_models = {m["model"]: m for m in summarize_models(baseline_runs)}
    models = []
    for m in summarize_models(runs):
        p = previous_models.get(m["model"])
        if p is None:
            continue
        models.append(
            {
                "model": m["model"],
                "score_prev": p["score_mean"],
                "score_curr": m["score_mean"],
                "seconds_prev": p["seconds_median"],
                "seconds_curr": m["seconds_median"],
            }
        )

    previous_keys = set(previous)
    return {
        "baseline": baseline_name,
        "summary": {
            "runs_prev": len(baseline_runs),
            "runs_curr": len(runs),
            "score_prev": mean_score(baseline_runs),
            "score_curr": mean_score(runs),
            "not_ok_prev": sum(r["status"] != "ok" for r in baseline_runs),
            "not_ok_curr": sum(r["status"] != "ok" for r in runs),
            "seconds_prev": sum(r["seconds"] for r in baseline_runs),
            "seconds_curr": sum(r["seconds"] for r in runs),
        },
        "models": models,
        "pairs": pairs,
        "unmatched_current": sum(run_key(r) not in previous_keys for r in runs),
        "unmatched_previous": sum(
            run_key(r) not in current_keys for r in baseline_runs
        ),
    }


def build_payload(
    folder_name: str,
    runs: list[dict],
    baseline: tuple[str, list[dict]] | None = None,
) -> dict:
    test_ids: list[str] = []
    for run in runs:
        if run["test_id"] not in test_ids:
            test_ids.append(run["test_id"])

    started = sorted(r["started_at"] for r in runs if r["started_at"])
    tokens = [r["tokens"] for r in runs if r["tokens"] is not None]
    summary = {
        "runs": len(runs),
        "models": len({r["model"] for r in runs}),
        "tests": len(test_ids),
        "ok": sum(r["status"] == "ok" for r in runs),
        "not_ok": sum(r["status"] != "ok" for r in runs),
        "truncated": sum(r["status"] == "truncated" for r in runs),
        "seconds": sum(r["seconds"] for r in runs),
        "tokens": sum(tokens),
        "first_started": started[0] if started else None,
        "last_started": started[-1] if started else None,
    }
    return {
        "folder": folder_name,
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "summary": summary,
        "models": summarize_models(runs),
        "tests": [{"id": t, "label": t.replace("_", " ")} for t in test_ids],
        "runs": runs,
        "comparison": build_comparison(runs, *baseline) if baseline else None,
    }


def render_summary(summary: dict) -> str:
    cards = [
        ("Run", fmt_int(summary["runs"])),
        ("Modelli", fmt_int(summary["models"])),
        ("Test", fmt_int(summary["tests"])),
        ("Non ok (troncate o errore)", fmt_int(summary["not_ok"])),
        ("Token totali", fmt_int(summary["tokens"])),
        ("Tempo totale", fmt_duration(summary["seconds"])),
    ]
    items = "".join(
        f'<div class="card"><b>{esc(value)}</b><span>{esc(label)}</span></div>'
        for label, value in cards
    )
    return f'<div class="cards">{items}</div>'


def render_period(summary: dict) -> str:
    first, last = summary["first_started"], summary["last_started"]
    if not first:
        return ""
    return f"Run del {esc(first[:10])}" + (
        f" al {esc(last[:10])}" if last[:10] != first[:10] else ""
    )


def render_table(runs: list[dict]) -> str:
    rows = []
    for run in runs:
        failed = run["failed_checks"]
        if failed:
            items = "".join(f"<li>{esc(label)}</li>" for label in failed)
            failed_cell = f"<details><summary>{len(failed)} non superati</summary><ul>{items}</ul></details>"
        else:
            failed_cell = "—"
        rows.append(
            "<tr>"
            f'<td><a href="{esc(run["file"])}">{esc(run["file"])}</a></td>'
            f"<td>{esc(run['model'])}</td>"
            f"<td>{esc(run['test_id'])}</td>"
            f"<td>{esc(run['status'])}</td>"
            f"<td>{run['passed']}/{run['total']}</td>"
            f"<td>{fmt_seconds(run['seconds'])}</td>"
            f"<td>{fmt_int(run['tokens'])}</td>"
            f"<td>{failed_cell}</td>"
            "</tr>"
        )
    headers = [
        "File",
        "Modello",
        "Test",
        "Stato",
        "Check superati",
        "Secondi",
        "Token",
        "Check non superati",
    ]
    head = "".join(f'<th scope="col">{h}</th>' for h in headers)
    return (
        f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(rows)}</tbody></table>"
    )


def fmt_pp(delta: float | None) -> str:
    if delta is None:
        return "n/d"
    points = round(delta * 100)
    if points == 0:
        return "±0 pp"
    return f"{'+' if points > 0 else '−'}{abs(points)} pp"


def fmt_pct(value: float | None) -> str:
    return "n/d" if value is None else f"{round(value * 100)}%"


def render_changes_table(pairs: list[dict]) -> str:
    changed = [
        p for p in pairs if p["delta"] != 0 or p["prev_status"] != p["curr_status"]
    ]
    if not changed:
        return f'<p class="note">Nessuna variazione di punteggio o stato tra le {fmt_int(len(pairs))} run abbinate.</p>'
    rows = [
        "<tr>"
        f"<td>{esc(p['file'])}</td>"
        f"<td>{esc(p['model'])}</td>"
        f"<td>{esc(p['test_id'])}</td>"
        f"<td>{p['prev_passed']}/{p['prev_total']} → {p['curr_passed']}/{p['curr_total']}</td>"
        f"<td>{esc(fmt_pp(p['delta']))}</td>"
        f"<td>{esc(p['prev_status'])} → {esc(p['curr_status'])}</td>"
        f"<td>{fmt_seconds(p['prev_seconds'])} → {fmt_seconds(p['curr_seconds'])}</td>"
        "</tr>"
        for p in changed
    ]
    headers = [
        "File",
        "Modello",
        "Test",
        "Check superati",
        "Variazione",
        "Stato",
        "Secondi",
    ]
    head = "".join(f'<th scope="col">{h}</th>' for h in headers)
    note = f'<p class="note">{fmt_int(len(pairs) - len(changed))} run invariate non elencate.</p>'
    return (
        note
        + f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(rows)}</tbody></table>"
    )


def render_comparison(comparison: dict | None) -> str:
    if not comparison:
        return ""
    s = comparison["summary"]
    cards = [
        (
            "Score medio, tutte le run",
            f"{fmt_pct(s['score_prev'])} → {fmt_pct(s['score_curr'])}",
        ),
        ("Run non ok", f"{fmt_int(s['not_ok_prev'])} → {fmt_int(s['not_ok_curr'])}"),
        (
            "Tempo totale",
            f"{fmt_duration(s['seconds_prev'])} → {fmt_duration(s['seconds_curr'])}",
        ),
        ("Run abbinate", fmt_int(len(comparison["pairs"]))),
    ]
    items = "".join(
        f'<div class="card"><b>{esc(value)}</b><span>{esc(label)}</span></div>'
        for label, value in cards
    )
    unmatched = (
        f"Non abbinate: {fmt_int(comparison['unmatched_current'])} nel report corrente, "
        f"{fmt_int(comparison['unmatched_previous'])} nel precedente."
    )
    header = (
        f"<section><h2>Confronto con {esc(comparison['baseline'])}</h2>"
        f'<p class="lead">Run abbinate per modello e test. {esc(unmatched)}</p>'
        f'<div class="cards">{items}</div></section>'
    )
    charts = [
        (
            "Il punteggio è migliorato?",
            "chart-compare-score",
            "Due pallini per modello: grigio il benchmark precedente, blu quello attuale. L'etichetta riporta la variazione in punti percentuali.",
        ),
        (
            "Dove cambia il punteggio?",
            "chart-delta-heatmap",
            "Ogni cella confronta la stessa coppia modello-test. Blu: più check superati; rosso: meno. Sotto la variazione: check superati prima → adesso.",
        ),
        (
            "Il tempo è cambiato?",
            "chart-compare-time",
            "Tempo mediano per modello, scala logaritmica. Grigio: precedente; blu: attuale.",
        ),
    ]
    sections = "".join(
        f"<section><h2>{esc(title)}</h2><figure><figcaption>{esc(caption)}</figcaption>"
        f'<div id="{chart_id}"></div></figure></section>'
        for title, chart_id, caption in charts
    )
    changes = f"<section><h2>Run che cambiano</h2>{render_changes_table(comparison['pairs'])}</section>"
    return header + sections + changes


def render_report(payload: dict, synthesis: str = "") -> str:
    # Single pass: values are never re-scanned for placeholders.
    values = {
        "TITLE": esc(f"Benchmark {payload['folder']}"),
        "PERIOD": render_period(payload["summary"]),
        "SYNTHESIS": synthesis,
        "SUMMARY": render_summary(payload["summary"]),
        "TABLE": render_table(payload["runs"]),
        "COMPARE": render_comparison(payload["comparison"]),
        "D3_URL": esc(D3_URL),
        "DATA": json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c"),
    }
    return re.sub(r"@@([A-Z0-9_]+)@@", lambda m: values[m.group(1)], TEMPLATE)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog=Path(argv[0]).name,
        description="Genera report.htm con grafici D3.js per una cartella di run di benchmark.",
    )
    parser.add_argument("folder", type=Path, help="cartella con le run JSON")
    parser.add_argument(
        "--confronto",
        type=Path,
        metavar="CARTELLA",
        help="cartella di un benchmark precedente da confrontare",
    )
    parser.add_argument(
        "--sintesi",
        type=Path,
        metavar="FILE_HTML",
        help="frammento HTML (file locale fidato) inserito in testa al report come executive summary",
    )
    args = parser.parse_args(argv[1:])

    folder = args.folder
    if not folder.is_dir():
        print(f"Cartella non trovata: {folder}", file=sys.stderr)
        return 1
    runs = load_runs(folder)
    if not runs:
        print(f"Nessuna run JSON in {folder}", file=sys.stderr)
        return 1

    baseline = None
    if args.confronto is not None:
        if not args.confronto.is_dir():
            print(
                f"Cartella di confronto non trovata: {args.confronto}", file=sys.stderr
            )
            return 1
        baseline_runs = load_runs(args.confronto)
        if not baseline_runs:
            print(f"Nessuna run JSON in {args.confronto}", file=sys.stderr)
            return 1
        baseline = (args.confronto.resolve().name, baseline_runs)

    synthesis = ""
    if args.sintesi is not None:
        if not args.sintesi.is_file():
            print(f"File di sintesi non trovato: {args.sintesi}", file=sys.stderr)
            return 1
        synthesis = args.sintesi.read_text(encoding="utf-8")

    payload = build_payload(folder.resolve().name, runs, baseline)
    output = folder / OUTPUT_NAME
    output.write_text(render_report(payload, synthesis), encoding="utf-8")
    print(f"Report generato: {output} ({len(runs)} run)")
    return 0


TEMPLATE = """<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>@@TITLE@@</title>
<style>
  :root { --ink: #1f2933; --muted: #52606d; --line: #d9e2ec; --accent: #2f6fb0; }
  body { font-family: system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif; color: var(--ink);
         max-width: 960px; margin: 0 auto; padding: 24px; line-height: 1.5; }
  h1 { font-size: 1.6rem; margin: 0 0 4px; }
  h2 { font-size: 1.2rem; margin: 40px 0 4px; }
  .lead, .note, figcaption { color: var(--muted); font-size: .92rem; }
  figure { margin: 0; }
  figcaption { margin-bottom: 8px; }
  .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin: 20px 0; }
  .card { border: 1px solid var(--line); border-radius: 8px; padding: 10px 12px; }
  .card b { display: block; font-size: 1.3rem; }
  .card span { color: var(--muted); font-size: .85rem; }
  svg { width: 100%; height: auto; display: block; font-size: 13px; color: var(--ink); fill: var(--ink); }
  table { border-collapse: collapse; width: 100%; font-size: .88rem; }
  th, td { border-bottom: 1px solid var(--line); padding: 6px 8px; text-align: left; vertical-align: top; }
  th { background: #f5f7fa; }
  details summary { cursor: pointer; color: var(--accent); }
  details ul { margin: 6px 0 0; padding-left: 18px; }
</style>
</head>
<body>
<header>
  <h1>@@TITLE@@</h1>
  <p class="lead">@@PERIOD@@</p>
</header>
@@SYNTHESIS@@
@@SUMMARY@@
@@COMPARE@@
<section>
  <h2>Quale modello è più accurato?</h2>
  <figure>
    <figcaption>Score medio per modello: media dei punteggi dei test, ciascuno con lo stesso peso. Accanto a ogni barra, i check superati sul totale.</figcaption>
    <div id="chart-score"></div>
  </figure>
</section>
<section>
  <h2>Dove falliscono i modelli?</h2>
  <figure>
    <figcaption>Check superati per run. «truncated» indica una risposta interrotta al limite di generazione: il punteggio si riferisce al testo parziale.</figcaption>
    <div id="chart-heatmap"></div>
  </figure>
</section>
<section>
  <h2>Qualità contro tempo</h2>
  <figure>
    <figcaption>Un punto per modello: in alto a sinistra = più accurato e più veloce. Tempo mediano per run, scala logaritmica.</figcaption>
    <div id="chart-scatter"></div>
  </figure>
</section>
<section>
  <h2>Dettaglio run</h2>
  <p class="note">Tempi end-to-end della chiamata, incluso il caricamento del modello (timing del runner).</p>
  @@TABLE@@
</section>
<script type="application/json" id="bench-data">@@DATA@@</script>
<script src="@@D3_URL@@"></script>
<script>
const DATA = JSON.parse(document.getElementById('bench-data').textContent);
const IT = d3.formatLocale({decimal: ',', thousands: '.', grouping: [3], currency: ['', ''], percent: '%'});
const pct = d => IT.format('.0%')(d);
const secs = s => IT.format(',.1f')(s) + ' s';
const ACCENT = '#2f6fb0';
const GRID = '#d9e2ec';
const INK = '#1f2933';

function svgFor(id, width, height, label) {
  return d3.select('#' + id).append('svg')
    .attr('viewBox', `0 0 ${width} ${height}`)
    .attr('role', 'img')
    .attr('aria-label', label);
}

function contrastText(bg) {
  const lum = c => {
    const v = d3.rgb(c);
    const f = x => { x /= 255; return x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(v.r) + 0.7152 * f(v.g) + 0.0722 * f(v.b);
  };
  const L = lum(bg);
  const white = 1.05 / (L + 0.05);
  const ink = (L + 0.05) / (lum(INK) + 0.05);
  return white >= ink ? '#ffffff' : INK;
}

function chartScore() {
  const rows = DATA.models.filter(d => d.score_mean !== null);
  const W = 760, rowH = 36, m = {top: 8, right: 170, bottom: 34, left: 170};
  const ih = rows.length * rowH, iw = W - m.left - m.right;
  const svg = svgFor('chart-score', W, ih + m.top + m.bottom, 'Barre: score medio per modello');
  const g = svg.append('g').attr('transform', `translate(${m.left},${m.top})`);
  const x = d3.scaleLinear().domain([0, 1]).range([0, iw]);
  const y = d3.scaleBand().domain(rows.map(d => d.model)).range([0, ih]).padding(0.28);

  g.append('g').attr('transform', `translate(0,${ih})`)
    .call(d3.axisBottom(x).ticks(5).tickFormat(pct).tickSize(-ih))
    .call(a => { a.select('.domain').remove(); a.selectAll('.tick line').attr('stroke', GRID); });
  g.append('g').call(d3.axisLeft(y).tickSize(0)).call(a => a.select('.domain').remove());

  g.selectAll('rect.bar').data(rows).join('rect')
    .attr('class', 'bar')
    .attr('x', 0)
    .attr('y', d => y(d.model))
    .attr('width', d => x(d.score_mean))
    .attr('height', y.bandwidth())
    .attr('fill', ACCENT)
    .append('title')
    .text(d => `${d.model}: ${pct(d.score_mean)} (${d.passed}/${d.total} check), tempo mediano ${secs(d.seconds_median)}`);

  g.selectAll('text.value').data(rows).join('text')
    .attr('x', d => x(d.score_mean) + 6)
    .attr('y', d => y(d.model) + y.bandwidth() / 2)
    .attr('dominant-baseline', 'middle')
    .text(d => `${pct(d.score_mean)} · ${d.passed}/${d.total} check`);
}

function chartHeatmap() {
  const models = DATA.models.map(d => d.model);
  const tests = DATA.tests;
  const runs = new Map(DATA.runs.map(r => [r.model + '|' + r.test_id, r]));
  const cw = 128, ch = 50, left = 150, top = 52, legendH = 90;
  const W = left + tests.length * cw + 12, H = top + models.length * ch + legendH;
  const svg = svgFor('chart-heatmap', W, H, 'Mappa di calore: check superati per modello e test');
  const color = d3.scaleSequential(d3.interpolateViridis).domain([0, 1]);

  svg.selectAll('text.col').data(tests).join('text')
    .attr('x', (d, j) => left + j * cw + cw / 2)
    .attr('y', top - 14)
    .attr('text-anchor', 'middle')
    .text(d => d.label);

  svg.selectAll('text.row').data(models).join('text')
    .attr('x', left - 10)
    .attr('y', (d, i) => top + i * ch + ch / 2)
    .attr('text-anchor', 'end')
    .attr('dominant-baseline', 'middle')
    .text(d => d);

  const cells = models.flatMap((model, i) => tests.map((t, j) => ({
    model, i, j, test: t.label, run: runs.get(model + '|' + t.id),
  })));
  const cell = svg.selectAll('g.cell').data(cells).join('g')
    .attr('class', 'cell')
    .attr('transform', d => `translate(${left + d.j * cw},${top + d.i * ch})`);

  const fill = d => (d.run && d.run.score !== null) ? color(d.run.score) : '#e4e7eb';
  cell.append('rect')
    .attr('x', 2).attr('y', 2).attr('width', cw - 4).attr('height', ch - 4).attr('rx', 4)
    .attr('fill', fill);
  cell.append('text')
    .attr('x', cw / 2).attr('y', ch / 2 - 3).attr('text-anchor', 'middle')
    .attr('fill', d => contrastText(fill(d)))
    .text(d => d.run ? `${d.run.passed}/${d.run.total}` : 'n/d');
  cell.append('text')
    .attr('x', cw / 2).attr('y', ch / 2 + 12).attr('text-anchor', 'middle').attr('font-size', 11)
    .attr('fill', d => contrastText(fill(d)))
    .text(d => d.run && d.run.status !== 'ok' ? d.run.status : '');
  cell.append('title')
    .text(d => d.run ? `${d.model} · ${d.test}: ${d.run.passed}/${d.run.total} check, ${secs(d.run.seconds)}, ${d.run.status}` : `${d.model} · ${d.test}: nessun dato`);

  const grad = svg.append('defs').append('linearGradient').attr('id', 'heat-grad');
  d3.range(0, 1.0001, 0.1).forEach(t => grad.append('stop')
    .attr('offset', `${t * 100}%`).attr('stop-color', d3.interpolateViridis(t)));
  const lx = left, lw = 260, ly = H - legendH + 30;
  svg.append('rect').attr('x', lx).attr('y', ly).attr('width', lw).attr('height', 12)
    .attr('fill', 'url(#heat-grad)');
  [0, 0.5, 1].forEach(t => svg.append('text')
    .attr('x', lx + t * lw).attr('y', ly + 28).attr('text-anchor', t === 0 ? 'start' : t === 1 ? 'end' : 'middle')
    .text(pct(t)));
  svg.append('text').attr('x', lx + lw + 12).attr('y', ly + 11).attr('dominant-baseline', 'middle')
    .text('quota di check superati');
  if (cells.some(c => !c.run)) {
    svg.append('text').attr('x', lx).attr('y', ly - 10).attr('fill', INK)
      .text('Grigio: nessun dato');
  }
}

function chartScatter() {
  const pts = DATA.models.filter(d => d.score_mean !== null);
  const W = 760, H = 420, m = {top: 16, right: 36, bottom: 56, left: 64};
  const iw = W - m.left - m.right, ih = H - m.top - m.bottom;
  const svg = svgFor('chart-scatter', W, H, 'Dispersione: score medio contro tempo mediano per modello');
  const g = svg.append('g').attr('transform', `translate(${m.left},${m.top})`);

  const seconds = DATA.runs.map(r => r.seconds).filter(s => s > 0);
  const lo = Math.pow(10, Math.floor(Math.log10(Math.min(...seconds))));
  const hi = Math.pow(10, Math.ceil(Math.log10(Math.max(...seconds))));
  const x = d3.scaleLog().domain([lo, hi]).range([0, iw]);
  const y = d3.scaleLinear().domain([0, 1]).range([ih, 0]);

  g.append('g').attr('transform', `translate(0,${ih})`)
    .call(d3.axisBottom(x).tickValues([10, 100, 1000, 10000].filter(v => v >= lo && v <= hi)).tickFormat(IT.format(',.0f')))
    .call(a => a.select('.domain').attr('stroke', INK));
  g.append('g')
    .call(d3.axisLeft(y).ticks(5).tickFormat(pct).tickSize(-iw))
    .call(a => { a.select('.domain').remove(); a.selectAll('.tick line').attr('stroke', GRID); });

  g.append('text').attr('x', iw / 2).attr('y', ih + 44).attr('text-anchor', 'middle')
    .attr('fill', '#52606d').text('Tempo mediano per run (secondi, scala logaritmica)');
  g.append('text').attr('transform', 'rotate(-90)').attr('x', -ih / 2).attr('y', -46)
    .attr('text-anchor', 'middle').attr('fill', '#52606d').text('Score medio');

  const points = pts.map(d => ({d, px: x(d.seconds_median), py: y(d.score_mean)}))
    .sort((a, b) => a.px - b.px);
  const obstacles = points.map(p => ({x0: p.px - 7, x1: p.px + 7, y0: p.py - 7, y1: p.py + 7}));
  const overlaps = (a, b) => a.x0 < b.x1 && b.x0 < a.x1 && a.y0 < b.y1 && b.y0 < a.y1;
  const labels = points.map(p => {
    const w = p.d.model.length * 7.2;
    const lx = p.px + 9;
    const boxAt = ly => ({x0: lx, x1: lx + w, y0: ly - 10, y1: ly + 3});
    const ly = [p.py + 4, p.py + 18, p.py - 10, p.py + 32, p.py - 24]
      .find(v => obstacles.every(o => !overlaps(boxAt(v), o))) ?? p.py + 4;
    obstacles.push(boxAt(ly));
    return {...p, w, lx, ly};
  });

  g.selectAll('line.leader').data(labels.filter(l => l.ly !== l.py + 4)).join('line')
    .attr('x1', l => l.px).attr('y1', l => l.py).attr('x2', l => l.lx - 3).attr('y2', l => l.ly - 4)
    .attr('stroke', '#52606d').attr('stroke-width', 0.8);

  const point = g.selectAll('g.point').data(points).join('g')
    .attr('class', 'point')
    .attr('transform', p => `translate(${p.px},${p.py})`);
  point.append('circle').attr('r', 6).attr('fill', ACCENT).attr('stroke', '#ffffff').attr('stroke-width', 1.5);
  point.append('title')
    .text(p => `${p.d.model}: ${pct(p.d.score_mean)}, tempo mediano ${secs(p.d.seconds_median)}, ${p.d.not_ok} non ok`);

  g.selectAll('text.point-label').data(labels).join('text')
    .attr('class', 'point-label')
    .attr('x', l => l.lx).attr('y', l => l.ly)
    .text(l => l.d.model);
}

const PREV = '#9aa5b1';

function signedPp(v) {
  if (v === null) return 'n/d';
  const pts = Math.round(v * 100);
  if (pts === 0) return '±0 pp';
  return (pts > 0 ? '+' : '−') + Math.abs(pts) + ' pp';
}

function compareLegend(svg, x0, y0) {
  [['precedente', PREV], ['attuale', ACCENT]].forEach(([label, color], i) => {
    const gx = x0 + i * 130;
    svg.append('circle').attr('cx', gx).attr('cy', y0).attr('r', 6).attr('fill', color);
    svg.append('text').attr('x', gx + 12).attr('y', y0).attr('dominant-baseline', 'middle').text(label);
  });
}

function chartCompareScore() {
  const rows = DATA.comparison.models.filter(d => d.score_prev !== null && d.score_curr !== null);
  const W = 760, rowH = 40, m = {top: 34, right: 190, bottom: 34, left: 170};
  const ih = rows.length * rowH, iw = W - m.left - m.right;
  const svg = svgFor('chart-compare-score', W, ih + m.top + m.bottom, 'Confronto: score medio per modello, precedente e attuale');
  compareLegend(svg, m.left, 14);
  const g = svg.append('g').attr('transform', `translate(${m.left},${m.top})`);
  const x = d3.scaleLinear().domain([0, 1]).range([0, iw]);
  const y = d3.scaleBand().domain(rows.map(d => d.model)).range([0, ih]).padding(0.35);
  const cy = d => y(d.model) + y.bandwidth() / 2;

  g.append('g').attr('transform', `translate(0,${ih})`)
    .call(d3.axisBottom(x).ticks(5).tickFormat(pct).tickSize(-ih))
    .call(a => { a.select('.domain').remove(); a.selectAll('.tick line').attr('stroke', GRID); });
  g.append('g').call(d3.axisLeft(y).tickSize(0)).call(a => a.select('.domain').remove());

  g.selectAll('line.link').data(rows).join('line')
    .attr('x1', d => x(d.score_prev)).attr('x2', d => x(d.score_curr))
    .attr('y1', cy).attr('y2', cy).attr('stroke', '#b8c2cc').attr('stroke-width', 3);
  g.selectAll('circle.prev').data(rows).join('circle')
    .attr('cx', d => x(d.score_prev)).attr('cy', cy).attr('r', 6).attr('fill', PREV);
  g.selectAll('circle.curr').data(rows).join('circle')
    .attr('cx', d => x(d.score_curr)).attr('cy', cy).attr('r', 6).attr('fill', ACCENT);
  g.selectAll('text.delta').data(rows).join('text')
    .attr('x', iw + 12).attr('y', cy).attr('dominant-baseline', 'middle')
    .text(d => `${pct(d.score_prev)} → ${pct(d.score_curr)} · ${signedPp(d.score_curr - d.score_prev)}`);
}

function chartCompareTime() {
  const rows = DATA.comparison.models;
  const all = rows.flatMap(d => [d.seconds_prev, d.seconds_curr]).filter(s => s > 0);
  const W = 760, rowH = 40, m = {top: 34, right: 190, bottom: 56, left: 170};
  const ih = rows.length * rowH, iw = W - m.left - m.right;
  const svg = svgFor('chart-compare-time', W, ih + m.top + m.bottom, 'Confronto: tempo mediano per modello, precedente e attuale');
  compareLegend(svg, m.left, 14);
  const g = svg.append('g').attr('transform', `translate(${m.left},${m.top})`);
  const lo = Math.pow(10, Math.floor(Math.log10(Math.min(...all))));
  const hi = Math.pow(10, Math.ceil(Math.log10(Math.max(...all))));
  const x = d3.scaleLog().domain([lo, hi]).range([0, iw]);
  const y = d3.scaleBand().domain(rows.map(d => d.model)).range([0, ih]).padding(0.35);
  const cy = d => y(d.model) + y.bandwidth() / 2;

  g.append('g').attr('transform', `translate(0,${ih})`)
    .call(d3.axisBottom(x).tickValues([10, 100, 1000, 10000].filter(v => v >= lo && v <= hi)).tickFormat(IT.format(',.0f')))
    .call(a => a.select('.domain').attr('stroke', INK));
  g.append('g').call(d3.axisLeft(y).tickSize(0)).call(a => a.select('.domain').remove());
  g.append('text').attr('x', iw / 2).attr('y', ih + 44).attr('text-anchor', 'middle')
    .attr('fill', '#52606d').text('Tempo mediano per run (secondi, scala logaritmica)');

  g.selectAll('line.link').data(rows).join('line')
    .attr('x1', d => x(d.seconds_prev)).attr('x2', d => x(d.seconds_curr))
    .attr('y1', cy).attr('y2', cy).attr('stroke', '#b8c2cc').attr('stroke-width', 3);
  g.selectAll('circle.prev').data(rows).join('circle')
    .attr('cx', d => x(d.seconds_prev)).attr('cy', cy).attr('r', 6).attr('fill', PREV);
  g.selectAll('circle.curr').data(rows).join('circle')
    .attr('cx', d => x(d.seconds_curr)).attr('cy', cy).attr('r', 6).attr('fill', ACCENT);
  g.selectAll('text.delta').data(rows).join('text')
    .attr('x', iw + 12).attr('y', cy).attr('dominant-baseline', 'middle')
    .text(d => `${secs(d.seconds_prev)} → ${secs(d.seconds_curr)}`);
}

function chartDeltaHeatmap() {
  const models = DATA.comparison.models.map(d => d.model);
  const tests = DATA.tests;
  const pairs = new Map(DATA.comparison.pairs.map(p => [p.model + '|' + p.test_id, p]));
  const cw = 128, ch = 50, left = 150, top = 52, legendH = 90;
  const W = left + tests.length * cw + 12, H = top + models.length * ch + legendH;
  const svg = svgFor('chart-delta-heatmap', W, H, 'Mappa di calore: variazione del punteggio per modello e test');
  const color = d3.scaleDiverging(d3.interpolateRdBu).domain([-1, 0, 1]);

  svg.selectAll('text.col').data(tests).join('text')
    .attr('x', (d, j) => left + j * cw + cw / 2)
    .attr('y', top - 14)
    .attr('text-anchor', 'middle')
    .text(d => d.label);
  svg.selectAll('text.row').data(models).join('text')
    .attr('x', left - 10)
    .attr('y', (d, i) => top + i * ch + ch / 2)
    .attr('text-anchor', 'end')
    .attr('dominant-baseline', 'middle')
    .text(d => d);

  const cells = models.flatMap((model, i) => tests.map((t, j) => ({
    model, i, j, test: t.label, pair: pairs.get(model + '|' + t.id),
  })));
  const cell = svg.selectAll('g.cell').data(cells).join('g')
    .attr('class', 'cell')
    .attr('transform', d => `translate(${left + d.j * cw},${top + d.i * ch})`);

  const hasDelta = d => d.pair && d.pair.delta !== null;
  const fill = d => hasDelta(d) ? color(d.pair.delta) : '#e4e7eb';
  cell.append('rect')
    .attr('x', 2).attr('y', 2).attr('width', cw - 4).attr('height', ch - 4).attr('rx', 4)
    .attr('fill', fill);
  cell.append('text')
    .attr('x', cw / 2).attr('y', ch / 2 - 3).attr('text-anchor', 'middle')
    .attr('fill', d => contrastText(fill(d)))
    .text(d => hasDelta(d) ? signedPp(d.pair.delta) : 'n/d');
  cell.append('text')
    .attr('x', cw / 2).attr('y', ch / 2 + 12).attr('text-anchor', 'middle').attr('font-size', 11)
    .attr('fill', d => contrastText(fill(d)))
    .text(d => d.pair ? `${d.pair.prev_passed}/${d.pair.prev_total} → ${d.pair.curr_passed}/${d.pair.curr_total}` : '');
  cell.append('title')
    .text(d => d.pair
      ? `${d.model} · ${d.test}: ${d.pair.prev_passed}/${d.pair.prev_total} → ${d.pair.curr_passed}/${d.pair.curr_total} check, ${d.pair.prev_status} → ${d.pair.curr_status}`
      : `${d.model} · ${d.test}: nessun dato`);

  const grad = svg.append('defs').append('linearGradient').attr('id', 'delta-grad');
  d3.range(0, 1.0001, 0.1).forEach(t => grad.append('stop')
    .attr('offset', `${t * 100}%`).attr('stop-color', d3.interpolateRdBu(t)));
  const lx = left, lw = 260, ly = H - legendH + 30;
  svg.append('rect').attr('x', lx).attr('y', ly).attr('width', lw).attr('height', 12)
    .attr('fill', 'url(#delta-grad)');
  [['−100 pp', 0, 'start'], ['±0', 0.5, 'middle'], ['+100 pp', 1, 'end']].forEach(([label, t, anchor]) => svg.append('text')
    .attr('x', lx + t * lw).attr('y', ly + 28).attr('text-anchor', anchor).text(label));
  svg.append('text').attr('x', lx + lw + 12).attr('y', ly + 11).attr('dominant-baseline', 'middle')
    .text('rosso: peggio · blu: meglio');
  if (cells.some(c => !c.pair)) {
    svg.append('text').attr('x', lx).attr('y', ly - 10).attr('fill', INK)
      .text('Grigio: nessun dato');
  }
}

chartScore();
chartHeatmap();
chartScatter();
if (DATA.comparison) {
  chartCompareScore();
  chartDeltaHeatmap();
  chartCompareTime();
}
</script>
</body>
</html>
"""


if __name__ == "__main__":
    sys.exit(main(sys.argv))
