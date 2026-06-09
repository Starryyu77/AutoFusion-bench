"""FastAPI backend for the local exp-002 annotation app."""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .constants import FIELD_OPTIONS
from .media import default_repo_root, resolve_media_path, row_media
from .merge import merge_exports
from .storage import (
    export_annotations,
    get_annotation,
    import_sheet,
    list_instances,
    save_annotation,
    summary,
)


def env_path(name: str, default: Path) -> Path:
    return Path(os.environ.get(name, str(default))).expanduser()


REPO_ROOT = env_path("AUTOFUSION_REPO_ROOT", default_repo_root())
APP_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = env_path("ANNOTATION_DB_PATH", Path("/state/annotations.sqlite"))
FRONTEND_DIST = APP_ROOT.parent / "frontend" / "dist"

app = FastAPI(title="exp-002 local annotation app", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ImportRequest(BaseModel):
    path: str
    annotator: str = Field(min_length=1)
    session_name: Optional[str] = None
    replace: bool = True


class ExportRequest(BaseModel):
    output_path: str


class SaveRequest(BaseModel):
    annotation: dict
    annotator: Optional[str] = None


class MergeRequest(BaseModel):
    annotation_paths: List[str]
    output_path: str
    report_path: Optional[str] = None


@app.get("/api/health")
def health() -> dict:
    return {
        "ok": True,
        "db_path": str(DB_PATH),
        "repo_root": str(REPO_ROOT),
        "frontend_dist": str(FRONTEND_DIST),
    }


@app.get("/api/options")
def options() -> dict:
    return FIELD_OPTIONS


@app.post("/api/import")
def import_annotations(request: ImportRequest) -> dict:
    path = Path(request.path)
    if not path.is_absolute():
        path = REPO_ROOT / path
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"sheet not found: {path}")
    return import_sheet(DB_PATH, path, request.annotator, request.session_name, request.replace)


@app.get("/api/summary")
def app_summary() -> dict:
    return summary(DB_PATH)


@app.get("/api/instances")
def instances(
    status: Optional[str] = Query(default=None),
    q: Optional[str] = Query(default=None),
) -> List[dict]:
    return list_instances(DB_PATH, status=status, query=q)


@app.get("/api/instances/{instance_id}")
def instance_detail(instance_id: str) -> dict:
    row = get_annotation(DB_PATH, instance_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"instance not found: {instance_id}")
    return {"annotation": row, "media": row_media(row, repo_root=REPO_ROOT)}


@app.put("/api/instances/{instance_id}")
def update_instance(instance_id: str, request: SaveRequest) -> dict:
    try:
        row = save_annotation(DB_PATH, instance_id, request.annotation, annotator=request.annotator)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"annotation": row, "media": row_media(row, repo_root=REPO_ROOT)}


@app.post("/api/export")
def export(request: ExportRequest) -> dict:
    output_path = Path(request.output_path)
    if not output_path.is_absolute():
        output_path = REPO_ROOT / output_path
    return export_annotations(DB_PATH, output_path)


@app.post("/api/merge")
def merge(request: MergeRequest) -> dict:
    annotation_paths = []
    for raw_path in request.annotation_paths:
        path = Path(raw_path)
        annotation_paths.append(path if path.is_absolute() else REPO_ROOT / path)
    output_path = Path(request.output_path)
    if not output_path.is_absolute():
        output_path = REPO_ROOT / output_path
    report_path = None
    if request.report_path:
        report_path = Path(request.report_path)
        if not report_path.is_absolute():
            report_path = REPO_ROOT / report_path
    return merge_exports(annotation_paths, output_path, report_path)


@app.get("/api/media/file")
def media_file(path: str) -> FileResponse:
    resolved = resolve_media_path(path, repo_root=REPO_ROOT)
    if resolved is None:
        raise HTTPException(status_code=404, detail=f"media not found or not allowed: {path}")
    return FileResponse(resolved)


if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
