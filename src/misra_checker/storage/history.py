from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from misra_checker.core.models import ScanResult


class HistoryStore:
    def __init__(self, db_path: str) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS scans (
                    scan_id TEXT PRIMARY KEY,
                    started_at TEXT NOT NULL,
                    finished_at TEXT NOT NULL,
                    target TEXT NOT NULL,
                    total_findings INTEGER NOT NULL,
                    summary_json TEXT NOT NULL,
                    outputs_json TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def save_scan(self, result: ScanResult, target: str, outputs: dict[str, str]) -> None:
        summary = {
            "total_findings": len(result.findings),
            "baseline": sum(1 for f in result.findings if f.status.value == "baseline"),
            "suppressed": sum(1 for f in result.findings if f.status.value == "suppressed"),
            "deviation": sum(1 for f in result.findings if f.status.value == "deviation"),
            "new": sum(
                1
                for f in result.findings
                if f.status.value not in {"baseline", "suppressed", "deviation"}
            ),
        }
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO scans (
                    scan_id, started_at, finished_at, target, total_findings, summary_json, outputs_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    result.scan_id,
                    result.started_at,
                    result.finished_at,
                    target,
                    len(result.findings),
                    json.dumps(summary),
                    json.dumps(outputs),
                ),
            )
            conn.commit()

    def trend(self, limit: int = 20) -> list[dict[str, object]]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT scan_id, finished_at, target, total_findings, summary_json
                FROM scans ORDER BY finished_at DESC LIMIT ?
                """,
                (limit,),
            ).fetchall()
        result: list[dict[str, object]] = []
        for scan_id, finished_at, target, total_findings, summary_json in rows:
            result.append(
                {
                    "scan_id": scan_id,
                    "finished_at": finished_at,
                    "target": target,
                    "total_findings": total_findings,
                    "summary": json.loads(summary_json),
                }
            )
        return result
