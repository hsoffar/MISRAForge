# Architecture

## Product posture
MISRA Checker is a local-first static analysis platform for C/C++ with deterministic rule execution and explicit workflow controls (baseline/suppression/deviation/history).

The implementation prioritizes:
- deterministic behavior,
- graceful degradation when advanced dependencies are missing,
- stable module boundaries that can evolve into deeper semantic analysis.

## Runtime flow
1. CLI/GUI creates a `ScanRequest`.
2. `core/scan_service.py` loads config and discovers input files.
3. `parser/` parses files through selected backend (`clang` when available, otherwise lexical).
4. `rules/engine.py` runs deterministic rule checks using metadata from `registry/`.
5. `suppression/`, `baseline/`, and `findings/deviation.py` classify findings.
6. `reports/` exports JSON/HTML/CSV.
7. `storage/history.py` stores scan summaries in local SQLite.

## Module boundaries
- `cli/`: command-line entry points and workflows.
- `gui/`: PySide6 local GUI.
- `core/`: domain models and scan orchestration.
- `parser/`: file discovery, language detection, parser backends, parse diagnostics.
- `rules/`: rule interfaces, deterministic starter rules, execution engine.
- `registry/`: rule metadata definitions and registry.
- `findings/`: fingerprint and deviation helpers.
- `reports/`: serializers and report exporters.
- `config/`: config schema dataclasses and loader/validation.
- `suppression/`: suppression loading/matching and status application.
- `baseline/`: baseline loading, writing, and classification.
- `storage/`: local persistence (SQLite history).
- `plugins/`: extension placeholder for future external rules/adapters.

## Parser strategy
- `ClangParserBackend` is optional and selected when `clang.cindex` is available.
- `LexicalParserBackend` is always available and provides deterministic fallback.
- Parse failures are captured as diagnostics and reported instead of aborting the run.

## Rule strategy
- Rule metadata and executable logic are separated.
- Rules are deterministic and produce reproducible structured findings.
- Findings include fingerprints for stable workflow operations.
- Heuristic checks are marked as `possible` or `manual_review` as appropriate.

## Workflow controls
- Baseline: classify known findings as `baseline`.
- Suppressions: line/file/rule-based suppression to `suppressed`.
- Deviations: explicit accepted exceptions to `deviation` with justification.
- History: per-scan local SQLite summaries for trend tracking.

## Reporting
- JSON is the automation source.
- HTML is human-readable and navigable.
- CSV supports quick spreadsheet-style analysis.

## GUI
The GUI provides all required MVP tabs and uses the same backend as CLI:
- Project Selection
- Rule Selection
- Scan Configuration
- Findings
- Recommendations
- Deviations / Suppressions
- Metrics / Summary
- Logs / Diagnostics

## Stage 2 interface direction
Future optional local/on-prem LLM support should integrate as advisory modules only (explanations, grouping, drafting text) and never replace deterministic rule decisions.
