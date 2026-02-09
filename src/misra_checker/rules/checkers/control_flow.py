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
class ControlBracesRule(Rule):
    metadata: RuleMetadata

    def run(self, document: ParsedDocument) -> list[Finding]:
        findings: list[Finding] = []
        ctl = re.compile(r"^\s*(if|for|while)\s*\(.*\)\s*(?!\{)\S")
        for i, line in enumerate(document.lines, start=1):
            if ctl.search(line):
                findings.append(
                    Finding(
                        rule_id=self.metadata.rule_id,
                        message="control statement without braces detected",
                        location=SourceLocation(path=document.path, line=i, column=1),
                        language=document.language,
                        severity=self.metadata.severity,
                        category=self.metadata.category,
                        status=FindingStatus.CONFIRMED,
                    )
                )
                continue
            if re.match(r"^\s*(if|for|while)\s*\(.*\)\s*$", line):
                next_line = document.lines[i] if i < len(document.lines) else ""
                if next_line and next_line.lstrip().startswith("{"):
                    continue
                if next_line.strip() and not next_line.lstrip().startswith("//"):
                    findings.append(
                        Finding(
                            rule_id=self.metadata.rule_id,
                            message="control statement without braces detected",
                            location=SourceLocation(path=document.path, line=i, column=1),
                            language=document.language,
                            severity=self.metadata.severity,
                            category=self.metadata.category,
                            status=FindingStatus.CONFIRMED,
                        )
                    )
        return findings


@dataclass
class AssignInConditionRule(Rule):
    metadata: RuleMetadata

    def run(self, document: ParsedDocument) -> list[Finding]:
        findings: list[Finding] = []
        cond_start = re.compile(r"^\s*(if|while|for)\s*\((.*)\)")
        for i, line in enumerate(document.lines, start=1):
            match = cond_start.search(line)
            if not match:
                continue
            expr = match.group(2)
            if re.search(r"(?<![=!<>+\-*/%&|^])=(?!=)", expr):
                findings.append(
                    Finding(
                        rule_id=self.metadata.rule_id,
                        message="assignment detected in controlling expression",
                        location=SourceLocation(path=document.path, line=i, column=1),
                        language=document.language,
                        severity=self.metadata.severity,
                        category=self.metadata.category,
                        status=FindingStatus.POSSIBLE,
                    )
                )
        return findings


@dataclass
class SwitchDefaultRule(Rule):
    metadata: RuleMetadata

    def run(self, document: ParsedDocument) -> list[Finding]:
        findings: list[Finding] = []
        i = 0
        lines = document.lines
        while i < len(lines):
            line = lines[i]
            if not re.search(r"\bswitch\s*\(", line):
                i += 1
                continue

            brace_depth = line.count("{") - line.count("}")
            start_line = i + 1
            has_default = False
            j = i + 1
            while j < len(lines):
                cur = lines[j]
                brace_depth += cur.count("{") - cur.count("}")
                if re.search(r"^\s*default\s*:", cur):
                    has_default = True
                if brace_depth <= 0:
                    break
                j += 1

            if not has_default:
                findings.append(
                    Finding(
                        rule_id=self.metadata.rule_id,
                        message="switch statement without default clause",
                        location=SourceLocation(path=document.path, line=start_line, column=1),
                        language=document.language,
                        severity=self.metadata.severity,
                        category=self.metadata.category,
                        status=FindingStatus.MANUAL_REVIEW,
                    )
                )
            i = max(j, i + 1) + 1
        return findings


@dataclass
class SwitchBreakRule(Rule):
    metadata: RuleMetadata

    def run(self, document: ParsedDocument) -> list[Finding]:
        findings: list[Finding] = []
        lines = document.lines
        in_switch = False
        brace_depth = 0
        saw_case = False
        case_has_terminator = False
        case_line = 0

        def finish_case(final_line: int) -> None:
            if saw_case and not case_has_terminator:
                findings.append(
                    Finding(
                        rule_id=self.metadata.rule_id,
                        message="switch case may fall through without explicit terminator",
                        location=SourceLocation(path=document.path, line=case_line or final_line, column=1),
                        language=document.language,
                        severity=self.metadata.severity,
                        category=self.metadata.category,
                        status=FindingStatus.MANUAL_REVIEW,
                    )
                )

        for idx, line in enumerate(lines, start=1):
            if not in_switch and re.search(r"\bswitch\s*\(", line):
                in_switch = True
                brace_depth = line.count("{") - line.count("}")
                saw_case = False
                case_has_terminator = False
                case_line = idx
                continue

            if not in_switch:
                continue

            brace_depth += line.count("{") - line.count("}")

            if re.search(r"^\s*(case\b.*:|default\s*:)", line):
                finish_case(idx)
                saw_case = True
                case_has_terminator = False
                case_line = idx
                continue

            if re.search(r"\b(break|return|throw|continue)\b", line):
                case_has_terminator = True
            if "fallthrough" in line.lower():
                case_has_terminator = True

            if brace_depth <= 0:
                finish_case(idx)
                in_switch = False
                saw_case = False
                case_has_terminator = False
                case_line = 0

        return findings


@dataclass
class MultipleReturnRule(Rule):
    metadata: RuleMetadata

    def run(self, document: ParsedDocument) -> list[Finding]:
        findings: list[Finding] = []
        function_def = re.compile(r"^\s*[A-Za-z_]\w*[\w\s\*:&<>]*\b([A-Za-z_]\w*)\s*\([^;]*\)\s*\{")
        current_func: str | None = None
        brace_depth = 0
        returns = 0
        start_line = 0

        for i, line in enumerate(document.lines, start=1):
            if current_func is None:
                match = function_def.match(line)
                if match:
                    current_func = match.group(1)
                    start_line = i
                    brace_depth = line.count("{") - line.count("}")
                    returns = 0
                continue

            brace_depth += line.count("{") - line.count("}")
            if re.search(r"\breturn\b", line):
                returns += 1

            if brace_depth <= 0:
                if returns > 1:
                    findings.append(
                        Finding(
                            rule_id=self.metadata.rule_id,
                            message=f"function '{current_func}' has multiple return statements",
                            location=SourceLocation(path=document.path, line=start_line, column=1),
                            language=document.language,
                            severity=self.metadata.severity,
                            category=self.metadata.category,
                            status=FindingStatus.MANUAL_REVIEW,
                        )
                    )
                current_func = None
                brace_depth = 0

        return findings
