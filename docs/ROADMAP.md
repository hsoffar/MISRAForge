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

## Near-term next steps
1. Expand deterministic rule coverage with stronger semantic checks.
2. Improve Clang backend compile database integration depth.
3. Add changed-files/diff scan mode for CI-focused workflows.
4. Add richer suppression/deviation lifecycle metadata and approval states.
5. Strengthen HTML report UX (navigation, grouping, trend panels).
6. Add plugin loader contract for external local rule packs.

## Long-term direction
1. Build qualification-style evidence artifacts (traceability/test evidence).
2. Introduce optional local/on-prem advisory LLM adapter behind strict non-authoritative interfaces.
3. Harden packaging/distribution for Linux-first and cross-platform installers.
