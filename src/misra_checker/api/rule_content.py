from __future__ import annotations

import json
from pathlib import Path


def load_rule_content_map(path: str | None) -> dict[str, dict[str, str]]:
    if not path:
        return {}
    content_path = Path(path)
    if not content_path.exists():
        return {}
    try:
        payload = json.loads(content_path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    rules = payload.get("rules", [])
    if not isinstance(rules, list):
        return {}
    out: dict[str, dict[str, str]] = {}
    for item in rules:
        if not isinstance(item, dict):
            continue
        rule_id = item.get("rule_id")
        if not isinstance(rule_id, str) or not rule_id.strip():
            continue
        out[rule_id] = {
            "source": str(item.get("source", "")),
            "license": str(item.get("license", "")),
            "summary": str(item.get("summary", "")),
            "full_text": str(item.get("full_text", "")),
            "notes": str(item.get("notes", "")),
        }
    return out
