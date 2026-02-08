from __future__ import annotations

from pathlib import Path

import pytest

from misra_checker.config.loader import ConfigError, load_project_config


def test_load_project_config_yaml(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
profile: strict
report:
  output_dir: reports
  formats: [json, html]
rules:
  include_ids: [MC3R-FORBIDDEN-GOTO]
  categories: [control_flow]
suppression:
  file: suppressions.yaml
baseline:
  file: baseline.json
deviation:
  file: deviations.yaml
storage:
  history_db: .misra/history.db
""".strip(),
        encoding="utf-8",
    )

    cfg = load_project_config(config_path)
    assert cfg.profile == "strict"
    assert cfg.report.output_dir == "reports"
    assert cfg.rules.include_ids == ("MC3R-FORBIDDEN-GOTO",)
    assert cfg.suppression.file == "suppressions.yaml"
    assert cfg.baseline.file == "baseline.json"
    assert cfg.deviation.file == "deviations.yaml"
    assert cfg.storage.history_db == ".misra/history.db"


def test_load_project_config_rejects_bad_format(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text("report:\n  formats: [xml]", encoding="utf-8")

    with pytest.raises(ConfigError):
        load_project_config(config_path)
