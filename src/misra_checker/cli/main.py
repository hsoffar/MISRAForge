from __future__ import annotations

import argparse
import json
from pathlib import Path

from misra_checker import __version__
from misra_checker.baseline.service import write_baseline
from misra_checker.core.models import Finding, Language, ScanRequest, ScanTargetType, Severity, SourceLocation
from misra_checker.core.scan_service import ScanService
from misra_checker.storage.history import HistoryStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="misra-checker",
        description="Local MISRA-oriented static analysis MVP for C/C++.",
    )
    parser.add_argument("--version", action="store_true", help="Show version and exit")

    sub = parser.add_subparsers(dest="command")
    scan = sub.add_parser("scan", help="Run static analysis")
    scan_sub = scan.add_subparsers(dest="scan_mode", required=True)

    for mode in ("repo", "file"):
        p = scan_sub.add_parser(mode, help=f"Scan a {mode}")
        p.add_argument("target", help="Target path")
        p.add_argument("--config", help="Path to config YAML/JSON")
        p.add_argument("--output-dir", default="out", help="Report output directory")
        p.add_argument(
            "--format",
            dest="formats",
            action="append",
            choices=["json", "html", "csv"],
            default=[],
            help="Report format (repeatable)",
        )
        p.add_argument("--include-rule", action="append", default=[], help="Include rule ID")
        p.add_argument("--exclude-rule", action="append", default=[], help="Exclude rule ID")
        p.add_argument("--baseline-file", help="Baseline JSON file")
        p.add_argument("--suppression-file", help="Suppression YAML file")
        p.add_argument("--deviation-file", help="Deviation YAML file")
        p.add_argument("--history-db", help="SQLite path for scan history")

    baseline = sub.add_parser("baseline", help="Baseline operations")
    baseline_sub = baseline.add_subparsers(dest="baseline_cmd", required=True)
    create = baseline_sub.add_parser("create", help="Create baseline from a scan JSON report")
    create.add_argument("--scan-json", required=True, help="Path to JSON report from a scan")
    create.add_argument("--output", required=True, help="Output baseline JSON path")

    history = sub.add_parser("history", help="History operations")
    history_sub = history.add_subparsers(dest="history_cmd", required=True)
    trend = history_sub.add_parser("trend", help="Show scan trend")
    trend.add_argument("--db", default=".misra_checker/history.db", help="History SQLite file")
    trend.add_argument("--limit", type=int, default=10)

    return parser


def _run_scan(args: argparse.Namespace) -> int:
    target_type = ScanTargetType.REPOSITORY if args.scan_mode == "repo" else ScanTargetType.SINGLE_FILE

    request = ScanRequest(
        target=args.target,
        target_type=target_type,
        config_path=args.config,
        output_dir=args.output_dir,
        report_formats=tuple(args.formats or ["json", "html"]),
        include_rules=tuple(args.include_rule),
        exclude_rules=tuple(args.exclude_rule),
        baseline_file=args.baseline_file,
        suppression_file=args.suppression_file,
        deviation_file=args.deviation_file,
        history_db_path=args.history_db,
    )

    try:
        result, outputs = ScanService().run(request)
    except Exception as exc:
        print(f"Scan failed: {exc}")
        return 2

    print(f"Scan complete: {result.scan_id}")
    print(f"Analyzed files: {len(result.analyzed_files)}")
    print(f"Findings: {len(result.findings)}")
    if result.parse_diagnostics:
        print("Diagnostics:")
        for item in result.parse_diagnostics:
            print(f"  - {item}")
    if outputs:
        print("Reports:")
        for fmt, path in outputs.items():
            print(f"  - {fmt}: {path}")
    return 0


def _run_baseline_create(args: argparse.Namespace) -> int:
    report_path = Path(args.scan_json)
    if not report_path.exists():
        print(f"scan report does not exist: {report_path}")
        return 2

    payload = json.loads(report_path.read_text(encoding="utf-8"))
    findings_payload = payload.get("findings", [])
    findings: list[Finding] = []

    for item in findings_payload:
        try:
            findings.append(
                Finding(
                    rule_id=item["rule_id"],
                    message=item["message"],
                    location=SourceLocation(
                        path=item["location"]["path"],
                        line=int(item["location"]["line"]),
                        column=int(item["location"]["column"]),
                    ),
                    language=Language(item["language"]),
                    severity=Severity(item["severity"]),
                    category=item["category"],
                    fingerprint=item["fingerprint"],
                )
            )
        except Exception:
            continue

    output = write_baseline(args.output, findings)
    print(f"Baseline written: {output} ({len(findings)} entries)")
    return 0


def _run_history_trend(args: argparse.Namespace) -> int:
    rows = HistoryStore(args.db).trend(limit=args.limit)
    if not rows:
        print("No scan history found")
        return 0

    for row in rows:
        summary = row["summary"]
        print(
            f"{row['finished_at']} {row['scan_id']} total={row['total_findings']} "
            f"new={summary.get('new', 0)} baseline={summary.get('baseline', 0)} "
            f"suppressed={summary.get('suppressed', 0)} deviation={summary.get('deviation', 0)}"
        )
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.version:
        print(__version__)
        return 0

    if args.command == "scan":
        return _run_scan(args)

    if args.command == "baseline" and args.baseline_cmd == "create":
        return _run_baseline_create(args)

    if args.command == "history" and args.history_cmd == "trend":
        return _run_history_trend(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
