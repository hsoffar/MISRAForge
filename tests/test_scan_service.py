from __future__ import annotations

from pathlib import Path

from misra_checker.core.models import ScanRequest, ScanTargetType
from misra_checker.core.scan_service import ScanService


def test_scan_service_repo_exports_json_html(tmp_path: Path) -> None:
    request = ScanRequest(
        target="samples/simple_repo",
        target_type=ScanTargetType.REPOSITORY,
        output_dir=str(tmp_path),
        report_formats=("json", "html"),
    )

    result, outputs = ScanService().run(request)
    assert result.analyzed_files
    assert "json" in outputs and "html" in outputs
    assert Path(outputs["json"]).exists()
    assert Path(outputs["html"]).exists()


def test_scan_service_single_file(tmp_path: Path) -> None:
    target = tmp_path / "s.c"
    target.write_text("int main(void){goto end; end: return 0;}\n", encoding="utf-8")

    request = ScanRequest(
        target=str(target),
        target_type=ScanTargetType.SINGLE_FILE,
        output_dir=str(tmp_path / "out"),
        report_formats=("json",),
    )

    result, outputs = ScanService().run(request)
    assert len(result.analyzed_files) == 1
    assert result.findings
    assert "json" in outputs
