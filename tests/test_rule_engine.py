from __future__ import annotations

from misra_checker.core.models import ScanTargetType
from misra_checker.parser.discovery import discover_project_input
from misra_checker.parser.service import ParserService
from misra_checker.registry.rule_registry import build_default_registry
from misra_checker.rules.engine import RuleEngine, RuleFilter


def test_rule_engine_finds_sample_issues() -> None:
    project = discover_project_input("samples/simple_repo", ScanTargetType.REPOSITORY)
    docs, errors = ParserService(prefer_clang=False).parse_project(project)
    assert not errors

    engine = RuleEngine(build_default_registry())
    findings = engine.run(docs)
    rule_ids = {f.rule_id for f in findings}

    assert "MC3R-FORBIDDEN-GOTO" in rule_ids
    assert "MC3A-MACRO-FUNC" in rule_ids
    assert "MC3A-PRINTF" in rule_ids
    assert "MC3R-FORBIDDEN-RECURSION" in rule_ids
    assert "MC3A-TAB-CHAR" in rule_ids


def test_rule_filter_include_id() -> None:
    project = discover_project_input("samples/simple_repo", ScanTargetType.REPOSITORY)
    docs, _ = ParserService(prefer_clang=False).parse_project(project)

    engine = RuleEngine(build_default_registry())
    findings = engine.run(docs, RuleFilter(include_ids=("MC3R-FORBIDDEN-GOTO",)))

    assert findings
    assert all(item.rule_id == "MC3R-FORBIDDEN-GOTO" for item in findings)
