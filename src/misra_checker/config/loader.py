from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from misra_checker.config.models import (
    BaselineConfig,
    DeviationConfig,
    ProjectConfig,
    ReportConfig,
    RuleSelectionConfig,
    StorageConfig,
    SuppressionConfig,
)


class ConfigError(ValueError):
    pass


_ALLOWED_REPORT_FORMATS = {"json", "html", "csv"}


def _load_raw(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ConfigError(f"Config file does not exist: {path}")

    if path.suffix.lower() in {".yaml", ".yml"}:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    elif path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        raise ConfigError("Config format must be YAML or JSON")

    if not isinstance(data, dict):
        raise ConfigError("Top-level config must be a mapping object")
    return data


def _as_tuple(value: Any, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ConfigError(f"{field_name} must be a list of strings")
    return tuple(value)


def _optional_string_field(raw: dict[str, Any], key: str, parent: str) -> str | None:
    value = raw.get(key)
    if value is not None and not isinstance(value, str):
        raise ConfigError(f"{parent}.{key} must be a string")
    return value


def load_project_config(path: str | Path) -> ProjectConfig:
    raw = _load_raw(Path(path))

    profile = raw.get("profile", "default")
    if not isinstance(profile, str) or not profile:
        raise ConfigError("profile must be a non-empty string")

    report_raw = raw.get("report", {})
    if not isinstance(report_raw, dict):
        raise ConfigError("report must be an object")

    output_dir = report_raw.get("output_dir", "out")
    if not isinstance(output_dir, str) or not output_dir:
        raise ConfigError("report.output_dir must be a non-empty string")

    formats = _as_tuple(report_raw.get("formats", ["json", "html"]), "report.formats")
    unknown_formats = sorted(set(formats) - _ALLOWED_REPORT_FORMATS)
    if unknown_formats:
        raise ConfigError(f"Unsupported report format(s): {', '.join(unknown_formats)}")

    rules_raw = raw.get("rules", {})
    if not isinstance(rules_raw, dict):
        raise ConfigError("rules must be an object")

    rule_cfg = RuleSelectionConfig(
        include_ids=_as_tuple(rules_raw.get("include_ids", []), "rules.include_ids"),
        exclude_ids=_as_tuple(rules_raw.get("exclude_ids", []), "rules.exclude_ids"),
        categories=_as_tuple(rules_raw.get("categories", []), "rules.categories"),
        languages=_as_tuple(rules_raw.get("languages", []), "rules.languages"),
        levels=_as_tuple(rules_raw.get("levels", []), "rules.levels"),
    )

    suppression_raw = raw.get("suppression", {})
    if not isinstance(suppression_raw, dict):
        raise ConfigError("suppression must be an object")

    baseline_raw = raw.get("baseline", {})
    if not isinstance(baseline_raw, dict):
        raise ConfigError("baseline must be an object")

    deviation_raw = raw.get("deviation", {})
    if not isinstance(deviation_raw, dict):
        raise ConfigError("deviation must be an object")

    storage_raw = raw.get("storage", {})
    if not isinstance(storage_raw, dict):
        raise ConfigError("storage must be an object")
    history_db = storage_raw.get("history_db", ".misra_checker/history.db")
    if not isinstance(history_db, str) or not history_db:
        raise ConfigError("storage.history_db must be a non-empty string")

    return ProjectConfig(
        profile=profile,
        report=ReportConfig(output_dir=output_dir, formats=formats),
        rules=rule_cfg,
        suppression=SuppressionConfig(file=_optional_string_field(suppression_raw, "file", "suppression")),
        baseline=BaselineConfig(file=_optional_string_field(baseline_raw, "file", "baseline")),
        deviation=DeviationConfig(file=_optional_string_field(deviation_raw, "file", "deviation")),
        storage=StorageConfig(history_db=history_db),
    )
