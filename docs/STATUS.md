# STATUS

## 2026-03-06 - Milestone 0
### Completed
- Read and followed `AGENTS_MILESTONES.md`.
- Initialized foundational docs: `README.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, `docs/STATUS.md`.
- Added Python project setup (`pyproject.toml`) with CLI/GUI entry points.
- Created required top-level package/module directories under `src/misra_checker/`.

### Smoke checks
- Pending: run `python -m misra_checker.cli.main --help` after initial entrypoints are added.

### Incomplete / limitations
- Core implementation beyond scaffold is pending subsequent milestones.

## 2026-03-06 - Milestone 1
### Completed
- Implemented typed domain models for rules, findings, scan request/result, severity/status, suppressions, deviations, and baseline entries.
- Added project config models and deterministic YAML/JSON config loader with validation and clear error handling.
- Added rule metadata registry with starter MISRA-oriented metadata IDs and neutral rationale summaries.
- Added stable finding fingerprint function for run-to-run identity tracking.
- Added sample project config (`samples/project_config.yaml`).

### Smoke checks
- `PYTHONPATH=src pytest -q` -> 3 passed.

### Incomplete / limitations
- Rule execution pipeline and parser abstraction are not yet implemented (next milestones).
- Config validation currently uses dataclass + manual checks rather than JSON schema.

## 2026-03-06 - Milestone 2
### Completed
- Implemented repository and single-file input discovery with recursive source file enumeration.
- Added language detection for C/C++ file extensions.
- Added compile database discovery (`compile_commands.json` in root/build).
- Implemented parser abstraction with:
  - optional `ClangParserBackend` (when `clang.cindex` is available),
  - deterministic `LexicalParserBackend` fallback.
- Added parser service that captures parse failures as diagnostics/errors instead of crashing scans.
- Added sample C/C++ files for analysis in `samples/simple_repo/src/`.

### Smoke checks
- `PYTHONPATH=src pytest -q` -> 6 passed.

### Incomplete / limitations
- Clang backend currently uses direct parse args and does not yet fully consume compile DB flags.
- Parsed representation is lexical-first; advanced semantic AST-driven checks are future work.

## 2026-03-06 - Milestone 3
### Completed
- Implemented rule engine with registration-driven rule object construction and execution pipeline.
- Added rule filtering by rule ID, category, language, and level.
- Implemented deterministic starter checks:
  - `MC3R-FORBIDDEN-GOTO`
  - `MC3A-MACRO-FUNC`
  - `MC3R-CAST-CSTYLE`
  - `MC3R-FORBIDDEN-RECURSION`
  - `MC3A-TAB-CHAR`
- Mapped rule results to structured findings with statuses (`confirmed`, `possible`, `manual_review`), recommendation templates, and fingerprints.

### Smoke checks
- `PYTHONPATH=src pytest -q` -> 8 passed.

### Incomplete / limitations
- Recursion and C-style cast detections are lexical heuristics; they prioritize deterministic behavior and may produce conservative/manual-review findings.
- Rule plugin loading is scaffolded by module boundary only; dynamic external plugin loading is not yet implemented.

## 2026-03-06 - Milestone 4
### Completed
- Implemented scan orchestration service connecting config, discovery, parser, rule engine, and report exporters.
- Added JSON/HTML/CSV report exporters.
- Implemented CLI scan workflow with subcommands:
  - `scan repo <path>`
  - `scan file <path>`
- Added CLI options for config path, rule include/exclude filters, output directory, and report formats.
- Added integration tests for repo and single-file scan flows and report generation.

### Smoke checks
- `PYTHONPATH=src pytest -q` -> 11 passed.
- `PYTHONPATH=src python -m misra_checker.cli.main scan repo samples/simple_repo --output-dir out --format json --format html` -> successful, reports generated.
- `PYTHONPATH=src python -m misra_checker.cli.main scan file samples/simple_repo/src/main.c --output-dir out --format json` -> successful.

### Incomplete / limitations
- CLI currently supports include/exclude rule IDs directly; advanced filter flags (category/language/level) are config-driven, not yet direct CLI flags.
- HTML report is functional and navigable but intentionally minimal styling.

## 2026-03-06 - Milestone 5
### Completed
- Added suppression workflow support with YAML entries:
  - line-level,
  - file-level (path pattern),
  - rule-level.
- Added baseline load/apply/create support using JSON baseline snapshots.
- Added deviation workflow support with YAML records keyed by finding fingerprint and justification text.
- Integrated classification into scan flow with clear statuses (`suppressed`, `baseline`, `deviation`, plus existing finding statuses).
- Added local SQLite history store with per-scan summary metrics and trend retrieval.
- Extended CLI with:
  - `baseline create --scan-json ... --output ...`
  - `history trend --db ... --limit ...`
  - scan-time controls for baseline/suppression/deviation/history inputs.

### Smoke checks
- `PYTHONPATH=src pytest -q` -> 12 passed.
- `PYTHONPATH=src python -m misra_checker.cli.main scan repo samples/simple_repo --output-dir out --format json --history-db .misra_checker/history.db` -> successful.
- `PYTHONPATH=src python -m misra_checker.cli.main baseline create --scan-json out/scan-0ace68e0a7.json --output out/baseline.json` -> successful.
- `PYTHONPATH=src python -m misra_checker.cli.main history trend --db .misra_checker/history.db --limit 5` -> successful.

### Incomplete / limitations
- Baseline entries currently rely on fingerprint equality only; advanced fuzzy matching is not implemented.
- Deviation records are fingerprint-keyed and do not yet include approval lifecycle state machine.

## 2026-03-06 - Milestone 6
### Completed
- Implemented local PySide6 GUI MVP with required tabs:
  1. Project Selection
  2. Rule Selection
  3. Scan Configuration
  4. Findings
  5. Recommendations
  6. Deviations / Suppressions
  7. Metrics / Summary
  8. Logs / Diagnostics
- Added runnable scan workflow in GUI:
  - select repo/single-file target,
  - select enabled rules,
  - configure outputs and workflow control files,
  - run scan,
  - view findings and recommendations,
  - view summary metrics including per-file finding heatmap.
- Added graceful fallback when PySide6 is not installed.

### Smoke checks
- `PYTHONPATH=src pytest -q` -> 13 passed.
- `PYTHONPATH=src python -m misra_checker.gui.app` -> prints dependency message and exits cleanly when PySide6 unavailable.

### Blockers and fallback
- Blocker: PySide6 is not installed in the current environment, so full GUI runtime interaction could not be exercised here.
- Fallback: GUI entrypoint degrades gracefully with explicit install guidance; CLI remains fully operational.

### Incomplete / limitations
- GUI currently focuses on MVP functionality and does not yet include advanced interactive source navigation widgets.

## 2026-03-06 - Milestone 7
### Completed
- Expanded and stabilized test suite across config loading, parser discovery/service, rule engine, scan orchestration, CLI parsing, workflow controls, and GUI entrypoint importability.
- Added sample C/C++ inputs and sample workflow files (`samples/simple_repo`, suppressions/deviations/config).
- Hardened docs (`README.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`) to match implemented behavior and known gaps.
- Added plugin contract placeholder for future external local rule packs.

### Smoke checks
- `PYTHONPATH=src pytest -q` -> 13 passed.
- `PYTHONPATH=src python -m misra_checker.cli.main scan repo samples/simple_repo --config samples/project_config.yaml --output-dir out --format json --format html` -> successful.
- `PYTHONPATH=src python -m misra_checker.cli.main scan file samples/simple_repo/src/util.cpp --output-dir out --format json` -> successful.
- `PYTHONPATH=src python -m misra_checker.cli.main baseline create --scan-json out/scan-23205a04ba.json --output out/baseline_from_final.json` -> successful.
- `PYTHONPATH=src python -m misra_checker.cli.main history trend --db .misra_checker/history.db --limit 3` -> successful.

### Blockers and fallback
- Blocker: PySide6 unavailable in current environment for interactive GUI validation.
- Fallback: GUI code is implemented and entrypoint is graceful when dependency is missing.

### Honest limitations
- No claim of full MISRA C++:2023 compliance.
- Current rule set is a deterministic starter subset.
- Some checks are lexical/manual-review heuristics pending deeper semantic analysis.
- Diff/changed-files-only scanning is not yet implemented.
- Deviation lifecycle and plugin loading are foundational, not fully mature.

### Next obvious step
- Install GUI dependency (`pip install -e .[gui]`) and run `python -m misra_checker.gui.app` to validate the interactive workflow end-to-end locally.
