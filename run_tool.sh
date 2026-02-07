#!/usr/bin/env sh
set -eu

# Run MISRA Checker CLI from repository root.
# Usage:
#   ./run_tool.sh --help
#   ./run_tool.sh scan repo samples/simple_repo --output-dir out --format json

if [ -x ".venv312/bin/python" ]; then
  PYTHON_BIN=".venv312/bin/python"
elif [ -x ".venv/bin/python" ]; then
  PYTHON_BIN=".venv/bin/python"
elif command -v python3.12 >/dev/null 2>&1; then
  PYTHON_BIN="python3.12"
else
  PYTHON_BIN="python"
fi

PYTHONPATH=src "$PYTHON_BIN" -m misra_checker.cli.main "$@"
