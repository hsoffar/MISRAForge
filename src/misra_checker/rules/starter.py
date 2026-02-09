from __future__ import annotations

# Backward-compatible exports. New modular checkers live under rules/checkers/.
from misra_checker.rules.checkers.control_flow import (  # noqa: F401
    AssignInConditionRule,
    ControlBracesRule,
    GotoRule,
    MultipleReturnRule,
    SwitchBreakRule,
    SwitchDefaultRule,
)
from misra_checker.rules.checkers.io_usage import PrintfRule  # noqa: F401
from misra_checker.rules.checkers.language_subset import RecursionRule  # noqa: F401
from misra_checker.rules.checkers.lexical import LineLengthRule, TabCharacterRule, TrailingWhitespaceRule  # noqa: F401
from misra_checker.rules.checkers.maintainability import MagicNumberRule  # noqa: F401
from misra_checker.rules.checkers.numeric import FloatEqualityRule  # noqa: F401
from misra_checker.rules.checkers.preprocessor import MacroFunctionRule  # noqa: F401
from misra_checker.rules.checkers.type_safety import CStyleCastRule  # noqa: F401
