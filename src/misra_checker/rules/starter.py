from __future__ import annotations

import re
from dataclasses import dataclass

from misra_checker.core.models import Finding, FindingStatus, RuleMetadata, SourceLocation
from misra_checker.parser.models import ParsedDocument
from misra_checker.rules.base import Rule


@dataclass
class GotoRule(Rule):
    metadata: RuleMetadata

    def run(self, document: ParsedDocument) -> list[Finding]:
        findings: list[Finding] = []
        for i, line in enumerate(document.lines, start=1):
            if re.search(r"\bgoto\b", line):
                findings.append(
                    Finding(
                        rule_id=self.metadata.rule_id,
                        message="goto usage detected",
                        location=SourceLocation(path=document.path, line=i, column=max(line.find("goto") + 1, 1)),
                        language=document.language,
                        severity=self.metadata.severity,
                        category=self.metadata.category,
                        status=FindingStatus.CONFIRMED,
                    )
                )
        return findings


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


@dataclass
class RecursionRule(Rule):
    metadata: RuleMetadata

    def run(self, document: ParsedDocument) -> list[Finding]:
        findings: list[Finding] = []
        function_def = re.compile(r"^\s*[A-Za-z_]\w*[\w\s\*:&<>]*\b([A-Za-z_]\w*)\s*\([^;]*\)\s*\{")
        current_func: str | None = None
        func_start_line = 0
        brace_depth = 0

        for i, line in enumerate(document.lines, start=1):
            if current_func is None:
                match = function_def.match(line)
                if match:
                    current_func = match.group(1)
                    func_start_line = i
                    brace_depth = line.count("{") - line.count("}")
                continue

            brace_depth += line.count("{") - line.count("}")
            if re.search(rf"\b{re.escape(current_func)}\s*\(", line):
                findings.append(
                    Finding(
                        rule_id=self.metadata.rule_id,
                        message=f"possible recursion in function '{current_func}'",
                        location=SourceLocation(path=document.path, line=func_start_line, column=1),
                        language=document.language,
                        severity=self.metadata.severity,
                        category=self.metadata.category,
                        status=FindingStatus.MANUAL_REVIEW,
                    )
                )
                current_func = None
                brace_depth = 0
                continue

            if brace_depth <= 0:
                current_func = None
                brace_depth = 0

        return findings


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
