#!/usr/bin/env python3
"""Check local configuration for the exp-002 annotation app."""

from __future__ import annotations

import argparse
import importlib.util
import os
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path


def app_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_repo_root(root: Path) -> Path:
    return root.parents[2]


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def command_version(command: str) -> str | None:
    path = shutil.which(command)
    if path is None:
        return None
    try:
        result = subprocess.run(
            [command, "--version"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return path
    return result.stdout.strip() or result.stderr.strip() or path


def add_result(results: list[tuple[str, str, str]], status: str, label: str, detail: str) -> None:
    results.append((status, label, detail))


def check_runtime_import(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-runtime-deps", action="store_true")
    parser.add_argument("--skip-runtime-deps", action="store_true")
    parser.add_argument(
        "--sheet",
        default="experiments/exp-002-diag-action-pilot/annotations/smoke_annotation_sheet_v1.draft.jsonl",
    )
    args = parser.parse_args()

    root = app_root()
    env_values = parse_env_file(root / ".env")
    repo_root = Path(
        os.environ.get("AUTOFUSION_REPO_ROOT")
        or env_values.get("AUTOFUSION_REPO_ROOT")
        or default_repo_root(root)
    ).expanduser()
    db_path = Path(
        os.environ.get("ANNOTATION_DB_PATH")
        or env_values.get("ANNOTATION_DB_PATH")
        or root / "state" / "annotations.sqlite"
    ).expanduser()
    media_map = os.environ.get("ANNOTATION_MEDIA_MAP") or env_values.get("ANNOTATION_MEDIA_MAP") or ""

    results: list[tuple[str, str, str]] = []

    if sys.version_info >= (3, 9):
        add_result(results, "ok", "python", sys.version.split()[0])
    else:
        add_result(results, "fail", "python", f"{sys.version.split()[0]} found; require >= 3.9")

    for command in ["node", "npm"]:
        version = command_version(command)
        if version is None:
            add_result(results, "fail", command, "not found on PATH")
        else:
            add_result(results, "ok", command, version.splitlines()[0])

    if repo_root.exists():
        add_result(results, "ok", "repo root", str(repo_root))
    else:
        add_result(results, "fail", "repo root", f"not found: {repo_root}")

    sheet_path = Path(args.sheet)
    if not sheet_path.is_absolute():
        sheet_path = repo_root / sheet_path
    if sheet_path.exists():
        add_result(results, "ok", "sample sheet", str(sheet_path))
    else:
        add_result(results, "fail", "sample sheet", f"not found: {sheet_path}")

    try:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        probe_path = db_path.parent / ".write_probe.sqlite"
        with sqlite3.connect(probe_path) as connection:
            connection.execute("CREATE TABLE IF NOT EXISTS probe(ok INTEGER)")
        probe_path.unlink(missing_ok=True)
        add_result(results, "ok", "state dir", str(db_path.parent))
    except OSError as exc:
        add_result(results, "fail", "state dir", f"not writable: {db_path.parent} ({exc})")

    if media_map:
        malformed = [chunk for chunk in media_map.split(";") if chunk.strip() and "=" not in chunk]
        if malformed:
            add_result(results, "fail", "media map", f"malformed entries: {malformed}")
        else:
            add_result(results, "ok", "media map", media_map)
    else:
        add_result(results, "warn", "media map", "not set; page will show media missing for remote paths")

    if args.require_runtime_deps and not args.skip_runtime_deps:
        for module in ["fastapi", "uvicorn", "pydantic"]:
            if check_runtime_import(module):
                add_result(results, "ok", f"python module {module}", "importable")
            else:
                add_result(results, "fail", f"python module {module}", "not importable; run scripts/bootstrap_local.sh")

    frontend_dist = root / "frontend" / "dist" / "index.html"
    if frontend_dist.exists():
        add_result(results, "ok", "frontend build", str(frontend_dist))
    else:
        add_result(results, "warn", "frontend build", "missing; run scripts/bootstrap_local.sh or npm run build")

    width = max(len(label) for _, label, _ in results)
    for status, label, detail in results:
        print(f"[{status.upper():4}] {label:<{width}}  {detail}")

    return 1 if any(status == "fail" for status, _, _ in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
