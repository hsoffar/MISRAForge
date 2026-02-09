# Roadmap

## Completed in this run
1. Milestone 0: discovery/docs/scaffold/entrypoints.
2. Milestone 1: core models, config validation, registry metadata, fingerprinting.
3. Milestone 2: repo/single-file loader, language detection, parser abstraction + diagnostics.
4. Milestone 3: deterministic rule engine and starter checks.
5. Milestone 4: scan orchestration, CLI scan commands, JSON/HTML/CSV reports.
6. Milestone 5: baseline/suppression/deviation/history workflows.
7. Milestone 6: local GUI MVP with required tabs and scan workflow.
8. Milestone 7: tests/samples/doc hardening and explicit limitations.
9. Milestone 8: reporting/dashboard uplift (coverage metrics, grouped HTML, web dashboard command, stable latest report filenames + archive snapshots).
10. Milestone 9: centralized launcher workflows, rule quality matrix, and local automation API endpoints.
11. Milestone 10: FastAPI control dashboard with scan orchestration, issue pivots, per-file scan actions, and local rule-content detail panels.
12. Milestone 11: browser-first FastAPI layout and stronger grouping/filtering surface.
13. Milestone 12: React+TypeScript professional tabbed frontend track integrated with FastAPI APIs.

## Near-term next steps
1. Expand deterministic rule coverage with stronger semantic checks and larger rule families.
2. Improve Clang backend compile database integration depth.
3. Add changed-files/diff scan mode for CI-focused workflows.
4. Add richer suppression/deviation lifecycle metadata and approval states.
5. Strengthen dashboard UX (history charts, source drill-down, triage workflow views).
6. Add plugin loader contract for external local rule packs.
7. Publish rule implementation backlog grouped by MISRA category with test acceptance criteria per rule.

## Long-term direction
1. Build qualification-style evidence artifacts (traceability/test evidence).
2. Introduce optional local/on-prem advisory LLM adapter behind strict non-authoritative interfaces.
3. Harden packaging/distribution for Linux-first and cross-platform installers.
