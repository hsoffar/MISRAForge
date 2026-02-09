from __future__ import annotations

import re
from dataclasses import dataclass

from misra_checker.core.models import Finding, FindingStatus, RuleMetadata, SourceLocation
from misra_checker.parser.models import ParsedDocument
from misra_checker.rules.base import Rule


@dataclass
class MacroFunctionRule(Rule):
    metadata: RuleMetadata

    def run(self, document: ParsedDocument) -> list[Finding]:
        findings: list[Finding] = []
        for i, line in enumerate(document.lines, start=1):
            if re.match(r"\s*#\s*define\s+[A-Za-z_]\w*\s*\(", line):
                findings.append(
                    Finding(
                        rule_id=self.metadata.rule_id,
                        message="function-like macro definition detected",
                        location=SourceLocation(path=document.path, line=i, column=1),
                        language=document.language,
                        severity=self.metadata.severity,
                        category=self.metadata.category,
                        status=FindingStatus.MANUAL_REVIEW,
                    )
                )
        return findings
