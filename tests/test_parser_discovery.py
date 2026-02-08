from __future__ import annotations

from pathlib import Path

from misra_checker.core.models import Language, ScanTargetType
from misra_checker.parser.discovery import detect_language, discover_project_input
from misra_checker.parser.service import ParserService


def test_detect_language() -> None:
    assert detect_language("a.c") == Language.C
    assert detect_language("a.cpp") == Language.CPP


def test_discover_repo_and_parse() -> None:
    project = discover_project_input("samples/simple_repo", ScanTargetType.REPOSITORY)
    assert len(project.files) >= 2

    docs, errors = ParserService(prefer_clang=False).parse_project(project)
    assert not errors
    assert len(docs) >= 2


def test_single_file_mode(tmp_path: Path) -> None:
    path = tmp_path / "one.c"
    path.write_text("int main(void){return 0;}\n", encoding="utf-8")
    project = discover_project_input(str(path), ScanTargetType.SINGLE_FILE)
    assert project.files == (str(path.resolve()),)
