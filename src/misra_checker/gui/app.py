from __future__ import annotations

import json
from pathlib import Path

from misra_checker.core.models import ScanRequest, ScanTargetType
from misra_checker.core.scan_service import ScanService
from misra_checker.registry.rule_registry import build_default_registry
from misra_checker.storage.history import HistoryStore


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
            self.setWindowTitle("MISRAForge")
            self.resize(1200, 780)
            self._last_result = None
            self._last_outputs: dict[str, str] = {}
            self._auto_timer = QtCore.QTimer(self)
            self._auto_timer.timeout.connect(self._run_scan)

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
            self.dashboard_tab = self._build_dashboard_tab()
            self.logs_tab = self._build_logs_tab()

            self.tabs.addTab(self.project_tab, "Project Selection")
            self.tabs.addTab(self.rule_tab, "Rule Selection")
            self.tabs.addTab(self.scan_cfg_tab, "Scan Configuration")
            self.tabs.addTab(self.findings_tab, "Findings")
            self.tabs.addTab(self.reco_tab, "Recommendations")
            self.tabs.addTab(self.dev_sup_tab, "Deviations / Suppressions")
            self.tabs.addTab(self.metrics_tab, "Metrics / Summary")
            self.tabs.addTab(self.dashboard_tab, "Dashboard / Automation")
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
            self.auto_interval_sec = QtWidgets.QSpinBox()
            self.auto_interval_sec.setMinimum(5)
            self.auto_interval_sec.setMaximum(24 * 60 * 60)
            self.auto_interval_sec.setValue(60)
            self.auto_start_btn = QtWidgets.QPushButton("Start Auto Run")
            self.auto_stop_btn = QtWidgets.QPushButton("Stop Auto Run")
            self.auto_start_btn.clicked.connect(self._start_auto_run)
            self.auto_stop_btn.clicked.connect(self._stop_auto_run)

            formats = QtWidgets.QHBoxLayout()
            formats.addWidget(self.json_cb)
            formats.addWidget(self.html_cb)
            formats.addWidget(self.csv_cb)
            auto_controls = QtWidgets.QHBoxLayout()
            auto_controls.addWidget(self.auto_interval_sec)
            auto_controls.addWidget(QtWidgets.QLabel("seconds"))
            auto_controls.addWidget(self.auto_start_btn)
            auto_controls.addWidget(self.auto_stop_btn)

            f.addRow("Output directory", self.output_dir_edit)
            f.addRow("Baseline file", self.baseline_edit)
            f.addRow("Suppression file", self.suppression_edit)
            f.addRow("Deviation file", self.deviation_edit)
            f.addRow("History DB", self.history_edit)
            f.addRow("Report formats", formats)
            f.addRow("Auto run interval", auto_controls)
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

        def _build_dashboard_tab(self) -> QtWidgets.QWidget:
            w = QtWidgets.QWidget()
            l = QtWidgets.QVBoxLayout(w)

            top = QtWidgets.QHBoxLayout()
            self.group_combo = QtWidgets.QComboBox()
            self.group_combo.addItems(["file", "rule", "status"])
            self.group_combo.currentTextChanged.connect(self._refresh_group_table)
            self.run_now_btn = QtWidgets.QPushButton("Run Now")
            self.run_now_btn.clicked.connect(self._run_scan)
            self.refresh_hist_btn = QtWidgets.QPushButton("Refresh History")
            self.refresh_hist_btn.clicked.connect(self._refresh_history)
            top.addWidget(QtWidgets.QLabel("Group findings by"))
            top.addWidget(self.group_combo)
            top.addStretch(1)
            top.addWidget(self.run_now_btn)
            top.addWidget(self.refresh_hist_btn)
            l.addLayout(top)

            self.group_table = QtWidgets.QTableWidget(0, 2)
            self.group_table.setHorizontalHeaderLabels(["Group", "Count"])
            self.group_table.horizontalHeader().setStretchLastSection(True)
            l.addWidget(self.group_table)

            l.addWidget(QtWidgets.QLabel("Recent runs"))
            self.history_table = QtWidgets.QTableWidget(0, 4)
            self.history_table.setHorizontalHeaderLabels(["Finished", "Target", "Total", "New"])
            self.history_table.horizontalHeader().setStretchLastSection(True)
            l.addWidget(self.history_table)
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
            self._log(f"Run complete: findings={len(result.findings)} files={len(result.analyzed_files)}")

        def _populate_from_result(self) -> None:
            if self._last_result is None:
                return

            result = self._last_result
            self.project_info.setText(
                f"Latest run | files={len(result.analyzed_files)} | findings={len(result.findings)}"
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
                "run": "latest",
                "outputs": self._last_outputs,
                "status_counts": status_count,
                "file_heatmap": heatmap,
                "rules_available": len(result.available_rule_ids),
                "rules_hit": len({f.rule_id for f in result.findings}),
            }
            self.metrics_box.setPlainText(json.dumps(metrics, indent=2))
            self._refresh_group_table()
            self._refresh_history()

            if result.parse_diagnostics:
                for diag in result.parse_diagnostics:
                    self._log(f"Diagnostic: {diag}")

        def _start_auto_run(self) -> None:
            interval_ms = int(self.auto_interval_sec.value()) * 1000
            self._auto_timer.start(interval_ms)
            self._log(f"Auto run started (interval={self.auto_interval_sec.value()}s)")

        def _stop_auto_run(self) -> None:
            self._auto_timer.stop()
            self._log("Auto run stopped")

        def _refresh_group_table(self, *_args: object) -> None:
            if self._last_result is None:
                self.group_table.setRowCount(0)
                return

            mode = self.group_combo.currentText()
            counts: dict[str, int] = {}
            for finding in self._last_result.findings:
                if mode == "file":
                    key = finding.location.path
                elif mode == "rule":
                    key = finding.rule_id
                else:
                    key = finding.status.value
                counts[key] = counts.get(key, 0) + 1

            rows = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
            self.group_table.setRowCount(len(rows))
            for i, (key, value) in enumerate(rows):
                self.group_table.setItem(i, 0, QtWidgets.QTableWidgetItem(key))
                self.group_table.setItem(i, 1, QtWidgets.QTableWidgetItem(str(value)))

        def _refresh_history(self) -> None:
            db = self.history_edit.text().strip()
            if not db:
                self.history_table.setRowCount(0)
                return
            try:
                rows = HistoryStore(db).trend(limit=20)
            except Exception as exc:
                self._log(f"History read failed: {exc}")
                return

            self.history_table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                summary = row.get("summary", {})
                values = [
                    str(row.get("finished_at", "")),
                    str(row.get("target", "")),
                    str(row.get("total_findings", "")),
                    str(summary.get("new", "")),
                ]
                for c, v in enumerate(values):
                    self.history_table.setItem(i, c, QtWidgets.QTableWidgetItem(v))


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
