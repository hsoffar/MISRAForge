from __future__ import annotations


RECOMMENDATIONS = {
    "MC3R-FORBIDDEN-GOTO": "Refactor control flow to structured constructs (if/while/for/function extraction).",
    "MC3A-MACRO-FUNC": "Replace function-like macro with inline/static function where feasible.",
    "MC3R-CAST-CSTYLE": "Prefer explicit C++ cast forms and verify narrowing/safety semantics.",
    "MC3R-FORBIDDEN-RECURSION": "Refactor recursive logic to iterative form for bounded-stack behavior.",
    "MC3A-TAB-CHAR": "Replace tabs with spaces according to project formatting policy.",
}


def recommendation_for(rule_id: str) -> str:
    return RECOMMENDATIONS.get(rule_id, "Review and remediate per project coding standard.")
