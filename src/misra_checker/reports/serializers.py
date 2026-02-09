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
    by_rule = _count_by(result, "rule_id")
    by_status = _count_by(result, "status")
    by_file = _count_by_path(result)
    available_rules = sorted(set(result.available_rule_ids))
    rules_with_findings = sorted(by_rule.keys())
    coverage_pct = 0.0
    if available_rules:
        coverage_pct = (len(rules_with_findings) / len(available_rules)) * 100.0

    return {
        "scan_id": result.scan_id,
        "started_at": result.started_at,
        "finished_at": result.finished_at,
        "analyzed_files": result.analyzed_files,
        "parse_diagnostics": result.parse_diagnostics,
        "findings": [finding_to_dict(item) for item in result.findings],
        "summary": {
            "total_findings": len(result.findings),
            "by_status": by_status,
            "by_rule": by_rule,
            "by_file": by_file,
            "rule_coverage": {
                "available_rules": available_rules,
                "total_available_rules": len(available_rules),
                "rules_with_findings": rules_with_findings,
                "rules_with_findings_count": len(rules_with_findings),
                "rule_detection_coverage_pct": round(coverage_pct, 2),
            },
        },
    }


def _count_by(result: ScanResult, field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for finding in result.findings:
        value = getattr(finding, field)
        key = value.value if hasattr(value, "value") else str(value)
        counts[key] = counts.get(key, 0) + 1
    return counts


def _count_by_path(result: ScanResult) -> dict[str, int]:
    counts: dict[str, int] = {}
    for finding in result.findings:
        key = finding.location.path
        counts[key] = counts.get(key, 0) + 1
    return counts
