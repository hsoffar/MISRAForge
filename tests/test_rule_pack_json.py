from __future__ import annotations

from misra_checker.core.models import ScanRequest, ScanTargetType
from misra_checker.core.scan_service import ScanService
from misra_checker.registry.rule_registry import build_default_registry
from misra_checker.rules.pack_loader import load_rule_pack


def test_rule_pack_loader_registers_and_builds_rules() -> None:
    registry = build_default_registry()
    rules, recommendations = load_rule_pack("samples/custom_rules_demo.json", registry)
    assert rules
    assert "ORG-DEMO-PRINTF" in recommendations
    assert registry.get("ORG-DEMO-PRINTF").category == "io_usage"


def test_scan_service_applies_rule_pack(tmp_path) -> None:
    request = ScanRequest(
        target="samples/simple_repo",
        target_type=ScanTargetType.REPOSITORY,
        output_dir=str(tmp_path),
        report_formats=("json",),
        rule_pack_file="samples/custom_rules_demo.json",
    )
    result, _ = ScanService().run(request)
    assert any(item.rule_id == "ORG-DEMO-PRINTF" for item in result.findings)
