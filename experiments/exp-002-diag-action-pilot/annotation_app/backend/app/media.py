"""Media path mapping and serving helpers."""

from __future__ import annotations

import mimetypes
import os
from pathlib import Path
from urllib.parse import quote


def default_repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / ".git").exists() and (parent / "experiments").exists():
            return parent
    return Path(__file__).resolve().parents[5]


def parse_media_map(value: str | None) -> list[tuple[str, Path]]:
    if not value:
        return []
    mappings: list[tuple[str, Path]] = []
    for chunk in value.split(";"):
        stripped = chunk.strip()
        if not stripped:
            continue
        if "=" not in stripped:
            raise ValueError(f"invalid media map entry {stripped!r}; expected remote=local")
        remote, local = stripped.split("=", 1)
        mappings.append((remote.rstrip("/"), Path(local).expanduser()))
    return mappings


def configured_media_map() -> list[tuple[str, Path]]:
    return parse_media_map(os.environ.get("ANNOTATION_MEDIA_MAP"))


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def resolve_media_path(
    original_path: str | None,
    repo_root: Path | None = None,
    mappings: list[tuple[str, Path]] | None = None,
) -> Path | None:
    if not original_path:
        return None
    repo_root = repo_root or default_repo_root()
    mappings = mappings if mappings is not None else configured_media_map()
    raw = str(original_path)
    candidates: list[Path] = []

    for remote_prefix, local_prefix in mappings:
        if raw == remote_prefix or raw.startswith(remote_prefix + "/"):
            suffix = raw[len(remote_prefix) :].lstrip("/")
            candidates.append(local_prefix / suffix)

    path = Path(raw)
    if path.is_absolute():
        candidates.append(path)
    else:
        candidates.append(repo_root / path)

    allowed_roots = [repo_root, *[local for _, local in mappings]]
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            if any(_is_relative_to(candidate, root) for root in allowed_roots):
                return candidate.resolve()
    return None


def media_kind(path: str | None) -> str:
    if not path:
        return "missing"
    suffix = Path(path).suffix.lower()
    if suffix in {".mp4", ".mov", ".m4v", ".webm", ".avi", ".mkv"}:
        return "video"
    if suffix in {".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg"}:
        return "audio"
    if suffix in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}:
        return "image"
    return "file"


def media_info(original_path: str | None, label: str, repo_root: Path | None = None) -> dict:
    resolved = resolve_media_path(original_path, repo_root=repo_root)
    kind = media_kind(original_path)
    info = {
        "label": label,
        "path": original_path,
        "kind": kind,
        "exists": resolved is not None,
        "url": None,
        "mime_type": mimetypes.guess_type(original_path or "")[0],
    }
    if resolved is not None:
        info["resolved_path"] = str(resolved)
        info["url"] = f"/api/media/file?path={quote(str(original_path), safe='')}"
    return info


def row_media(row: dict, repo_root: Path | None = None) -> dict:
    media = row.get("media", {})
    items = [
        media_info(media.get("source_video_path"), "source", repo_root=repo_root),
        media_info(media.get("corrupted_video_path"), "corrupted", repo_root=repo_root),
    ]
    seen = {(item.get("label"), item.get("path")) for item in items}
    extra_items = media.get("items", [])
    if not isinstance(extra_items, list):
        extra_items = []
    for index, item in enumerate(extra_items):
        if not isinstance(item, dict):
            continue
        label = str(item.get("label") or item.get("role") or f"media_{index + 1}")
        path = item.get("path") or item.get("media_path") or item.get("file")
        key = (label, path)
        if key in seen:
            continue
        info = media_info(path, label, repo_root=repo_root)
        info["role"] = item.get("role")
        info["modality"] = item.get("modality")
        items.append(info)
        seen.add(key)
    return {
        "source": items[0],
        "corrupted": items[1],
        "items": items,
    }
