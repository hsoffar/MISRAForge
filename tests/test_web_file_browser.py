from __future__ import annotations

from misra_checker.api.server import build_project_browser


def test_build_project_browser_for_sample_repo() -> None:
    payload = build_project_browser("samples/simple_repo")
    assert payload["exists"] is True
    assert payload["file_count"] >= 1
    assert "tree" in payload
