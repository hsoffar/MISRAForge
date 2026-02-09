from __future__ import annotations

from misra_checker.cli.main import build_parser


def test_cli_parser_has_scan_command() -> None:
    parser = build_parser()
    args = parser.parse_args(["scan", "repo", "samples/simple_repo"])
    assert args.command == "scan"
    assert args.scan_mode == "repo"
    assert args.rule_pack is None


def test_cli_parser_has_rules_matrix_command() -> None:
    parser = build_parser()
    args = parser.parse_args(["rules", "matrix"])
    assert args.command == "rules"
    assert args.rules_cmd == "matrix"
    assert args.scan_json == "out/report.json"


def test_cli_parser_has_api_serve_command() -> None:
    parser = build_parser()
    args = parser.parse_args(["api", "serve"])
    assert args.command == "api"
    assert args.api_cmd == "serve"
    assert args.port == 8775
    assert args.rule_content_file == "samples/rule_content_open.json"
