from __future__ import annotations

import csv
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

    rows = "\n".join(
        (
            f"<tr><td>{idx}</td><td>{f.rule_id}</td><td>{f.status.value}</td><td>{f.severity.value}</td>"
            f"<td>{f.location.path}:{f.location.line}:{f.location.column}</td><td>{f.message}</td>"
            f"<td>{f.recommendation}</td></tr>"
        )
        for idx, f in enumerate(result.findings, start=1)
    )

    html = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <title>MISRA Checker Report {result.scan_id}</title>
  <style>
    body {{ font-family: "DejaVu Sans", sans-serif; margin: 24px; background: #f7f9fc; color: #152238; }}
    h1 {{ margin-bottom: 8px; }}
    .meta {{ margin-bottom: 16px; }}
    table {{ border-collapse: collapse; width: 100%; background: #fff; }}
    th, td {{ border: 1px solid #d9e2ef; padding: 8px; text-align: left; font-size: 13px; }}
    th {{ background: #e9f0fa; }}
  </style>
</head>
<body>
  <h1>MISRA Checker MVP Report</h1>
  <div class=\"meta\">
    <div><strong>Scan ID:</strong> {result.scan_id}</div>
    <div><strong>Started:</strong> {result.started_at}</div>
    <div><strong>Finished:</strong> {result.finished_at}</div>
    <div><strong>Files analyzed:</strong> {len(result.analyzed_files)}</div>
    <div><strong>Total findings:</strong> {len(result.findings)}</div>
  </div>
  <table>
    <thead>
      <tr><th>#</th><th>Rule</th><th>Status</th><th>Severity</th><th>Location</th><th>Message</th><th>Recommendation</th></tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")
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
