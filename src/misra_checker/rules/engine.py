from __future__ import annotations

from dataclasses import dataclass

from misra_checker.core.models import Finding
from misra_checker.findings.fingerprint import finding_fingerprint
from misra_checker.parser.models import ParsedDocument
from misra_checker.registry.rule_registry import RuleRegistry
from misra_checker.rules.base import Rule
from misra_checker.rules.checkers.registry import build_checker
from misra_checker.rules.default_pack import load_default_pack
from misra_checker.rules.recommendations import recommendation_for


@dataclass(frozen=True)
class RuleFilter:
    include_ids: tuple[str, ...] = ()
    exclude_ids: tuple[str, ...] = ()
    categories: tuple[str, ...] = ()
    languages: tuple[str, ...] = ()
    levels: tuple[str, ...] = ()


def _build_rule_objects(registry: RuleRegistry) -> list[Rule]:
    payload = load_default_pack()
    metadata_by_id = {item.rule_id: item for item in registry.all()}
    out: list[Rule] = []
    for item in payload.get("rules", []):
        if not isinstance(item, dict):
            continue
        rule_id = item.get("rule_id")
        if not isinstance(rule_id, str):
            continue
        meta = metadata_by_id.get(rule_id)
        if meta is None:
            continue
        implementation = item.get("implementation", {})
        if not isinstance(implementation, dict):
            continue
        if implementation.get("type") != "builtin":
            continue
        name = implementation.get("name")
        if not isinstance(name, str) or not name:
            continue
        params = implementation.get("params", {})
        if not isinstance(params, dict):
            params = {}
        out.append(build_checker(name=name, metadata=meta, params=params))
    return out


class RuleEngine:
    def __init__(
        self,
        registry: RuleRegistry,
        extra_rules: list[Rule] | None = None,
        recommendation_overrides: dict[str, str] | None = None,
    ) -> None:
        self.registry = registry
        self.rules = _build_rule_objects(registry) + list(extra_rules or [])
        self.recommendation_overrides = dict(recommendation_overrides or {})

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
                    finding.recommendation = self.recommendation_overrides.get(
                        finding.rule_id,
                        recommendation_for(finding.rule_id),
                    )
                    finding.fingerprint = finding_fingerprint(finding)
                    findings.append(finding)

        findings.sort(key=lambda f: (f.location.path, f.location.line, f.rule_id))
        return findings
