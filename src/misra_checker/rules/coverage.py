from __future__ import annotations

import json
from pathlib import Path

from misra_checker.registry.rule_registry import build_default_registry
from misra_checker.rules.engine import RuleEngine


def load_scan_payload(scan_json: str | None) -> dict[str, object]:
    if not scan_json:
        return {}
    path = Path(scan_json)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_rule_matrix(scan_payload: dict[str, object] | None = None, tests_dir: str = "tests") -> dict[str, object]:
    payload = scan_payload or {}
    summary = payload.get("summary", {}) if isinstance(payload, dict) else {}
    by_rule = summary.get("by_rule", {}) if isinstance(summary, dict) else {}
    by_rule_counts = by_rule if isinstance(by_rule, dict) else {}

    registry = build_default_registry()
    metas = registry.all()
    engine = RuleEngine(registry)
    implemented_ids = {rule.metadata.rule_id for rule in engine.rules}
    test_refs = _collect_test_references(tests_dir, [meta.rule_id for meta in metas])

    rows: list[dict[str, object]] = []
    for meta in metas:
        detected_count = int(by_rule_counts.get(meta.rule_id, 0) or 0)
        files = sorted(test_refs.get(meta.rule_id, []))
        rows.append(
            {
                "rule_id": meta.rule_id,
                "title": meta.title,
                "category": meta.category,
                "level": meta.level.value,
                "languages": [lang.value for lang in meta.languages],
                "implemented": meta.rule_id in implemented_ids,
                "tested": bool(files),
                "test_files": files,
                "detected_in_scan": detected_count > 0,
                "detected_count": detected_count,
            }
        )

    total = len(rows)
    implemented = sum(1 for row in rows if row["implemented"])
    tested = sum(1 for row in rows if row["tested"])
    detected = sum(1 for row in rows if row["detected_in_scan"])
    fully_covered = sum(1 for row in rows if row["implemented"] and row["tested"])
    return {
        "totals": {
            "rules_total": total,
            "implemented_count": implemented,
            "implemented_pct": _pct(implemented, total),
            "tested_count": tested,
            "tested_pct": _pct(tested, total),
            "detected_in_scan_count": detected,
            "detected_in_scan_pct": _pct(detected, total),
            "fully_covered_count": fully_covered,
            "fully_covered_pct": _pct(fully_covered, total),
        },
        "rules": rows,
    }


def _collect_test_references(tests_dir: str, rule_ids: list[str]) -> dict[str, set[str]]:
    refs: dict[str, set[str]] = {rule_id: set() for rule_id in rule_ids}
    root = Path(tests_dir)
    if not root.exists():
        return refs

    for path in sorted(root.rglob("*.py")):
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        for rule_id in rule_ids:
            if rule_id in text:
                refs[rule_id].add(str(path))
    return refs


def _pct(part: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round((part / total) * 100.0, 2)
