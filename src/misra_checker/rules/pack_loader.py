from __future__ import annotations

import json
import re
from pathlib import Path

from misra_checker.core.models import FindingStatus, Language, RuleLevel, RuleMetadata, Severity
from misra_checker.registry.rule_registry import RuleRegistry
from misra_checker.rules.base import Rule
from misra_checker.rules.regex_rule import RegexPatternRule


def load_rule_pack(
    pack_path: str,
    registry: RuleRegistry,
) -> tuple[list[Rule], dict[str, str]]:
    path = Path(pack_path)
    if not path.exists():
        raise ValueError(f"rule pack does not exist: {pack_path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    rules = payload.get("rules")
    if not isinstance(rules, list):
        raise ValueError("rule pack must include a top-level 'rules' list")

    out: list[Rule] = []
    recommendations: dict[str, str] = {}

    for item in rules:
        if not isinstance(item, dict):
            continue
        rule_id = _required_str(item, "rule_id")
        title = _required_str(item, "title")
        category = _required_str(item, "category")
        pattern = _required_str(item, "pattern")
        message = _required_str(item, "message")

        level = RuleLevel(str(item.get("level", "required")))
        severity = Severity(str(item.get("severity", "medium")))
        langs = tuple(Language(str(lang)) for lang in item.get("languages", ["c", "cpp"]))
        status = FindingStatus(str(item.get("status", "confirmed")))
        tags = tuple(str(x) for x in item.get("tags", []))
        rationale = str(item.get("rationale_summary", ""))
        recommendation = str(item.get("recommendation", "")).strip()

        metadata = RuleMetadata(
            rule_id=rule_id,
            title=title,
            category=category,
            level=level,
            languages=langs,
            severity=severity,
            tags=tags,
            rationale_summary=rationale,
        )
        registry.register(metadata)
        flags = _parse_flags(item.get("flags", []))
        out.append(
            RegexPatternRule(
                metadata=metadata,
                pattern=pattern,
                message=message,
                status=status,
                flags=flags,
            )
        )
        if recommendation:
            recommendations[rule_id] = recommendation

    return out, recommendations


def _required_str(item: dict[str, object], key: str) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"rule pack item missing valid '{key}'")
    return value.strip()


def _parse_flags(raw: object) -> int:
    if not isinstance(raw, list):
        return 0
    mapping = {
        "IGNORECASE": re.IGNORECASE,
        "MULTILINE": re.MULTILINE,
    }
    flags = 0
    for item in raw:
        if not isinstance(item, str):
            continue
        flags |= mapping.get(item.upper(), 0)
    return flags
