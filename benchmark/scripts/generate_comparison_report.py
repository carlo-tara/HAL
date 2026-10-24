#!/usr/bin/env python3
"""Generate report.htm + REPORT.md for a hal_system2 vs orcarouter_direct comparison run.

Generic over N models (reads results.json produced by run_orcarouter_comparison.py).
"""

from __future__ import annotations

import argparse
import json
from html import escape as esc
from pathlib import Path
from typing import TypeGuard

PATH_LABEL = {"hal_system2": "HAL System 2", "orcarouter_direct": "OrcaRouter diretto"}
STATUS_LABEL = {
    "ok": "OK",
    "error": "Errore",
    "empty_response": "Risposta vuota",
    "wrong_model_served": "Modello diverso",
    "not_executed_spend_limit": "Non eseguito (limite di spesa)",
}
SERIES_COLORS = [
    "#2563eb",
    "#d97706",
    "#7c3aed",
    "#059669",
    "#dc2626",
    "#0891b2",
    "#a16207",
    "#be185d",
]


def fmt(value: float | None, digits: int = 1) -> str:
    if value is None:
        return "—"
    return f"{value:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def short(model: str) -> str:
    return model.split("/")[-1]


def cell(results: list[dict], model: str, path: str, prompt: str) -> dict | None:
    for r in results:
        if (
            r["model_requested"] == model
            and r["path"] == path
            and r["prompt_id"] == prompt
        ):
            return r
    return None


def ok(r: dict | None) -> TypeGuard[dict]:
    return r is not None and r["status"] == "ok"


def usage_tokens(r: dict) -> tuple[int | None, int | None, int | None]:
    u = r.get("usage") or {}
    inp = u.get("prompt_tokens", u.get("input_tokens"))
    out = u.get("completion_tokens", u.get("output_tokens"))
    tot = u.get("total_tokens")
    if tot is None and inp is not None and out is not None:
        tot = inp + out
    return inp, out, tot


def seconds(r: dict | None) -> float | None:
    return r["seconds"] if ok(r) else None


def quality_of(r: dict | None) -> tuple[int, int]:
    if not ok(r):
        return 0, 0
    q = r.get("quality") or {}
    return q.get("passed", 0), q.get("total", 0)


def model_path_stats(
    results: list[dict], models: list[str], prompts: list[str]
) -> dict:
    stats: dict = {}
    for m in models:
        for p in PATH_LABEL:
            rows = [cell(results, m, p, pr) for pr in prompts]
            ok_rows = [r for r in rows if ok(r)]
            err_rows = [r for r in rows if r is not None and r["status"] == "error"]
            blocked = [
                r
                for r in rows
                if r is not None and r["status"] == "not_executed_spend_limit"
            ]
            passed = sum(quality_of(r)[0] for r in ok_rows)
            total = sum(quality_of(r)[1] for r in ok_rows)
            tok_in = sum((usage_tokens(r)[0] or 0) for r in ok_rows)
            tok_out = sum((usage_tokens(r)[1] or 0) for r in ok_rows)
            tok_tot = sum((usage_tokens(r)[2] or 0) for r in ok_rows)
            stats[(m, p)] = {
                "ok": len(ok_rows),
                "errors": len(err_rows),
                "blocked": len(blocked),
                "seconds": round(sum(r["seconds"] for r in ok_rows), 2),
                "quality_passed": passed,
                "quality_total": total,
                "tok_in": tok_in,
                "tok_out": tok_out,
                "tok_tot": tok_tot,
            }
    return stats


def paired_rows(
    results: list[dict], model: str, prompts: list[str]
) -> list[tuple[str, dict, dict]]:
    rows = []
    for pr in prompts:
        a, b = (
            cell(results, model, "hal_system2", pr),
            cell(results, model, "orcarouter_direct", pr),
        )
        if ok(a) and ok(b):
            rows.append((pr, a, b))
    return rows


def bar_chart(
    groups: list[str], series: list[tuple[str, str, list[float | None]]]
) -> str:
    width, height = 760, 320
    left, right, top, bottom = 56, 16, 16, 64
    iw, ih = width - left - right, height - top - bottom
    peak = max((v for _, _, vals in series for v in vals if v is not None), default=1)
    peak = peak * 1.1 or 1
    gw = iw / len(groups)
    bw = gw * 0.8 / len(series)
    out = [
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Tempi per prompt">'
    ]
    for i in range(6):
        value = peak * i / 5
        y = top + ih - ih * i / 5
        out.append(
            f'<line x1="{left}" x2="{width - right}" y1="{y:.1f}" y2="{y:.1f}" stroke="#e5e7eb"/>'
            f'<text x="{left - 6}" y="{y + 4:.1f}" text-anchor="end" class="axis">{fmt(value, 0)}</text>'
        )
    for gi, group in enumerate(groups):
        gx = left + gi * gw + gw * 0.1
        for si, (name, color, values) in enumerate(series):
            v = values[gi]
            x = gx + si * bw
            if v is None:
                continue
            h = ih * v / peak
            out.append(
                f'<rect x="{x:.1f}" y="{top + ih - h:.1f}" width="{bw - 3:.1f}" height="{h:.1f}" fill="{color}">'
                f"<title>{esc(name)} — {esc(group)}: {fmt(v)} s</title></rect>"
                f'<text x="{x + bw / 2 - 1:.1f}" y="{top + ih - h - 4:.1f}" text-anchor="middle" class="axis">{fmt(v, 0)}</text>'
            )
        out.append(
            f'<text x="{left + gi * gw + gw / 2:.1f}" y="{height - 40}" text-anchor="middle" class="axis">{esc(group)}</text>'
        )
    lx = left
    for name, color, _ in series:
        out.append(
            f'<rect x="{lx}" y="{height - 22}" width="12" height="12" fill="{color}"/>'
            f'<text x="{lx + 18}" y="{height - 12}" class="axis">{esc(name)}</text>'
        )
        lx += 190
    out.append(
        f'<text x="14" y="{top + ih / 2}" transform="rotate(-90 14 {top + ih / 2})" text-anchor="middle" class="axis">secondi</text>'
    )
    out.append("</svg>")
    return "".join(out)


CSS = """
:root { --ink:#111827; --muted:#6b7280; --line:#e5e7eb; --bg:#f9fafb; --card:#fff; }
body { font-family: system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif; color:var(--ink); background:var(--bg); margin:0; line-height:1.5; }
main { max-width: 980px; margin: 0 auto; padding: 24px 16px 64px; }
h1 { font-size: 1.6rem; margin: 0 0 4px; } h2 { font-size: 1.2rem; margin: 32px 0 8px; }
.sub { color: var(--muted); margin-bottom: 20px; }
.card { background: var(--card); border:1px solid var(--line); border-radius: 8px; padding: 16px 18px; margin: 12px 0; }
.alert { border-left: 4px solid #b91c1c; background:#fef2f2; }
.good { border-left: 4px solid #15803d; background:#f0fdf4; }
.kpis { display:grid; grid-template-columns: repeat(auto-fit,minmax(170px,1fr)); gap:12px; }
.kpi b { display:block; font-size:1.7rem; } .kpi span { color:var(--muted); font-size:.85rem; }
table { border-collapse: collapse; width:100%; font-size:.9rem; background:var(--card); }
th,td { border:1px solid var(--line); padding:6px 8px; text-align:left; }
thead th { background:#f3f4f6; } .num { text-align:right; font-variant-numeric: tabular-nums; }
td.ok { background:#dcfce7; text-align:center; } td.err { background:#fee2e2; text-align:center; } td.na { background:#f3f4f6; color:var(--muted); text-align:center; }
svg { width:100%; height:auto; } .axis { font-size:11px; fill:#374151; }
ul { margin: 6px 0 6px 20px; padding:0; } code { background:#f3f4f6; padding:1px 4px; border-radius:3px; }
.small { font-size:.85rem; color:var(--muted); }
"""


def build_html(report: dict) -> str:
    results = report["results"]
    method = report["method"]
    models = method["model_order"]
    prompts: list[str] = []
    for r in results:
        if r["prompt_id"] not in prompts:
            prompts.append(r["prompt_id"])
    stats = model_path_stats(results, models, prompts)

    total = len(results)
    n_ok = sum(1 for r in results if r["status"] == "ok")
    n_err = sum(1 for r in results if r["status"] == "error")
    n_blocked = sum(1 for r in results if r["status"] == "not_executed_spend_limit")

    # Paired overhead per model
    pair_sum: dict[str, tuple[float, float, int]] = {}
    for m in models:
        rows = paired_rows(results, m, prompts)
        if rows:
            pair_sum[m] = (
                sum(a["seconds"] for _, a, _ in rows),
                sum(b["seconds"] for _, _, b in rows),
                len(rows),
            )

    out = [
        "<!DOCTYPE html>",
        '<html lang="it"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>Confronto HAL System 2 vs OrcaRouter diretto</title>",
        f"<style>{CSS}</style></head><body><main>",
        "<h1>Confronto HAL System 2 vs OrcaRouter diretto</h1>",
        f'<div class="sub">Run <code>{esc(report.get("run_id", ""))}</code> · avvio {esc(report["started_at"])} · stato: <b>{esc(report["status"])}</b></div>',
        "<h2>Executive summary</h2>",
    ]

    complete = report["status"] == "completed"
    cls = "good" if complete else "alert"
    out.append(
        f'<div class="card {cls}"><b>{"Benchmark completo." if complete else "Benchmark incompleto."}</b> '
        f"{n_ok}/{total} richieste con output valido, {n_err} errori, {n_blocked} bloccate."
        "</div>"
    )

    kpis = [
        (f"{n_ok}/{total}", "richieste con output valido"),
        (str(n_err), "errori"),
        (str(n_blocked), "bloccate (limite spesa)"),
    ]
    for m in models:
        if m in pair_sum:
            hal_t, dir_t, n = pair_sum[m]
            overhead = (hal_t / dir_t - 1) * 100 if dir_t else 0
            kpis.append(
                (
                    f"{overhead:+.0f} %",
                    f"tempo HAL vs diretto · {short(m)} ({n} prompt appaiati)",
                )
            )
    out.append('<div class="kpis">')
    for value, label in kpis:
        out.append(
            f'<div class="card kpi"><b>{esc(value)}</b><span>{esc(label)}</span></div>'
        )
    out.append("</div>")

    # Key findings (computed)
    findings = []
    for m in models:
        rows = paired_rows(results, m, prompts)
        if not rows:
            continue
        h_q = sum(quality_of(a)[0] for _, a, _ in rows)
        h_qt = sum(quality_of(a)[1] for _, a, _ in rows)
        d_q = sum(quality_of(b)[0] for _, _, b in rows)
        d_qt = sum(quality_of(b)[1] for _, _, b in rows)
        slower = sum(1 for _, a, b in rows if a["seconds"] > b["seconds"])
        hal_t, dir_t, n = pair_sum[m]
        overhead = (hal_t / dir_t - 1) * 100 if dir_t else 0
        findings.append(
            f"<li><b>{esc(short(m))}</b>: qualità HAL {h_q}/{h_qt} vs diretto {d_q}/{d_qt} sui {n} prompt appaiati; "
            f"HAL è più lento su {slower}/{n} prompt, overhead totale {overhead:+.0f} %.</li>"
        )
    if findings:
        out.append(
            '<div class="card"><b>Risultati chiave (percorso HAL vs diretto, prompt appaiati)</b><ul>'
        )
        out.extend(findings)
        out.append("</ul></div>")

    # Coverage table
    out.append("<h2>Copertura delle run</h2>")
    out.append(
        "<table><thead><tr><th>Modello</th><th>Percorso</th>"
        + "".join(f"<th>{esc(pr.replace('_', ' '))}</th>" for pr in prompts)
        + "</tr></thead><tbody>"
    )
    for m in models:
        for p, path_label in PATH_LABEL.items():
            out.append(f"<tr><th>{esc(short(m))}</th><td>{esc(path_label)}</td>")
            for pr in prompts:
                r = cell(results, m, p, pr)
                if r is None:
                    out.append('<td class="na">—</td>')
                    continue
                if r["status"] == "ok":
                    out.append(
                        f'<td class="ok" title="OK in {fmt(r["seconds"])} s">{ok_title(r)}</td>'
                    )
                elif r["status"] == "not_executed_spend_limit":
                    out.append(
                        f'<td class="na" title="{esc(STATUS_LABEL.get(r["status"]) or "")}">—</td>'
                    )
                else:
                    detail = esc(STATUS_LABEL.get(r["status"]) or "")
                    if r.get("http_status"):
                        detail += f" (HTTP {r['http_status']})"
                    out.append(f'<td class="err" title="{detail}">ERR</td>')
            out.append("</tr>")
    out.append("</tbody></table>")
    out.append(
        '<p class="small">OK = output valido · ERR = errore · — = non eseguito o assente.</p>'
    )

    # Time chart
    out.append("<h2>Tempi per prompt</h2>")
    series = []
    ci = 0
    for m in models:
        for p, path_label in PATH_LABEL.items():
            vals = [seconds(cell(results, m, p, pr)) for pr in prompts]
            if any(v is not None for v in vals):
                series.append(
                    (
                        f"{short(m)} · {path_label}",
                        SERIES_COLORS[ci % len(SERIES_COLORS)],
                        vals,
                    )
                )
            ci += 1
    if series and prompts:
        out.append(
            f'<div class="card">{bar_chart([p.replace("_", " ") for p in prompts], series)}</div>'
        )

    # Paired tables per model
    out.append(
        "<h2>Confronto appaiato per modello (prompt ok su entrambi i percorsi)</h2>"
    )
    for m in models:
        rows = paired_rows(results, m, prompts)
        if not rows:
            continue
        out.append(f"<h3>{esc(short(m))}</h3>")
        out.append(
            "<table><thead><tr><th>Prompt</th><th>HAL (s)</th><th>Diretto (s)</th><th>Δ HAL</th><th>Rubriche HAL</th><th>Rubriche diretto</th></tr></thead><tbody>"
        )
        for pr, a, b in rows:
            b_secs = b["seconds"]
            delta = (a["seconds"] / b_secs - 1) * 100 if b_secs else 0
            aq, aqt = quality_of(a)
            bq, bqt = quality_of(b)
            out.append(
                f"<tr><td>{esc(pr)}</td><td class='num'>{fmt(a['seconds'])}</td>"
                f"<td class='num'>{fmt(b['seconds'])}</td><td class='num'>{delta:+.0f} %</td>"
                f"<td class='num'>{aq}/{aqt}</td><td class='num'>{bq}/{bqt}</td></tr>"
            )
        hal_t, dir_t, n = pair_sum[m]
        out.append(
            f'<tr><th>Totale ({n})</th><td class="num"><b>{fmt(hal_t)}</b></td>'
            f'<td class="num"><b>{fmt(dir_t)}</b></td><td class="num"><b>{(hal_t / dir_t - 1) * 100:+.0f} %</b></td>'
            f'<td class="num"></td><td class="num"></td></tr>'
        )
        out.append("</tbody></table>")

    # Token summary per model/path
    out.append("<h2>Consumo token per modello e percorso</h2>")
    out.append(
        "<table><thead><tr><th>Modello</th><th>Percorso</th><th>Run OK</th><th>Input</th><th>Output</th><th>Totale</th><th>Media/run</th><th>Tempo ok (s)</th><th>Rubriche</th></tr></thead><tbody>"
    )
    for m in models:
        for p, path_label in PATH_LABEL.items():
            s = stats[(m, p)]
            avg = round(s["tok_tot"] / s["ok"]) if s["ok"] else None
            out.append(
                f"<tr><td>{esc(short(m))}</td><td>{esc(path_label)}</td><td class='num'>{s['ok']}/{len(prompts)}</td>"
                f"<td class='num'>{s['tok_in']:,}</td><td class='num'>{s['tok_out']:,}</td><td class='num'>{s['tok_tot']:,}</td>"
                f"<td class='num'>{fmt(avg, 0)}</td><td class='num'>{fmt(s['seconds'])}</td>"
                f"<td class='num'>{s['quality_passed']}/{s['quality_total']}</td></tr>"
            )
    out.append("</tbody></table>")

    # Detail of valid requests
    out.append("<h2>Dettaglio delle richieste valide</h2>")
    out.append(
        "<table><thead><tr><th>Modello</th><th>Percorso</th><th>Prompt</th><th>Secondi</th><th>Token in</th><th>Token out</th><th>Rubriche</th><th>Modello servito</th></tr></thead><tbody>"
    )
    for r in results:
        if not ok(r):
            continue
        inp, outp, _ = usage_tokens(r)
        q = r.get("quality") or {}
        out.append(
            f"<tr><td>{esc(short(r['model_requested']))}</td><td>{esc(PATH_LABEL.get(r['path'], ''))}</td>"
            f"<td>{esc(r['prompt_id'])}</td><td class='num'>{fmt(r['seconds'])}</td>"
            f"<td class='num'>{inp if inp is not None else '—'}</td><td class='num'>{outp if outp is not None else '—'}</td>"
            f"<td class='num'>{q.get('passed', 0)}/{q.get('total', 0)}</td><td>{esc(r.get('model_served') or '—')}</td></tr>"
        )
    out.append("</tbody></table>")

    # Errors detail
    errs = [r for r in results if r["status"] == "error"]
    if errs:
        out.append("<h2>Errori</h2><ul>")
        for r in errs:
            detail = r.get("error_detail") or ""
            out.append(
                f"<li><code>{esc(short(r['model_requested']))}</code> · {esc(PATH_LABEL[r['path']])} · {esc(r['prompt_id'])}: "
                f"HTTP {r.get('http_status')} — {esc(str(detail)[:160])}</li>"
            )
        out.append("</ul>")

    out.append("<h2>Note di lettura</h2><ul>")
    out.append(
        "<li><code>status: ok</code> non equivale a risposta corretta: la qualità è una rubrica euristica.</li>"
    )
    out.append(
        "<li>Con n=1 per cella e temperatura 0.6 le differenze di token sono rumore di campionamento.</li>"
    )
    out.append(
        "<li>Il percorso HAL ha un timeout upstream di 60 s: prompt di generazione lunga possono fallire via HAL e riuscire in diretto.</li>"
    )
    out.append("</ul>")
    out.append("</main></body></html>")
    return "\n".join(out)


def ok_title(r: dict) -> str:
    q = r.get("quality") or {}
    if q:
        return f"OK {q.get('passed', 0)}/{q.get('total', 0)}"
    return "OK"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()
    report = json.loads((args.run_dir / "results.json").read_text(encoding="utf-8"))
    report.setdefault("run_id", args.run_id or args.run_dir.name)
    html = build_html(report)
    (args.run_dir / "report.htm").write_text(html, encoding="utf-8")
    print(f"written {args.run_dir / 'report.htm'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
