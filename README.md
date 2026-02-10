# MISRA Checker

Local-first static analysis platform for C/C++ with MISRA-oriented deterministic checks, modular checker architecture, JSON-driven rule catalog, and a React UI.

## Current architecture
- Core scan orchestration: `src/misra_checker/core/`
- Rule metadata/catalog (default): `src/misra_checker/rules/default_rule_pack.json`
- Rule engine: `src/misra_checker/rules/engine.py`
- Modular checker modules: `src/misra_checker/rules/checkers/`
- Checker factory/registry: `src/misra_checker/rules/checkers/registry.py`
- Custom JSON regex rule packs: `src/misra_checker/rules/pack_loader.py`
- API backend for UI: `src/misra_checker/api/server.py`
- Frontend UI: `ui/`

## How rules work
There are two rule sources:

1. Default built-in catalog (JSON)
- File: `src/misra_checker/rules/default_rule_pack.json`
- Defines rule metadata and which checker module/class runs each rule:
  - `implementation.type = "builtin"`
  - `implementation.name = "...CheckerClass..."`

2. Custom rule packs (JSON)
- File example: `samples/custom_rules_demo.json`
- Defines regex-driven custom rules without Python edits.
- Loaded with `--rule-pack`.

## Add your rules here
### A) Add/edit built-in checker rules (JSON + module)
1. Add metadata entry to:
- `src/misra_checker/rules/default_rule_pack.json`

2. Point it to checker implementation:
- `implementation.name` must match a checker in:
  - `src/misra_checker/rules/checkers/registry.py`

3. If needed, create a new checker module/class under:
- `src/misra_checker/rules/checkers/`

### B) Add quick custom rules via JSON only
1. Create or edit a JSON pack like:
- `samples/custom_rules_demo.json`

2. Run scan with pack:
```bash
./run_tool.sh scan repo samples/simple_repo \
  --output-dir out --format json \
  --rule-pack samples/custom_rules_demo.json
```

## Rule-pack JSON format
```json
{
  "pack_name": "custom-pack",
  "rules": [
    {
      "rule_id": "ORG-CUSTOM-1",
      "title": "Rule title",
      "category": "custom_category",
      "level": "advisory",
      "severity": "low",
      "languages": ["c", "cpp"],
      "pattern": "\\bprintf\\s*\\(",
      "message": "printf usage detected",
      "status": "manual_review",
      "flags": ["IGNORECASE"],
      "recommendation": "Use project logging abstraction"
    }
  ]
}
```

## Current integrated rules
Run:
```bash
./run_tool.sh rules list
```
Current total in matrix: 15 rules (implemented/tested).

## Run commands
Setup:
```bash
./misraforge.sh setup
```

Scan repo:
```bash
./run_tool.sh scan repo samples/simple_repo --output-dir out --format json --format html
```

Show matrix:
```bash
./run_tool.sh rules matrix --scan-json out/report.json --tests-dir tests --output out/rule-matrix.json
```

Start API:
```bash
./misraforge.sh api
```

Start UI (auto-starts API backend):
```bash
./misraforge.sh ui
```

## API endpoints
- `/api/health`
- `/api/scan/latest`
- `/api/scan/run`
- `/api/summary`
- `/api/findings`
- `/api/rules`
- `/api/rules/{rule_id}`
- `/api/rules/matrix`
- `/api/files`

## Validation
```bash
PYTHONPATH=src pytest -q
```

## Compliance note
This tool does not claim full MISRA C++:2023 compliance yet. It provides a growing MISRA-oriented deterministic subset plus extensible custom rule packs.

## License
This project is licensed under the GNU General Public License v3.0 (GPL-3.0-only).
See `LICENSE` for full terms.
