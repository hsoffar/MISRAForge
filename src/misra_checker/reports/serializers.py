from __future__ import annotations

from dataclasses import asdict

from misra_checker.core.models import Finding, ScanResult


def finding_to_dict(finding: Finding) -> dict[str, object]:
    payload = asdict(finding)
    payload["language"] = finding.language.value
    payload["severity"] = finding.severity.value
    payload["status"] = finding.status.value
    return payload


def scan_result_to_dict(result: ScanResult) -> dict[str, object]:
    return {
        "scan_id": result.scan_id,
        "started_at": result.started_at,
        "finished_at": result.finished_at,
        "analyzed_files": result.analyzed_files,
        "parse_diagnostics": result.parse_diagnostics,
        "findings": [finding_to_dict(item) for item in result.findings],
        "summary": {
            "total_findings": len(result.findings),
            "by_status": _count_by(result, "status"),
            "by_rule": _count_by(result, "rule_id"),
        },
    }


def _count_by(result: ScanResult, field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for finding in result.findings:
        value = getattr(finding, field)
        key = value.value if hasattr(value, "value") else str(value)
        counts[key] = counts.get(key, 0) + 1
    return counts
