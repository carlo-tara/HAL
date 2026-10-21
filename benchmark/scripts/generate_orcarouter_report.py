#!/usr/bin/env python3
"""Generate report.htm (executive summary + comparison) for an orcarouter comparison run."""

from __future__ import annotations

import argparse
import json
from html import escape as esc
from pathlib import Path
from typing import TypeGuard

PATH_LABEL = {"hal_system2": "HAL System 2", "orcarouter_direct": "OrcaRouter diretto"}
PATH_COLOR = {"hal_system2": "#d97706", "orcarouter_direct": "#2563eb"}
OPUS_COLOR = "#7c3aed"
STATUS_LABEL = {
    "ok": "OK",
    "error": "Errore",
    "not_executed_spend_limit": "Non eseguito (limite di spesa)",
}


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
                out.append(
                    f'<text x="{x + bw / 2:.1f}" y="{top + ih - 6}" text-anchor="middle" class="axis" fill="#b91c1c">n/d</text>'
                )
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
        lx += 200
    out.append(
        f'<text x="14" y="{top + ih / 2}" transform="rotate(-90 14 {top + ih / 2})" text-anchor="middle" class="axis">secondi</text>'
    )
    out.append("</svg>")
    return "".join(out)


def token_bar_chart(
    groups: list[str],
    input_vals: list[int | None],
    output_vals: list[int | None],
) -> str:
    """Stacked bar chart: input (bottom) + output (top) per group."""
    width, height = 760, 280
    left, right, top, bottom = 56, 16, 16, 56
    iw, ih = width - left - right, height - top - bottom
    totals = [(a or 0) + (b or 0) for a, b in zip(input_vals, output_vals)]
    peak = max(totals, default=1)
    peak = peak * 1.15 or 1
    gw = iw / len(groups)
    bw = gw * 0.6
    out = [
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Token per prompt">'
    ]
    for i in range(6):
        value = peak * i / 5
        y = top + ih - ih * i / 5
        out.append(
            f'<line x1="{left}" x2="{width - right}" y1="{y:.1f}" y2="{y:.1f}" stroke="#e5e7eb"/>'
            f'<text x="{left - 6}" y="{y + 4:.1f}" text-anchor="end" class="axis">{fmt(value, 0)}</text>'
        )
    for gi, group in enumerate(groups):
        gx = left + gi * gw + (gw - bw) / 2
        inp = input_vals[gi]
        outp = output_vals[gi]
        if inp is None and outp is None:
            out.append(
                f'<text x="{gx + bw / 2:.1f}" y="{top + ih - 6}" text-anchor="middle" class="axis" fill="#b91c1c">n/d</text>'
            )
            continue
        h_in = ih * (inp or 0) / peak
        h_out = ih * (outp or 0) / peak
        y_in_top = top + ih - h_in
        y_out_top = y_in_top - h_out
        if inp is not None:
            out.append(
                f'<rect x="{gx:.1f}" y="{y_in_top:.1f}" width="{bw:.1f}" height="{h_in:.1f}" fill="#3b82f6">'
                f"<title>{esc(group)} input: {inp:,} token</title></rect>"
            )
        if outp is not None:
            out.append(
                f'<rect x="{gx:.1f}" y="{y_out_top:.1f}" width="{bw:.1f}" height="{h_out:.1f}" fill="#10b981">'
                f"<title>{esc(group)} output: {outp:,} token</title></rect>"
            )
        out.append(
            f'<text x="{left + gi * gw + gw / 2:.1f}" y="{height - 16}" text-anchor="middle" class="axis">{esc(group)}</text>'
        )
    lx = left
    for name, color in [("Input", "#3b82f6"), ("Output", "#10b981")]:
        out.append(
            f'<rect x="{lx}" y="{height - 6}" width="10" height="10" fill="{color}"/>'
            f'<text x="{lx + 14}" y="{height - 2}" class="axis">{name}</text>'
        )
        lx += 80
    out.append(
        f'<text x="14" y="{top + ih / 2}" transform="rotate(-90 14 {top + ih / 2})" text-anchor="middle" class="axis">token</text>'
    )
    out.append("</svg>")
    return "".join(out)


def build(report: dict) -> str:
    results = report["results"]
    method = report["method"]
    models = method["model_order"]
    prompts = []
    for r in results:
        if r["prompt_id"] not in prompts:
            prompts.append(r["prompt_id"])
    sonnet, opus = models[0], models[1]

    def ok(r: dict | None) -> TypeGuard[dict]:
        return r is not None and r["status"] == "ok"

    def seconds(model: str, path: str, prompt: str) -> float | None:
        r = cell(results, model, path, prompt)
        return r["seconds"] if ok(r) else None

    total = len(results)
    n_ok = sum(1 for r in results if r["status"] == "ok")
    n_blocked = sum(1 for r in results if r["status"] == "not_executed_spend_limit")
    n_err = sum(1 for r in results if r["status"] == "error")
    runs_valid = sum(
        1
        for m in models
        for p in PATH_LABEL
        if any(ok(cell(results, m, p, pr)) for pr in prompts)
    )

    # Paired Sonnet comparison (only prompts ok on both paths)
    paired = []
    for pr in prompts:
        a, b = (
            cell(results, sonnet, "hal_system2", pr),
            cell(results, sonnet, "orcarouter_direct", pr),
        )
        if ok(a) and ok(b):
            paired.append((pr, a, b))
    hal_t = sum(a["seconds"] for _, a, _ in paired)
    dir_t = sum(b["seconds"] for _, _, b in paired)
    overhead = (hal_t / dir_t - 1) * 100 if dir_t else 0
    hal_fail = []
    hal_fail_secs = None
    for pr in prompts:
        failed = cell(results, sonnet, "hal_system2", pr)
        if failed is not None and failed["status"] == "error":
            hal_fail.append(pr)
            hal_fail_secs = failed["seconds"]
    direct_for_failed = [
        s
        for pr in hal_fail
        if (s := seconds(sonnet, "orcarouter_direct", pr)) is not None
    ]
    paired_ids = [pr for pr, _, _ in paired]

    def quality(
        model: str, path: str, only: list[str] | None = None
    ) -> tuple[int, int]:
        passed = tot = 0
        for pr in only if only is not None else prompts:
            r = cell(results, model, path, pr)
            if ok(r) and r.get("quality"):
                passed += r["quality"]["passed"]
                tot += r["quality"]["total"]
        return passed, tot

    sq_h, sq_d, oq_d = (
        quality(sonnet, "hal_system2", paired_ids),
        quality(sonnet, "orcarouter_direct", paired_ids),
        quality(opus, "orcarouter_direct"),
    )

    # ── Token aggregation per model+path ────────────────────────────────
    token_agg: dict[tuple, dict] = {}
    for r in results:
        if r["status"] != "ok":
            continue
        key = (r["model_requested"], r["path"])
        entry = token_agg.setdefault(
            key,
            {
                "prompt": 0,
                "completion": 0,
                "total": 0,
                "count": 0,
                "per_prompt": [],
                "cache_text": 0,
                "cache_creation_5m": 0,
                "cache_creation_1h": 0,
                "reasoning": 0,
                "audio_in": 0,
                "audio_out": 0,
                "image_in": 0,
                "efficiency": [],
            },
        )
        u = r.get("usage") or {}
        entry["prompt"] += u.get("prompt_tokens", 0) or 0
        entry["completion"] += u.get("completion_tokens", 0) or 0
        entry["total"] += u.get("total_tokens", 0) or 0
        entry["count"] += 1
        entry["per_prompt"].append(
            (
                r["prompt_id"],
                u.get("prompt_tokens", 0) or 0,
                u.get("completion_tokens", 0) or 0,
            )
        )
        # Claude-specific cache tokens
        pd = u.get("prompt_tokens_details") or {}
        ct = pd.get("cached_tokens", 0) or 0
        entry["cache_text"] += ct
        entry["audio_in"] += pd.get("audio_tokens", 0) or 0
        entry["image_in"] += pd.get("image_tokens", 0) or 0
        cc5 = u.get("claude_cache_creation_5_m_tokens", 0) or 0
        cc1h = u.get("claude_cache_creation_1_h_tokens", 0) or 0
        entry["cache_creation_5m"] += cc5
        entry["cache_creation_1h"] += cc1h
        cd = u.get("completion_tokens_details") or {}
        entry["reasoning"] += cd.get("reasoning_tokens", 0) or 0
        entry["audio_out"] += cd.get("audio_tokens", 0) or 0
        # efficiency: total tokens / seconds
        secs = r.get("seconds")
        if secs and secs > 0:
            entry["efficiency"].append(entry["total"] / secs)

    # Build token summary table rows (one row per model+path combo with data)
    token_summary_rows = []
    for m in models:
        for p in PATH_LABEL:
            key = (m, p)
            e = token_agg.get(key)
            if not e or e["count"] == 0:
                continue
            avg = e["total"] / e["count"] if e["count"] else 0
            out_ratio = (e["completion"] / e["prompt"] * 100) if e["prompt"] else 0
            token_summary_rows.append(
                f"<tr><td>{esc(short(m))}</td><td>{esc(PATH_LABEL[p])}</td>"
                f"<td class='num'>{e['count']}</td>"
                f"<td class='num'>{fmt(e['prompt'], 0)}</td>"
                f"<td class='num'>{fmt(e['completion'], 0)}</td>"
                f"<td class='num'><b>{fmt(e['total'], 0)}</b></td>"
                f"<td class='num'>{fmt(avg, 0)}</td>"
                f"<td class='num'>{fmt(out_ratio, 0)} %</td></tr>"
            )

    # Per-prompt breakdown table
    prompt_breakdown_rows = []
    for m in models:
        for p in PATH_LABEL:
            key = (m, p)
            e = token_agg.get(key)
            if not e or not e["per_prompt"]:
                continue
            prompt_breakdown_rows.append(
                f"<tr><th rowspan='{len(e['per_prompt'])}'>{esc(short(m))}</th>"
                f"<th rowspan='{len(e['per_prompt'])}'>{esc(PATH_LABEL[p])}</th>"
                f"<td class='num'>{esc(e['per_prompt'][0][0])}</td>"
                f"<td class='num'>{fmt(e['per_prompt'][0][1], 0)}</td>"
                f"<td class='num'>{fmt(e['per_prompt'][0][2], 0)}</td>"
                f"<td class='num'>{fmt(e['per_prompt'][0][1] + e['per_prompt'][0][2], 0)}</td></tr>"
                + "\n".join(
                    f"<tr><td class='num'>{esc(pp[0])}</td>"
                    f"<td class='num'>{fmt(pp[1], 0)}</td>"
                    f"<td class='num'>{fmt(pp[2], 0)}</td>"
                    f"<td class='num'>{fmt(pp[1] + pp[2], 0)}</td></tr>"
                    for pp in e["per_prompt"][1:]
                )
            )

    # Cache analysis (Claude models only)
    cache_rows = []
    reasoning_rows = []
    for m in models:
        for p in PATH_LABEL:
            key = (m, p)
            e = token_agg.get(key)
            if not e or e["count"] == 0:
                continue
            # Only show cache/reasoning for Anthropic models
            if "anthropic" in m:
                cache_pct = (e["cache_text"] / e["prompt"] * 100) if e["prompt"] else 0
                cache_rows.append(
                    f"<tr><td>{esc(short(m))}</td><td>{esc(PATH_LABEL[p])}</td>"
                    f"<td class='num'>{fmt(e['cache_text'], 0)}</td>"
                    f"<td class='num'>{fmt(cache_pct, 0)} %</td>"
                    f"<td class='num'>{fmt(e['cache_creation_5m'], 0)}</td>"
                    f"<td class='num'>{fmt(e['cache_creation_1h'], 0)}</td>"
                    f"<td class='num'>{fmt(e['audio_in'], 0)}</td>"
                    f"<td class='num'>{fmt(e['image_in'], 0)}</td></tr>"
                )
            if e["reasoning"] > 0:
                reason_pct = (
                    e["reasoning"] / e["completion"] * 100 if e["completion"] else 0
                )
                reasoning_rows.append(
                    f"<tr><td>{esc(short(m))}</td><td>{esc(PATH_LABEL[p])}</td>"
                    f"<td class='num'>{fmt(e['reasoning'], 0)}</td>"
                    f"<td class='num'>{fmt(reason_pct, 0)} %</td></tr>"
                )

    # Efficiency metrics
    eff_rows = []
    for m in models:
        for p in PATH_LABEL:
            key = (m, p)
            e = token_agg.get(key)
            if not e or not e["efficiency"]:
                continue
            avg_eff = sum(e["efficiency"]) / len(e["efficiency"])
            max_eff = max(e["efficiency"])
            min_eff = min(e["efficiency"])
            eff_rows.append(
                f"<tr><td>{esc(short(m))}</td><td>{esc(PATH_LABEL[p])}</td>"
                f"<td class='num'>{fmt(avg_eff, 0)}</td>"
                f"<td class='num'>{fmt(max_eff, 0)}</td>"
                f"<td class='num'>{fmt(min_eff, 0)}</td>"
                f"<td class='num'>{fmt(e['count'])}</td></tr>"
            )

    # Tables
    coverage_rows = []
    for m in models:
        for p in PATH_LABEL:
            tds = []
            for pr in prompts:
                r = cell(results, m, p, pr)
                st = r["status"] if r is not None else "n/d"
                cls = {"ok": "ok", "error": "err"}.get(st, "na")
                label = {
                    "ok": "OK",
                    "error": "ERR",
                    "not_executed_spend_limit": "—",
                }.get(st, "?")
                tip = STATUS_LABEL.get(st, st)
                if r is not None and r.get("http_status") and st != "ok":
                    tip += f" (HTTP {r['http_status']})"
                tds.append(f'<td class="{cls}" title="{esc(tip)}">{label}</td>')
            coverage_rows.append(
                f"<tr><th>{esc(short(m))}</th><td>{esc(PATH_LABEL[p])}</td>{''.join(tds)}</tr>"
            )

    detail_rows = []
    for m in (sonnet, opus):
        for p in PATH_LABEL:
            for pr in prompts:
                r = cell(results, m, p, pr)
                if not ok(r):
                    continue
                u = r.get("usage") or {}
                q = r.get("quality") or {}
                detail_rows.append(
                    f"<tr><td>{esc(short(m))}</td><td>{esc(PATH_LABEL[p])}</td><td>{esc(pr)}</td>"
                    f'<td class="num">{fmt(r["seconds"])}</td>'
                    f'<td class="num">{u.get("prompt_tokens", "—")}</td>'
                    f'<td class="num">{u.get("completion_tokens", "—")}</td>'
                    f'<td class="num">{q.get("passed", "—")}/{q.get("total", "—")}</td></tr>'
                )

    pair_rows = "".join(
        f"<tr><td>{esc(pr)}</td><td class='num'>{fmt(a['seconds'])}</td><td class='num'>{fmt(b['seconds'])}</td>"
        f"<td class='num'>{fmt((a['seconds'] / b['seconds'] - 1) * 100, 0)} %</td></tr>"
        for pr, a, b in paired
    )

    chart = bar_chart(
        [p.replace("_", " ") for p in prompts],
        [
            (
                f"{short(sonnet)} · HAL",
                PATH_COLOR["hal_system2"],
                [seconds(sonnet, "hal_system2", p) for p in prompts],
            ),
            (
                f"{short(sonnet)} · diretto",
                PATH_COLOR["orcarouter_direct"],
                [seconds(sonnet, "orcarouter_direct", p) for p in prompts],
            ),
            (
                f"{short(opus)} · diretto",
                OPUS_COLOR,
                [seconds(opus, "orcarouter_direct", p) for p in prompts],
            ),
        ],
    )

    # Token stacked bar chart (input vs output per prompt)
    token_groups = [p.replace("_", " ") for p in prompts]
    token_input_series: list[int | None] = []
    token_output_series: list[int | None] = []
    for pr in prompts:
        r = cell(results, sonnet, "orcarouter_direct", pr)
        if ok(r):
            u = r.get("usage") or {}
            token_input_series.append(u.get("prompt_tokens", 0) or 0)
            token_output_series.append(u.get("completion_tokens", 0) or 0)
        else:
            token_input_series.append(None)
            token_output_series.append(None)
    token_chart = token_bar_chart(token_groups, token_input_series, token_output_series)

    slower = sum(1 for _, a, b in paired if a["seconds"] > b["seconds"])
    opus_note = ""
    opus_prog = cell(results, opus, "orcarouter_direct", "programmazione")
    opus_tr = cell(results, opus, "orcarouter_direct", "sintesi_traduzione")
    if ok(opus_prog) and ok(opus_tr):
        opus_note = (
            f"Opus 5.5 diretto passa {oq_d[0]}/{oq_d[1]} controlli: "
            f"<code>programmazione</code> {opus_prog['quality']['passed']}/{opus_prog['quality']['total']} "
            f"con {opus_prog['usage'].get('completion_tokens')} token in uscita (probabile troncamento) e "
            f"<code>sintesi_traduzione</code> {opus_tr['quality']['passed']}/{opus_tr['quality']['total']} "
            f"con {opus_tr['usage'].get('completion_tokens')} token."
        )

    return f"""<!DOCTYPE html>
<html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Confronto HAL System 2 vs OrcaRouter diretto</title>
<style>
:root {{ --ink:#111827; --muted:#6b7280; --line:#e5e7eb; --bg:#f9fafb; --card:#fff; }}
body {{ font-family: system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif; color:var(--ink); background:var(--bg); margin:0; line-height:1.5; }}
main {{ max-width: 980px; margin: 0 auto; padding: 24px 16px 64px; }}
h1 {{ font-size: 1.6rem; margin: 0 0 4px; }} h2 {{ font-size: 1.2rem; margin: 32px 0 8px; }}
.sub {{ color: var(--muted); margin-bottom: 20px; }}
.card {{ background: var(--card); border:1px solid var(--line); border-radius: 8px; padding: 16px 18px; margin: 12px 0; }}
.alert {{ border-left: 4px solid #b91c1c; background:#fef2f2; }}
.kpis {{ display:grid; grid-template-columns: repeat(auto-fit,minmax(170px,1fr)); gap:12px; }}
.kpi b {{ display:block; font-size:1.7rem; }} .kpi span {{ color:var(--muted); font-size:.85rem; }}
table {{ border-collapse: collapse; width:100%; font-size:.9rem; background:var(--card); }}
th,td {{ border:1px solid var(--line); padding:6px 8px; text-align:left; }}
thead th {{ background:#f3f4f6; }} .num {{ text-align:right; font-variant-numeric: tabular-nums; }}
td.ok {{ background:#dcfce7; text-align:center; }} td.err {{ background:#fee2e2; text-align:center; }} td.na {{ background:#f3f4f6; color:var(--muted); text-align:center; }}
svg {{ width:100%; height:auto; }} .axis {{ font-size:11px; fill:#374151; }}
ul {{ margin: 6px 0 6px 20px; padding:0; }} code {{ background:#f3f4f6; padding:1px 4px; border-radius:3px; }}
.small {{ font-size:.85rem; color:var(--muted); }}
</style></head><body><main>
<h1>Confronto HAL System 2 vs OrcaRouter diretto</h1>
<div class="sub">Run <code>{esc(Path(report.get("run_dir", "20261021_8")).name)}</code> · avvio {esc(report["started_at"][:19])} UTC · stato: <b>{esc(report["status"])}</b></div>

<h2>Executive summary</h2>
<div class="card alert"><b>Benchmark incompleto.</b> Solo {runs_valid} run su {method["total_runs"]} hanno prodotto output valido.
Dalla quinta run OrcaRouter ha risposto <code>403 token cycle spend limit reached</code> (reset 2026-10-26 00:00 UTC):
{n_blocked} richieste su {total} non hanno generato output. GPT-6 Luna e GPT-6.1 Sol <b>non sono confrontabili</b>.</div>

<div class="kpis">
 <div class="card kpi"><b>{n_ok}/{total}</b><span>richieste con output valido</span></div>
 <div class="card kpi"><b>{n_blocked}</b><span>bloccate dal limite di spesa</span></div>
 <div class="card kpi"><b>{n_err}</b><span>errori reali (timeout HAL 60 s)</span></div>
 <div class="card kpi"><b>+{fmt(overhead, 0)} %</b><span>tempo HAL vs diretto, Sonnet, {len(paired)} prompt appaiati</span></div>
</div>

<div class="card"><b>Risultati chiave</b><ul>
<li><b>Qualità:</b> a parità di modello (Sonnet 5.5) i due percorsi non differiscono: HAL {sq_h[0]}/{sq_h[1]} e diretto {sq_d[0]}/{sq_d[1]} sugli stessi {len(paired)} prompt completati su entrambi i percorsi.</li>
<li><b>Latenza:</b> HAL aggiunge in media {fmt(overhead, 0)} % sui prompt appaiati ({fmt(hal_t)} s vs {fmt(dir_t)} s totali); HAL è più lento su {slower} prompt su {len(paired)}, ma con una sola misura per cella lo scarto per singolo prompt è poco affidabile.</li>
<li><b>Affidabilità:</b> HAL ha un timeout upstream fisso di 60 s ({"<code>" + ", ".join(hal_fail) + "</code>" if hal_fail else "nessun fallimento"}{" fallito a " + fmt(hal_fail_secs) + " s" if hal_fail_secs else ""}); in diretto lo stesso prompt richiede {", ".join(fmt(s) + " s" for s in direct_for_failed) or "—"}. È la differenza strutturale più rilevante.</li>
<li><b>Opus 5.5 (solo diretto):</b> {opus_note or "dati insufficienti."} Con una sola misura non è un giudizio sul modello.</li>
</ul></div>

<div class="card"><b>Raccomandazioni</b><ul>
<li>Portare il timeout upstream di HAL oltre 60 s (o renderlo configurabile per prompt di generazione lunga): senza, Opus e i modelli GPT-6 falliranno verosimilmente sul Sudoku (Opus diretto: ~99 s).</li>
<li>Ripristinare il limite di spesa della chiave OrcaRouter e rilanciare le 5 run mancanti (~25–35 min con pause da 180 s).</li>
<li>Per decisioni di modello servono ripetizioni (n≥3 per cella): a temperatura 0.6 le differenze di token tra singole run sono rumore.</li>
<li>Se serve confrontare anche il workflow <code>source_chunks</code> di HAL, va eseguito con il runner canonico esteso agli ID OrcaRouter: qui HAL è una singola chiamata.</li>
</ul></div>

<h2>Copertura delle run</h2>
<table><thead><tr><th>Modello</th><th>Percorso</th>{"".join(f"<th>{esc(p.replace("_", " "))}</th>" for p in prompts)}</tr></thead>
<tbody>{"".join(coverage_rows)}</tbody></table>
<p class="small">OK = output valido · ERR = errore reale · — = non eseguito per limite di spesa. Passa il mouse su una cella per il dettaglio.</p>

<h2>Tempi per prompt</h2>
<div class="card">{chart}<div class="small">“n/d” = nessun output valido (timeout HAL a 60 s). I modelli GPT-6 e Opus via HAL non sono rappresentati.</div></div>

<h2>Confronto appaiato: {esc(short(sonnet))}, HAL vs diretto</h2>
<table><thead><tr><th>Prompt</th><th>HAL (s)</th><th>Diretto (s)</th><th>Δ HAL</th></tr></thead><tbody>{pair_rows}
<tr><th>Totale</th><td class="num"><b>{fmt(hal_t)}</b></td><td class="num"><b>{fmt(dir_t)}</b></td><td class="num"><b>{fmt(overhead, 0)} %</b></td></tr></tbody></table>

<h2>Dettaglio delle richieste valide</h2>
<table><thead><tr><th>Modello</th><th>Percorso</th><th>Prompt</th><th>Secondi</th><th>Token in</th><th>Token out</th><th>Rubriche</th></tr></thead>
<tbody>{"".join(detail_rows)}</tbody></table>

<h2>Consumo token per modello</h2>
<div class="card">
<h3>Riepilogo per modello e percorso</h3>
<table><thead><tr><th>Modello</th><th>Percorso</th><th>Run OK</th><th>Token in (input)</th><th>Token out (output)</th><th>Totale</th><th>Media/run</th><th>Out/Input %</th></tr></thead>
<tbody>{"".join(token_summary_rows) if token_summary_rows else "<tr><td colspan='8' class='na'>Nessun dato token disponibile</td></tr>"}</tbody></table>
<p class="small">Out/Input % = output tokens / input tokens × 100 (rapporto di espansione del testo generato).</p>
</div>

<div class="card">
<h3>Input vs Output tokens per prompt</h3>
{token_chart}
<p class="small">Barre impilate: blu = input tokens, verde = output tokens. Dati dal percorso Sonnet 5.5 diretto.</p>
</div>

<div class="card">
<h3>Dettaglio per prompt</h3>
<table><thead><tr><th rowspan="2">Modello</th><th rowspan="2">Percorso</th><th>Prompt</th><th>Input</th><th>Output</th><th>Totale</th></tr></thead>
<tbody>{"".join(prompt_breakdown_rows) if prompt_breakdown_rows else "<tr><td colspan='6' class='na'>Nessun dato token disponibile</td></tr>"}</tbody></table>
</div>

<div class="card">
<h3>Cache tokens (modelli Anthropic)</h3>
<table><thead><tr><th>Modello</th><th>Percorso</th><th>Cached tokens</th><th>% sul totale input</th><th>Cache creation 5m</th><th>Cache creation 1h</th><th>Audio input</th><th>Image input</th></tr></thead>
<tbody>{"".join(cache_rows) if cache_rows else "<tr><td colspan='8' class='na'>Nessun dato cache (nessun modello Anthropic con dati validi)</td></tr>"}</tbody></table>
<p class="small">I cached tokens sono token di input già presenti nella finestra contestuale, che non vengono ricalcolati. Le metriche "cache creation" indicano i token usati per popolare la cache.</p>
</div>

<div class="card">
<h3>Reasoning tokens (modelli con ragionamento)</h3>
<table><thead><tr><th>Modello</th><th>Percorso</th><th>Reasoning tokens</th><th>% sul totale output</th></tr></thead>
<tbody>{"".join(reasoning_rows) if reasoning_rows else "<tr><td colspan='4' class='na'>Nessun dato reasoning tokens disponibile</td></tr>"}</tbody></table>
<p class="small">I reasoning tokens rappresentano il processo di pensiero interno del modello prima della risposta finale. Tipici di Claude Opus e modelli Sonnet con ragionamento attivo.</p>
</div>

<div class="card">
<h3>Efficienza: token/secondo</h3>
<table><thead><tr><th>Modello</th><th>Percorso</th><th>Media</th><th>Max</th><th>Min</th><th>N run</th></tr></thead>
<tbody>{"".join(eff_rows) if eff_rows else "<tr><td colspan='6' class='na'>Nessun dato efficienza disponibile</td></tr>"}</tbody></table>
<p class="small">Token/secondo = total_tokens / seconds. Misura quanti token (input + output) il sistema elabora in media al secondo. Un valore più alto indica maggiore throughput.</p>
</div>

<h2>Metodo e limiti</h2>
<div class="card"><ul>
<li>Stessi 5 prompt e rubriche di <code>{esc(method["prompts_file"])}</code>; stesso messaggio utente, temperatura {method["temperature"]}, <code>stream: false</code>, <code>Cache-Control: no-cache</code> su entrambi i percorsi.</li>
<li>Percorsi: HAL System 2 (<code>{esc(method["hal_endpoint"])}</code>, con preflight Laya, routing e telemetria) e OrcaRouter diretto (<code>{esc(method["direct_endpoint"])}</code>). HAL non è un backend indipendente: inoltra a OrcaRouter.</li>
<li>Ordine alternato per modello, {method["cooldown_seconds_between_runs"]} s tra ogni run.</li>
<li>Zed UI non è stato testato (non pilotabile da questo ambiente). Una sola misura per cella.</li>
<li>L’ID modello restituito da OrcaRouter è uno slug (<code>claude-sonnet-5-5</code>): lo status iniziale “wrong_model_served” era un falso positivo ed è stato corretto.</li>
<li>Le rubriche sono euristiche (presenza di parole chiave, lunghezza, JSON/HTML valido): non valutano la correttezza semantica.</li>
</ul></div>
</main></body></html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    report = json.loads((args.run_dir / "results.json").read_text(encoding="utf-8"))
    report["run_dir"] = str(args.run_dir)
    out = args.run_dir / "report.htm"
    out.write_text(build(report), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
