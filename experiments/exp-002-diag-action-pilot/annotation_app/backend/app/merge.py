"""Merge annotator exports and produce an adjudication report."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from .constants import DISAGREEMENT_FIELDS
from .jsonl_io import read_jsonl, write_jsonl
from .storage import utc_now


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def merge_exports(annotation_paths: list[Path], output_path: Path, report_path: Path | None = None) -> dict[str, Any]:
    grouped: dict[str, list[tuple[str, dict]]] = defaultdict(list)
    for path in annotation_paths:
        for row in read_jsonl(path):
            instance_id = str(row.get("instance_id", ""))
            if not instance_id:
                raise ValueError(f"{path}: row missing instance_id")
            grouped[instance_id].append((str(path), row))

    merged_rows: list[dict] = []
    report_rows: list[dict[str, Any]] = []
    for instance_id in sorted(grouped):
        candidates = grouped[instance_id]
        base = json.loads(json.dumps(candidates[0][1], ensure_ascii=False))
        disagreements = []
        for field in DISAGREEMENT_FIELDS:
            values = {}
            for source_path, row in candidates:
                values.setdefault(canonical(row.get(field)), []).append(source_path)
            if len(values) > 1:
                disagreements.append(
                    {
                        "field": field,
                        "values": [
                            {
                                "value": json.loads(serialized),
                                "sources": sources,
                            }
                            for serialized, sources in values.items()
                        ],
                    }
                )

        metadata = base.setdefault("annotation_app_metadata", {})
        metadata["merged_at"] = utc_now()
        metadata["merge_sources"] = [source_path for source_path, _ in candidates]
        if disagreements:
            base["review_status"] = "needs_adjudication"
            base["annotation_app_disagreements"] = disagreements
            report_rows.append({"instance_id": instance_id, "disagreements": disagreements})
        merged_rows.append(base)

    count = write_jsonl(output_path, merged_rows)
    if report_path is not None:
        write_report(report_path, report_rows, annotation_paths, output_path)
    return {
        "output_path": str(output_path),
        "report_path": str(report_path) if report_path else None,
        "rows_merged": count,
        "instances_with_disagreement": len(report_rows),
    }


def write_report(
    report_path: Path,
    report_rows: list[dict[str, Any]],
    annotation_paths: list[Path],
    output_path: Path,
) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# exp-002 annotation merge report",
        "",
        f"- merged_at: {utc_now()}",
        f"- output_jsonl: {output_path}",
        "- sources:",
    ]
    lines.extend(f"  - {path}" for path in annotation_paths)
    lines.extend(["", f"Instances with disagreements: {len(report_rows)}", ""])
    for row in report_rows:
        lines.append(f"## {row['instance_id']}")
        for disagreement in row["disagreements"]:
            lines.append(f"- field: `{disagreement['field']}`")
            for item in disagreement["values"]:
                value = json.dumps(item["value"], ensure_ascii=False, sort_keys=True)
                sources = ", ".join(item["sources"])
                lines.append(f"  - value: `{value}`")
                lines.append(f"    sources: {sources}")
        lines.append("")
    report_path.write_text("\n".join(lines), encoding="utf-8")

