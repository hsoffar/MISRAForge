from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import shutil
from uuid import uuid4

from misra_checker.baseline.service import apply_baseline, load_baseline
from misra_checker.config.loader import load_project_config
from misra_checker.core.models import ScanRequest, ScanResult
from misra_checker.findings.deviation import apply_deviations, load_deviations
from misra_checker.parser.discovery import discover_project_input
from misra_checker.parser.service import ParserService
from misra_checker.registry.rule_registry import build_default_registry
from misra_checker.reports.exporters import export_csv, export_html, export_json
from misra_checker.rules.base import Rule
from misra_checker.rules.engine import RuleEngine, RuleFilter
from misra_checker.rules.pack_loader import load_rule_pack
from misra_checker.storage.history import HistoryStore
from misra_checker.suppression.service import apply_suppressions, load_suppressions


@dataclass
class ScanService:
    def run(self, request: ScanRequest) -> tuple[ScanResult, dict[str, str]]:
        started_at = datetime.now(timezone.utc).isoformat()

        config = None
        if request.config_path:
            config = load_project_config(request.config_path)

        project_input = discover_project_input(request.target, request.target_type)
        parser = ParserService(prefer_clang=True)
        docs, parse_errors = parser.parse_project(project_input)

        registry = build_default_registry()
        extra_rules: list[Rule] = []
        recommendation_overrides: dict[str, str] = {}

        include_ids = request.include_rules
        exclude_ids = request.exclude_rules
        categories: tuple[str, ...] = ()
        languages: tuple[str, ...] = ()
        levels: tuple[str, ...] = ()

        baseline_file = request.baseline_file
        suppression_file = request.suppression_file
        deviation_file = request.deviation_file
        history_db = request.history_db_path
        rule_pack_file = request.rule_pack_file

        if config:
            include_ids = include_ids or config.rules.include_ids
            exclude_ids = exclude_ids or config.rules.exclude_ids
            categories = config.rules.categories
            languages = config.rules.languages
            levels = config.rules.levels
            baseline_file = baseline_file or config.baseline.file
            suppression_file = suppression_file or config.suppression.file
            deviation_file = deviation_file or config.deviation.file
            history_db = history_db or config.storage.history_db

        if rule_pack_file:
            loaded_rules, loaded_recommendations = load_rule_pack(rule_pack_file, registry)
            extra_rules.extend(loaded_rules)
            recommendation_overrides.update(loaded_recommendations)

        engine = RuleEngine(
            registry,
            extra_rules=extra_rules,
            recommendation_overrides=recommendation_overrides,
        )

        findings = engine.run(
            docs,
            RuleFilter(
                include_ids=include_ids,
                exclude_ids=exclude_ids,
                categories=categories,
                languages=languages,
                levels=levels,
            ),
        )

        apply_suppressions(findings, load_suppressions(suppression_file))
        apply_baseline(findings, load_baseline(baseline_file))
        apply_deviations(findings, load_deviations(deviation_file))

        diagnostics: list[str] = list(parse_errors)
        for doc in docs:
            diagnostics.extend([f"{d.path}: {d.message}" for d in doc.diagnostics])

        result = ScanResult(
            scan_id=f"scan-{uuid4().hex[:10]}",
            started_at=started_at,
            finished_at=datetime.now(timezone.utc).isoformat(),
            findings=findings,
            parse_diagnostics=diagnostics,
            analyzed_files=[doc.path for doc in docs],
            available_rule_ids=[meta.rule_id for meta in registry.all()],
        )

        out_dir = Path(request.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        output_paths: dict[str, str] = {}
        archive_dir = out_dir / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)
        stamp = result.finished_at.replace(":", "").replace("-", "").replace("T", "_").replace("+", "_").replace(".", "_")
        for fmt in request.report_formats:
            if fmt == "json":
                current = out_dir / "report.json"
                output_paths[fmt] = export_json(result, current)
                shutil.copy2(current, archive_dir / f"{stamp}.json")
            elif fmt == "html":
                current = out_dir / "report.html"
                output_paths[fmt] = export_html(result, current)
                shutil.copy2(current, archive_dir / f"{stamp}.html")
            elif fmt == "csv":
                current = out_dir / "report.csv"
                output_paths[fmt] = export_csv(result, current)
                shutil.copy2(current, archive_dir / f"{stamp}.csv")

        if history_db:
            HistoryStore(history_db).save_scan(result, request.normalized_target(), output_paths)

        return result, output_paths
