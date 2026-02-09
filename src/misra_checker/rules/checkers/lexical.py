from __future__ import annotations

from dataclasses import dataclass

from misra_checker.core.models import Finding, FindingStatus, RuleMetadata, SourceLocation
from misra_checker.parser.models import ParsedDocument
from misra_checker.rules.base import Rule


@dataclass
class TabCharacterRule(Rule):
    metadata: RuleMetadata

    def run(self, document: ParsedDocument) -> list[Finding]:
        findings: list[Finding] = []
        for i, line in enumerate(document.lines, start=1):
            if "\t" in line:
                findings.append(
                    Finding(
                        rule_id=self.metadata.rule_id,
                        message="tab character detected",
                        location=SourceLocation(path=document.path, line=i, column=line.find("\t") + 1),
                        language=document.language,
                        severity=self.metadata.severity,
                        category=self.metadata.category,
                        status=FindingStatus.CONFIRMED,
                    )
                )
        return findings


@dataclass
class LineLengthRule(Rule):
    metadata: RuleMetadata
    limit: int = 120

    def run(self, document: ParsedDocument) -> list[Finding]:
        findings: list[Finding] = []
        for i, line in enumerate(document.lines, start=1):
            if len(line) > self.limit:
                findings.append(
                    Finding(
                        rule_id=self.metadata.rule_id,
                        message=f"line length {len(line)} exceeds limit {self.limit}",
                        location=SourceLocation(path=document.path, line=i, column=self.limit + 1),
                        language=document.language,
                        severity=self.metadata.severity,
                        category=self.metadata.category,
                        status=FindingStatus.CONFIRMED,
                    )
                )
        return findings


@dataclass
class TrailingWhitespaceRule(Rule):
    metadata: RuleMetadata

    def run(self, document: ParsedDocument) -> list[Finding]:
        findings: list[Finding] = []
        for i, line in enumerate(document.lines, start=1):
            if line.rstrip(" \t") != line:
                findings.append(
                    Finding(
                        rule_id=self.metadata.rule_id,
                        message="trailing whitespace detected",
                        location=SourceLocation(path=document.path, line=i, column=len(line.rstrip(" \t")) + 1),
                        language=document.language,
                        severity=self.metadata.severity,
                        category=self.metadata.category,
                        status=FindingStatus.CONFIRMED,
                    )
                )
        return findings
