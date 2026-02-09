from __future__ import annotations

from dataclasses import dataclass, field

from misra_checker.core.models import Language, RuleLevel, RuleMetadata, Severity
from misra_checker.rules.default_pack import load_default_pack


@dataclass
class RuleRegistry:
    _rules: dict[str, RuleMetadata] = field(default_factory=dict)

    def register(self, metadata: RuleMetadata) -> None:
        if metadata.rule_id in self._rules:
            raise ValueError(f"Duplicate rule id: {metadata.rule_id}")
        self._rules[metadata.rule_id] = metadata

    def get(self, rule_id: str) -> RuleMetadata:
        return self._rules[rule_id]

    def all(self) -> list[RuleMetadata]:
        return [self._rules[key] for key in sorted(self._rules.keys())]


def build_default_registry() -> RuleRegistry:
    registry = RuleRegistry()
    payload = load_default_pack()
    rules = payload.get("rules", [])
    for item in rules:
        if not isinstance(item, dict):
            continue
        metadata = RuleMetadata(
            rule_id=str(item["rule_id"]),
            title=str(item["title"]),
            category=str(item["category"]),
            level=RuleLevel(str(item.get("level", "required"))),
            languages=tuple(Language(str(lang)) for lang in item.get("languages", ["c", "cpp"])),
            severity=Severity(str(item.get("severity", "medium"))),
            tags=tuple(str(tag) for tag in item.get("tags", [])),
            rationale_summary=str(item.get("rationale_summary", "")),
        )
        registry.register(metadata)
    return registry
