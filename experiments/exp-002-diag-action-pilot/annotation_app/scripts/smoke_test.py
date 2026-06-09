#!/usr/bin/env python3
"""End-to-end smoke test for the local AutoFusion annotation app."""

from __future__ import annotations

import argparse
import json
import os
import re
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path


def app_root() -> Path:
    return Path(__file__).resolve().parents[1]


def repo_root(root: Path) -> Path:
    for parent in root.parents:
        if (parent / ".git").exists() and (parent / "experiments").exists():
            return parent
    return root.parents[2]


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def request_json(url: str, method: str = "GET", payload: dict | None = None) -> dict | list:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def request_text(url: str) -> str:
    with urllib.request.urlopen(url, timeout=10) as response:
        return response.read().decode("utf-8")


def wait_for_server(base_url: str, process: subprocess.Popen, timeout_seconds: int = 20) -> None:
    deadline = time.time() + timeout_seconds
    last_error: Exception | None = None
    while time.time() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"server exited early with code {process.returncode}")
        try:
            request_json(f"{base_url}/api/health")
            return
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            time.sleep(0.2)
    raise RuntimeError(f"server did not become ready: {last_error}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sheet",
        default="experiments/exp-002-diag-action-pilot/annotations/smoke_annotation_sheet_v1.draft.jsonl",
    )
    parser.add_argument("--annotator", default="smoke-test")
    parser.add_argument("--keep-db", action="store_true")
    args = parser.parse_args()

    root = app_root()
    repository = repo_root(root)
    backend = root / "backend"
    validator = repository / "experiments/exp-002-diag-action-pilot/scripts/validate_jsonl.py"
    sheet_path = Path(args.sheet)
    if not sheet_path.is_absolute():
        sheet_path = repository / sheet_path
    if not sheet_path.exists():
        raise SystemExit(f"sheet not found: {sheet_path}")

    temp_dir = Path(tempfile.mkdtemp(prefix="autofusion-annotation-smoke-"))
    db_path = temp_dir / "annotations.sqlite"
    export_path = temp_dir / "export.jsonl"
    smoke_sheet_path = temp_dir / "smoke_with_extra_media.jsonl"
    port = free_port()
    base_url = f"http://127.0.0.1:{port}"

    rows = []
    with sheet_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                rows.append(json.loads(stripped))
    if not rows:
        raise SystemExit(f"sheet is empty: {sheet_path}")
    rows[0].setdefault("media", {}).setdefault("items", []).extend(
        [
            {
                "label": "extra_audio",
                "role": "evidence",
                "modality": "audio",
                "path": "experiments/exp-002-diag-action-pilot/annotation_app/fixtures/missing_audio.wav",
            },
            {
                "label": "reference_image",
                "role": "evidence",
                "modality": "image",
                "path": "experiments/exp-002-diag-action-pilot/annotation_app/fixtures/missing_image.png",
            },
        ]
    )
    with smoke_sheet_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    env = os.environ.copy()
    env["AUTOFUSION_REPO_ROOT"] = str(repository)
    env["ANNOTATION_DB_PATH"] = str(db_path)
    env["PYTHONPATH"] = str(backend)

    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
        "--app-dir",
        str(backend),
    ]
    process = subprocess.Popen(command, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        wait_for_server(base_url, process)
        html = request_text(f"{base_url}/")
        assets = re.findall(r'(?:src|href)="([^"]+)"', html)
        if not assets:
            raise RuntimeError("frontend HTML did not reference bundled assets")
        for asset in assets:
            if asset.startswith("/"):
                request_text(f"{base_url}{asset}")

        import_result = request_json(
            f"{base_url}/api/import",
            method="POST",
            payload={
                "path": str(smoke_sheet_path),
                "annotator": args.annotator,
                "session_name": "smoke-test",
                "replace": True,
            },
        )
        if import_result.get("rows_imported") != 5:
            raise RuntimeError(f"expected 5 imported rows, got {import_result}")

        instances = request_json(f"{base_url}/api/instances")
        if len(instances) != 5:
            raise RuntimeError(f"expected 5 instances, got {len(instances)}")

        first_id = instances[0]["instance_id"]
        detail = request_json(f"{base_url}/api/instances/{first_id}")
        annotation = detail["annotation"]
        media_items = detail["media"].get("items", [])
        if len(media_items) < 4:
            raise RuntimeError("detail response did not include source/corrupted plus media.items entries")

        annotation["review_status"] = "in_progress"
        annotation.setdefault("recovery_evidence", {})["annotation_app_time_spans"] = [
            {"modality": "audio", "start": 0.0, "end": 1.0, "note": "smoke-test"}
        ]
        annotation.setdefault("defect_location", {})["bboxes"] = [
            {"media": "source", "modality": "video", "time": 0.0, "x": 0.1, "y": 0.1, "width": 0.2, "height": 0.2}
        ]
        updated = request_json(
            f"{base_url}/api/instances/{first_id}",
            method="PUT",
            payload={"annotation": annotation, "annotator": args.annotator},
        )
        if updated["annotation"]["review_status"] != "in_progress":
            raise RuntimeError("PUT did not persist review_status")

        export_result = request_json(
            f"{base_url}/api/export",
            method="POST",
            payload={"output_path": str(export_path)},
        )
        if export_result.get("rows_exported") != 5 or not export_path.exists():
            raise RuntimeError(f"export failed: {export_result}")

        subprocess.run(
            [sys.executable, str(validator), "--kind", "annotations", str(export_path)],
            check=True,
            cwd=repository,
        )

        summary = {
            "base_url": base_url,
            "db_path": str(db_path),
            "export_path": str(export_path),
            "instances": len(instances),
            "frontend_assets": len(assets),
            "media_items_first_instance": len(media_items),
            "validator": "ok",
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        if args.keep_db:
            print(f"kept smoke artifacts in {temp_dir}", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
