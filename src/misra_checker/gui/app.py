from __future__ import annotations

import json
from pathlib import Path

from misra_checker.core.models import ScanRequest, ScanTargetType
from misra_checker.core.scan_service import ScanService
from misra_checker.registry.rule_registry import build_default_registry


class _GuiUnavailable:
    @staticmethod
    def main() -> int:
        print("PySide6 is not installed. Install with: pip install -e .[gui]")
        return 1


try:
    from PySide6 import QtCore, QtWidgets
except ImportError:
    QtCore = None
    QtWidgets = None


if QtWidgets is not None:

    class MainWindow(QtWidgets.QMainWindow):
        def __init__(self) -> None:
            super().__init__()
            self.setWindowTitle("MISRA Checker MVP")
            self.resize(1200, 780)
            self._last_result = None
            self._last_outputs: dict[str, str] = {}

            root = QtWidgets.QWidget()
            self.setCentralWidget(root)
            layout = QtWidgets.QVBoxLayout(root)

            toolbar = QtWidgets.QHBoxLayout()
            self.target_edit = QtWidgets.QLineEdit("samples/simple_repo")
            self.mode_combo = QtWidgets.QComboBox()
            self.mode_combo.addItems(["repository", "single_file"])
            browse_btn = QtWidgets.QPushButton("Browse")
            run_btn = QtWidgets.QPushButton("Run Scan")
            browse_btn.clicked.connect(self._browse_target)
            run_btn.clicked.connect(self._run_scan)

            toolbar.addWidget(QtWidgets.QLabel("Target"))
            toolbar.addWidget(self.target_edit, 1)
            toolbar.addWidget(QtWidgets.QLabel("Mode"))
            toolbar.addWidget(self.mode_combo)
            toolbar.addWidget(browse_btn)
            toolbar.addWidget(run_btn)
            layout.addLayout(toolbar)

            self.tabs = QtWidgets.QTabWidget()
            layout.addWidget(self.tabs, 1)

            self.project_tab = self._build_project_tab()
            self.rule_tab = self._build_rule_tab()
            self.scan_cfg_tab = self._build_scan_config_tab()
            self.findings_tab = self._build_findings_tab()
            self.reco_tab = self._build_recommendations_tab()
            self.dev_sup_tab = self._build_deviation_suppression_tab()
            self.metrics_tab = self._build_metrics_tab()
            self.logs_tab = self._build_logs_tab()

            self.tabs.addTab(self.project_tab, "Project Selection")
            self.tabs.addTab(self.rule_tab, "Rule Selection")
            self.tabs.addTab(self.scan_cfg_tab, "Scan Configuration")
            self.tabs.addTab(self.findings_tab, "Findings")
            self.tabs.addTab(self.reco_tab, "Recommendations")
            self.tabs.addTab(self.dev_sup_tab, "Deviations / Suppressions")
            self.tabs.addTab(self.metrics_tab, "Metrics / Summary")
            self.tabs.addTab(self.logs_tab, "Logs / Diagnostics")

        def _build_project_tab(self) -> QtWidgets.QWidget:
            w = QtWidgets.QWidget()
            l = QtWidgets.QVBoxLayout(w)
            l.addWidget(QtWidgets.QLabel("Select a repository or single file from the top bar."))
            self.project_info = QtWidgets.QLabel("No scan executed yet.")
            l.addWidget(self.project_info)
            return w

        def _build_rule_tab(self) -> QtWidgets.QWidget:
            w = QtWidgets.QWidget()
            l = QtWidgets.QVBoxLayout(w)
            l.addWidget(QtWidgets.QLabel("Enable deterministic starter rules:"))
            self.rule_list = QtWidgets.QListWidget()
            registry = build_default_registry()
            for meta in registry.all():
                item = QtWidgets.QListWidgetItem(f"{meta.rule_id} [{meta.level.value}] {meta.title}")
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                item.setCheckState(QtCore.Qt.Checked)
                item.setData(QtCore.Qt.UserRole, meta.rule_id)
                self.rule_list.addItem(item)
            l.addWidget(self.rule_list)
            return w

        def _build_scan_config_tab(self) -> QtWidgets.QWidget:
            w = QtWidgets.QWidget()
            f = QtWidgets.QFormLayout(w)
            self.output_dir_edit = QtWidgets.QLineEdit("out")
            self.baseline_edit = QtWidgets.QLineEdit("")
            self.suppression_edit = QtWidgets.QLineEdit("")
            self.deviation_edit = QtWidgets.QLineEdit("")
            self.history_edit = QtWidgets.QLineEdit(".misra_checker/history.db")

            self.json_cb = QtWidgets.QCheckBox("JSON")
            self.json_cb.setChecked(True)
            self.html_cb = QtWidgets.QCheckBox("HTML")
            self.html_cb.setChecked(True)
            self.csv_cb = QtWidgets.QCheckBox("CSV")

            formats = QtWidgets.QHBoxLayout()
            formats.addWidget(self.json_cb)
            formats.addWidget(self.html_cb)
            formats.addWidget(self.csv_cb)

            f.addRow("Output directory", self.output_dir_edit)
            f.addRow("Baseline file", self.baseline_edit)
            f.addRow("Suppression file", self.suppression_edit)
            f.addRow("Deviation file", self.deviation_edit)
            f.addRow("History DB", self.history_edit)
            f.addRow("Report formats", formats)
            return w

        def _build_findings_tab(self) -> QtWidgets.QWidget:
            w = QtWidgets.QWidget()
            l = QtWidgets.QVBoxLayout(w)
            self.findings_table = QtWidgets.QTableWidget(0, 7)
            self.findings_table.setHorizontalHeaderLabels(
                ["Rule", "Status", "Severity", "Path", "Line", "Message", "Fingerprint"]
            )
            self.findings_table.horizontalHeader().setStretchLastSection(True)
            l.addWidget(self.findings_table)
            return w

        def _build_recommendations_tab(self) -> QtWidgets.QWidget:
            w = QtWidgets.QWidget()
            l = QtWidgets.QVBoxLayout(w)
            self.reco_box = QtWidgets.QPlainTextEdit()
            self.reco_box.setReadOnly(True)
            l.addWidget(self.reco_box)
            return w

        def _build_deviation_suppression_tab(self) -> QtWidgets.QWidget:
            w = QtWidgets.QWidget()
            l = QtWidgets.QVBoxLayout(w)
            l.addWidget(QtWidgets.QLabel("Configure baseline/suppression/deviation files in Scan Configuration tab."))
            self.ds_box = QtWidgets.QPlainTextEdit()
            self.ds_box.setReadOnly(True)
            l.addWidget(self.ds_box)
            return w

        def _build_metrics_tab(self) -> QtWidgets.QWidget:
            w = QtWidgets.QWidget()
            l = QtWidgets.QVBoxLayout(w)
            self.metrics_box = QtWidgets.QPlainTextEdit()
            self.metrics_box.setReadOnly(True)
            l.addWidget(self.metrics_box)
            return w

        def _build_logs_tab(self) -> QtWidgets.QWidget:
            w = QtWidgets.QWidget()
            l = QtWidgets.QVBoxLayout(w)
            self.log_box = QtWidgets.QPlainTextEdit()
            self.log_box.setReadOnly(True)
            l.addWidget(self.log_box)
            return w

        def _log(self, message: str) -> None:
            self.log_box.appendPlainText(message)

        def _browse_target(self) -> None:
            mode = self.mode_combo.currentText()
            if mode == "repository":
                path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Repository")
            else:
                path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select File", filter="C/C++ (*.c *.h *.cpp *.cc *.cxx *.hpp *.hh *.hxx)")
            if path:
                self.target_edit.setText(path)

        def _selected_rule_ids(self) -> tuple[str, ...]:
            ids: list[str] = []
            for i in range(self.rule_list.count()):
                item = self.rule_list.item(i)
                if item.checkState() == QtCore.Qt.Checked:
                    ids.append(item.data(QtCore.Qt.UserRole))
            return tuple(ids)

        def _selected_formats(self) -> tuple[str, ...]:
            fmts: list[str] = []
            if self.json_cb.isChecked():
                fmts.append("json")
            if self.html_cb.isChecked():
                fmts.append("html")
            if self.csv_cb.isChecked():
                fmts.append("csv")
            return tuple(fmts or ["json"])

        def _run_scan(self) -> None:
            target = self.target_edit.text().strip()
            if not target:
                self._log("Target is empty")
                return

            mode = self.mode_combo.currentText()
            target_type = ScanTargetType.REPOSITORY if mode == "repository" else ScanTargetType.SINGLE_FILE

            request = ScanRequest(
                target=target,
                target_type=target_type,
                output_dir=self.output_dir_edit.text().strip() or "out",
                report_formats=self._selected_formats(),
                include_rules=self._selected_rule_ids(),
                baseline_file=self.baseline_edit.text().strip() or None,
                suppression_file=self.suppression_edit.text().strip() or None,
                deviation_file=self.deviation_edit.text().strip() or None,
                history_db_path=self.history_edit.text().strip() or None,
            )

            try:
                result, outputs = ScanService().run(request)
            except Exception as exc:
                self._log(f"Scan failed: {exc}")
                return

            self._last_result = result
            self._last_outputs = outputs
            self._populate_from_result()
            self._log(f"Scan complete: {result.scan_id} findings={len(result.findings)}")

        def _populate_from_result(self) -> None:
            if self._last_result is None:
                return

            result = self._last_result
            self.project_info.setText(
                f"Scan {result.scan_id} | files={len(result.analyzed_files)} | findings={len(result.findings)}"
            )

            self.findings_table.setRowCount(len(result.findings))
            recommendations: list[str] = []
            by_path: dict[str, int] = {}
            status_count: dict[str, int] = {}
            ds_lines: list[str] = []

            for r, finding in enumerate(result.findings):
                by_path[finding.location.path] = by_path.get(finding.location.path, 0) + 1
                status_count[finding.status.value] = status_count.get(finding.status.value, 0) + 1

                cols = [
                    finding.rule_id,
                    finding.status.value,
                    finding.severity.value,
                    finding.location.path,
                    str(finding.location.line),
                    finding.message,
                    finding.fingerprint,
                ]
                for c, value in enumerate(cols):
                    self.findings_table.setItem(r, c, QtWidgets.QTableWidgetItem(value))

                recommendations.append(
                    f"{finding.rule_id} @ {finding.location.path}:{finding.location.line} -> {finding.recommendation}"
                )

                if "suppression_reason" in finding.extra:
                    ds_lines.append(f"Suppressed {finding.fingerprint}: {finding.extra['suppression_reason']}")
                if "deviation_justification" in finding.extra:
                    ds_lines.append(f"Deviation {finding.fingerprint}: {finding.extra['deviation_justification']}")

            self.reco_box.setPlainText("\n".join(recommendations))
            self.ds_box.setPlainText("\n".join(ds_lines) or "No suppression/deviation annotations in current result.")

            heatmap = sorted(by_path.items(), key=lambda kv: kv[1], reverse=True)
            metrics = {
                "scan_id": result.scan_id,
                "outputs": self._last_outputs,
                "status_counts": status_count,
                "file_heatmap": heatmap,
            }
            self.metrics_box.setPlainText(json.dumps(metrics, indent=2))

            if result.parse_diagnostics:
                for diag in result.parse_diagnostics:
                    self._log(f"Diagnostic: {diag}")


    def main() -> int:
        app = QtWidgets.QApplication([])
        window = MainWindow()
        window.show()
        return app.exec()

else:

    def main() -> int:
        return _GuiUnavailable.main()


if __name__ == "__main__":
    raise SystemExit(main())
