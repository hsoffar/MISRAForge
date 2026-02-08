from __future__ import annotations

from pathlib import Path

import yaml

from misra_checker.core.models import DeviationRecord, Finding, FindingStatus


def load_deviations(path: str | None) -> dict[str, DeviationRecord]:
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        return {}

    raw = yaml.safe_load(p.read_text(encoding="utf-8")) or []
    deviations: dict[str, DeviationRecord] = {}
    for item in raw:
        if not isinstance(item, dict):
            continue
        fp = item.get("finding_fingerprint")
        just = item.get("justification")
        if isinstance(fp, str) and isinstance(just, str):
            deviations[fp] = DeviationRecord(
                finding_fingerprint=fp,
                justification=just,
                approved_by=item.get("approved_by", ""),
            )
    return deviations


def apply_deviations(findings: list[Finding], deviations: dict[str, DeviationRecord]) -> None:
    for finding in findings:
        if finding.fingerprint not in deviations:
            continue
        if finding.status == FindingStatus.SUPPRESSED:
            continue
        finding.status = FindingStatus.DEVIATION
        finding.extra["deviation_justification"] = deviations[finding.fingerprint].justification
