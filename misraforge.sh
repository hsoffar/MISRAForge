#!/usr/bin/env sh
set -eu

# Single launcher for MISRAForge.
# Examples:
#   ./misraforge.sh setup
#   ./misraforge.sh scan repo samples/simple_repo --output-dir out --format json --format html
#   ./misraforge.sh quality
#   ./misraforge.sh all samples/simple_repo
#   ./misraforge.sh ui
#   ./misraforge.sh api
#   ./misraforge.sh gui
#   ./misraforge.sh history

pick_python() {
  if [ -x ".venv312/bin/python" ]; then
    echo ".venv312/bin/python"
    return
  fi
  if [ -x ".venv/bin/python" ]; then
    echo ".venv/bin/python"
    return
  fi
  if command -v python3.12 >/dev/null 2>&1; then
    echo "python3.12"
    return
  fi
  if command -v python3 >/dev/null 2>&1; then
    echo "python3"
    return
  fi
  echo "python"
}

PYTHON_BIN="$(pick_python)"

setup_env() {
  if [ ! -x ".venv312/bin/python" ]; then
    if command -v python3.12 >/dev/null 2>&1; then
      python3.12 -m venv .venv312
    else
      "$PYTHON_BIN" -m venv .venv312
    fi
  fi
  .venv312/bin/pip install -e '.[dev,web]'
}

main() {
  if [ "$#" -eq 0 ]; then
    set -- --help
  fi

  case "$1" in
    setup)
      setup_env
      ;;
    gui)
      shift
      PYTHONPATH=src "$PYTHON_BIN" -m misra_checker.gui.app "$@"
      ;;
    ui)
      shift
      PYTHONPATH=src "$PYTHON_BIN" -m misra_checker.cli.main api serve --scan-json out/report.json --tests-dir tests --rule-content-file samples/rule_content_open.json --host 127.0.0.1 --port 8775 >/tmp/misra_ui_api.log 2>&1 &
      API_PID=$!
      sleep 1
      cleanup() {
        kill "$API_PID" >/dev/null 2>&1 || true
      }
      trap cleanup EXIT INT TERM
      (cd ui && npm run dev "$@")
      ;;
    ui-build)
      shift
      (cd ui && npm run build "$@")
      ;;
    api)
      shift
      if [ "$#" -eq 0 ]; then
        PYTHONPATH=src "$PYTHON_BIN" -m misra_checker.cli.main api serve --scan-json out/report.json --tests-dir tests --rule-content-file samples/rule_content_open.json --host 127.0.0.1 --port 8775
      else
        PYTHONPATH=src "$PYTHON_BIN" -m misra_checker.cli.main api serve "$@"
      fi
      ;;
    quality)
      shift
      PYTHONPATH=src "$PYTHON_BIN" -m pytest -q
      PYTHONPATH=src "$PYTHON_BIN" -m misra_checker.cli.main rules matrix --scan-json out/report.json --tests-dir tests --output out/rule-matrix.json
      ;;
    all)
      shift
      TARGET="${1:-samples/simple_repo}"
      PYTHONPATH=src "$PYTHON_BIN" -m pytest -q
      PYTHONPATH=src "$PYTHON_BIN" -m misra_checker.cli.main scan repo "$TARGET" --output-dir out --format json --format html --format csv
      PYTHONPATH=src "$PYTHON_BIN" -m misra_checker.cli.main rules matrix --scan-json out/report.json --tests-dir tests --output out/rule-matrix.json
      echo "All done."
      echo "UI:        ./misraforge.sh ui"
      echo "API:       ./misraforge.sh api"
      ;;
    history)
      shift
      if [ "$#" -eq 0 ]; then
        PYTHONPATH=src "$PYTHON_BIN" -m misra_checker.cli.main history trend --db .misra_checker/history.db --limit 20
      else
        PYTHONPATH=src "$PYTHON_BIN" -m misra_checker.cli.main history "$@"
      fi
      ;;
    *)
      PYTHONPATH=src "$PYTHON_BIN" -m misra_checker.cli.main "$@"
      ;;
  esac
}

main "$@"
