from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class Language(str, Enum):
    C = "c"
    CPP = "cpp"
    UNKNOWN = "unknown"


class RuleLevel(str, Enum):
    REQUIRED = "required"
    ADVISORY = "advisory"


class Severity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class FindingStatus(str, Enum):
    CONFIRMED = "confirmed"
    POSSIBLE = "possible"
    SUPPRESSED = "suppressed"
    BASELINE = "baseline"
    DEVIATION = "deviation"
    MANUAL_REVIEW = "manual_review"


class ScanTargetType(str, Enum):
    REPOSITORY = "repository"
    SINGLE_FILE = "single_file"


@dataclass(frozen=True)
class RuleMetadata:
    rule_id: str
    title: str
    category: str
    level: RuleLevel
    languages: tuple[Language, ...]
    severity: Severity
    tags: tuple[str, ...] = ()
    rationale_summary: str = ""


@dataclass(frozen=True)
class SourceLocation:
    path: str
    line: int
    column: int = 1


@dataclass
class Finding:
    rule_id: str
    message: str
    location: SourceLocation
    language: Language
    severity: Severity
    category: str
    status: FindingStatus = FindingStatus.CONFIRMED
    fingerprint: str = ""
    recommendation: str = ""
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SuppressionEntry:
    rule_id: str | None
    path_pattern: str
    line: int | None = None
    reason: str = ""


@dataclass(frozen=True)
class DeviationRecord:
    finding_fingerprint: str
    justification: str
    approved_by: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class BaselineEntry:
    fingerprint: str
    rule_id: str
    path: str


@dataclass
class ScanRequest:
    target: str
    target_type: ScanTargetType
    config_path: str | None = None
    output_dir: str = "out"
    report_formats: tuple[str, ...] = ("json",)
    include_rules: tuple[str, ...] = ()
    exclude_rules: tuple[str, ...] = ()
    baseline_file: str | None = None
    suppression_file: str | None = None
    deviation_file: str | None = None
    history_db_path: str | None = None
    rule_pack_file: str | None = None

    def normalized_target(self) -> str:
        return str(Path(self.target).resolve())


@dataclass
class ScanResult:
    scan_id: str
    started_at: str
    finished_at: str
    findings: list[Finding]
    parse_diagnostics: list[str] = field(default_factory=list)
    analyzed_files: list[str] = field(default_factory=list)
    available_rule_ids: list[str] = field(default_factory=list)
