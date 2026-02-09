from __future__ import annotations

import re
from dataclasses import dataclass

from misra_checker.core.models import Finding, FindingStatus, RuleMetadata, SourceLocation
from misra_checker.parser.models import ParsedDocument
from misra_checker.rules.base import Rule


@dataclass
class PrintfRule(Rule):
    metadata: RuleMetadata

    def run(self, document: ParsedDocument) -> list[Finding]:
        findings: list[Finding] = []
        for i, line in enumerate(document.lines, start=1):
            match = re.search(r"\bprintf\s*\(", line)
            if not match:
                continue
            findings.append(
                Finding(
                    rule_id=self.metadata.rule_id,
                    message="printf usage detected",
                    location=SourceLocation(path=document.path, line=i, column=match.start() + 1),
                    language=document.language,
                    severity=self.metadata.severity,
                    category=self.metadata.category,
                    status=FindingStatus.MANUAL_REVIEW,
                )
            )
        return findings
