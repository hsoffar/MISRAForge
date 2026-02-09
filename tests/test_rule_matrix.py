from __future__ import annotations

from misra_checker.rules.coverage import build_rule_matrix


def test_rule_matrix_includes_expected_rule_fields() -> None:
    payload = {
        "summary": {
            "by_rule": {
                "MC3R-FORBIDDEN-GOTO": 3,
                "MC3A-TAB-CHAR": 1,
            }
        }
    }
    matrix = build_rule_matrix(payload, tests_dir="tests")

    assert matrix["totals"]["rules_total"] >= 5
    assert matrix["totals"]["implemented_count"] >= 5
    rows = {item["rule_id"]: item for item in matrix["rules"]}
    assert rows["MC3R-FORBIDDEN-GOTO"]["detected_count"] == 3
    assert rows["MC3R-FORBIDDEN-GOTO"]["tested"] is True
