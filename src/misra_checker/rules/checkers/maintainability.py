from __future__ import annotations

import re
from dataclasses import dataclass

from misra_checker.core.models import Finding, FindingStatus, RuleMetadata, SourceLocation
from misra_checker.parser.models import ParsedDocument
from misra_checker.rules.base import Rule


@dataclass
class MagicNumberRule(Rule):
    metadata: RuleMetadata

    def run(self, document: ParsedDocument) -> list[Finding]:
        findings: list[Finding] = []
        literal = re.compile(r"(?<![A-Za-z_])(-?\d+(?:\.\d+)?)(?![A-Za-z_])")
        for i, line in enumerate(document.lines, start=1):
            clean = line.split("//", 1)[0]
            if "#" in clean:
                continue
            for match in literal.finditer(clean):
                token = match.group(1)
                if token in {"0", "1", "-1", "0.0", "1.0", "-1.0"}:
                    continue
                if re.search(r"\b(enum|case)\b", clean):
                    continue
                findings.append(
                    Finding(
                        rule_id=self.metadata.rule_id,
                        message=f"magic number literal detected: {token}",
                        location=SourceLocation(path=document.path, line=i, column=match.start() + 1),
                        language=document.language,
                        severity=self.metadata.severity,
                        category=self.metadata.category,
                        status=FindingStatus.MANUAL_REVIEW,
                    )
                )
                break
        return findings
