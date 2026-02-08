from __future__ import annotations

import json
from pathlib import Path

import yaml

from misra_checker.core.models import ScanRequest, ScanTargetType
from misra_checker.core.scan_service import ScanService
from misra_checker.storage.history import HistoryStore


def test_baseline_and_suppression_and_deviation(tmp_path: Path) -> None:
    history_db = tmp_path / "history.db"
    out_dir = tmp_path / "out"

    first_request = ScanRequest(
        target="samples/simple_repo",
        target_type=ScanTargetType.REPOSITORY,
        output_dir=str(out_dir),
        report_formats=("json",),
        history_db_path=str(history_db),
    )
    first_result, first_outputs = ScanService().run(first_request)
    assert first_result.findings

    baseline_path = tmp_path / "baseline.json"
    baseline_payload = {
        "entries": [
            {
                "fingerprint": f.fingerprint,
                "rule_id": f.rule_id,
                "path": f.location.path,
            }
            for f in first_result.findings
        ]
    }
    baseline_path.write_text(json.dumps(baseline_payload), encoding="utf-8")

    suppressed = next(f for f in first_result.findings if f.rule_id == "MC3A-TAB-CHAR")
    suppressions_path = tmp_path / "suppressions.yaml"
    suppressions_path.write_text(
        yaml.safe_dump(
            [
                {
                    "rule_id": "MC3A-TAB-CHAR",
                    "path_pattern": "*main.c",
                    "line": suppressed.location.line,
                    "reason": "accepted",
                }
            ]
        ),
        encoding="utf-8",
    )

    deviations_path = tmp_path / "deviations.yaml"
    deviations_path.write_text(
        yaml.safe_dump(
            [
                {
                    "finding_fingerprint": suppressed.fingerprint,
                    "justification": "tooling transition",
                }
            ]
        ),
        encoding="utf-8",
    )

    second_request = ScanRequest(
        target="samples/simple_repo",
        target_type=ScanTargetType.REPOSITORY,
        output_dir=str(out_dir),
        report_formats=("json",),
        baseline_file=str(baseline_path),
        suppression_file=str(suppressions_path),
        deviation_file=str(deviations_path),
        history_db_path=str(history_db),
    )
    second_result, _ = ScanService().run(second_request)

    statuses = {f.rule_id: f.status.value for f in second_result.findings}
    assert "baseline" in statuses.values() or "suppressed" in statuses.values() or "deviation" in statuses.values()

    trend = HistoryStore(str(history_db)).trend(limit=5)
    assert trend
    assert trend[0]["summary"]["total_findings"] >= 1
    assert Path(first_outputs["json"]).exists()
