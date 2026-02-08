from __future__ import annotations

from pathlib import Path

from misra_checker.core.models import Language, ScanTargetType
from misra_checker.parser.models import ProjectInput

_C_EXT = {".c", ".h"}
_CPP_EXT = {".cc", ".cp", ".cpp", ".cxx", ".hpp", ".hh", ".hxx"}


def detect_language(path: str | Path) -> Language:
    suffix = Path(path).suffix.lower()
    if suffix in _C_EXT:
        return Language.C
    if suffix in _CPP_EXT:
        return Language.CPP
    return Language.UNKNOWN


def is_source_file(path: str | Path) -> bool:
    return detect_language(path) in {Language.C, Language.CPP}


def find_compile_database(root: str | Path) -> str | None:
    root_path = Path(root)
    candidates = [
        root_path / "compile_commands.json",
        root_path / "build" / "compile_commands.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate.resolve())
    return None


def discover_project_input(target: str, target_type: ScanTargetType) -> ProjectInput:
    target_path = Path(target)
    if target_type == ScanTargetType.SINGLE_FILE:
        if not target_path.exists():
            raise FileNotFoundError(f"Single-file target not found: {target}")
        if not is_source_file(target_path):
            raise ValueError(f"Unsupported file extension for analysis: {target}")
        return ProjectInput(files=(str(target_path.resolve()),), compile_commands_path=None)

    if not target_path.exists() or not target_path.is_dir():
        raise FileNotFoundError(f"Repository target not found or not a directory: {target}")

    files: list[str] = []
    for path in sorted(target_path.rglob("*")):
        if path.is_file() and is_source_file(path):
            files.append(str(path.resolve()))

    return ProjectInput(
        files=tuple(files),
        compile_commands_path=find_compile_database(target_path),
    )
