from __future__ import annotations

from misra_checker.api.rule_content import load_rule_content_map


def test_load_rule_content_map_from_sample() -> None:
    data = load_rule_content_map("samples/rule_content_open.json")
    assert "MC3R-FORBIDDEN-GOTO" in data
    assert "summary" in data["MC3R-FORBIDDEN-GOTO"]
