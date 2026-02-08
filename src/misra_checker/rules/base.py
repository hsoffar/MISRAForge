from __future__ import annotations

from abc import ABC, abstractmethod

from misra_checker.core.models import Finding, RuleMetadata
from misra_checker.parser.models import ParsedDocument


class Rule(ABC):
    metadata: RuleMetadata

    @abstractmethod
    def run(self, document: ParsedDocument) -> list[Finding]:
        raise NotImplementedError
