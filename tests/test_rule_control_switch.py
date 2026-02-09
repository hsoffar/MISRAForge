from __future__ import annotations

from misra_checker.core.models import Language
from misra_checker.parser.models import ParsedDocument
from misra_checker.registry.rule_registry import build_default_registry
from misra_checker.rules.engine import RuleEngine, RuleFilter


def _doc(text: str) -> ParsedDocument:
    return ParsedDocument(
        path="switch_sample.c",
        language=Language.C,
        content=text,
        lines=text.splitlines(),
    )


def test_switch_rules_and_assignment_in_condition() -> None:
    document = _doc(
        "int f(int v) {\n"
        "  if (v = 3) {\n"
        "    return v;\n"
        "  }\n"
        "  switch (v) {\n"
        "    case 1:\n"
        "      v += 1;\n"
        "    case 2:\n"
        "      return v;\n"
        "  }\n"
        "  return 0;\n"
        "}\n"
    )
    engine = RuleEngine(build_default_registry())
    findings = engine.run(
        [document],
        RuleFilter(
            include_ids=(
                "MC3R-ASSIGN-IN-CONDITION",
                "MC3R-SWITCH-DEFAULT",
                "MC3R-SWITCH-BREAK",
                "MC3R-MULTI-RETURN",
            )
        ),
    )
    ids = {item.rule_id for item in findings}
    assert "MC3R-ASSIGN-IN-CONDITION" in ids
    assert "MC3R-SWITCH-DEFAULT" in ids
    assert "MC3R-SWITCH-BREAK" in ids
    assert "MC3R-MULTI-RETURN" in ids
