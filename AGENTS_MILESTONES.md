# MISRA Checker Local Product Build Instructions — Milestone Execution Version

## Mission
Build a serious, fully local static-analysis product that can evolve into a credible MISRA C++:2023 checking platform while also supporting C codebases.

This is **not** a toy script. It is a modular developer product intended for safety-conscious and embedded-oriented teams. The outcome should be a working local toolchain with a clear path toward stronger rule coverage, validation, and future optional local/on-prem LLM assistance.

## Operating Constraints
- Everything must run locally.
- No cloud dependency is allowed in the product itself.
- No source code may leave the machine.
- Stage 1 must be deterministic and must not depend on any LLM.
- Stage 2 may optionally add a local or on-prem LLM adapter, but the rule engine remains the single source of truth.
- Design for maintainability, extensibility, validation, and future qualification-style evidence.
- Assume the codebase being analyzed may be in **C**, **C++**, or mixed.
- Support **repository-wide scanning** and **single-file scanning**.
- Support **GUI** and **CLI** usage.
- Support **Linux first**, but keep cross-platform packaging in mind.
- MISRA rule texts are copyrighted. Do **not** embed copyrighted rule text unless explicitly provided by the user via licensed content. Use rule IDs, metadata, tags, applicability, severity, rationale summaries you generate yourself, and configuration-driven rule packs.

## Product Vision
Create a local static-analysis platform with these major capabilities:
1. Parse and inspect C and C++ repositories.
2. Run rule-based checks with a plugin-like architecture.
3. Produce structured findings and compliance-oriented reports.
4. Let engineers choose rules, files, repositories, profiles, suppressions, and deviation records.
5. Offer a local GUI for practical workflows.
6. Provide a clean foundation for future advanced semantic checks and optional local LLM assistance.

## Delivery Philosophy
Build this as a sequence of **stable milestones**. At the end of every milestone:
- The repository should remain in a runnable, inspectable state.
- The current limitations must be documented honestly.
- New code must include tests where practical.
- Existing behavior must not be silently broken.
- A short progress note must be written into `docs/STATUS.md`.

Prefer a working vertical slice over broad but unfinished abstractions.

## Required Working Pattern
1. Read this file fully before doing any work.
2. Start by creating or updating the following docs:
   - `README.md`
   - `docs/ARCHITECTURE.md`
   - `docs/ROADMAP.md`
   - `docs/STATUS.md`
3. Work through the milestones **in order**.
4. After each milestone, run the relevant tests or smoke checks.
5. If blocked, document the blocker in `docs/STATUS.md`, apply a scoped fallback, and continue.
6. Do not stop at architecture-only output; implement code.
7. Do not claim complete MISRA C++:2023 compliance unless it is truly implemented and validated.

## Preferred Technical Direction
Use a practical hybrid architecture:
- **Core language / backend**: Python for orchestration and fast iteration, with a clean path to performance-sensitive native modules later.
- **Parsing / semantic analysis**:
  - Prefer **Clang/LLVM-based** parsing for C/C++ semantic accuracy.
  - Consider **libclang** or Clang tooling integration as the main semantic backbone.
  - Optionally use **tree-sitter** for fast indexing/navigation where full semantic analysis is not required.
- **GUI**:
  - Prefer **PySide6 / Qt** for a native-feeling GUI.
  - Acceptable alternative: local-only web UI if it stays simple and fully local.
- **Reporting**:
  - HTML report with navigation and drill-down.
  - JSON output for automation.
  - CSV export if feasible in MVP.
- **Storage**:
  - Lightweight local persistence such as SQLite for scan history, baselines, and deviation tracking.
- **Testing**:
  - pytest-based test suite.
  - Golden repos and regression corpus.

If you choose a different stack, justify it clearly in `docs/ARCHITECTURE.md`.

## Milestone Plan

### Milestone 0 — Discovery, Architecture, and Scaffold
**Goal**: Establish the product shape and a runnable project skeleton.

**Deliverables**:
- `README.md` with product intent and local-only constraints.
- `docs/ARCHITECTURE.md` with module boundaries and tradeoffs.
- `docs/ROADMAP.md` with milestone breakdown.
- `docs/STATUS.md` initialized.
- Project scaffold with package layout.
- Build/test/dev setup.
- Minimal entrypoints for CLI and app startup.

**Exit criteria**:
- Repository structure exists and is coherent.
- Developer can install dependencies and run a help command.
- Architecture docs reflect the implementation direction.

**Fallbacks if blocked**:
- If full packaging is not ready, create a direct `python -m ...` entry path and document it.

---

### Milestone 1 — Core Domain Models and Configuration
**Goal**: Build the stable internal contracts.

**Deliverables**:
- Core models for rules, findings, scans, statuses, severities, suppressions, deviations, and baselines.
- Config loader for project config, enabled rules, and report settings.
- Validation for config inputs.
- Rule metadata registry.
- Fingerprint strategy for findings.

**Exit criteria**:
- Models are typed and documented.
- Config files can be loaded from disk.
- A sample project config works.

**Fallbacks if blocked**:
- If full schema validation is slow to build, start with dataclass/pydantic validation and document limits.

---

### Milestone 2 — Project Loader and Parser Abstraction
**Goal**: Make code discovery and parsing possible for both repo and single-file modes.

**Deliverables**:
- Repository/project loader.
- Language detection.
- Single-file mode.
- Compile database discovery if present.
- Parser abstraction layer.
- A first parser backend implementation.
- Parse diagnostics capture.

**Exit criteria**:
- The tool can enumerate analyzable source files.
- A parsed representation or fallback token/index form is available.
- Parser failures are reported instead of crashing the run.

**Fallbacks if blocked**:
- If semantic Clang parsing is partially blocked by environment dependencies, implement a layered backend:
  1. lexical/text backend for selected rules,
  2. optional libclang backend when available.
- Document reduced coverage clearly.

---

### Milestone 3 — Rule Engine and Starter Checks
**Goal**: Deliver real deterministic analysis.

**Deliverables**:
- Rule engine with registration, enable/disable, filtering, and execution pipeline.
- Representative deterministic starter rules across categories such as:
  - forbidden constructs,
  - macro misuse,
  - unsafe casts where detectable,
  - control-flow patterns,
  - lexical/style constraints,
  - language subset restrictions.
- Rule results mapped into the findings model.
- Recommendation templates per rule.

**Exit criteria**:
- Running the engine against a sample repository produces findings.
- Rules can be selected by ID/category/language/profile.
- Findings are stable and reproducible.

**Fallbacks if blocked**:
- Prefer fewer high-confidence rules over many weak ones.
- Mark heuristic/manual-review findings explicitly.

---

### Milestone 4 — Scan Orchestration, Reports, and CLI
**Goal**: Create a usable end-to-end workflow.

**Deliverables**:
- Scan coordinator/orchestrator.
- JSON report export.
- HTML report export with navigation.
- CLI commands for:
  - repo scan,
  - single-file scan,
  - config selection,
  - rule filtering,
  - report export.
- Sample local run documented in README.

**Exit criteria**:
- A user can run the tool from CLI and produce a report.
- HTML and JSON reports are both generated.
- Errors are actionable and logged.

**Fallbacks if blocked**:
- If polished HTML is not finished, ship a functional navigable report first and document styling gaps.

---

### Milestone 5 — Baseline, Suppressions, Deviations, and History
**Goal**: Make the tool usable in real engineering workflows.

**Deliverables**:
- Baseline creation and comparison.
- New vs existing finding classification.
- Suppression support:
  - line-level,
  - file-level,
  - rule-level.
- Deviation records with justification text.
- Local persistence for scan history.
- Summary metrics/trend support.

**Exit criteria**:
- Baseline comparison works.
- A finding can be classified as new/baseline/suppressed/deviation.
- Suppression/deviation behavior is documented and test-covered.

**Fallbacks if blocked**:
- If SQLite history is not finished, persist baseline and scan snapshots in versioned JSON as an interim step.

---

### Milestone 6 — Local GUI MVP
**Goal**: Provide a practical local interactive workflow.

**Deliverables**:
- GUI with at least these views/tabs:
  - Project Selection
  - Rule Selection
  - Scan Configuration
  - Findings
  - Recommendations
  - Deviations / Suppressions
  - Metrics / Summary
  - Logs / Diagnostics
- Ability to select repo or single file.
- Ability to run analysis.
- Ability to view findings.
- Ability to export reports.

**Exit criteria**:
- GUI launches locally.
- User can select a target and run a scan.
- Findings are visible in a table.

**Fallbacks if blocked**:
- If full tab completeness is too large for the current run, implement the first functional subset:
  - target selection,
  - rule selection,
  - run scan,
  - findings table,
  - export action.
- Leave placeholder tabs only if clearly marked as such.

---

### Milestone 7 — Tests, Samples, Documentation, and Hardening
**Goal**: Leave behind a credible MVP, not just code.

**Deliverables**:
- Unit tests.
- Integration/smoke tests.
- Sample C and C++ repos or files with expected findings.
- Honest README usage instructions.
- Documented limitations.
- Known gaps and next steps.

**Exit criteria**:
- A new user can run the tool locally.
- The repo contains tests and sample artifacts.
- MVP limitations are explicit.

**Fallbacks if blocked**:
- Prefer smaller but reliable sample coverage over broad unverified claims.

## Required Module Boundaries
At minimum include these modules, with clean responsibility separation:
- `cli/`
- `gui/`
- `core/`
- `parser/`
- `rules/`
- `registry/`
- `findings/`
- `reports/`
- `config/`
- `suppression/`
- `baseline/`
- `storage/`
- `plugins/`
- `tests/`
- `samples/`
- `docs/`

## Functional Requirements
Implement these capabilities:
- Full repository recursive scan.
- Single-file scan.
- Optional changed-files-only or diff-based scan if practical.
- Rule filtering by ID, language, category, required/advisory, and enabled profile.
- HTML and JSON reports in MVP.
- Clear distinction between confirmed, possible, suppressed, baseline, deviation, and manual-review findings.

## GUI Requirements
Provide at least these views/tabs:
1. Project Selection
2. Rule Selection
3. Scan Configuration
4. Findings
5. Recommendations
6. Deviations / Suppressions
7. Metrics / Summary
8. Logs / Diagnostics

Be practical and somewhat innovative:
- folder/module heatmap if feasible,
- new vs baseline comparison,
- rule coverage/maturity indicators,
- compliance dashboard,
- clickable navigation to source locations where feasible.

## Quality Bar
- Prefer correctness and transparency over inflated rule counts.
- Prefer deterministic checks over speculative analysis.
- Prefer stable abstractions over quick hacks that block later growth.
- Keep the codebase runnable after every milestone.
- Document what is implemented vs aspirational.

## Stage 2 Forward Interface
Design but do not depend on an optional future LLM adapter for:
- natural-language explanation,
- remediation ideas,
- grouping related findings,
- draft deviation text,
- educational hints.

The LLM must always be advisory only.

## Required End State for This Run
By the end of the run, aim to leave the repository with:
- a coherent project scaffold,
- docs and architecture notes,
- deterministic rule engine foundation,
- repo and single-file scanning,
- CLI,
- reports,
- at least a minimal GUI,
- tests and sample inputs,
- honest documentation of limitations and next steps.

If the full target cannot be completed in one run, maximize the value of completed milestones and make the next step obvious in `docs/STATUS.md`.
