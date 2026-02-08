from __future__ import annotations

import json
from pathlib import Path

from misra_checker.core.models import BaselineEntry, Finding, FindingStatus


def load_baseline(path: str | None) -> dict[str, BaselineEntry]:
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        return {}
    raw = json.loads(p.read_text(encoding="utf-8"))
    entries = raw.get("entries", []) if isinstance(raw, dict) else []
    result: dict[str, BaselineEntry] = {}
    for item in entries:
        if not isinstance(item, dict):
            continue
        fp = item.get("fingerprint")
        rule_id = item.get("rule_id")
        path_value = item.get("path")
        if isinstance(fp, str) and isinstance(rule_id, str) and isinstance(path_value, str):
            result[fp] = BaselineEntry(fingerprint=fp, rule_id=rule_id, path=path_value)
    return result


def apply_baseline(findings: list[Finding], baseline: dict[str, BaselineEntry]) -> None:
    for finding in findings:
        if finding.status == FindingStatus.SUPPRESSED:
            continue
        if finding.fingerprint in baseline:
            finding.status = FindingStatus.BASELINE


def create_baseline_payload(findings: list[Finding]) -> dict[str, object]:
    entries = [
        {
            "fingerprint": item.fingerprint,
            "rule_id": item.rule_id,
            "path": item.location.path,
        }
        for item in findings
    ]
    return {"entries": entries}


def write_baseline(path: str | Path, findings: list[Finding]) -> str:
    payload = create_baseline_payload(findings)
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return str(out)
