from __future__ import annotations

from dataclasses import dataclass

from misra_checker.core.models import Finding
from misra_checker.findings.fingerprint import finding_fingerprint
from misra_checker.parser.models import ParsedDocument
from misra_checker.registry.rule_registry import RuleRegistry
from misra_checker.rules.base import Rule
from misra_checker.rules.recommendations import recommendation_for
from misra_checker.rules.starter import (
    CStyleCastRule,
    GotoRule,
    MacroFunctionRule,
    RecursionRule,
    TabCharacterRule,
)


@dataclass(frozen=True)
class RuleFilter:
    include_ids: tuple[str, ...] = ()
    exclude_ids: tuple[str, ...] = ()
    categories: tuple[str, ...] = ()
    languages: tuple[str, ...] = ()
    levels: tuple[str, ...] = ()


def _build_rule_objects(registry: RuleRegistry) -> list[Rule]:
    metadata = {item.rule_id: item for item in registry.all()}
    return [
        GotoRule(metadata=metadata["MC3R-FORBIDDEN-GOTO"]),
        MacroFunctionRule(metadata=metadata["MC3A-MACRO-FUNC"]),
        CStyleCastRule(metadata=metadata["MC3R-CAST-CSTYLE"]),
        RecursionRule(metadata=metadata["MC3R-FORBIDDEN-RECURSION"]),
        TabCharacterRule(metadata=metadata["MC3A-TAB-CHAR"]),
    ]


class RuleEngine:
    def __init__(self, registry: RuleRegistry) -> None:
        self.registry = registry
        self.rules = _build_rule_objects(registry)

    def _accept(self, rule: Rule, rule_filter: RuleFilter) -> bool:
        meta = rule.metadata
        if rule_filter.include_ids and meta.rule_id not in rule_filter.include_ids:
            return False
        if rule_filter.exclude_ids and meta.rule_id in rule_filter.exclude_ids:
            return False
        if rule_filter.categories and meta.category not in rule_filter.categories:
            return False
        if rule_filter.languages:
            langs = {lang.value for lang in meta.languages}
            if not langs.intersection(rule_filter.languages):
                return False
        if rule_filter.levels and meta.level.value not in rule_filter.levels:
            return False
        return True

    def run(self, documents: list[ParsedDocument], rule_filter: RuleFilter | None = None) -> list[Finding]:
        active_filter = rule_filter or RuleFilter()
        findings: list[Finding] = []

        for doc in documents:
            for rule in self.rules:
                if not self._accept(rule, active_filter):
                    continue
                if doc.language not in rule.metadata.languages:
                    continue

                for finding in rule.run(doc):
                    finding.recommendation = recommendation_for(finding.rule_id)
                    finding.fingerprint = finding_fingerprint(finding)
                    findings.append(finding)

        findings.sort(key=lambda f: (f.location.path, f.location.line, f.rule_id))
        return findings
