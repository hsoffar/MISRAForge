from __future__ import annotations

import re
from dataclasses import dataclass

from misra_checker.core.models import Finding, FindingStatus, RuleMetadata, SourceLocation
from misra_checker.parser.models import ParsedDocument
from misra_checker.rules.base import Rule


@dataclass
class FloatEqualityRule(Rule):
    metadata: RuleMetadata

    def run(self, document: ParsedDocument) -> list[Finding]:
        findings: list[Finding] = []
        compare = re.compile(r"(==|!=)")
        float_hint = re.compile(r"\d+\.\d+|\d+[eE][+-]?\d+|\d+\.\d*[fF]\b|\d+[fF]\b")
        for i, line in enumerate(document.lines, start=1):
            if not compare.search(line):
                continue
            if float_hint.search(line):
                findings.append(
                    Finding(
                        rule_id=self.metadata.rule_id,
                        message="possible direct floating-point equality comparison",
                        location=SourceLocation(path=document.path, line=i, column=1),
                        language=document.language,
                        severity=self.metadata.severity,
                        category=self.metadata.category,
                        status=FindingStatus.POSSIBLE,
                    )
                )
        return findings
