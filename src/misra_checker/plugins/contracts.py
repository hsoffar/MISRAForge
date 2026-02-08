from __future__ import annotations

from typing import Protocol

from misra_checker.rules.base import Rule


class RulePlugin(Protocol):
    """Future local plugin contract for external deterministic rule providers."""

    def build_rules(self) -> list[Rule]:
        ...
