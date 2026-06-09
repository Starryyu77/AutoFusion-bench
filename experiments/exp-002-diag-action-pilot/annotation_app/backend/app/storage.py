"""SQLite persistence for local exp-002 annotation review sessions."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .jsonl_io import read_jsonl, write_jsonl


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    ensure_schema(connection)
    return connection


def ensure_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            annotator TEXT NOT NULL,
            source_path TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS annotations (
            instance_id TEXT PRIMARY KEY,
            session_id INTEGER NOT NULL,
            annotator TEXT NOT NULL,
            row_json TEXT NOT NULL,
            review_status TEXT NOT NULL,
            imported_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(session_id) REFERENCES sessions(id)
        );

        CREATE INDEX IF NOT EXISTS idx_annotations_review_status
            ON annotations(review_status);
        """
    )
    connection.commit()


def normalize_annotation(row: dict[str, Any], annotator: str | None = None) -> dict[str, Any]:
    if "instance_id" not in row or not row["instance_id"]:
        raise ValueError("annotation row missing instance_id")

    normalized = json.loads(json.dumps(row, ensure_ascii=False))
    normalized.setdefault("review_status", "needs_human_review")
    normalized.setdefault("modalities_presented", ["audio", "video"])
    normalized.setdefault("annotation_confidence", "low")
    normalized.setdefault("annotator_notes", "")
    normalized.setdefault("risk_sensitive", True)

    metadata = normalized.setdefault("annotation_app_metadata", {})
    metadata["schema"] = "exp-002-v1"
    metadata["updated_at"] = utc_now()
    if annotator:
        metadata["annotator"] = annotator

    return normalized


def import_sheet(
    db_path: Path,
    sheet_path: Path,
    annotator: str,
    session_name: str | None = None,
    replace: bool = True,
) -> dict[str, Any]:
    rows = read_jsonl(sheet_path)
    imported_at = utc_now()
    name = session_name or sheet_path.stem
    with connect(db_path) as connection:
        cursor = connection.execute(
            "INSERT INTO sessions(name, annotator, source_path, created_at) VALUES (?, ?, ?, ?)",
            (name, annotator, str(sheet_path), imported_at),
        )
        session_id = int(cursor.lastrowid)
        inserted = 0
        skipped = 0
        for raw_row in rows:
            row = normalize_annotation(raw_row, annotator=annotator)
            payload = json.dumps(row, ensure_ascii=False, sort_keys=True)
            values = (
                row["instance_id"],
                session_id,
                annotator,
                payload,
                row.get("review_status", "needs_human_review"),
                imported_at,
                imported_at,
            )
            if replace:
                connection.execute(
                    """
                    INSERT INTO annotations(
                        instance_id, session_id, annotator, row_json,
                        review_status, imported_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(instance_id) DO UPDATE SET
                        session_id=excluded.session_id,
                        annotator=excluded.annotator,
                        row_json=excluded.row_json,
                        review_status=excluded.review_status,
                        updated_at=excluded.updated_at
                    """,
                    values,
                )
                inserted += 1
            else:
                cursor = connection.execute(
                    """
                    INSERT OR IGNORE INTO annotations(
                        instance_id, session_id, annotator, row_json,
                        review_status, imported_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    values,
                )
                if cursor.rowcount:
                    inserted += 1
                else:
                    skipped += 1
        connection.commit()
    return {
        "db_path": str(db_path),
        "sheet_path": str(sheet_path),
        "session_id": session_id,
        "rows_seen": len(rows),
        "rows_imported": inserted,
        "rows_skipped": skipped,
    }


def list_instances(db_path: Path, status: str | None = None, query: str | None = None) -> list[dict[str, Any]]:
    sql = "SELECT instance_id, row_json, review_status, annotator, updated_at FROM annotations"
    clauses = []
    params: list[Any] = []
    if status and status != "all":
        clauses.append("review_status = ?")
        params.append(status)
    if query:
        clauses.append("(instance_id LIKE ? OR row_json LIKE ?)")
        like = f"%{query}%"
        params.extend([like, like])
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY instance_id"

    with connect(db_path) as connection:
        rows = connection.execute(sql, params).fetchall()

    summaries = []
    for db_row in rows:
        row = json.loads(db_row["row_json"])
        generator_hint = row.get("generator_hint", {})
        summaries.append(
            {
                "instance_id": db_row["instance_id"],
                "source_id": row.get("source_id", ""),
                "question": row.get("question", ""),
                "review_status": db_row["review_status"],
                "main_answerability": row.get("main_answerability", ""),
                "corruption_type": generator_hint.get("corruption_type", ""),
                "affected_modality": generator_hint.get("affected_modality", ""),
                "annotator": db_row["annotator"],
                "updated_at": db_row["updated_at"],
            }
        )
    return summaries


def get_annotation(db_path: Path, instance_id: str) -> dict[str, Any] | None:
    with connect(db_path) as connection:
        row = connection.execute(
            "SELECT row_json FROM annotations WHERE instance_id = ?",
            (instance_id,),
        ).fetchone()
    if row is None:
        return None
    return json.loads(row["row_json"])


def save_annotation(db_path: Path, instance_id: str, annotation: dict[str, Any], annotator: str | None = None) -> dict[str, Any]:
    row = normalize_annotation(annotation, annotator=annotator)
    if row["instance_id"] != instance_id:
        raise ValueError(f"instance_id mismatch: path={instance_id} body={row['instance_id']}")

    updated_at = utc_now()
    payload = json.dumps(row, ensure_ascii=False, sort_keys=True)
    with connect(db_path) as connection:
        existing = connection.execute(
            "SELECT session_id, annotator, imported_at FROM annotations WHERE instance_id = ?",
            (instance_id,),
        ).fetchone()
        if existing is None:
            cursor = connection.execute(
                "INSERT INTO sessions(name, annotator, source_path, created_at) VALUES (?, ?, ?, ?)",
                ("manual", annotator or "local", "manual", updated_at),
            )
            session_id = int(cursor.lastrowid)
            imported_at = updated_at
            db_annotator = annotator or "local"
        else:
            session_id = int(existing["session_id"])
            imported_at = existing["imported_at"]
            db_annotator = annotator or existing["annotator"]

        connection.execute(
            """
            INSERT INTO annotations(
                instance_id, session_id, annotator, row_json,
                review_status, imported_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(instance_id) DO UPDATE SET
                row_json=excluded.row_json,
                review_status=excluded.review_status,
                annotator=excluded.annotator,
                updated_at=excluded.updated_at
            """,
            (
                instance_id,
                session_id,
                db_annotator,
                payload,
                row.get("review_status", "needs_human_review"),
                imported_at,
                updated_at,
            ),
        )
        connection.commit()
    return row


def export_annotations(db_path: Path, output_path: Path) -> dict[str, Any]:
    with connect(db_path) as connection:
        rows = connection.execute(
            "SELECT row_json FROM annotations ORDER BY instance_id"
        ).fetchall()
    annotations = [json.loads(row["row_json"]) for row in rows]
    count = write_jsonl(output_path, annotations)
    return {"output_path": str(output_path), "rows_exported": count}


def summary(db_path: Path) -> dict[str, Any]:
    with connect(db_path) as connection:
        status_rows = connection.execute(
            "SELECT review_status, COUNT(*) AS n FROM annotations GROUP BY review_status"
        ).fetchall()
        sessions = connection.execute(
            "SELECT id, name, annotator, source_path, created_at FROM sessions ORDER BY id"
        ).fetchall()
    return {
        "db_path": str(db_path),
        "status_counts": {row["review_status"]: row["n"] for row in status_rows},
        "sessions": [dict(row) for row in sessions],
    }

