from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from misra_checker.parser.models import ParseDiagnostic, ParsedDocument
from misra_checker.parser.discovery import detect_language


class ParserBackend(ABC):
    name: str

    @abstractmethod
    def parse_file(self, path: str, compile_commands_path: str | None = None) -> ParsedDocument:
        raise NotImplementedError


class LexicalParserBackend(ParserBackend):
    name = "lexical"

    def parse_file(self, path: str, compile_commands_path: str | None = None) -> ParsedDocument:
        file_path = Path(path)
        content = file_path.read_text(encoding="utf-8", errors="replace")
        lines = content.splitlines()
        diagnostics: list[ParseDiagnostic] = []
        if "\ufffd" in content:
            diagnostics.append(
                ParseDiagnostic(path=str(file_path), message="Invalid UTF-8 byte sequence replaced")
            )
        return ParsedDocument(
            path=str(file_path),
            language=detect_language(file_path),
            content=content,
            lines=lines,
            diagnostics=diagnostics,
            backend=self.name,
        )


class ClangParserBackend(ParserBackend):
    name = "clang"

    def __init__(self) -> None:
        try:
            from clang import cindex  # type: ignore
        except ImportError as exc:
            raise RuntimeError("clang.cindex is not available") from exc
        self._cindex = cindex

    def parse_file(self, path: str, compile_commands_path: str | None = None) -> ParsedDocument:
        file_path = Path(path)
        content = file_path.read_text(encoding="utf-8", errors="replace")
        lines = content.splitlines()

        args: list[str] = []
        if file_path.suffix.lower() in {".c", ".h"}:
            args += ["-x", "c", "-std=c11"]
        else:
            args += ["-x", "c++", "-std=c++17"]

        index = self._cindex.Index.create()
        tu = index.parse(str(file_path), args=args)

        diagnostics = [
            ParseDiagnostic(path=str(file_path), message=str(diag.spelling), severity=str(diag.severity))
            for diag in tu.diagnostics
        ]

        return ParsedDocument(
            path=str(file_path),
            language=detect_language(file_path),
            content=content,
            lines=lines,
            diagnostics=diagnostics,
            backend=self.name,
        )
