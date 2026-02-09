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

## 2026-03-06 - Milestone 8
### Completed
- Improved report summaries with additional deterministic metrics:
  - `summary.by_file`
  - `summary.by_rule`
  - `summary.rule_coverage` (available rules, hit rules, coverage percentage).
- Upgraded HTML report UX to support local filtering/grouping (`file`, `rule`, `flat`) with status overview cards.
- Added local web dashboard serving command:
  - `web serve --scan-json ... --host ... --port ...`
  - dashboard groups and filters findings interactively from the JSON report.
- Stabilized output naming for latest artifacts:
  - `out/report.json`
  - `out/report.html`
  - `out/report.csv`
  - plus timestamped archives under `out/archive/`.
- Extended GUI metrics/dashboard behavior with grouping and recent history panels.

### Smoke checks
- `PYTHONPATH=src pytest -q` -> 15 passed.
- `PYTHONPATH=src python -m misra_checker.cli.main scan repo samples/simple_repo --output-dir out --format json --format html --format csv` -> successful; stable report filenames created.
- `PYTHONPATH=src python -m misra_checker.cli.main web serve --scan-json out/report.json --host 127.0.0.1 --port 8765` with local probe to `http://127.0.0.1:8765/data` -> successful JSON response.

### Incomplete / limitations
- Web dashboard currently visualizes a single JSON report file per run and does not yet provide multi-run trend pages.
- GUI and web dashboard currently do not include inline source viewer/deep code navigation.

## 2026-03-06 - Milestone 9
### Completed
- Added rule quality matrix generation to identify per-rule implementation/test/detection coverage:
  - CLI: `rules matrix --scan-json ... --tests-dir ... --output ...`
  - JSON output includes totals and per-rule rows.
- Added rule inventory command:
  - CLI: `rules list` (text or JSON).
- Added local automation API server for tool integrations:
  - CLI: `api serve --scan-json ... --tests-dir ... --host ... --port ...`
  - endpoints: `/health`, `/rules`, `/scan/latest`, `/rules/matrix`.
- Upgraded dashboard runtime:
  - serves matrix data endpoint (`/matrix`),
  - visual charts for status and top files,
  - rule quality table with implementation/testing/detection fields.
- Expanded single launcher (`misraforge.sh`) with centralized workflows:
  - `quality` (tests + rule matrix),
  - `all` (tests + scan + reports + rule matrix),
  - `api`,
  - existing `web`, `gui`, `history`, `scan`, `setup`.

### Smoke checks
- `PYTHONPATH=src pytest -q` -> 18 passed.
- `./misraforge.sh quality` -> successful.
- `./misraforge.sh all samples/simple_repo` -> successful; generated reports and `out/rule-matrix.json`.
- `api serve` probe:
  - `/health` -> status ok
  - `/rules/matrix` -> returns matrix JSON
- `web serve` probe:
  - `/matrix` -> returns matrix JSON

### Incomplete / limitations
- The project still does **not** claim complete MISRA C++:2023 rule coverage.
- Current implementation remains a deterministic starter pack with a stronger coverage/testing visibility layer.

## 2026-03-06 - Milestone 10
### Completed
- Added FastAPI-based web control dashboard (`web serve --engine fastapi`) focused on full workflow control:
  - run repository scans and single-file scans from the web UI,
  - browse issues grouped by file/rule/status/flat,
  - click file entries to filter findings and launch per-file scan.
- Added deviation visibility by rule in the dashboard summary panel.
- Added rule details interaction (hover/click) with extended metadata panel.
- Added local rule-content pack support in the web UI:
  - open demo pack: `samples/rule_content_open.json`,
  - private/local template: `samples/rule_content_local.example.json`.
- Added FastAPI endpoints supporting dashboard interactions:
  - `/api/scan/run`
  - `/api/scan/latest`
  - `/api/summary`
  - `/api/findings`
  - `/api/rules`
  - `/api/rules/{rule_id}`
  - `/api/rules/matrix`
  - `/api/health`
- Added `web` optional dependency group (`fastapi`, `uvicorn`) and updated launcher/setup to support it.

### Smoke checks
- `PYTHONPATH=src pytest -q` -> 19 passed.
- `PYTHONPATH=src python -m misra_checker.cli.main web serve --help` -> shows fastapi/baseline engine options.
- Local fastapi probe:
  - `/api/summary` returns grouped summary
  - `/api/rules/MC3R-FORBIDDEN-GOTO` returns rule details
  - `POST /api/scan/run` with single-file target returns successful run payload.

### Incomplete / limitations
- Rule full text availability depends on local licensed content you provide; repository includes open demo content only.
- Dashboard currently uses client-side rendering without server-side auth/session controls.

## 2026-03-06 - Milestone 11
### Completed
- Redesigned FastAPI dashboard layout for easier navigation:
  - left pane: project browser (folders/files),
  - center pane: grouped issues + combined filters,
  - right pane: rules list + rule detail panel + deviation summary.
- Added project browser backend endpoint:
  - `/api/files?root=<path>` returns folder/file tree for C/C++ source browsing.
- Expanded issue filtering in `/api/findings` with:
  - severity,
  - status,
  - rule_id,
  - file_path,
  - text query,
  - grouping mode.
- Added UI actions to select file from browser and run per-file scans directly.

### Smoke checks
- `PYTHONPATH=src pytest -q` -> 20 passed.
- FastAPI probe:
  - `/api/files?root=samples/simple_repo` -> returns folder/file tree payload.
  - `/api/findings?...` -> returns grouped/filtered response shape.

## 2026-03-06 - Milestone 12
### Completed
- Added a new professional GUI track under `ui/` using React + TypeScript (Vite).
- Implemented tabbed navigation:
  - `Overview`
  - `Explorer`
  - `Findings`
  - `Rules`
  - `Deviations`
- Added floating flyover behavior for rule details in `Rules` tab (hover-based panel near cursor).
- Added explorer-focused navigation in frontend:
  - file tree browsing,
  - file click sets file filter and target for quick per-file scan flow.
- Integrated frontend with existing FastAPI endpoints via Vite proxy (`/api -> :8765`).
- Added FastAPI CORS middleware for local frontend dev origins (`127.0.0.1:5173`, `localhost:5173`).
- Extended launcher with frontend commands:
  - `./misraforge.sh ui`
  - `./misraforge.sh ui-build`

### Smoke checks
- `PYTHONPATH=src pytest -q` -> 20 passed.
- `cd ui && npm run build` -> successful production build generated.

## 2026-03-06 - Milestone 13
### Completed
- Reworked the new React GUI visual design to a compact enterprise layout:
  - left vertical navigation rail with persistent tabs,
  - compact top scan controls,
  - clearer content hierarchy and reduced visual noise.
- Rebuilt Findings experience into a professional tri-pane workflow:
  - left filter panel,
  - center grouped issue list,
  - right issue inspector.
- Upgraded rule hover behavior to floating flyover cards (near cursor) instead of bottom-panel-only behavior.
- Updated color system to neutral/light, high-density styling for easier scanning and navigation.

### Smoke checks
- `cd ui && npm run build` -> successful.
- `PYTHONPATH=src pytest -q` -> 20 passed.

## 2026-03-06 - Milestone 14
### Completed
- Removed legacy `web` command path and old `src/misra_checker/web/` implementation.
- Consolidated all runtime endpoints behind `api serve` under `/api/*`.
- Migrated required UI backend behaviors into `src/misra_checker/api/server.py`:
  - scan run/latest,
  - summary/findings/rules/rule-matrix,
  - file browser tree endpoint.
- Updated launcher workflow:
  - `./misraforge.sh ui` now auto-starts API backend + React UI dev server.
  - no separate `web` command required.
- Updated UI dev proxy to the API port (`8775`).

### Smoke checks
- `PYTHONPATH=src pytest -q` -> 19 passed.
- `cd ui && npm run build` -> successful.
- API probe:
  - `/api/summary` returns expected payload,
  - `/api/files?root=samples/simple_repo` returns folder/file tree.

## 2026-03-07 - Milestone 15
### Completed
- Added JSON rule-pack integration for easy rule extension without Python edits.
- Added regex-based dynamic rule execution from pack files.
- Added scan CLI support:
  - `scan ... --rule-pack <path.json>`
- Added API scan support:
  - `POST /api/scan/run` with `rule_pack_file`.
- Added sample pack:
  - `samples/custom_rules_demo.json`.

### Smoke checks
- `PYTHONPATH=src pytest -q` -> 23 passed.
- Scan with custom pack produced custom rule finding (`ORG-DEMO-PRINTF`).

## 2026-03-07 - Milestone 16
### Completed
- Moved default built-in rule catalog into JSON:
  - `src/misra_checker/rules/default_rule_pack.json`
- Switched default registry and recommendations to load from this JSON catalog.
- Kept engine check implementations in Python but activation/metadata/recommendations are JSON-driven.

### Smoke checks
- `PYTHONPATH=src pytest -q` -> 23 passed.

## 2026-03-07 - Milestone 17
### Completed
- Refactored rule implementation into modular checker modules:
  - `rules/checkers/lexical.py`
  - `rules/checkers/control_flow.py`
  - `rules/checkers/preprocessor.py`
  - `rules/checkers/type_safety.py`
  - `rules/checkers/numeric.py`
  - `rules/checkers/maintainability.py`
  - `rules/checkers/language_subset.py`
  - `rules/checkers/io_usage.py`
- Added common checker factory registry API:
  - `rules/checkers/registry.py`
- Default JSON catalog now controls built-in checker binding through:
  - `implementation: { \"type\": \"builtin\", \"name\": \"...\" }`
- Added additional built-in rules integrated through JSON+modules:
  - `MC3A-PRINTF`
  - `MC3R-MULTI-RETURN`

### Smoke checks
- `PYTHONPATH=src pytest -q` -> 23 passed.
- `rules matrix` -> `total=15 implemented=15 tested=15`.
