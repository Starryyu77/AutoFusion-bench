"""Outcome-table loading and utility lookup."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from statistics import mean

from .constants import CLEAN_SLICE, DEGRADED_SLICES, EXPECTED_SPLITS, MAIN_CELLS, TEMPLATES
from .errors import ProtocolError
from .io import read_csv_records


@dataclass(frozen=True)
class OutcomeRow:
    split: str
    condition: str
    slice: str
    template: str
    seed: int
    macro_f1: float


def allowed_slices(condition: str) -> tuple[str, ...]:
    if condition.startswith("clean_"):
        return (CLEAN_SLICE,)
    return DEGRADED_SLICES


def load_outcome_table(path: Path) -> list[OutcomeRow]:
    rows = read_csv_records(path)
    required = {"split", "condition", "slice", "template", "seed", "macro_f1"}
    if rows and not required.issubset(rows[0]):
        missing = sorted(required - set(rows[0]))
        raise ProtocolError(f"outcome table missing columns: {missing}")

    outcomes: list[OutcomeRow] = []
    for row in rows:
        split = row["split"].strip()
        condition = row["condition"].strip()
        slice_name = row["slice"].strip()
        template = row["template"].strip()
        if split not in EXPECTED_SPLITS:
            raise ProtocolError(f"unknown outcome split: {split}")
        if condition not in MAIN_CELLS:
            raise ProtocolError(f"unknown outcome condition: {condition}")
        if slice_name not in allowed_slices(condition):
            raise ProtocolError(f"slice {slice_name} is not valid for {condition}")
        if template not in TEMPLATES:
            raise ProtocolError(f"unknown template in outcome table: {template}")
        outcomes.append(
            OutcomeRow(
                split=split,
                condition=condition,
                slice=slice_name,
                template=template,
                seed=int(row["seed"]),
                macro_f1=float(row["macro_f1"]),
            )
        )
    return outcomes


def assert_outcome_completeness(outcomes: list[OutcomeRow]) -> None:
    observed = {(r.split, r.condition, r.slice, r.template, r.seed) for r in outcomes}
    seeds_by_split = {
        split: sorted({r.seed for r in outcomes if r.split == split}) for split in EXPECTED_SPLITS
    }
    for split in EXPECTED_SPLITS:
        if not seeds_by_split[split]:
            raise ProtocolError(f"no outcome rows for split={split}")
        for condition in MAIN_CELLS:
            for slice_name in allowed_slices(condition):
                for template in TEMPLATES:
                    for seed in seeds_by_split[split]:
                        key = (split, condition, slice_name, template, seed)
                        if key not in observed:
                            raise ProtocolError(f"outcome table missing row: {key}")


class OutcomeLookup:
    def __init__(self, outcomes: list[OutcomeRow]):
        self.outcomes = outcomes
        self._by_key: dict[tuple[str, str, str, str, int], float] = {}
        for row in outcomes:
            key = (row.split, row.condition, row.slice, row.template, row.seed)
            self._by_key[key] = row.macro_f1

    def utility(
        self, split: str, condition: str, slice_name: str, template: str, seed: int
    ) -> float:
        try:
            return self._by_key[(split, condition, slice_name, template, seed)]
        except KeyError as exc:
            raise ProtocolError(
                "missing outcome utility for "
                f"split={split} condition={condition} slice={slice_name} "
                f"template={template} seed={seed}"
            ) from exc

    def mean_utility(
        self,
        *,
        split: str,
        template: str,
        condition: str | None = None,
        slice_name: str | None = None,
        budget_conditions: tuple[str, ...] | None = None,
    ) -> float:
        values = [
            row.macro_f1
            for row in self.outcomes
            if row.split == split
            and row.template == template
            and (condition is None or row.condition == condition)
            and (slice_name is None or row.slice == slice_name)
            and (budget_conditions is None or row.condition in budget_conditions)
        ]
        if not values:
            raise ProtocolError(
                "no outcome rows for mean utility: "
                f"split={split} template={template} condition={condition} slice={slice_name}"
            )
        return mean(values)

    def test_keys(self) -> list[tuple[str, str, int]]:
        keys = {(row.condition, row.slice, row.seed) for row in self.outcomes if row.split == "test"}
        return sorted(keys)

