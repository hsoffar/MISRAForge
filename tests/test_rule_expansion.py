from __future__ import annotations

from misra_checker.core.models import Language
from misra_checker.parser.models import ParsedDocument
from misra_checker.registry.rule_registry import build_default_registry
from misra_checker.rules.engine import RuleEngine, RuleFilter


def _doc(text: str) -> ParsedDocument:
    lines = text.splitlines()
    return ParsedDocument(
        path="unit_sample.cpp",
        language=Language.CPP,
        content=text,
        lines=lines,
    )


def test_new_rules_detect_expected_patterns() -> None:
    document = _doc(
        "int main() {\n"
        "  int x = 42;    \n"
        "  if (x > 0) x = x + 2;\n"
        "  if (1.0 == x) { return 0; }\n"
        "  return 0;\n"
        "}\n"
        + ("// " + ("a" * 130))
    )
    engine = RuleEngine(build_default_registry())
    findings = engine.run(
        [document],
        RuleFilter(
            include_ids=(
                "MC3A-LINE-LENGTH",
                "MC3A-TRAILING-WHITESPACE",
                "MC3R-CONTROL-BRACES",
                "MC3R-FLOAT-EQUALITY",
                "MC3R-MAGIC-NUMBER",
            )
        ),
    )
    got = {item.rule_id for item in findings}
    assert "MC3A-LINE-LENGTH" in got
    assert "MC3A-TRAILING-WHITESPACE" in got
    assert "MC3R-CONTROL-BRACES" in got
    assert "MC3R-FLOAT-EQUALITY" in got
    assert "MC3R-MAGIC-NUMBER" in got
