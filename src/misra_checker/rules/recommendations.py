from __future__ import annotations

from functools import lru_cache

from misra_checker.rules.default_pack import load_default_pack


@lru_cache(maxsize=1)
def _recommendations() -> dict[str, str]:
    payload = load_default_pack()
    out: dict[str, str] = {}
    for item in payload.get("rules", []):
        if not isinstance(item, dict):
            continue
        rule_id = item.get("rule_id")
        recommendation = item.get("recommendation")
        if isinstance(rule_id, str) and isinstance(recommendation, str) and recommendation.strip():
            out[rule_id] = recommendation.strip()
    return out


def recommendation_for(rule_id: str) -> str:
    return _recommendations().get(rule_id, "Review and remediate per project coding standard.")
