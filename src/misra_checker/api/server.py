from __future__ import annotations

from pathlib import Path
from typing import Any


def serve_api(
    scan_json: str = "out/report.json",
    tests_dir: str = "tests",
    rule_content_file: str = "samples/rule_content_open.json",
    host: str = "127.0.0.1",
    port: int = 8775,
) -> None:
    try:
        import uvicorn
        from fastapi import FastAPI, HTTPException, Query
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.responses import JSONResponse
    except ModuleNotFoundError as exc:
        print(f"Missing dependency: {exc.name}")
        print("Install with: pip install -e '.[web]'")
        raise SystemExit(2) from exc

    from misra_checker.api.rule_content import load_rule_content_map
    from misra_checker.core.models import ScanRequest, ScanTargetType
    from misra_checker.core.scan_service import ScanService
    from misra_checker.registry.rule_registry import build_default_registry
    from misra_checker.reports.serializers import scan_result_to_dict
    from misra_checker.rules.coverage import build_rule_matrix, load_scan_payload

    app = FastAPI(title="MISRA Checker API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    state: dict[str, str] = {"scan_json": scan_json, "last_target": "samples/simple_repo"}

    def _latest_payload() -> dict[str, Any]:
        return load_scan_payload(state["scan_json"])

    def _rules_payload() -> dict[str, Any]:
        registry = build_default_registry()
        rule_content = load_rule_content_map(rule_content_file)
        matrix = build_rule_matrix(_latest_payload(), tests_dir)
        matrix_map = {row["rule_id"]: row for row in matrix["rules"]}
        rows = []
        for meta in registry.all():
            info = rule_content.get(meta.rule_id, {})
            row = matrix_map.get(meta.rule_id, {})
            rows.append(
                {
                    "rule_id": meta.rule_id,
                    "title": meta.title,
                    "category": meta.category,
                    "level": meta.level.value,
                    "severity": meta.severity.value,
                    "languages": [lang.value for lang in meta.languages],
                    "rationale_summary": meta.rationale_summary,
                    "implemented": bool(row.get("implemented", False)),
                    "tested": bool(row.get("tested", False)),
                    "detected_count": int(row.get("detected_count", 0)),
                    "test_files": row.get("test_files", []),
                    "content_source": info.get("source", ""),
                    "content_license": info.get("license", ""),
                    "content_summary": info.get("summary", ""),
                    "content_full_text": info.get("full_text", ""),
                    "content_notes": info.get("notes", ""),
                }
            )
        return {"count": len(rows), "rules": rows}

    @app.get("/")
    def root() -> dict[str, Any]:
        return {
            "service": "misra-checker-api",
            "status": "ok",
            "docs": "/docs",
            "endpoints": [
                "/api/health",
                "/api/scan/latest",
                "/api/scan/run",
                "/api/summary",
                "/api/findings",
                "/api/rules",
                "/api/rules/{rule_id}",
                "/api/rules/matrix",
                "/api/files",
            ],
        }

    @app.get("/api/health")
    def health() -> dict[str, Any]:
        path = Path(state["scan_json"])
        return {"status": "ok", "scan_json": str(path), "exists": path.exists()}

    @app.get("/api/scan/latest")
    def scan_latest() -> dict[str, Any]:
        payload = _latest_payload()
        if not payload:
            raise HTTPException(status_code=404, detail=f"scan report not found: {state['scan_json']}")
        return payload

    @app.post("/api/scan/run")
    def scan_run(body: dict[str, Any]) -> JSONResponse:
        target = str(body.get("target", "")).strip()
        if not target:
            raise HTTPException(status_code=400, detail="target is required")
        target_type_raw = str(body.get("target_type", "repo")).strip().lower()
        if target_type_raw not in ("repo", "file"):
            raise HTTPException(status_code=400, detail="target_type must be 'repo' or 'file'")
        target_type = ScanTargetType.REPOSITORY if target_type_raw == "repo" else ScanTargetType.SINGLE_FILE

        formats = body.get("formats", ["json", "html"])
        if not isinstance(formats, list) or not formats:
            formats = ["json", "html"]
        request = ScanRequest(
            target=target,
            target_type=target_type,
            output_dir=str(body.get("output_dir", "out")),
            report_formats=tuple(str(item) for item in formats),
            include_rules=tuple(str(item) for item in body.get("include_rules", [])),
            exclude_rules=tuple(str(item) for item in body.get("exclude_rules", [])),
            baseline_file=body.get("baseline_file"),
            suppression_file=body.get("suppression_file"),
            deviation_file=body.get("deviation_file"),
            history_db_path=body.get("history_db"),
            config_path=body.get("config"),
            rule_pack_file=body.get("rule_pack_file"),
        )
        result, outputs = ScanService().run(request)
        state["scan_json"] = outputs.get("json", state["scan_json"])
        state["last_target"] = target
        payload = scan_result_to_dict(result)
        return JSONResponse({"run": payload, "outputs": outputs, "scan_json": state["scan_json"]})

    @app.get("/api/summary")
    def summary() -> dict[str, Any]:
        payload = _latest_payload()
        if not payload:
            return {"summary": {}, "by_file": {}, "by_rule": {}, "deviation_by_rule": {}, "files": []}

        findings = payload.get("findings", [])
        by_file: dict[str, int] = {}
        by_rule: dict[str, int] = {}
        deviation_by_rule: dict[str, int] = {}
        for item in findings:
            if not isinstance(item, dict):
                continue
            rule_id = str(item.get("rule_id", ""))
            finding_status = str(item.get("status", ""))
            location = item.get("location", {}) if isinstance(item.get("location"), dict) else {}
            path = str(location.get("path", ""))
            if path:
                by_file[path] = by_file.get(path, 0) + 1
            if rule_id:
                by_rule[rule_id] = by_rule.get(rule_id, 0) + 1
                if finding_status == "deviation":
                    deviation_by_rule[rule_id] = deviation_by_rule.get(rule_id, 0) + 1
        return {
            "summary": payload.get("summary", {}),
            "by_file": dict(sorted(by_file.items(), key=lambda kv: (-kv[1], kv[0]))),
            "by_rule": dict(sorted(by_rule.items(), key=lambda kv: (-kv[1], kv[0]))),
            "deviation_by_rule": dict(sorted(deviation_by_rule.items(), key=lambda kv: (-kv[1], kv[0]))),
            "files": sorted(by_file.keys()),
        }

    @app.get("/api/findings")
    def findings(
        group_by: str = Query("flat", pattern="^(flat|file|rule|status)$"),
        key: str = "",
        q: str = "",
        severity: str = "",
        status: str = "",
        rule_id: str = "",
        file_path: str = "",
    ) -> dict[str, Any]:
        payload = _latest_payload()
        items = payload.get("findings", []) if payload else []
        filtered: list[dict[str, Any]] = []
        q_low = q.strip().lower()
        for item in items:
            if not isinstance(item, dict):
                continue
            location = item.get("location", {}) if isinstance(item.get("location"), dict) else {}
            text = " ".join(
                [
                    str(item.get("rule_id", "")),
                    str(item.get("status", "")),
                    str(item.get("severity", "")),
                    str(location.get("path", "")),
                    str(item.get("message", "")),
                    str(item.get("recommendation", "")),
                ]
            ).lower()
            if q_low and q_low not in text:
                continue
            if severity and str(item.get("severity", "")) != severity:
                continue
            if status and str(item.get("status", "")) != status:
                continue
            if rule_id and str(item.get("rule_id", "")) != rule_id:
                continue
            if file_path and str(location.get("path", "")) != file_path:
                continue
            filtered.append(item)

        if group_by == "flat":
            if key:
                filtered = [item for item in filtered if str(item.get("rule_id", "")) == key]
            return {"group_by": "flat", "total": len(filtered), "groups": {"all": filtered}}

        def _get_group_value(item: dict[str, Any]) -> str:
            if group_by == "rule":
                return str(item.get("rule_id", ""))
            if group_by == "status":
                return str(item.get("status", ""))
            location = item.get("location", {}) if isinstance(item.get("location"), dict) else {}
            return str(location.get("path", ""))

        groups: dict[str, list[dict[str, Any]]] = {}
        for item in filtered:
            group = _get_group_value(item)
            if key and group != key:
                continue
            groups.setdefault(group, []).append(item)
        grouped = dict(sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])))
        return {"group_by": group_by, "total": len(filtered), "groups": grouped}

    @app.get("/api/rules")
    def rules() -> dict[str, Any]:
        return _rules_payload()

    @app.get("/api/rules/{rule_id}")
    def rule_details(rule_id: str) -> dict[str, Any]:
        payload = _rules_payload()
        for item in payload["rules"]:
            if item["rule_id"] == rule_id:
                return item
        raise HTTPException(status_code=404, detail=f"rule not found: {rule_id}")

    @app.get("/api/rules/matrix")
    def rule_matrix() -> dict[str, Any]:
        return build_rule_matrix(_latest_payload(), tests_dir)

    @app.get("/api/files")
    def files(root: str = "") -> dict[str, Any]:
        selected_root = root.strip() or state.get("last_target", "").strip() or "."
        return build_project_browser(selected_root)

    print(f"API: http://{host}:{port}")
    print(f"OpenAPI docs: http://{host}:{port}/docs")
    uvicorn.run(app, host=host, port=port, log_level="warning")


def build_project_browser(root: str) -> dict[str, Any]:
    path = Path(root).resolve()
    if not path.exists():
        return {"root": str(path), "exists": False, "folder_count": 0, "file_count": 0, "tree": {}}
    if path.is_file():
        return {
            "root": str(path.parent),
            "exists": True,
            "folder_count": 1,
            "file_count": 1,
            "tree": {"name": path.parent.name or str(path.parent), "folders": [], "files": [str(path)]},
        }

    tree, folder_count, file_count = _walk_tree(path, depth=0, max_depth=6)
    return {
        "root": str(path),
        "exists": True,
        "folder_count": folder_count,
        "file_count": file_count,
        "tree": tree,
    }


def _walk_tree(path: Path, depth: int, max_depth: int) -> tuple[dict[str, Any], int, int]:
    node: dict[str, Any] = {"name": path.name or str(path), "folders": [], "files": []}
    folder_count = 1
    file_count = 0
    if depth > max_depth:
        return node, folder_count, file_count

    try:
        entries = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    except Exception:
        return node, folder_count, file_count

    for entry in entries:
        if entry.name.startswith('.'):
            continue
        if entry.is_dir():
            child, sub_folders, sub_files = _walk_tree(entry, depth=depth + 1, max_depth=max_depth)
            node["folders"].append(child)
            folder_count += sub_folders
            file_count += sub_files
            continue

        if entry.suffix.lower() not in {".c", ".cc", ".cpp", ".cxx", ".h", ".hpp", ".hh", ".hxx"}:
            continue
        node["files"].append(str(entry))
        file_count += 1
    return node, folder_count, file_count
