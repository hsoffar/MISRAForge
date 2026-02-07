# MISRA Checker (Local MVP)

MISRA Checker is a local static-analysis MVP for C/C++ codebases with MISRA-oriented deterministic checks.

It is designed as a product foundation, not a one-off script:
- local-only execution,
- deterministic rule engine as source of truth,
- repository and single-file scanning,
- CLI and local GUI entry points,
- report generation and triage workflows.

## Compliance statement
This project does **not** claim full MISRA C++:2023 compliance.
It currently provides a deterministic starter rule set using neutral rule metadata and IDs only.
No copyrighted MISRA rule text is embedded.

## Implemented MVP capabilities
- Recursive repository scan and single-file scan.
- Parser abstraction:
  - optional Clang backend (`clang.cindex`) when available,
  - lexical fallback backend for guaranteed local operation.
- Deterministic rule engine with starter rules:
  - forbidden `goto`,
  - function-like macro detection,
  - C-style cast pattern detection (C++),
  - recursion pattern detection,
  - tab character detection.
- Findings model with statuses:
  - `confirmed`, `possible`, `manual_review`, `suppressed`, `baseline`, `deviation`.
- Rule filtering by ID (CLI) and by ID/category/language/level (config).
- JSON, HTML, and CSV reports.
- Baseline creation and baseline comparison.
- Suppressions (line/file/rule-level via YAML patterns).
- Deviation records with justification (fingerprint keyed).
- Local SQLite scan history with trend summaries.
- GUI MVP (PySide6) with required tabs and basic scan workflow.

## Project layout
- `src/misra_checker/cli/`
- `src/misra_checker/gui/`
- `src/misra_checker/core/`
- `src/misra_checker/parser/`
- `src/misra_checker/rules/`
- `src/misra_checker/registry/`
- `src/misra_checker/findings/`
- `src/misra_checker/reports/`
- `src/misra_checker/config/`
- `src/misra_checker/suppression/`
- `src/misra_checker/baseline/`
- `src/misra_checker/storage/`
- `src/misra_checker/plugins/`
- `tests/`
- `samples/`
- `docs/`

## Setup
```bash
python3.12 -m venv .venv312
source .venv312/bin/activate
pip install -e '.[dev]'
```

GUI dependency:
```bash
pip install -e '.[gui]'
```

This project requires Python `>=3.10` (`pyproject.toml`).

## CLI usage
Help:
```bash
./run_tool.sh --help
```

Repository scan:
```bash
./run_tool.sh scan repo samples/simple_repo \
  --output-dir out --format json --format html
```

Single-file scan:
```bash
./run_tool.sh scan file samples/simple_repo/src/main.c \
  --output-dir out --format json
```

Scan with baseline/suppression/deviation/history:
```bash
./run_tool.sh scan repo samples/simple_repo \
  --baseline-file out/baseline.json \
  --suppression-file samples/suppressions.yaml \
  --deviation-file samples/deviations.yaml \
  --history-db .misra_checker/history.db \
  --output-dir out --format json --format html
```

Create baseline from JSON report:
```bash
./run_tool.sh baseline create \
  --scan-json out/<scan-id>.json --output out/baseline.json
```

Show history trend:
```bash
./run_tool.sh history trend --db .misra_checker/history.db --limit 10
```

Alternative CLI entrypoint after install:
```bash
misra-checker --help
```

## GUI usage
```bash
python -m misra_checker.gui.app
```

The GUI includes tabs for project selection, rule selection, scan configuration, findings, recommendations, deviations/suppressions, metrics/summary, and logs/diagnostics.

## Testing
```bash
PYTHONPATH=src pytest -q
```

## Known limitations
- Not a complete MISRA C++:2023 implementation.
- Current starter rules are lexical/high-confidence heuristics.
- Clang backend availability depends on local environment.
- GUI requires PySide6 and may not run until installed.
- Diff/changed-files-only scanning is not yet implemented.
- Deviation workflow is fingerprint-based and lacks full approval lifecycle.

## Documentation
- Architecture: `docs/ARCHITECTURE.md`
- Roadmap: `docs/ROADMAP.md`
- Milestone execution log: `docs/STATUS.md`

## License
This project uses the Attribution-Required Source License (ARSL) v1.0.
Any redistribution or derivative work must keep clear attribution to:
"Original project by hsoffar"
See `LICENSE` for full terms.
