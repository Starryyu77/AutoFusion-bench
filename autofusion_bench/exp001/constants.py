"""Protocol constants for exp-001."""

from __future__ import annotations

TEMPLATES = ("T", "A", "V", "TA", "TV", "AV", "TAV")

TEMPLATE_MODALITIES = {
    "T": frozenset({"T"}),
    "A": frozenset({"A"}),
    "V": frozenset({"V"}),
    "TA": frozenset({"T", "A"}),
    "TV": frozenset({"T", "V"}),
    "AV": frozenset({"A", "V"}),
    "TAV": frozenset({"T", "A", "V"}),
}

UNIMODAL_TEMPLATES = ("T", "A", "V")
BIMODAL_TEMPLATES = ("TA", "TV", "AV")

POLICIES = (
    "random_legal",
    "clean_best",
    "static_full",
    "budget_only",
    "reliability_only",
    "joint",
    "feasible_oracle",
)

SINGLE_AXIS_POLICIES = (
    "clean_best",
    "static_full",
    "budget_only",
    "reliability_only",
)

MAIN_CELLS = ("clean_loose", "clean_tight", "degraded_loose", "degraded_tight")
DEGRADED_SLICES = (
    "degraded_text",
    "degraded_audio",
    "degraded_video",
    "mixed_degraded",
)
CLEAN_SLICE = "clean"

CONDITION_BUDGET = {
    "clean_loose": "loose",
    "degraded_loose": "loose",
    "clean_tight": "tight",
    "degraded_tight": "tight",
}

EXPECTED_SPLITS = ("validation", "test")

FORBIDDEN_PROXY_FIELDS = {
    "label",
    "class",
    "target",
    "y",
    "condition",
    "condition_label",
    "clean_degraded",
    "degraded",
    "affected_modality",
    "degraded_modality",
    "corrupted_modality",
    "severity",
    "corruption_severity",
    "random_seed",
    "seed",
    "oracle_template",
    "oracle_selected_template",
    "template_outcome",
    "test_outcome",
    "macro_f1",
}

