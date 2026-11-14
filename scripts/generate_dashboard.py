#!/usr/bin/env python3
"""Generate a self-contained, sanitized AQABSI HTML dashboard from a run manifest.

The dashboard embeds the sanitized run data as JSON and renders summary cards,
a findings banner, a filterable/searchable test-case table grouped by module,
a requirement x status coverage heatmap, and an optional PRD section rendered
from Markdown. No secrets, tokens, or passwords are written to the output.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from generate_artifacts import sanitize, validate_manifest


STATUSES = ("pass", "fail", "blocked", "skipped", "not_run", "flaky", "environment_error")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_prd_markdown(prd_path: Path | None) -> str:
    if prd_path is None:
        return ""
    return _read_text(prd_path)


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


def _embed(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def build_dashboard_html(run: dict[str, Any], prd_markdown: str, generated_at: str) -> str:
    payload = {"run": run, "prd_markdown": prd_markdown, "generated_at": generated_at}
    return HTML_TEMPLATE.replace("__AQABSI_DATA__", _embed(payload))


HTML_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AQABSI QA Dashboard</title>
<style>
  /* TestSprite-style · cool white + cyan · AQABSI QA dashboard · app screen */
  :root {
    --bg: #f8fafc;
    --surface: #ffffff;
    --surface-2: #f1f5f9;
    --border: #e2e8f0;
    --border-strong: #cbd5e1;
    --text: #0f172a;
    --muted: #64748b;
    --faint: #94a3b8;
    --accent: #0891b2;
    --accent-strong: #0e7490;
    --accent-soft: #ecfeff;
    --pass: #16a34a;
    --fail: #dc2626;
    --blocked: #d97706;
    --skipped: #64748b;
    --not_run: #94a3b8;
    --flaky: #7c3aed;
    --environment_error: #ea580c;
    --radius: 12px;
    --shadow: 0 1px 2px rgba(15,23,42,.05), 0 1px 3px rgba(15,23,42,.07);
    --shadow-lg: 0 4px 12px rgba(15,23,42,.08);
    --sans: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    --mono: "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  }
  * { box-sizing: border-box; }
  html, body { overflow-x: clip; }
  body {
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font-family: var(--sans);
    font-size: 16px;
    line-height: 1.55;
    -webkit-font-smoothing: antialiased;
    text-rendering: optimizeLegibility;
  }
  body::before {
    content: "";
    position: fixed; inset: 0 0 auto 0; height: 3px;
    background: linear-gradient(90deg, var(--accent), #22d3ee 55%, var(--accent-strong));
    z-index: 10;
  }
  .wrap { max-width: 1200px; margin: 0 auto; padding: 44px 28px 80px; }
  header { border-bottom: 1px solid var(--border); padding-bottom: 22px; margin-bottom: 30px; }
  header h1 { margin: 0 0 10px; font-size: 1.6rem; font-weight: 700; letter-spacing: -0.025em; }
  header h1 .kicker { color: var(--accent); }
  .meta { display: flex; flex-wrap: wrap; gap: 6px 16px; color: var(--muted); font-size: 0.875rem; }
  .meta code { color: var(--text); background: var(--surface-2); border: 1px solid var(--border); padding: 1px 7px; border-radius: 6px; font-family: var(--mono); font-size: 0.82rem; }
  h2 { font-size: 0.95rem; font-weight: 650; margin: 36px 0 14px; color: var(--text); letter-spacing: -0.01em; }
  h2 .rule { display: inline-block; width: 18px; height: 3px; background: var(--accent); border-radius: 2px; margin-right: 9px; vertical-align: middle; }
  .cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(148px, 1fr)); gap: 14px; }
  .card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 18px 20px; box-shadow: var(--shadow); }
  .card .num { font-size: 1.9rem; font-weight: 700; line-height: 1.1; font-variant-numeric: tabular-nums; letter-spacing: -0.02em; }
  .card .lbl { color: var(--muted); font-size: 0.82rem; margin-top: 6px; }
  .banner { border-radius: var(--radius); padding: 16px 20px; margin: 18px 0 0; border: 1px solid var(--border); font-size: 0.9rem; box-shadow: var(--shadow); }
  .banner.danger { background: #fef2f2; border-color: #fecaca; }
  .banner.warning { background: #fffbeb; border-color: #fde68a; }
  .banner.ok { background: #f0fdf4; border-color: #bbf7d0; }
  .banner .b-title { font-weight: 650; margin-bottom: 5px; }
  .controls { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; margin: 18px 0; }
  .controls input[type="search"] {
    flex: 1 1 280px; background: var(--surface); border: 1px solid var(--border); border-radius: 8px;
    color: var(--text); padding: 10px 14px; font-size: 0.9rem; font-family: var(--sans); box-shadow: var(--shadow);
  }
  .controls input[type="search"]:focus-visible,
  .controls select:focus-visible { outline: 2px solid var(--accent); outline-offset: 1px; border-color: var(--accent); }
  .controls select { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; color: var(--text); padding: 10px 12px; font-size: 0.88rem; font-family: var(--sans); box-shadow: var(--shadow); }
  .filters { display: flex; flex-wrap: wrap; gap: 8px; }
  .filter-btn {
    background: var(--surface); border: 1px solid var(--border); color: var(--muted);
    border-radius: 999px; padding: 6px 14px; font-size: 0.8rem; cursor: pointer; font-family: var(--sans); box-shadow: var(--shadow);
  }
  .filter-btn.active { color: #ffffff; border-color: transparent; font-weight: 600; }
  .filter-btn:focus-visible { outline: 2px solid var(--accent); outline-offset: 1px; }
  .module-group { margin: 22px 0 8px; }
  .module-group .mod-head { display: flex; align-items: baseline; gap: 10px; }
  .module-group .mod-name { font-weight: 650; color: var(--accent-strong); }
  .module-group .mod-count { color: var(--faint); font-size: 0.8rem; }
  table { width: 100%; border-collapse: collapse; font-size: 0.84rem; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); box-shadow: var(--shadow); }
  th, td { text-align: left; padding: 10px 12px; border-bottom: 1px solid var(--border); vertical-align: top; }
  thead th { background: var(--surface-2); }
  th { color: var(--muted); font-weight: 600; font-size: 0.76rem; }
  tbody tr:last-child td { border-bottom: none; }
  td.id, td.status, td.sev { white-space: nowrap; }
  code { font-family: var(--mono); font-size: 0.85em; }
  .pill { display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 0.74rem; font-weight: 600; }
  .pill.pass { background: #dcfce7; color: var(--pass); }
  .pill.fail { background: #fee2e2; color: var(--fail); }
  .pill.blocked { background: #fef3c7; color: var(--blocked); }
  .pill.skipped { background: #e2e8f0; color: var(--skipped); }
  .pill.not_run { background: #f1f5f9; color: var(--not_run); }
  .pill.flaky { background: #ede9fe; color: var(--flaky); }
  .pill.environment_error { background: #ffedd5; color: var(--environment_error); }
  .domain { display: inline-block; padding: 2px 8px; border-radius: 6px; font-size: 0.72rem; font-weight: 600; }
  .domain-be { background: #cffafe; color: #0e7490; }
  .domain-fe { background: #dbeafe; color: #1d4ed8; }
  .domain-both { background: #ede9fe; color: #7c3aed; }
  .heatmap { display: grid; gap: 3px; width: 100%; }
  .heatmap .h-row { display: grid; gap: 3px; align-items: center; }
  .heatmap .h-cell { padding: 7px 8px; border-radius: 7px; text-align: center; font-size: 0.8rem; min-width: 48px; font-variant-numeric: tabular-nums; }
  .heatmap .h-label { color: var(--muted); font-size: 0.82rem; padding-right: 8px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .heatmap .h-head { color: var(--muted); font-size: 0.72rem; text-align: center; }
  .prd { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 24px 28px; font-size: 0.9rem; box-shadow: var(--shadow); }
  .prd h1 { font-size: 1.35rem; }
  .prd h2 { margin-top: 24px; }
  .prd table { font-size: 0.8rem; box-shadow: none; }
  .prd th, .prd td { padding: 8px 10px; }
  .prd pre { background: var(--surface-2); border: 1px solid var(--border); border-radius: 8px; padding: 12px; overflow-x: auto; }
  .prd code { color: var(--accent-strong); }
  footer { color: var(--muted); font-size: 0.8rem; border-top: 1px solid var(--border); margin-top: 56px; padding-top: 18px; }
  .tabs { display: flex; gap: 4px; border-bottom: 1px solid var(--border); margin: 28px 0 8px; }
  .tab-btn { background: transparent; border: none; border-bottom: 2px solid transparent; color: var(--muted); padding: 10px 18px; font-size: 0.9rem; cursor: pointer; margin-bottom: -1px; font-family: var(--sans); }
  .tab-btn.active { color: var(--text); border-bottom-color: var(--accent); font-weight: 650; }
  .tab-btn:focus-visible { outline: 2px solid var(--accent); outline-offset: 1px; border-radius: 6px; }
  .evidence { margin-top: 6px; display: flex; flex-direction: column; gap: 2px; }
  .evidence .ev-line { font-size: 0.74rem; color: var(--muted); line-height: 1.45; font-family: var(--mono); white-space: pre-wrap; word-break: break-word; padding-left: 8px; border-left: 2px solid var(--border-strong); }
  .log-entry { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px 20px; margin-bottom: 12px; box-shadow: var(--shadow); }
  .log-entry .log-head { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; font-size: 0.84rem; }
  .log-entry .log-head .log-meta { color: var(--muted); }
  .log-entry .log-actual { margin-top: 7px; font-size: 0.84rem; }
  .case-row { cursor: pointer; user-select: none; }
  .case-row:hover td { background: var(--surface-2); }
  .caret { display: inline-block; width: 12px; color: var(--muted); }
  .detail-row td { background: var(--surface-2); padding: 0; border-bottom: 1px solid var(--border); }
  .detail { padding: 16px 20px 18px; display: flex; flex-direction: column; gap: 15px; }
  .detail-section .detail-title { font-size: 0.78rem; color: var(--muted); margin-bottom: 7px; font-weight: 600; }
  .detail-section ol, .detail-section ul { margin: 0; padding-left: 20px; font-size: 0.82rem; }
  .detail-section li { margin: 3px 0; }
  .detail-section .ev-line { border-left: none; padding-left: 0; }
  .actual-box { border: 1px solid var(--border); border-radius: 8px; padding: 11px 14px; font-size: 0.84rem; background: var(--surface); white-space: pre-wrap; word-break: break-word; }
  .actual-box.danger { background: #fef2f2; border-color: #fecaca; color: var(--fail); }
  .muted { color: var(--muted); }
  .empty { color: var(--muted); padding: 18px 0; }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1 id="title">AQABSI QA Dashboard</h1>
    <div class="meta" id="meta"></div>
  </header>

  <h2>Summary</h2>
  <div class="cards" id="cards"></div>
  <div id="banner"></div>

  <h2>Coverage matrix</h2>
  <div id="coverage"></div>

  <div class="tabs" id="tabs">
    <button class="tab-btn active" data-tab="cases">Test Cases</button>
    <button class="tab-btn" data-tab="log">Log Report</button>
  </div>

  <div id="panel-cases" class="panel">
    <div class="controls">
      <input type="search" id="search" placeholder="Search id, module, feature, scenario, expected, actual...">
      <select id="moduleSelect"><option value="__ALL__">All modules</option></select>
    </div>
    <div class="filters" id="filters"></div>
    <div id="cases"></div>
  </div>

  <div id="panel-log" class="panel" style="display:none;">
    <div id="logs"></div>
  </div>

  <section id="prdSection" style="display:none;">
    <h2>PRD</h2>
    <div class="prd" id="prd"></div>
  </section>

  <footer id="footer"></footer>
</div>

<script id="aqabsi-data" type="application/json">__AQABSI_DATA__</script>
<script>
(function () {
  const data = JSON.parse(document.getElementById('aqabsi-data').textContent);
  const run = data.run || {};
  const cases = (run.test_cases || []).slice();
  const STATUSES = ['pass','fail','blocked','skipped','not_run','flaky','environment_error'];
  const STATUS_META = {
    pass: {label:'Pass', color:'#16a34a'},
    fail: {label:'Fail', color:'#dc2626'},
    blocked: {label:'Blocked', color:'#d97706'},
    skipped: {label:'Skipped', color:'#64748b'},
    not_run: {label:'Not run', color:'#94a3b8'},
    flaky: {label:'Flaky', color:'#7c3aed'},
    environment_error: {label:'Env error', color:'#ea580c'}
  };
  const counts = {};
  STATUSES.forEach(s => counts[s] = 0);
  cases.forEach(c => { counts[c.status] = (counts[c.status] || 0) + 1; });

  function esc(s){ return String(s == null ? '' : s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
  function pill(status){
    const m = STATUS_META[status] || {label: status, color:'#64748b'};
    return '<span class="pill ' + esc(status) + '">' + esc(m.label) + '</span>';
  }
  function domainValue(c){
    const explicit = c.domain || c.tag;
    if (explicit) {
      const value = String(explicit);
      return value.toLowerCase() === 'both' ? 'both' : value.toUpperCase();
    }
    return ['component','e2e','accessibility','usability','compatibility'].includes(c.layer) ? 'FE' : 'BE';
  }
  function domainBadge(c){
    const value = domainValue(c);
    const cls = value === 'FE' ? 'domain-fe' : (value === 'both' ? 'domain-both' : 'domain-be');
    return '<span class="domain ' + cls + '">' + esc(value) + '</span>';
  }

  document.getElementById('title').textContent = run.title || 'AQABSI QA Dashboard';
  const src = run.source || {};
  document.getElementById('meta').innerHTML =
    '<span class="meta-item">Run <code>' + esc(run.run_id) + '</code></span>' +
    '<span class="meta-item">' + esc(run.module) + '</span>' +
    '<span class="meta-item">' + esc(run.environment) + '</span>' +
    (run.target ? '<span class="meta-item">target ' + esc(run.target) + '</span>' : '') +
    '<span class="meta-item">commit <code>' + esc(src.commit_sha || '—') + '</code></span>' +
    '<span class="meta-item">' + esc(src.repository || '') + '</span>';

  const cardsEl = document.getElementById('cards');
  const order = ['total'].concat(STATUSES);
  const cardData = {
    total: {label: 'Total', color: '#0891b2', value: cases.length},
    pass: {label: 'Pass', color: '#16a34a', value: counts.pass},
    fail: {label: 'Fail', color: '#dc2626', value: counts.fail},
    blocked: {label: 'Blocked', color: '#d97706', value: counts.blocked},
    skipped: {label: 'Skipped', color: '#64748b', value: counts.skipped},
    not_run: {label: 'Not run', color: '#94a3b8', value: counts.not_run},
    flaky: {label: 'Flaky', color: '#7c3aed', value: counts.flaky},
    environment_error: {label: 'Env error', color: '#ea580c', value: counts.environment_error}
  };
  cardsEl.innerHTML = order.map(k => {
    const d = cardData[k];
    return '<div class="card"><div class="num" style="color:' + d.color + '">' + d.value +
      '</div><div class="lbl">' + esc(d.label) + '</div></div>';
  }).join('');

  const banner = document.getElementById('banner');
  const fails = cases.filter(c => c.status === 'fail');
  const blocked = cases.filter(c => c.status === 'blocked');
  const important = fails.filter(c => c.severity === 'critical' || c.severity === 'high');
  if (important.length) {
    banner.innerHTML = '<div class="banner danger"><div class="b-title">Important failures</div>' +
      important.map(c => '<div>' + esc(c.id) + ' — ' + esc(c.scenario) + '</div>').join('') + '</div>';
  } else if (fails.length || blocked.length) {
    const items = fails.concat(blocked);
    banner.innerHTML = '<div class="banner warning"><div class="b-title">Findings requiring triage</div>' +
      items.slice(0, 12).map(c => '<div>' + esc(c.id) + ' (' + esc(c.status) + ') — ' + esc(c.scenario) + '</div>').join('') +
      (items.length > 12 ? '<div>+' + (items.length - 12) + ' more</div>' : '') + '</div>';
  } else if (cases.some(c => c.status === 'pass')) {
    banner.innerHTML = '<div class="banner ok"><div class="b-title">No confirmed failures</div>' +
      'Executed cases passed; remaining cases were not executed or are pending triage.</div>';
  } else {
    banner.innerHTML = '<div class="banner"><div class="b-title">Not executed</div>This run has not been executed yet.</div>';
  }

  const moduleSelect = document.getElementById('moduleSelect');
  const modules = Array.from(new Set(cases.map(c => c.module || 'Uncategorized')));
  modules.forEach(m => {
    const opt = document.createElement('option');
    opt.value = m; opt.textContent = m;
    moduleSelect.appendChild(opt);
  });

  const filtersEl = document.getElementById('filters');
  const active = new Set(STATUSES);
  STATUSES.forEach(s => {
    const m = STATUS_META[s];
    const btn = document.createElement('button');
    btn.className = 'filter-btn active';
    btn.style.setProperty('--fc', m.color);
    btn.textContent = m.label + ' (' + counts[s] + ')';
    btn.onclick = () => {
      if (active.has(s)) { active.delete(s); btn.classList.remove('active'); }
      else { active.add(s); btn.classList.add('active'); }
      btn.classList.contains('active') ? btn.style.background = m.color : btn.style.background = '';
      renderCases();
    };
    btn.style.background = m.color;
    filtersEl.appendChild(btn);
  });

  function matchesSearch(c, q) {
    if (!q) return true;
    q = q.toLowerCase();
    const hay = [c.id, c.module, c.feature, c.scenario, c.expected_result, c.actual_result,
      (c.steps || []).join(' '), (c.requirement_ids || []).join(' ')].join(' ').toLowerCase();
    return hay.includes(q);
  }

  function renderCases() {
    const q = document.getElementById('search').value.trim();
    const mod = moduleSelect.value;
    const el = document.getElementById('cases');
    const visible = cases.filter(c => active.has(c.status) && matchesSearch(c, q) &&
      (mod === '__ALL__' || (c.module || 'Uncategorized') === mod));
    if (!visible.length) { el.innerHTML = '<div class="empty">No test cases match the current filters.</div>'; return; }
    const groups = {};
    visible.forEach(c => { const k = c.module || 'Uncategorized'; (groups[k] = groups[k] || []).push(c); });
    let html = '';
    Object.keys(groups).sort().forEach(mod => {
      const list = groups[mod];
      html += '<div class="module-group"><div class="mod-head"><span class="mod-name">' + esc(mod) +
        '</span><span class="mod-count">' + list.length + ' case(s)</span></div></div>';
      html += '<table><thead><tr><th>ID</th><th>Requirement</th><th>Feature</th><th>Layer</th><th>Domain</th>' +
        '<th>Scenario</th><th>Expected</th><th>Actual</th><th>Status</th><th>Severity</th></tr></thead><tbody>';
      list.forEach(c => {
        html += '<tr class="case-row"><td class="id"><code><span class="caret">▸</span> ' + esc(c.id) + '</code></td>' +
          '<td>' + esc((c.requirement_ids || []).join(', ') || '—') + '</td>' +
          '<td>' + esc(c.feature || '—') + '</td>' +
          '<td>' + esc(c.layer) + '</td>' +
          '<td>' + domainBadge(c) + '</td>' +
          '<td>' + esc(c.scenario) + '</td>' +
          '<td>' + esc(c.expected_result) + '</td>' +
          '<td><div>' + esc(c.actual_result || '—') + '</div>' + evidenceBlock(c) + '</td>' +
          '<td class="status">' + pill(c.status) + '</td>' +
          '<td class="sev">' + esc(c.severity || '—') + '</td></tr>' + detailRow(c);
      });
      html += '</tbody></table>';
    });
    el.innerHTML = html;
  }

  function detailRow(c) {
    const steps = (c.steps || []).filter(Boolean);
    const evidence = (c.evidence || []).filter(Boolean);
    const danger = ['fail', 'blocked', 'environment_error'].includes(c.status);
    const stepsHtml = steps.length
      ? '<ol>' + steps.map(s => '<li>' + esc(s) + '</li>').join('') + '</ol>'
      : '<div class="muted">Not recorded</div>';
    const evidenceHtml = evidence.length
      ? '<ul>' + evidence.map(e => '<li class="ev-line">' + esc(e) + '</li>').join('') + '</ul>'
      : '<div class="muted">Not recorded</div>';
    const actualHtml = '<div class="actual-box' + (danger ? ' danger' : '') + '">' + esc(c.actual_result || '—') + '</div>';
    return '<tr class="detail-row" style="display:none"><td colspan="10"><div class="detail">' +
      '<div class="detail-section"><div class="detail-title">Steps</div>' + stepsHtml + '</div>' +
      '<div class="detail-section"><div class="detail-title">Execution log / Evidence</div>' + evidenceHtml + '</div>' +
      '<div class="detail-section"><div class="detail-title">Hasil &amp; Alasan</div>' + actualHtml + '</div>' +
      '</div></td></tr>';
  }

  function evidenceBlock(c) {
    const ev = (c.evidence || []).filter(Boolean);
    if (!ev.length) return '';
    return '<div class="evidence">' + ev.map(line => '<div class="ev-line">' + esc(line) + '</div>').join('') + '</div>';
  }

  function renderLogs() {
    const el = document.getElementById('logs');
    const withLogs = cases.filter(c => (c.evidence && c.evidence.length) || c.actual_result);
    if (!withLogs.length) {
      el.innerHTML = '<div class="empty">No execution logs recorded for this run.</div>';
      return;
    }
    el.innerHTML = withLogs.map(c => {
      const ev = (c.evidence || []).filter(Boolean);
      return '<div class="log-entry">' +
        '<div class="log-head"><code>' + esc(c.id) + '</code>' + pill(c.status) + domainBadge(c) +
        '<span class="log-meta">' + esc(c.module || '') + (c.feature ? ' / ' + esc(c.feature) : '') + '</span></div>' +
        '<div class="log-actual">' + esc(c.actual_result || '—') + '</div>' +
        (ev.length ? '<div class="evidence">' + ev.map(line => '<div class="ev-line">' + esc(line) + '</div>').join('') + '</div>' : '') +
        '</div>';
    }).join('');
  }

  function renderCoverage() {
    const el = document.getElementById('coverage');
    const reqs = Array.from(new Set(cases.flatMap(c => c.requirement_ids || []))).sort();
    if (!reqs.length) { el.innerHTML = '<div class="empty">No requirement traceability recorded for this run.</div>'; return; }
    const cols = STATUSES.filter(s => counts[s] > 0 || s === 'fail');
    let html = '<div class="heatmap">';
    html += '<div class="h-row" style="grid-template-columns: 220px repeat(' + cols.length + ', 1fr);">' +
      '<div class="h-head h-label">Requirement</div>' +
      cols.map(s => '<div class="h-head" style="color:' + STATUS_META[s].color + '">' + esc(STATUS_META[s].label) + '</div>').join('') +
      '</div>';
    reqs.forEach(r => {
      html += '<div class="h-row" style="grid-template-columns: 220px repeat(' + cols.length + ', 1fr);">' +
        '<div class="h-label">' + esc(r) + '</div>';
      cols.forEach(s => {
        const n = cases.filter(c => (c.requirement_ids || []).includes(r) && c.status === s).length;
        const color = STATUS_META[s].color;
        const bg = n ? color + '1a' : 'transparent';
        const border = n ? color + '4d' : 'var(--border)';
        const fg = n ? color : 'var(--muted)';
        html += '<div class="h-cell" style="background:' + bg + '; border:1px solid ' + border + '; color:' + fg + '">' + (n || '') + '</div>';
      });
      html += '</div>';
    });
    html += '</div>';
    el.innerHTML = html;
  }

  document.getElementById('search').addEventListener('input', renderCases);
  moduleSelect.addEventListener('change', renderCases);

  document.getElementById('cases').addEventListener('click', (event) => {
    const row = event.target.closest('.case-row');
    if (!row) return;
    const detail = row.nextElementSibling;
    if (!detail || !detail.classList.contains('detail-row')) return;
    const isHidden = detail.style.display === 'none';
    detail.style.display = isHidden ? '' : 'none';
    const caret = row.querySelector('.caret');
    if (caret) caret.textContent = isHidden ? '▾' : '▸';
  });

  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(other => other.classList.toggle('active', other === btn));
      const target = btn.getAttribute('data-tab');
      document.getElementById('panel-cases').style.display = target === 'cases' ? '' : 'none';
      document.getElementById('panel-log').style.display = target === 'log' ? '' : 'none';
    });
  });

  const prdSection = document.getElementById('prdSection');
  if (data.prd_markdown) {
    prdSection.style.display = 'block';
    document.getElementById('prd').innerHTML = renderMarkdown(data.prd_markdown);
  }

  document.getElementById('footer').textContent =
    'Sanitized draft generated ' + esc(data.generated_at || '') +
    '. Publishing and assignment require explicit authorization.';

  function escapeHtml(s){ return String(s == null ? '' : s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
  function inlineMd(s){
    s = escapeHtml(s);
    s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    s = s.replace(/`([^`]+)`/g, '<code>$1</code>');
    return s;
  }
  function renderMarkdown(md){
    if (!md) return '';
    const lines = md.split(/\r?\n/);
    const out = [];
    let i = 0, inCode = false;
    while (i < lines.length) {
      const line = lines[i];
      if (inCode) {
        if (/^\s*```/.test(line)) { inCode = false; out.push('</code></pre>'); }
        else out.push(escapeHtml(line));
        i++; continue;
      }
      if (/^\s*```/.test(line)) { inCode = true; out.push('<pre><code>'); i++; continue; }
      const h = line.match(/^\s*(#{1,6})\s+(.*)$/);
      if (h) { const lvl = h[1].length; out.push('<h' + lvl + '>' + inlineMd(h[2]) + '</h' + lvl + '>'); i++; continue; }
      if (/^\s*$/.test(line)) { i++; continue; }
      if (line.trim().startsWith('|') && i + 1 < lines.length && /^\s*\|?[\s:|-]+\|?\s*$/.test(lines[i+1]) && lines[i+1].includes('-')) {
        const header = line.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map(c => '<th>' + inlineMd(c.trim()) + '</th>').join('');
        let html = '<table><thead><tr>' + header + '</tr></thead><tbody>';
        i += 2;
        while (i < lines.length && lines[i].trim().startsWith('|')) {
          const cells = lines[i].trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map(c => '<td>' + inlineMd(c.trim()) + '</td>').join('');
          html += '<tr>' + cells + '</tr>';
          i++;
        }
        html += '</tbody></table>';
        out.push(html); continue;
      }
      if (/^\s*[-*+]\s+/.test(line)) {
        out.push('<ul>');
        while (i < lines.length && /^\s*[-*+]\s+/.test(lines[i])) {
          out.push('<li>' + inlineMd(lines[i].replace(/^\s*[-*+]\s+/, '')) + '</li>');
          i++;
        }
        out.push('</ul>'); continue;
      }
      if (/^\s*\d+\.\s+/.test(line)) {
        out.push('<ol>');
        while (i < lines.length && /^\s*\d+\.\s+/.test(lines[i])) {
          out.push('<li>' + inlineMd(lines[i].replace(/^\s*\d+\.\s+/, '')) + '</li>');
          i++;
        }
        out.push('</ol>'); continue;
      }
      out.push('<p>' + inlineMd(line) + '</p>');
      i++;
    }
    if (inCode) out.push('</code></pre>');
    return out.join('');
  }

  renderCoverage();
  renderCases();
  renderLogs();
})();
</script>
</body>
</html>
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

    prd_markdown = load_prd_markdown(prd_path)
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
