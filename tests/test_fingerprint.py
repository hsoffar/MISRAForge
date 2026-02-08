from __future__ import annotations

from misra_checker.core.models import Finding, Language, Severity, SourceLocation
from misra_checker.findings.fingerprint import finding_fingerprint


def test_fingerprint_stable() -> None:
    finding = Finding(
        rule_id="MC3R-FORBIDDEN-GOTO",
        message="goto usage detected",
        location=SourceLocation(path="main.c", line=10, column=5),
        language=Language.C,
        severity=Severity.MEDIUM,
        category="control_flow",
    )
    first = finding_fingerprint(finding)
    second = finding_fingerprint(finding)
    assert first == second
    assert len(first) == 16
