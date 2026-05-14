"""Cost table validation and budget-tier construction."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .constants import BIMODAL_TEMPLATES, TEMPLATES, UNIMODAL_TEMPLATES
from .errors import ProtocolError
from .io import read_csv_records


@dataclass(frozen=True)
class CostRow:
    template: str
    p50_ms: float
    p95_ms: float
    peak_memory_mb: float


@dataclass(frozen=True)
class BudgetProfile:
    loose_ms: float
    tight_ms: float
    legal_by_budget: dict[str, tuple[str, ...]]
    spread_ratio: float
    tav_vs_unimodal_ratio: float
    warnings: tuple[str, ...]


def load_cost_table(path: Path) -> dict[str, CostRow]:
    rows = read_csv_records(path)
    required = {"template", "p50_ms", "p95_ms", "peak_memory_mb"}
    if rows and not required.issubset(rows[0]):
        missing = sorted(required - set(rows[0]))
        raise ProtocolError(f"cost table missing columns: {missing}")

    costs: dict[str, CostRow] = {}
    for row in rows:
        template = row["template"].strip()
        if template not in TEMPLATES:
            raise ProtocolError(f"unknown template in cost table: {template}")
        costs[template] = CostRow(
            template=template,
            p50_ms=float(row["p50_ms"]),
            p95_ms=float(row["p95_ms"]),
            peak_memory_mb=float(row["peak_memory_mb"]),
        )

    expected = set(TEMPLATES)
    observed = set(costs)
    if observed != expected:
        raise ProtocolError(
            f"cost table templates mismatch; missing={sorted(expected - observed)} "
            f"extra={sorted(observed - expected)}"
        )
    if any(row.p95_ms <= 0 for row in costs.values()):
        raise ProtocolError("all p95_ms costs must be positive")
    return costs


def build_budget_profile(
    costs: dict[str, CostRow],
    *,
    min_spread_ratio: float = 1.5,
    preferred_tav_unimodal_ratio: float = 1.25,
) -> BudgetProfile:
    p95_values = [row.p95_ms for row in costs.values()]
    spread_ratio = max(p95_values) / min(p95_values)
    if spread_ratio < min_spread_ratio:
        raise ProtocolError(
            f"budget-validity gate failed: p95 spread {spread_ratio:.3f} "
            f"< {min_spread_ratio:.3f}"
        )

    max_unimodal = max(costs[t].p95_ms for t in UNIMODAL_TEMPLATES)
    tav_ratio = costs["TAV"].p95_ms / max_unimodal
    warnings: list[str] = []
    if tav_ratio < preferred_tav_unimodal_ratio:
        warnings.append(
            "preferred TAV-vs-unimodal cost separation not met: "
            f"{tav_ratio:.3f} < {preferred_tav_unimodal_ratio:.3f}"
        )

    loose = 1.05 * max(p95_values)
    tight = _choose_tight_budget(costs)
    legal_by_budget = {
        "loose": tuple(t for t in TEMPLATES if costs[t].p95_ms <= loose),
        "tight": tuple(t for t in TEMPLATES if costs[t].p95_ms <= tight),
    }

    if "TAV" in legal_by_budget["tight"]:
        raise ProtocolError("budget-validity gate failed: TAV is legal under tight")
    if not set(UNIMODAL_TEMPLATES).issubset(legal_by_budget["tight"]):
        raise ProtocolError("budget-validity gate failed: not all unimodal templates legal")
    if not set(BIMODAL_TEMPLATES).intersection(legal_by_budget["tight"]):
        raise ProtocolError("budget-validity gate failed: no bimodal template legal")

    return BudgetProfile(
        loose_ms=loose,
        tight_ms=tight,
        legal_by_budget=legal_by_budget,
        spread_ratio=spread_ratio,
        tav_vs_unimodal_ratio=tav_ratio,
        warnings=tuple(warnings),
    )


def _choose_tight_budget(costs: dict[str, CostRow]) -> float:
    lower_bound = max(costs[t].p95_ms for t in UNIMODAL_TEMPLATES)
    tav_cost = costs["TAV"].p95_ms
    candidates = sorted({row.p95_ms for row in costs.values() if lower_bound <= row.p95_ms < tav_cost})
    for candidate in candidates:
        legal = {template for template, row in costs.items() if row.p95_ms <= candidate}
        if (
            set(UNIMODAL_TEMPLATES).issubset(legal)
            and set(BIMODAL_TEMPLATES).intersection(legal)
            and "TAV" not in legal
        ):
            return candidate
    raise ProtocolError(
        "budget-validity gate failed: cannot define tight tier from cost table "
        "with all unimodal legal, at least one bimodal legal, and TAV illegal"
    )

