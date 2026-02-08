Build the MISRA checker MVP described in `AGENTS_MILESTONES.md`.

Execution mode:
- Work autonomously through the milestones in order.
- Keep the repository in a runnable state after each milestone.
- Make practical decisions and proceed without unnecessary questions.
- If blocked, document the blocker and implement the strongest fallback that preserves forward progress.
- Do real implementation work, not docs-only output.

Mandatory first actions:
1. Read `AGENTS_MILESTONES.md` fully.
2. Create or update:
   - `README.md`
   - `docs/ARCHITECTURE.md`
   - `docs/ROADMAP.md`
   - `docs/STATUS.md`
3. Add the initial project scaffold.

Milestone execution rules:
- Finish Milestone 0 before starting Milestone 1.
- At the end of each milestone:
  - update `docs/STATUS.md`,
  - run relevant tests or smoke checks,
  - document what works and what is incomplete.
- Prefer a working end-to-end vertical slice by Milestone 4 over broad unfinished abstractions.
- Do not claim full MISRA C++:2023 compliance.
- Do not embed copyrighted MISRA rule text.
- Use rule IDs and neutral metadata only.

Implementation priority:
1. Milestone 0 — Discovery, architecture, scaffold.
2. Milestone 1 — Core models, config, registry.
3. Milestone 2 — Project loader, parser abstraction, single-file/repo input handling.
4. Milestone 3 — Rule engine and representative deterministic rules.
5. Milestone 4 — Scan orchestration, HTML/JSON reports, CLI.
6. Milestone 5 — Baseline, suppressions, deviations, local history.
7. Milestone 6 — Local GUI MVP.
8. Milestone 7 — Tests, samples, docs hardening.

Minimum acceptable end state for this run:
- The repository contains a coherent Python-based MVP implementation.
- CLI scan works for at least one local sample project.
- HTML and JSON reports are generated.
- Single-file scan is supported.
- GUI launches and can perform at least a basic scan workflow.
- Tests exist for core paths.
- Limitations and next steps are documented honestly.

Preferred implementation details:
- Python backend.
- libclang/Clang-oriented parser abstraction where possible.
- Optional lightweight fallback backend for lexical checks if Clang setup is unavailable.
- PySide6 GUI if practical.
- SQLite or JSON-backed local persistence for baseline/history.

When making tradeoffs:
- Choose deterministic, testable behavior.
- Prefer fewer high-confidence rules over more weak ones.
- Prefer graceful degradation over failing the whole run.
- Prefer code that can evolve into a serious product.

Definition of success:
Leave behind a repo that looks like the first credible version of a local MISRA-oriented static-analysis product rather than a proof-of-concept script.
