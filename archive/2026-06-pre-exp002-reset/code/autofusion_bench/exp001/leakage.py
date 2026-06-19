"""Leakage and corruption-manifest checks for exp-001."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .constants import DEGRADED_SLICES, FORBIDDEN_PROXY_FIELDS
from .errors import ProtocolError
from .io import read_csv_records


@dataclass(frozen=True)
class GateCheck:
    name: str
    passed: bool
    detail: str


def validate_q_proxy_table(path: Path) -> list[GateCheck]:
    rows = read_csv_records(path)
    if not rows:
        raise ProtocolError("q proxy table is empty")
    fields = {field.strip().lower() for field in rows[0]}
    forbidden = sorted(fields.intersection(FORBIDDEN_PROXY_FIELDS))
    if forbidden:
        raise ProtocolError(f"q proxy table includes forbidden fields: {forbidden}")
    return [
        GateCheck(
            name="reliability_proxy_boundary_check",
            passed=True,
            detail="q proxy table omits forbidden label/condition/severity/outcome fields",
        )
    ]


def validate_q_diagnostics(path: Path) -> list[GateCheck]:
    rows = read_csv_records(path)
    required_checks = {"q_only_task_classifier", "q_shuffle_control"}
    observed: dict[str, bool] = {}
    for row in rows:
        name = row.get("check", "").strip()
        passed = row.get("passed", "").strip().lower() in {"true", "1", "yes", "pass"}
        observed[name] = passed
    missing = sorted(required_checks - set(observed))
    if missing:
        raise ProtocolError(f"q diagnostics missing checks: {missing}")
    failed = sorted(name for name, passed in observed.items() if not passed)
    if failed:
        raise ProtocolError(f"q diagnostics failed checks: {failed}")
    return [
        GateCheck(name=name, passed=True, detail="provided diagnostic passed")
        for name in sorted(required_checks)
    ]


def validate_class_stratified_corruption(
    path: Path, *, max_imbalance_ratio: float = 1.5
) -> list[GateCheck]:
    rows = read_csv_records(path)
    required = {"split", "label", "degraded_slice"}
    if rows and not required.issubset(rows[0]):
        missing = sorted(required - set(rows[0]))
        raise ProtocolError(f"corruption manifest missing columns: {missing}")

    counts: dict[tuple[str, str], dict[str, int]] = {}
    for row in rows:
        slice_name = row["degraded_slice"].strip()
        if slice_name not in DEGRADED_SLICES:
            continue
        key = (row["split"].strip(), row["label"].strip())
        counts.setdefault(key, {slice_key: 0 for slice_key in DEGRADED_SLICES})
        counts[key][slice_name] += 1

    if not counts:
        raise ProtocolError("corruption manifest has no degraded-slice rows")

    for key, per_slice in counts.items():
        values = list(per_slice.values())
        if min(values) == 0:
            raise ProtocolError(f"corruption assignment is not class-stratified for {key}: {per_slice}")
        ratio = max(values) / min(values)
        if ratio > max_imbalance_ratio:
            raise ProtocolError(
                f"corruption slice imbalance {ratio:.3f} exceeds {max_imbalance_ratio:.3f} "
                f"for {key}: {per_slice}"
            )

    return [
        GateCheck(
            name="class_stratified_corruption_check",
            passed=True,
            detail=f"all split/label groups have degraded-slice ratio <= {max_imbalance_ratio}",
        )
    ]

