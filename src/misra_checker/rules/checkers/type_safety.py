from __future__ import annotations

import re
from dataclasses import dataclass

from misra_checker.core.models import Finding, FindingStatus, RuleMetadata, SourceLocation
from misra_checker.parser.models import ParsedDocument
from misra_checker.rules.base import Rule


@dataclass
class CStyleCastRule(Rule):
    metadata: RuleMetadata

    def run(self, document: ParsedDocument) -> list[Finding]:
        if document.language.value != "cpp":
            return []

        findings: list[Finding] = []
        pattern = re.compile(r"\([A-Za-z_][\w:\s\*&<>]*\)\s*[A-Za-z_(]")
        for i, line in enumerate(document.lines, start=1):
            match = pattern.search(line)
            if match:
                findings.append(
                    Finding(
                        rule_id=self.metadata.rule_id,
                        message="C-style cast pattern detected",
                        location=SourceLocation(path=document.path, line=i, column=match.start() + 1),
                        language=document.language,
                        severity=self.metadata.severity,
                        category=self.metadata.category,
                        status=FindingStatus.POSSIBLE,
                    )
                )
        return findings
