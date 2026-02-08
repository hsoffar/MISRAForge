from __future__ import annotations

import importlib


def test_gui_entrypoint_callable() -> None:
    app = importlib.import_module("misra_checker.gui.app")
    assert hasattr(app, "main")
