from __future__ import annotations

from dataclasses import dataclass, field

from misra_checker.core.models import Language, RuleLevel, RuleMetadata, Severity


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


DEFAULT_RULE_METADATA = [
    RuleMetadata(
        rule_id="MC3R-CAST-CSTYLE",
        title="Avoid C-style casts",
        category="type_safety",
        level=RuleLevel.REQUIRED,
        languages=(Language.CPP,),
        severity=Severity.MEDIUM,
        tags=("casts", "safety"),
        rationale_summary="C-style casts may hide unsafe or narrowing conversions.",
    ),
    RuleMetadata(
        rule_id="MC3R-FORBIDDEN-GOTO",
        title="Avoid goto",
        category="control_flow",
        level=RuleLevel.REQUIRED,
        languages=(Language.C, Language.CPP),
        severity=Severity.MEDIUM,
        tags=("control-flow",),
        rationale_summary="Unstructured jumps can reduce analyzability and maintainability.",
    ),
    RuleMetadata(
        rule_id="MC3A-MACRO-FUNC",
        title="Function-like macro usage review",
        category="preprocessor",
        level=RuleLevel.ADVISORY,
        languages=(Language.C, Language.CPP),
        severity=Severity.LOW,
        tags=("macros", "manual-review"),
        rationale_summary="Function-like macros can introduce side effects and hidden behavior.",
    ),
    RuleMetadata(
        rule_id="MC3R-FORBIDDEN-RECURSION",
        title="Recursion usage review",
        category="language_subset",
        level=RuleLevel.REQUIRED,
        languages=(Language.C, Language.CPP),
        severity=Severity.HIGH,
        tags=("recursion", "manual-review"),
        rationale_summary="Recursion can challenge bounded stack/resource analysis.",
    ),
    RuleMetadata(
        rule_id="MC3A-TAB-CHAR",
        title="Avoid tab characters",
        category="lexical_style",
        level=RuleLevel.ADVISORY,
        languages=(Language.C, Language.CPP),
        severity=Severity.INFO,
        tags=("style",),
        rationale_summary="Tabs reduce formatting consistency across tools.",
    ),
]


def build_default_registry() -> RuleRegistry:
    registry = RuleRegistry()
    for metadata in DEFAULT_RULE_METADATA:
        registry.register(metadata)
    return registry
