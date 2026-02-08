# Codex unattended run notes

## Files
- `AGENTS_MILESTONES.md` — persistent repo instructions
- `TASK_MISRA_MILESTONES.md` — one-shot execution task

## Recommended usage
Place `AGENTS_MILESTONES.md` in the repo root as `AGENTS.md`.

Then run from the repository root:

```bash
cp AGENTS_MILESTONES.md AGENTS.md
codex exec --full-auto "$(cat TASK_MISRA_MILESTONES.md)"
```

If you want Codex to work inside a specific repo from another directory:

```bash
codex exec --full-auto -C /path/to/repo "$(cat /path/to/TASK_MISRA_MILESTONES.md)"
```

## Practical suggestion
Before leaving the run unattended, make sure the repo is either:
- a clean disposable branch, or
- a working tree with changes committed/stashed.

This milestone prompt is designed so Codex should:
- build incrementally,
- leave docs showing progress,
- keep the project runnable after each stage,
- fall back gracefully if libclang or GUI setup is partially blocked.
