from __future__ import annotations

from collections.abc import Callable

from misra_checker.core.models import RuleMetadata
from misra_checker.rules.base import Rule
from misra_checker.rules.checkers.control_flow import (
    AssignInConditionRule,
    ControlBracesRule,
    GotoRule,
    MultipleReturnRule,
    SwitchBreakRule,
    SwitchDefaultRule,
)
from misra_checker.rules.checkers.io_usage import PrintfRule
from misra_checker.rules.checkers.language_subset import RecursionRule
from misra_checker.rules.checkers.lexical import LineLengthRule, TabCharacterRule, TrailingWhitespaceRule
from misra_checker.rules.checkers.maintainability import MagicNumberRule
from misra_checker.rules.checkers.numeric import FloatEqualityRule
from misra_checker.rules.checkers.preprocessor import MacroFunctionRule
from misra_checker.rules.checkers.type_safety import CStyleCastRule


CheckerFactory = Callable[[RuleMetadata, dict[str, object]], Rule]


def _default_factory(cls: type[Rule]) -> CheckerFactory:
    def _build(metadata: RuleMetadata, params: dict[str, object]) -> Rule:
        return cls(metadata=metadata, **params)

    return _build


CHECKER_FACTORIES: dict[str, CheckerFactory] = {
    "LineLengthRule": _default_factory(LineLengthRule),
    "TrailingWhitespaceRule": _default_factory(TrailingWhitespaceRule),
    "TabCharacterRule": _default_factory(TabCharacterRule),
    "GotoRule": _default_factory(GotoRule),
    "ControlBracesRule": _default_factory(ControlBracesRule),
    "AssignInConditionRule": _default_factory(AssignInConditionRule),
    "SwitchDefaultRule": _default_factory(SwitchDefaultRule),
    "SwitchBreakRule": _default_factory(SwitchBreakRule),
    "MultipleReturnRule": _default_factory(MultipleReturnRule),
    "MacroFunctionRule": _default_factory(MacroFunctionRule),
    "CStyleCastRule": _default_factory(CStyleCastRule),
    "FloatEqualityRule": _default_factory(FloatEqualityRule),
    "MagicNumberRule": _default_factory(MagicNumberRule),
    "RecursionRule": _default_factory(RecursionRule),
    "PrintfRule": _default_factory(PrintfRule),
}


def build_checker(name: str, metadata: RuleMetadata, params: dict[str, object] | None = None) -> Rule:
    factory = CHECKER_FACTORIES.get(name)
    if factory is None:
        raise ValueError(f"unknown checker name: {name}")
    return factory(metadata, dict(params or {}))
