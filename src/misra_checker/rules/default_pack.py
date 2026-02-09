from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


DEFAULT_RULE_PACK_PATH = Path(__file__).resolve().parent / "default_rule_pack.json"


@lru_cache(maxsize=1)
def load_default_pack() -> dict[str, Any]:
    payload = json.loads(DEFAULT_RULE_PACK_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("default rule pack must be an object")
    rules = payload.get("rules")
    if not isinstance(rules, list):
        raise ValueError("default rule pack must contain 'rules' list")
    return payload
