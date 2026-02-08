from __future__ import annotations

from misra_checker.cli.main import build_parser


def test_cli_parser_has_scan_command() -> None:
    parser = build_parser()
    args = parser.parse_args(["scan", "repo", "samples/simple_repo"])
    assert args.command == "scan"
    assert args.scan_mode == "repo"
