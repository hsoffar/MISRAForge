from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ReportConfig:
    output_dir: str = "out"
    formats: tuple[str, ...] = ("json", "html")


@dataclass(frozen=True)
class RuleSelectionConfig:
    include_ids: tuple[str, ...] = ()
    exclude_ids: tuple[str, ...] = ()
    categories: tuple[str, ...] = ()
    languages: tuple[str, ...] = ()
    levels: tuple[str, ...] = ()


@dataclass(frozen=True)
class SuppressionConfig:
    file: str | None = None


@dataclass(frozen=True)
class BaselineConfig:
    file: str | None = None


@dataclass(frozen=True)
class DeviationConfig:
    file: str | None = None


@dataclass(frozen=True)
class StorageConfig:
    history_db: str = ".misra_checker/history.db"


@dataclass(frozen=True)
class ProjectConfig:
    profile: str = "default"
    report: ReportConfig = field(default_factory=ReportConfig)
    rules: RuleSelectionConfig = field(default_factory=RuleSelectionConfig)
    suppression: SuppressionConfig = field(default_factory=SuppressionConfig)
    baseline: BaselineConfig = field(default_factory=BaselineConfig)
    deviation: DeviationConfig = field(default_factory=DeviationConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
