from __future__ import annotations

from dataclasses import dataclass, field

from misra_checker.core.models import Language


@dataclass(frozen=True)
class ParseDiagnostic:
    path: str
    message: str
    severity: str = "warning"


@dataclass
class ParsedDocument:
    path: str
    language: Language
    content: str
    lines: list[str]
    diagnostics: list[ParseDiagnostic] = field(default_factory=list)
    backend: str = "lexical"


@dataclass(frozen=True)
class ProjectInput:
    files: tuple[str, ...]
    compile_commands_path: str | None = None
