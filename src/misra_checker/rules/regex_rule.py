from __future__ import annotations

import re
from dataclasses import dataclass

from misra_checker.core.models import Finding, FindingStatus, RuleMetadata, SourceLocation
from misra_checker.parser.models import ParsedDocument
from misra_checker.rules.base import Rule


@dataclass
class RegexPatternRule(Rule):
    metadata: RuleMetadata
    pattern: str
    message: str
    status: FindingStatus = FindingStatus.CONFIRMED
    flags: int = 0

    def run(self, document: ParsedDocument) -> list[Finding]:
        findings: list[Finding] = []
        compiled = re.compile(self.pattern, self.flags)
        for line_no, line in enumerate(document.lines, start=1):
            match = compiled.search(line)
            if not match:
                continue
            findings.append(
                Finding(
                    rule_id=self.metadata.rule_id,
                    message=self.message,
                    location=SourceLocation(path=document.path, line=line_no, column=match.start() + 1),
                    language=document.language,
                    severity=self.metadata.severity,
                    category=self.metadata.category,
                    status=self.status,
                )
            )
        return findings
