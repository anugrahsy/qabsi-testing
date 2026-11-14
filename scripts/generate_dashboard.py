#!/usr/bin/env python3
"""Generate a self-contained, sanitized AQABSI HTML dashboard from a run manifest.

Design: minimalist & elegant — sticky nav menu (Ringkasan / PRD / Hasil Test),
validated CVD-safe status palette, a per-case detail drawer, dark/light theme.
No secrets, tokens, or passwords are written to the output (sanitized via
generate_artifacts.sanitize).
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from generate_artifacts import sanitize, validate_manifest


# Validated reference status palette (fixed, never themed): good / warning / serious / critical.
STATUS = {
    "pass":              {"label": "Pass",     "color": "#0ca30c", "glyph": "check"},
    "fail":              {"label": "Fail",     "color": "#d03b3b", "glyph": "x"},
    "blocked":           {"label": "Blocked",  "color": "#fab219", "glyph": "alert"},
    "skipped":           {"label": "Skipped",  "color": "#8a8984", "glyph": "dash"},
    "not_run":           {"label": "Not run",  "color": "#a3a29c", "glyph": "dash"},
    "flaky":             {"label": "Flaky",    "color": "#ec835a", "glyph": "wave"},
    "environment_error": {"label": "Env error","color": "#ec835a", "glyph": "alert"},
}
ORDER = ("fail", "pass", "blocked", "skipped", "environment_error", "flaky", "not_run")


def e(value: Any) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def glyph(status: str) -> str:
    g = STATUS.get(status, STATUS["not_run"])["glyph"]
    if g == "check":
        return '<svg viewBox="0 0 12 12" aria-hidden="true"><path d="M2.5 6.2 5 8.7l4.6-5" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    if g == "x":
        return '<svg viewBox="0 0 12 12" aria-hidden="true"><path d="M3 3l6 6M9 3l-6 6" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round"/></svg>'
    if g == "alert":
        return '<svg viewBox="0 0 12 12" aria-hidden="true"><path d="M6 2.2 11 10H1z" fill="none" stroke="#0b0b0b" stroke-width="1.4" stroke-linejoin="round"/><path d="M6 5.2v2.4" stroke="#0b0b0b" stroke-width="1.4" stroke-linecap="round"/><circle cx="6" cy="9" r="0.7" fill="#0b0b0b"/></svg>'
    if g == "wave":
        return '<svg viewBox="0 0 12 12" aria-hidden="true"><path d="M1.5 6c1.5 0 1.5-3 3-3s1.5 3 3 3 1.5-3 3-3" fill="none" stroke="#0b0b0b" stroke-width="1.4" stroke-linecap="round"/></svg>'
    return '<svg viewBox="0 0 12 12" aria-hidden="true"><path d="M2.5 6h7" stroke="#fff" stroke-width="2" stroke-linecap="round"/></svg>'


def pill(status: str) -> str:
    st = STATUS.get(status, STATUS["not_run"])
    return (f'<span class="pill"><span class="pill-dot" style="background:{st["color"]}">{glyph(status)}</span>'
            f'<span class="pill-label">{e(st["label"])}</span></span>')


def sev_color(sev: Any) -> str:
    return {"critical": "#d03b3b", "high": "#ec835a", "medium": "#fab219", "low": "#8a8984"}.get(sev, "#8a8984")


def compact(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def md_inline(s: str) -> str:
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return s


def md_to_html(md: str) -> str:
    lines = md.replace("\r\n", "\n").split("\n")
    blocks: list[str] = []
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            i += 1
            continue
        if s.startswith("```"):
            buf: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(html.escape(lines[i]))
                i += 1
            i += 1
            blocks.append("<pre><code>" + "\n".join(buf) + "</code></pre>")
            continue
        hm = re.match(r"^(#{1,6})\s+(.*)$", s)
        if hm:
            lvl = min(len(hm.group(1)) + 2, 6)  # keep a single h1/h2 for the page chrome
            blocks.append(f"<h{lvl}>{md_inline(hm.group(2))}</h{lvl}>")
            i += 1
            continue
        if s.startswith(">"):
            blocks.append("<blockquote>" + md_inline(s.lstrip("> ").strip()) + "</blockquote>")
            i += 1
            continue
        if s.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            header = rows[0]
            body = rows[1:]
            if body and all(re.match(r"^:?-{2,}:?$", c) for c in body[0]):
                body = body[1:]
            t = '<div class="prd-scroll"><table class="prd-table"><thead><tr>' + \
                "".join(f"<th>{md_inline(h)}</th>" for h in header) + "</tr></thead><tbody>"
            for r in body:
                t += "<tr>" + "".join(f"<td>{md_inline(c)}</td>" for c in r) + "</tr>"
            t += "</tbody></table></div>"
            blocks.append(t)
            continue
        if re.match(r"^[-*]\s+", s):
            items = []
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i].strip()):
                items.append("<li>" + md_inline(re.sub(r"^[-*]\s+", "", lines[i].strip())) + "</li>")
                i += 1
            blocks.append("<ul>" + "".join(items) + "</ul>")
            continue
        if re.match(r"^\d+\.\s+", s):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i].strip()):
                items.append("<li>" + md_inline(re.sub(r"^\d+\.\s+", "", lines[i].strip())) + "</li>")
                i += 1
            blocks.append("<ol>" + "".join(items) + "</ol>")
            continue
        blocks.append("<p>" + md_inline(s) + "</p>")
        i += 1
    return "\n".join(blocks)


def prd_json_to_markdown(data: dict[str, Any]) -> str:
    """Render a PRD JSON document into a compact Markdown block for the dashboard."""
    document = data.get("document") or {}
    lines: list[str] = []
    title = document.get("title") or data.get("summary") or "PRD"
    lines.append(f"# {title}")
    meta: list[str] = []
    version = document.get("version")
    status = document.get("status")
    if version:
        meta.append(f"Version: {version}")
    if status:
        meta.append(f"Status: {status}")
    for field in ("owner", "business_owner", "technical_owner", "qa_owner"):
        value = document.get(field)
        if value:
            meta.append(f"{field.replace('_', ' ').title()}: {value}")
    if meta:
        lines.append("")
        lines.append(" | ".join(meta))
    summary = data.get("summary")
    if summary:
        lines.append("")
        lines.append("## Summary")
        lines.append("")
        lines.append(str(summary))
    scope = data.get("scope") or {}
    in_scope = scope.get("in_scope") or []
    out_of_scope = scope.get("out_of_scope") or []
    if in_scope or out_of_scope:
        lines.append("")
        lines.append("## Scope")
        lines.append("")
        if in_scope:
            lines.append("**In scope:** " + ", ".join(str(item) for item in in_scope))
        if out_of_scope:
            lines.append("**Out of scope:** " + ", ".join(str(item) for item in out_of_scope))
    requirements = data.get("requirements") or []
    if requirements:
        lines.append("")
        lines.append("## Requirements")
        lines.append("")
        lines.append("| ID | Requirement | Priority | Confidence | Acceptance criteria |")
        lines.append("|---|---|---|---|---|")
        for req in requirements:
            if not isinstance(req, dict):
                continue
            criteria = "; ".join(str(item) for item in (req.get("acceptance_criteria") or []))
            lines.append(
                " | ".join(
                    (
                        str(req.get("id") or "—"),
                        str(req.get("statement") or "—"),
                        str(req.get("priority") or "—"),
                        str(req.get("confidence") or "—"),
                        criteria.replace("|", "\\|"),
                    )
                )
            )
    risks = data.get("risks") or []
    if risks:
        lines.append("")
        lines.append("## Risks")
        lines.append("")
        for risk in risks:
            if isinstance(risk, dict):
                lines.append(f"- **{risk.get('id') or 'Risk'}**: {risk.get('impact') or '—'}")
            else:
                lines.append(f"- {risk}")
    return "\n".join(lines)


def build_dashboard_html(run: dict[str, Any], prd_markdown: str, generated_at: str) -> str:
    cases = [c for c in run.get("test_cases", []) if isinstance(c, dict)]
    total = len(cases)

    counts: dict[str, int] = {}
    for t in cases:
        s = t.get("status") or "not_run"
        counts[s] = counts.get(s, 0) + 1
    nfail = counts.get("fail", 0)
    npass = counts.get("pass", 0)
    nblock = counts.get("blocked", 0)
    nnotrun = counts.get("not_run", 0)
    nenv = counts.get("environment_error", 0) + counts.get("flaky", 0)
    nskip = counts.get("skipped", 0)

    sev_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3, None: 9}
    findings = sorted([t for t in cases if t.get("status") == "fail"],
                      key=lambda t: (sev_rank.get(t.get("severity"), 9), str(t.get("id"))))

    mods: dict[str, dict[str, int]] = {}
    for t in cases:
        mod = t.get("feature") or t.get("module") or "—"
        d = mods.setdefault(mod, {"pass": 0, "fail": 0, "blocked": 0, "not_run": 0, "total": 0})
        d["total"] += 1
        s = t.get("status")
        if s in d:
            d[s] += 1
    mod_rows = sorted(mods.items(), key=lambda kv: (-kv[1]["fail"], -kv[1]["total"]))

    def seg_bar() -> str:
        parts = [("fail", nfail), ("pass", npass), ("blocked", nblock),
                 ("environment_error", nenv), ("skipped", nskip), ("not_run", nnotrun)]
        parts = [p for p in parts if p[1] > 0]
        segs = "".join(
            f'<span style="flex-grow:{n};background:{STATUS[s]["color"]}" title="{STATUS[s]["label"]}: {n}"></span>'
            for s, n in parts)
        return '<div class="segbar" role="img" aria-label="Distribusi status test case">' + segs + "</div>"

    def legend() -> str:
        return "".join(
            f'<div class="legend-item"><span class="pill-dot" style="background:{STATUS[s]["color"]}">{glyph(s)}</span>'
            f'<span>{e(STATUS[s]["label"])}</span><span class="legend-n">{counts[s]}</span></div>'
            for s in ORDER if counts.get(s, 0) > 0)

    find_cards = ""
    for t in findings[:8]:
        sev = t.get("severity") or "medium"
        actual = e(t.get("actual_result") or "")
        if len(actual) > 200:
            actual = actual[:200] + "…"
        find_cards += (
            f'<article class="finding" style="--sev:{sev_color(sev)}">'
            f'<div class="finding-head"><span class="sev" style="color:{sev_color(sev)}">{e(str(sev).upper())}</span>'
            f'<code class="fid">{e(t.get("id"))}</code></div>'
            f'<h3>{e(t.get("title") or t.get("scenario"))}</h3>'
            f'<p class="finding-result">{actual or "—"}</p></article>')

    mod_html = ""
    for mod, v in mod_rows:
        mod_html += (f'<tr><td class="mod-name">{e(mod)}</td><td class="num">{v["total"]}</td>'
                     f'<td class="num ok">{v["fail"] or "–"}</td><td class="num">{v["pass"] or "–"}</td>'
                     f'<td class="num">{v["blocked"] or "–"}</td><td class="num muted">{v["not_run"] or "–"}</td></tr>')

    tbody = ""
    detail: dict[str, dict[str, Any]] = {}
    for t in cases:
        tid = str(t.get("id"))
        s = t.get("status") or "not_run"
        sev = t.get("severity")
        tbody += (f'<tr class="case-row" data-id="{e(tid)}" data-status="{e(s)}" tabindex="0" '
                  f'data-search="{e(tid)} {e(t.get("title") or "")} {e(t.get("feature") or "")}">'
                  f'<td class="td-id"><code>{e(tid)}</code></td>'
                  f'<td class="td-title">{e(t.get("title") or t.get("scenario") or "—")}</td>'
                  f'<td class="td-feat">{e(t.get("feature") or "—")}</td>'
                  f'<td class="td-layer">{e(t.get("layer") or "—")}</td>'
                  f'<td>{pill(s)}</td>'
                  f'<td class="td-pri">{e(t.get("priority") or "—")}</td>'
                  f'<td class="td-sev"><span class="sevchip" style="color:{sev_color(sev)}">{e(str(sev) or "–")}</span></td></tr>')
        detail[tid] = {
            "id": tid, "title": t.get("title") or t.get("scenario") or "—",
            "feature": t.get("feature") or "—", "module": t.get("module") or "—",
            "layer": t.get("layer") or "—", "domain": t.get("domain") or "—",
            "technique": t.get("technique") or "—", "status": s,
            "priority": t.get("priority") or "—", "severity": sev,
            "scenario": t.get("scenario") or "",
            "preconditions": t.get("preconditions") or [],
            "steps": t.get("steps") or [],
            "test_data": compact(t.get("test_data")),
            "expected_result": t.get("expected_result") or "",
            "actual_result": t.get("actual_result") or "",
            "evidence": t.get("evidence") or [],
            "notes": t.get("notes") or "",
            "requirement_ids": t.get("requirement_ids") or [],
            "risk_ids": t.get("risk_ids") or [],
            "source_ids": t.get("source_ids") or [],
        }

    prd_html = md_to_html(prd_markdown) if prd_markdown else ""

    env = run.get("environment") or "—"
    run_id = run.get("run_id") or "—"
    module = run.get("module") or "—"
    src = run.get("source") or {}
    repo = src.get("repository") or "—"
    commit = (src.get("commit_sha") or "—")[:12]
    limitations = run.get("limitations") or []

    hero_num = nfail if nfail else npass
    hero_unit = f" / {total} gagal" if nfail else f" / {total} lolos"
    hero_cap = (
        f'{len(findings)} temuan <strong>fail</strong> terkonfirmasi; <strong>{nnotrun}</strong> '
        f'kasus belum dieksekusi.'
        if nfail else
        "Tidak ada fail terkonfirmasi pada run ini."
    )
    lim_html = "".join(f"<li>{e(x)}</li>" for x in limitations[:8])

    CSS = _CSS
    JS = _JS

    statdef_json = json.dumps(STATUS, ensure_ascii=False)
    statuscolor_json = json.dumps({s: v["color"] for s, v in STATUS.items()}, ensure_ascii=False)
    detail_json = json.dumps(detail, ensure_ascii=False)

    prd_nav = '<button class="nav-link" data-view="prd">PRD</button>' if prd_html else ""
    prd_view = (f'<section class="view" data-view="prd"><div class="hero" style="padding-bottom:4px">'
                f'<div class="eyebrow">Product Requirements Document</div></div><div class="prd">{prd_html}</div></section>'
                if prd_html else "")

    return f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AQABSI · QA Report · {e(run_id)}</title>
<meta name="description" content="Laporan QA {e(module)} — {e(env)} ({e(run_id)})">
<style>{CSS}</style>
</head>
<body>
<a class="skip" href="#hasil">Lompat ke hasil test</a>
<nav class="nav"><div class="nav-inner">
  <a class="wordmark" id="wordmark" href="#ringkasan">AQABSI<small>QA Report</small></a>
  <div class="nav-links">
    <button class="nav-link" data-view="ringkasan">Ringkasan</button>
    {prd_nav}
    <button class="nav-link" data-view="hasil">Hasil Test</button>
  </div>
  <button class="tgl" id="themeBtn" aria-label="Ganti tema terang/gelap">Tema</button>
</div></nav>

<main>

<section class="view" data-view="ringkasan">
  <div class="hero">
    <div class="eyebrow">{e(module)} · {e(env)} · {e(run_id)}</div>
    <div class="hero-num">{hero_num}<span class="unit">{hero_unit}</span></div>
    <p class="hero-cap">{hero_cap}</p>
  </div>

  <div class="tiles">
    <div class="tile"><div class="t-label">Pass</div><div class="t-val"><span class="dot" style="background:var(--good)"></span>{npass}</div></div>
    <div class="tile"><div class="t-label">Fail</div><div class="t-val"><span class="dot" style="background:var(--critical)"></span>{nfail}</div></div>
    <div class="tile"><div class="t-label">Blocked</div><div class="t-val"><span class="dot" style="background:var(--warning)"></span>{nblock}</div></div>
    <div class="tile"><div class="t-label">Not run</div><div class="t-val"><span class="dot" style="background:var(--muted)"></span>{nnotrun}</div></div>
  </div>

  <section>
    <div class="sec-head"><h2>Distribusi status</h2><span class="sec-sub">{total} test case</span></div>
    {seg_bar()}
    <div class="legend">{legend()}</div>
  </section>

  <section>
    <div class="sec-head"><h2>Temuan utama</h2><span class="sec-sub">fail terkonfirmasi</span></div>
    <div class="findings">{find_cards or '<p class="note">Tidak ada fail.</p>'}</div>
  </section>

  <section class="grid2">
    <div>
      <div class="sec-head"><h2>Coverage per modul</h2></div>
      <div class="card" style="padding:6px">
        <table class="mod-table">
          <thead><tr><th>Modul</th><th style="text-align:right">Total</th><th style="text-align:right">Fail</th><th style="text-align:right">Pass</th><th style="text-align:right">Blocked</th><th style="text-align:right">Not run</th></tr></thead>
          <tbody>{mod_html}</tbody>
        </table>
      </div>
    </div>
    <div>
      <div class="sec-head"><h2>Batasan &amp; catatan</h2></div>
      <div class="card"><ul style="margin:0;padding-left:18px">{lim_html or '<li>—</li>'}</ul>
        <p class="note">Draft Confluence &amp; ClickUp = dry-run, belum dipublikasikan.</p>
      </div>
    </div>
  </section>
</section>

{prd_view}

<section class="view" data-view="hasil" id="hasil">
  <div class="sec-head" style="margin-top:34px"><h2>Hasil Test</h2><span class="sec-sub">{total} test case · klik baris untuk detail</span></div>
  <div class="controls">
    <input class="search" id="q" type="search" placeholder="Cari ID / judul / modul…" aria-label="Cari test case">
    <div class="filt" id="filt" role="group" aria-label="Filter status"></div>
  </div>
  <div class="tablewrap">
    <table id="tc">
      <thead><tr><th>ID</th><th>Test case</th><th>Modul</th><th>Layer</th><th>Status</th><th>Priority</th><th>Severity</th></tr></thead>
      <tbody>{tbody}</tbody>
    </table>
  </div>
</section>

<footer>
  <div class="sec-head"><h2>Metodologi &amp; evidence</h2></div>
  <ul>
    <li>Run <code>{e(run_id)}</code> · environment <code>{e(env)}</code> · repo <code>{e(repo)}</code> · commit <code>{e(commit)}</code></li>
    <li>Sanitized draft · {e(generated_at[:16].replace('T', ' '))} UTC</li>
    <li>Publikasi &amp; assignment butuh otorisasi eksplisit.</li>
  </ul>
</footer>

</main>

<div class="backdrop" id="backdrop"></div>
<aside class="drawer" id="drawer" role="dialog" aria-modal="true" aria-label="Detail test case">
  <div class="drawer-head" id="drawerHead"><h3></h3><button class="drawer-x" id="drawerX2" aria-label="Tutup">×</button></div>
  <div class="drawer-body" id="drawerBody"></div>
</aside>

<script type="application/json" id="caseData">{detail_json}</script>
<script type="application/json" id="statusJson">{statuscolor_json}</script>
<script>window.STATUSDEF={statdef_json};window.STATUSCOLOR={statuscolor_json};
{JS}
</script>
</body>
</html>"""


_CSS = r"""
:root{color-scheme:light;
 --page:#fafaf9; --surface:#ffffff; --ink:#111110; --ink2:#5c5b57; --muted:#8a8984;
 --grid:#e8e7e2; --baseline:#c9c8c2; --ring:rgba(17,17,16,.10);
 --good:#0ca30c; --warning:#fab219; --serious:#ec835a; --critical:#d03b3b; --accent:#2a78d6;
 --mono:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
[data-theme="dark"]{color-scheme:dark;
 --page:#0e0e0d; --surface:#171716; --ink:#f2f1ed; --ink2:#c4c3ba; --muted:#8a8984;
 --grid:#2a2a28; --baseline:#3a3936; --ring:rgba(255,255,255,.10);
 --good:#0ca30c; --warning:#fab219; --serious:#ec835a; --critical:#e66767; --accent:#3987e5}
@media (prefers-color-scheme:dark){:root:where(:not([data-theme="light"])){color-scheme:dark;
 --page:#0e0e0d; --surface:#171716; --ink:#f2f1ed; --ink2:#c4c3ba; --muted:#8a8984;
 --grid:#2a2a28; --baseline:#3a3936; --ring:rgba(255,255,255,.10);
 --good:#0ca30c; --warning:#fab219; --serious:#ec835a; --critical:#e66767; --accent:#3987e5}}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--page);color:var(--ink);font-family:var(--mono);font-size:15px;line-height:1.55;-webkit-font-smoothing:antialiased}
a{color:var(--accent)}
.skip{position:absolute;left:-9999px;top:0;background:var(--accent);color:#fff;padding:8px 14px;border-radius:6px;z-index:99}
.skip:focus{left:12px;top:12px}
.nav{position:sticky;top:0;z-index:30;background:color-mix(in srgb,var(--page) 84%,transparent);backdrop-filter:blur(14px) saturate(1.2);border-bottom:1px solid var(--grid)}
.nav-inner{max-width:1180px;margin:0 auto;padding:0 24px;height:62px;display:flex;align-items:center;gap:20px}
.wordmark{font-size:15px;font-weight:650;letter-spacing:-.01em;color:var(--ink);text-decoration:none;white-space:nowrap}
.wordmark small{font-weight:450;color:var(--muted);margin-left:6px}
.nav-links{display:flex;gap:2px;margin-left:auto}
.nav-link{font:inherit;font-size:13.5px;color:var(--muted);background:transparent;border:none;padding:9px 14px;cursor:pointer;border-radius:9px;position:relative;transition:color .15s}
.nav-link:hover{color:var(--ink)}
.nav-link.active{color:var(--ink);font-weight:600}
.nav-link.active::after{content:"";position:absolute;left:14px;right:14px;bottom:3px;height:2px;background:var(--accent);border-radius:2px}
.tgl{font:inherit;font-size:12.5px;color:var(--ink2);background:transparent;border:1px solid var(--ring);border-radius:999px;padding:6px 13px;cursor:pointer;white-space:nowrap}
.tgl:hover{border-color:var(--baseline)}
main{max-width:1180px;margin:0 auto;padding:0 24px}
.view{display:none}
.view.active{display:block;animation:in .22s ease}
@keyframes in{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:none}}
.hero{padding:64px 0 20px;max-width:760px}
.eyebrow{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);font-weight:600}
.hero-num{font-size:72px;font-weight:640;letter-spacing:-.035em;line-height:1;margin:14px 0 10px}
.hero-num .unit{font-size:22px;font-weight:480;color:var(--muted);letter-spacing:0}
.hero-cap{color:var(--ink2);max-width:60ch;font-size:15px}
.hero-cap code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:13px}
.tiles{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid var(--grid);border-bottom:1px solid var(--grid);margin:26px 0 0}
.tile{padding:24px 6px}
.tile + .tile{border-left:1px solid var(--grid)}
.t-label{font-size:12px;color:var(--muted)}
.t-val{font-size:34px;font-weight:640;margin-top:6px;font-variant-numeric:tabular-nums;display:flex;align-items:center;gap:10px;letter-spacing:-.02em}
.t-val .dot{width:11px;height:11px;border-radius:50%;flex:none}
section{padding:40px 0}
.sec-head{display:flex;align-items:baseline;gap:12px;margin-bottom:18px}
h2{font-size:16px;font-weight:650;letter-spacing:-.01em;margin:0}
.sec-sub{font-size:13px;color:var(--muted)}
.segbar{display:flex;height:12px;border-radius:999px;overflow:hidden;gap:2px}
.segbar span{min-width:4px}
.legend{display:flex;flex-wrap:wrap;gap:8px 20px;margin-top:16px}
.legend-item{display:flex;align-items:center;gap:7px;font-size:13px;color:var(--ink2)}
.legend-n{font-variant-numeric:tabular-nums;font-weight:600;color:var(--ink)}
.pill{display:inline-flex;align-items:center;gap:6px;font-size:12.5px;font-weight:550;white-space:nowrap}
.pill-dot{width:14px;height:14px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;flex:none}
.pill-dot svg{width:11px;height:11px}
.findings{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}
.finding{background:var(--surface);border:1px solid var(--grid);border-left:3px solid var(--sev);border-radius:12px;padding:16px 18px;transition:border-color .15s}
.finding:hover{border-color:var(--baseline)}
.finding-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:7px}
.sev{font-size:10.5px;font-weight:700;letter-spacing:.08em}
.fid{font-size:11px;color:var(--muted);font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.finding h3{font-size:14.5px;margin:0 0 7px;font-weight:620;line-height:1.35}
.finding-result{font-size:12.5px;color:var(--ink2);margin:0;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;overflow-wrap:anywhere}
.controls{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:16px}
.search{flex:1;min-width:220px;font:inherit;font-size:14px;color:var(--ink);background:var(--surface);border:1px solid var(--grid);border-radius:10px;padding:10px 14px}
.search:focus{outline:2px solid var(--accent);outline-offset:1px;border-color:transparent}
.filt{display:flex;gap:6px;flex-wrap:wrap}
.fbtn{font:inherit;font-size:12.5px;color:var(--ink2);background:transparent;border:1px solid var(--grid);border-radius:999px;padding:6px 12px;cursor:pointer;display:inline-flex;align-items:center;gap:6px}
.fbtn:hover{border-color:var(--baseline)}
.fbtn[aria-pressed="true"]{background:var(--ink);color:var(--page);border-color:var(--ink)}
.tablewrap{overflow-x:auto;border:1px solid var(--grid);border-radius:14px;background:var(--surface)}
table{width:100%;border-collapse:collapse;font-size:13.5px}
thead th{position:sticky;top:62px;background:var(--surface);text-align:left;font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);font-weight:600;padding:13px 14px;border-bottom:1px solid var(--grid)}
tbody td{padding:12px 14px;border-bottom:1px solid var(--grid);vertical-align:top}
tbody tr:last-child td{border-bottom:none}
tr.case-row{cursor:pointer;transition:background .12s}
tr.case-row:hover{background:color-mix(in srgb,var(--accent) 5%,transparent)}
tr.case-row:focus-visible{outline:2px solid var(--accent);outline-offset:-2px}
.td-id code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px;color:var(--ink2);white-space:nowrap}
.td-title{font-weight:560}
.td-feat{color:var(--ink2)}
.td-layer,.td-pri,.td-sev{color:var(--muted);white-space:nowrap}
.sevchip{font-weight:650;text-transform:uppercase;font-size:11px}
.mod-table{width:100%;font-size:13.5px;border-collapse:collapse}
.mod-table td,.mod-table th{padding:9px 12px;text-align:left;border-bottom:1px solid var(--grid)}
.mod-table th{font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted);font-weight:600}
.mod-name{font-weight:600}
.num{font-variant-numeric:tabular-nums;text-align:right}
.num.ok{color:var(--critical);font-weight:650}
.num.muted{color:var(--muted)}
.grid2{display:grid;grid-template-columns:1.5fr 1fr;gap:36px;align-items:start}
.card{background:var(--surface);border:1px solid var(--grid);border-radius:14px;padding:22px}
.prd{max-width:720px}
.prd h3{font-size:20px;font-weight:650;letter-spacing:-.01em;margin:26px 0 10px}
.prd h4{font-size:15px;font-weight:620;margin:18px 0 6px}
.prd p{margin:8px 0;color:var(--ink2)}
.prd ul,.prd ol{margin:8px 0;padding-left:22px;color:var(--ink2)}
.prd li{margin:5px 0}
.prd code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12.5px;background:color-mix(in srgb,var(--ink) 6%,transparent);padding:1px 5px;border-radius:5px}
.prd pre{background:var(--page);border:1px solid var(--grid);border-radius:10px;padding:14px;overflow-x:auto}
.prd pre code{background:transparent;padding:0}
.prd blockquote{border-left:3px solid var(--accent);margin:14px 0;padding:2px 18px;color:var(--ink2);font-size:14px}
.prd-scroll{overflow-x:auto}
.prd-table{border-collapse:collapse;font-size:13px;min-width:560px}
.prd-table th,.prd-table td{border:1px solid var(--grid);padding:8px 12px;text-align:left;vertical-align:top}
.prd-table th{background:var(--page);font-weight:600}
.prd-table code{font-size:12px}
footer{padding:44px 0 70px;color:var(--ink2);font-size:13px;border-top:1px solid var(--grid);margin-top:20px}
footer ul{margin:0;padding-left:18px}
footer li{margin:5px 0}
.note{font-size:12.5px;color:var(--muted);margin-top:12px}
.drawer{position:fixed;top:0;right:-560px;width:min(560px,100vw);height:100vh;background:var(--surface);border-left:1px solid var(--grid);box-shadow:-16px 0 44px rgba(0,0,0,.14);transition:right .28s cubic-bezier(.2,.8,.2,1);z-index:50;display:flex;flex-direction:column}
.drawer.open{right:0}
.drawer-head{display:flex;align-items:flex-start;justify-content:space-between;gap:14px;padding:22px 24px;border-bottom:1px solid var(--grid)}
.drawer-head h3{font-size:17px;margin:0;font-weight:650;line-height:1.3;letter-spacing:-.01em}
.drawer-x{font:inherit;font-size:22px;background:transparent;border:none;color:var(--muted);cursor:pointer;padding:2px 9px;border-radius:7px;line-height:1}
.drawer-x:hover{background:var(--page)}
.drawer-body{padding:20px 24px 44px;overflow-y:auto;flex:1}
.dl{display:grid;grid-template-columns:118px 1fr;gap:6px 14px;font-size:13.5px;margin:0 0 20px}
.dl dt{color:var(--muted);font-weight:550}
.dl dd{margin:0;color:var(--ink);overflow-wrap:anywhere}
.dsec{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);font-weight:600;margin:18px 0 7px}
.dlist{margin:0;padding-left:19px;color:var(--ink2);font-size:13.5px}
.dlist li{margin:4px 0}
.dtext{font-size:13.5px;color:var(--ink2);margin:0;white-space:pre-wrap}
.dmono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12.5px;background:var(--page);border:1px solid var(--grid);border-radius:9px;padding:10px 12px;overflow-wrap:anywhere;white-space:pre-wrap;color:var(--ink)}
.dchips{display:flex;flex-wrap:wrap;gap:6px}
.dchip{font-size:11.5px;color:var(--ink2);border:1px solid var(--grid);border-radius:999px;padding:2px 9px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.backdrop{position:fixed;inset:0;background:rgba(0,0,0,.32);opacity:0;pointer-events:none;transition:opacity .28s;z-index:40}
.backdrop.show{opacity:1;pointer-events:auto}
@media(max-width:840px){.tiles{grid-template-columns:repeat(2,1fr)}.tile:nth-child(3){border-left:none}.tile:nth-child(n+3){border-top:1px solid var(--grid)}.findings{grid-template-columns:1fr}.grid2{grid-template-columns:1fr}.hero-num{font-size:52px}.nav-links{gap:0}.nav-link{padding:9px 10px}.dl{grid-template-columns:1fr}}
"""

_JS = r"""
(function(){
  var root=document.documentElement, btn=document.getElementById('themeBtn');
  var saved=null;try{saved=localStorage.getItem('aqabsi-theme')}catch(e){}
  if(saved==='dark')root.setAttribute('data-theme','dark');else if(saved==='light')root.setAttribute('data-theme','light');
  btn.addEventListener('click',function(){var n=root.getAttribute('data-theme')==='dark'?'light':'dark';root.setAttribute('data-theme',n);try{localStorage.setItem('aqabsi-theme',n)}catch(e){}});

  var links=[].slice.call(document.querySelectorAll('.nav-link'));
  var views=[].slice.call(document.querySelectorAll('.view'));
  function show(v){
    views.forEach(function(s){s.classList.toggle('active',s.dataset.view===v)});
    links.forEach(function(b){b.classList.toggle('active',b.dataset.view===v)});
    window.scrollTo({top:0,behavior:'auto'});
    try{history.replaceState(null,'','#'+v)}catch(e){}
  }
  links.forEach(function(b){b.addEventListener('click',function(){show(b.dataset.view)})});
  var wordmark=document.getElementById('wordmark');
  if(wordmark)wordmark.addEventListener('click',function(e){e.preventDefault();show('ringkasan')});
  var h=null;try{h=location.hash.replace('#','')}catch(e){}
  show(views.some(function(s){return s.dataset.view===h})?h:'ringkasan');

  var DETAIL=JSON.parse(document.getElementById('caseData').textContent);
  var rows=[].slice.call(document.querySelectorAll('tr.case-row'));
  var q=document.getElementById('q'), filt=document.getElementById('filt'), active={};
  var STATUSCOLOR=JSON.parse(document.getElementById('statusJson').textContent);
  Object.keys(STATUSCOLOR).forEach(function(s){
    var b=document.createElement('button');b.className='fbtn';b.type='button';b.setAttribute('aria-pressed','false');
    b.innerHTML='<span style="width:8px;height:8px;border-radius:50%;background:'+STATUSCOLOR[s]+';display:inline-block"></span>'+s.replace(/_/g,' ');
    b.addEventListener('click',function(){active[s]=!active[s];b.setAttribute('aria-pressed',active[s]?'true':'false');apply()});
    filt.appendChild(b);
  });
  function apply(){
    var txt=q.value.toLowerCase();
    rows.forEach(function(r){
      var okTxt=r.getAttribute('data-search').toLowerCase().indexOf(txt)>=0;
      var st=r.getAttribute('data-status');
      var on=Object.keys(active).filter(function(k){return active[k]});
      r.style.display=(okTxt&&(on.length===0||!!active[st]))?'':'none';
    });
  }
  q.addEventListener('input',apply);

  var drawer=document.getElementById('drawer'),backdrop=document.getElementById('backdrop');
  var dbody=document.getElementById('drawerBody'),dhead=document.getElementById('drawerHead');
  function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
  function lst(a){return (a&&a.length)?('<ul class="dlist">'+a.map(function(x){return '<li>'+esc(x)+'</li>'}).join('')+'</ul>'):'<p class="dtext">—</p>'}
  function chips(a){return (a&&a.length)?('<div class="dchips">'+a.map(function(x){return '<span class="dchip">'+esc(x)+'</span>'}).join('')+'</div>'):'<p class="dtext">—</p>'}
  function dpill(s){var st=window.STATUSDEF[s]||{label:s,color:'#a3a29c',glyph:'dash'};
    var g={'check':'<svg viewBox="0 0 12 12"><path d="M2.5 6.2 5 8.7l4.6-5" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
      'x':'<svg viewBox="0 0 12 12"><path d="M3 3l6 6M9 3l-6 6" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round"/></svg>',
      'alert':'<svg viewBox="0 0 12 12"><path d="M6 2.2 11 10H1z" fill="none" stroke="#0b0b0b" stroke-width="1.4" stroke-linejoin="round"/><path d="M6 5.2v2.4" stroke="#0b0b0b" stroke-width="1.4" stroke-linecap="round"/><circle cx="6" cy="9" r="0.7" fill="#0b0b0b"/></svg>',
      'dash':'<svg viewBox="0 0 12 12"><path d="M2.5 6h7" stroke="#fff" stroke-width="2" stroke-linecap="round"/></svg>',
      'wave':'<svg viewBox="0 0 12 12"><path d="M1.5 6c1.5 0 1.5-3 3-3s1.5 3 3 3 1.5-3 3-3" fill="none" stroke="#0b0b0b" stroke-width="1.4" stroke-linecap="round"/></svg>'}[st.glyph]||'';
    return '<span class="pill"><span class="pill-dot" style="background:'+st.color+'">'+g+'</span><span class="pill-label">'+esc(st.label)+'</span></span>';}
  function openCase(id){
    var d=DETAIL[id];if(!d)return;
    dhead.innerHTML='<h3>'+esc(d.title)+'</h3><button class="drawer-x" id="drawerX" aria-label="Tutup">×</button>';
    dbody.innerHTML=
      '<div class="dl">'+
        '<dt>ID</dt><dd><code>'+esc(d.id)+'</code></dd>'+
        '<dt>Status</dt><dd>'+dpill(d.status)+'</dd>'+
        '<dt>Modul</dt><dd>'+esc(d.feature)+'</dd>'+
        '<dt>Layer</dt><dd>'+esc(d.layer)+'</dd>'+
        '<dt>Priority</dt><dd>'+esc(d.priority)+'</dd>'+
        '<dt>Severity</dt><dd>'+esc(d.severity||'—')+'</dd>'+
        '<dt>Technique</dt><dd>'+esc(d.technique)+'</dd>'+
        '<dt>Domain</dt><dd>'+esc(d.domain)+'</dd>'+
      '</div>'+
      (d.scenario?'<div class="dsec">Scenario</div><p class="dtext">'+esc(d.scenario)+'</p>':'')+
      '<div class="dsec">Preconditions</div>'+lst(d.preconditions)+
      '<div class="dsec">Steps</div>'+lst(d.steps)+
      '<div class="dsec">Test data</div><div class="dmono">'+esc(d.test_data||'—')+'</div>'+
      '<div class="dsec">Expected result</div><div class="dmono">'+esc(d.expected_result)+'</div>'+
      '<div class="dsec">Actual result</div><div class="dmono">'+esc(d.actual_result||'—')+'</div>'+
      '<div class="dsec">Evidence</div>'+lst(d.evidence)+
      (d.notes?'<div class="dsec">Notes</div><p class="dtext">'+esc(d.notes)+'</p>':'')+
      '<div class="dsec">Requirement IDs</div>'+chips(d.requirement_ids)+
      '<div class="dsec">Risk IDs</div>'+chips(d.risk_ids)+
      '<div class="dsec">Source IDs</div>'+chips(d.source_ids);
    document.getElementById('drawerX').addEventListener('click',close);
    drawer.classList.add('open');backdrop.classList.add('show');document.body.style.overflow='hidden';
  }
  function close(){drawer.classList.remove('open');backdrop.classList.remove('show');document.body.style.overflow='';}
  rows.forEach(function(r){r.addEventListener('click',function(){openCase(r.getAttribute('data-id'))});r.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();openCase(r.getAttribute('data-id'))}})});
  document.getElementById('drawerX2').addEventListener('click',close);
  backdrop.addEventListener('click',close);
  document.addEventListener('keydown',function(e){if(e.key==='Escape')close()});
})();
"""


def generate(
    input_path: Path,
    output_dir: Path,
    prd_path: Path | None,
    prd_json_path: Path | None,
) -> None:
    raw = json.loads(input_path.read_text(encoding="utf-8"))
    validated = validate_manifest(raw)
    run = sanitize(validated)

    prd_markdown = ""
    if prd_path is not None:
        prd_markdown = prd_path.read_text(encoding="utf-8")
    if prd_json_path is not None:
        prd_json = json.loads(prd_json_path.read_text(encoding="utf-8"))
        prd_markdown = prd_json_to_markdown(prd_json) or prd_markdown

    generated_at = datetime.now(timezone.utc).isoformat()
    html = build_dashboard_html(run, prd_markdown, generated_at)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "dashboard.html").write_text(html, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="AQABSI test-run JSON manifest")
    parser.add_argument("output", type=Path, help="Directory to receive dashboard.html")
    parser.add_argument("--prd", type=Path, help="Optional PRD Markdown file to render")
    parser.add_argument("--prd-json", type=Path, help="Optional PRD JSON file to render")
    args = parser.parse_args()
    try:
        generate(args.input.resolve(), args.output.resolve(), args.prd, args.prd_json)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"AQABSI dashboard generation failed: {exc}", file=sys.stderr)
        return 2
    print(f"Generated AQABSI dashboard in {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
