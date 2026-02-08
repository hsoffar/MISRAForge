from __future__ import annotations

from fnmatch import fnmatch
from pathlib import Path

import yaml

from misra_checker.core.models import Finding, FindingStatus, SuppressionEntry


def load_suppressions(path: str | None) -> list[SuppressionEntry]:
    if not path:
        return []
    p = Path(path)
    if not p.exists():
        return []

    raw = yaml.safe_load(p.read_text(encoding="utf-8")) or []
    entries: list[SuppressionEntry] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        entries.append(
            SuppressionEntry(
                rule_id=item.get("rule_id"),
                path_pattern=item.get("path_pattern", "*"),
                line=item.get("line"),
                reason=item.get("reason", ""),
            )
        )
    return entries


def apply_suppressions(findings: list[Finding], suppressions: list[SuppressionEntry]) -> None:
    for finding in findings:
        for sup in suppressions:
            if sup.rule_id and sup.rule_id != finding.rule_id:
                continue
            if not fnmatch(finding.location.path, sup.path_pattern):
                continue
            if sup.line is not None and sup.line != finding.location.line:
                continue
            finding.status = FindingStatus.SUPPRESSED
            if sup.reason:
                finding.extra["suppression_reason"] = sup.reason
            break
