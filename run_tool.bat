@echo off
setlocal

REM Run MISRA Checker CLI from repository root.
REM Usage examples:
REM   run_tool.bat --help
REM   run_tool.bat scan repo samples\simple_repo --output-dir out --format json

set "PYTHONPATH=src"
python -m misra_checker.cli.main %*

endlocal
