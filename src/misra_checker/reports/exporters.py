from __future__ import annotations

import csv
import html
import json
from pathlib import Path

from misra_checker.core.models import ScanResult
from misra_checker.reports.serializers import scan_result_to_dict


def export_json(result: ScanResult, out_path: str | Path) -> str:
    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = scan_result_to_dict(result)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return str(path)


def export_html(result: ScanResult, out_path: str | Path) -> str:
    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = scan_result_to_dict(result)
    payload_json = json.dumps(payload)
    started_at = html.escape(result.started_at)
    finished_at = html.escape(result.finished_at)
    total_files = len(result.analyzed_files)
    total_findings = len(result.findings)

    report_html = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <title>MISRA Checker Report</title>
  <style>
    :root {{
      --bg: #f4f8fc;
      --card: #ffffff;
      --ink: #0f172a;
      --muted: #4b5563;
      --accent: #0055a4;
      --line: #d6dfeb;
      --pill: #e6f0ff;
    }}
    body {{ font-family: "DejaVu Sans", sans-serif; margin: 0; background: var(--bg); color: var(--ink); }}
    .wrap {{ max-width: 1200px; margin: 0 auto; padding: 24px; }}
    h1 {{ margin: 0 0 8px 0; }}
    .sub {{ color: var(--muted); margin-bottom: 20px; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin: 16px 0 20px; }}
    .card {{ background: var(--card); border: 1px solid var(--line); border-radius: 10px; padding: 14px; }}
    .label {{ color: var(--muted); font-size: 12px; }}
    .value {{ font-size: 24px; font-weight: 700; margin-top: 4px; }}
    .panel {{ background: var(--card); border: 1px solid var(--line); border-radius: 10px; padding: 16px; margin-bottom: 16px; }}
    .toolbar {{ display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 12px; }}
    select, input {{ border: 1px solid var(--line); border-radius: 8px; padding: 8px; font-size: 13px; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 8px; text-align: left; font-size: 13px; vertical-align: top; }}
    th {{ background: #f8fbff; position: sticky; top: 0; }}
    .group-title {{ font-weight: 700; margin: 10px 0 6px; }}
    .pill {{ display: inline-block; background: var(--pill); color: var(--accent); border-radius: 999px; padding: 2px 8px; font-size: 11px; }}
  </style>
</head>
<body>
  <div class=\"wrap\">
    <h1>MISRA Checker Report</h1>
    <div class=\"sub\">Latest run | {started_at} -> {finished_at}</div>
    <div class=\"cards\">
      <div class=\"card\"><div class=\"label\">Files Analyzed</div><div class=\"value\">{total_files}</div></div>
      <div class=\"card\"><div class=\"label\">Total Findings</div><div class=\"value\">{total_findings}</div></div>
      <div class=\"card\"><div class=\"label\">Available Rules</div><div class=\"value\" id=\"metric-rules-total\">0</div></div>
      <div class=\"card\"><div class=\"label\">Rules Hit</div><div class=\"value\" id=\"metric-rules-hit\">0</div></div>
      <div class=\"card\"><div class=\"label\">Rule Coverage</div><div class=\"value\" id=\"metric-coverage\">0%</div></div>
    </div>
    <div class=\"panel\">
      <div class=\"toolbar\">
        <select id=\"groupBy\">
          <option value=\"file\">Group by file</option>
          <option value=\"rule\">Group by rule</option>
          <option value=\"flat\">Flat list</option>
        </select>
        <input id=\"search\" type=\"search\" placeholder=\"Filter by path, rule, message...\" />
      </div>
      <div id=\"content\"></div>
    </div>
    <div class=\"panel\">
      <span class=\"pill\">Status counts</span>
      <div id=\"statusCounts\" style=\"margin-top:10px\"></div>
    </div>
  </div>
  <script>
    const payload = {payload_json};
    const findings = payload.findings || [];
    const summary = payload.summary || {{}};
    const coverage = summary.rule_coverage || {{}};
    document.getElementById("metric-rules-total").textContent = coverage.total_available_rules || 0;
    document.getElementById("metric-rules-hit").textContent = coverage.rules_with_findings_count || 0;
    document.getElementById("metric-coverage").textContent = `${{coverage.rule_detection_coverage_pct || 0}}%`;

    const statusCounts = summary.by_status || {{}};
    const statusNode = document.getElementById("statusCounts");
    statusNode.textContent = Object.entries(statusCounts).map(([k, v]) => `${{k}}: ${{v}}`).join(" | ");

    const content = document.getElementById("content");
    const groupBy = document.getElementById("groupBy");
    const search = document.getElementById("search");

    function esc(s) {{
      return String(s)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;");
    }}

    function rowHtml(f) {{
      const loc = `${{f.location.path}}:${{f.location.line}}:${{f.location.column}}`;
      return `<tr>
        <td>${{esc(f.rule_id)}}</td>
        <td>${{esc(f.status)}}</td>
        <td>${{esc(f.severity)}}</td>
        <td>${{esc(loc)}}</td>
        <td>${{esc(f.message)}}</td>
        <td>${{esc(f.recommendation || "")}}</td>
      </tr>`;
    }}

    function tableHtml(items) {{
      if (!items.length) return "<div>No findings match current filters.</div>";
      return `<table>
        <thead><tr><th>Rule</th><th>Status</th><th>Severity</th><th>Location</th><th>Message</th><th>Recommendation</th></tr></thead>
        <tbody>${{items.map(rowHtml).join("")}}</tbody>
      </table>`;
    }}

    function render() {{
      const q = search.value.trim().toLowerCase();
      const mode = groupBy.value;
      const filtered = findings.filter((f) => {{
        if (!q) return true;
        return [
          f.rule_id,
          f.status,
          f.severity,
          f.location?.path,
          f.message,
          f.recommendation,
        ].join(" ").toLowerCase().includes(q);
      }});

      if (mode === "flat") {{
        content.innerHTML = tableHtml(filtered);
        return;
      }}

      const keyFn = mode === "rule"
        ? (f) => f.rule_id
        : (f) => f.location?.path || "unknown";
      const groups = new Map();
      for (const f of filtered) {{
        const key = keyFn(f);
        if (!groups.has(key)) groups.set(key, []);
        groups.get(key).push(f);
      }}

      const sections = [...groups.entries()]
        .sort((a, b) => a[0].localeCompare(b[0]))
        .map(([key, items]) => `<div class="group-title">${{esc(key)}} (${{items.length}})</div>${{tableHtml(items)}}`)
        .join("");
      content.innerHTML = sections || "<div>No findings match current filters.</div>";
    }}

    groupBy.addEventListener("change", render);
    search.addEventListener("input", render);
    render();
  </script>
</body>
</html>
"""
    path.write_text(report_html, encoding="utf-8")
    return str(path)


def export_csv(result: ScanResult, out_path: str | Path) -> str:
    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.writer(fp)
        writer.writerow(
            [
                "rule_id",
                "status",
                "severity",
                "path",
                "line",
                "column",
                "message",
                "recommendation",
                "fingerprint",
            ]
        )
        for item in result.findings:
            writer.writerow(
                [
                    item.rule_id,
                    item.status.value,
                    item.severity.value,
                    item.location.path,
                    item.location.line,
                    item.location.column,
                    item.message,
                    item.recommendation,
                    item.fingerprint,
                ]
            )
    return str(path)
