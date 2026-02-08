from __future__ import annotations

from dataclasses import dataclass

from misra_checker.parser.backends import ClangParserBackend, LexicalParserBackend, ParserBackend
from misra_checker.parser.models import ParsedDocument, ProjectInput


@dataclass
class ParserService:
    prefer_clang: bool = True

    def _select_backend(self) -> ParserBackend:
        if self.prefer_clang:
            try:
                return ClangParserBackend()
            except RuntimeError:
                return LexicalParserBackend()
        return LexicalParserBackend()

    def parse_project(self, project_input: ProjectInput) -> tuple[list[ParsedDocument], list[str]]:
        backend = self._select_backend()
        docs: list[ParsedDocument] = []
        errors: list[str] = []
        for path in project_input.files:
            try:
                docs.append(backend.parse_file(path, project_input.compile_commands_path))
            except Exception as exc:  # pragma: no cover - hardening path
                errors.append(f"{path}: parse failure: {exc}")
        return docs, errors
