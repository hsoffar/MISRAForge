from __future__ import annotations

from misra_checker.core.models import (
    Finding,
    FindingStatus,
    Language,
    ScanResult,
    Severity,
    SourceLocation,
)
from misra_checker.reports.serializers import scan_result_to_dict


def test_summary_contains_file_and_rule_coverage_metrics() -> None:
    findings = [
        Finding(
            rule_id="MC3R-FORBIDDEN-GOTO",
            message="goto usage detected",
            location=SourceLocation(path="a.c", line=1, column=1),
            language=Language.C,
            severity=Severity.MEDIUM,
            category="control_flow",
            status=FindingStatus.CONFIRMED,
        ),
        Finding(
            rule_id="MC3A-TAB-CHAR",
            message="tab char",
            location=SourceLocation(path="a.c", line=2, column=1),
            language=Language.C,
            severity=Severity.INFO,
            category="lexical_style",
            status=FindingStatus.CONFIRMED,
        ),
    ]
    result = ScanResult(
        scan_id="scan-1",
        started_at="2026-02-06T00:00:00Z",
        finished_at="2026-02-06T00:01:00Z",
        findings=findings,
        analyzed_files=["a.c"],
        available_rule_ids=[
            "MC3R-FORBIDDEN-GOTO",
            "MC3A-TAB-CHAR",
            "MC3R-CAST-CSTYLE",
            "MC3A-MACRO-FUNC",
        ],
    )

    payload = scan_result_to_dict(result)
    summary = payload["summary"]
    assert summary["by_file"]["a.c"] == 2
    assert summary["by_rule"]["MC3R-FORBIDDEN-GOTO"] == 1
    assert summary["rule_coverage"]["total_available_rules"] == 4
    assert summary["rule_coverage"]["rules_with_findings_count"] == 2
    assert summary["rule_coverage"]["rule_detection_coverage_pct"] == 50.0

