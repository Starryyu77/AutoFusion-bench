"""Produce measured exp-001 tables from staged MELD assets."""

from __future__ import annotations

import csv
import hashlib
import math
import pickle
import random
import time
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from .constants import (
    BIMODAL_TEMPLATES,
    CLEAN_SLICE,
    DEGRADED_SLICES,
    MAIN_CELLS,
    TEMPLATE_MODALITIES,
    TEMPLATES,
)
from .errors import ProtocolError
from .io import write_csv_records, write_json
from .meld_schema import (
    ANNOTATION_FILES,
    EMOTION_LABELS,
    FEATURE_PICKLE_CANDIDATES,
    LABEL_TO_ID,
    RAW_SPLIT_DIRS,
    MeldRecord,
)


@dataclass(frozen=True)
class ProducerInputs:
    annotations_dir: Path
    features_dir: Path | None
    raw_root: Path | None
    output_dir: Path
    seeds: tuple[int, ...]
    video_source: str
    max_train_samples: int | None = None
    max_eval_samples: int | None = None


@dataclass(frozen=True)
class FeatureBundle:
    records: dict[str, list[MeldRecord]]
    features: dict[str, dict[str, np.ndarray]]
    sources: dict[str, str]


def produce_meld_tables(inputs: ProducerInputs) -> dict[str, Any]:
    records = load_annotations(inputs.annotations_dir)
    records = _limit_records(records, inputs.max_train_samples, inputs.max_eval_samples)
    bundle = build_feature_bundle(
        records,
        features_dir=inputs.features_dir,
        raw_root=inputs.raw_root,
        video_source=inputs.video_source,
    )

    train_rows = bundle.records["train"]
    eval_splits = ("validation", "test")
    models: dict[tuple[int, str], Any] = {}
    predictions: dict[tuple[int, str, str, str, str], np.ndarray] = {}
    outcome_rows: list[dict[str, Any]] = []
    profile_rows: list[dict[str, Any]] = []

    for seed in inputs.seeds:
        for template in TEMPLATES:
            model = train_template_model(bundle, template=template, seed=seed)
            models[(seed, template)] = model
            profile = profile_template(bundle, model, template=template)
            profile_rows.append({"template": template, **profile})

        for split in eval_splits:
            for condition in MAIN_CELLS:
                slices = (CLEAN_SLICE,) if condition.startswith("clean_") else DEGRADED_SLICES
                for slice_name in slices:
                    for template in TEMPLATES:
                        y_true, y_pred = predict_template(
                            bundle,
                            models[(seed, template)],
                            template=template,
                            split=split,
                            slice_name=slice_name,
                            seed=seed,
                        )
                        predictions[(seed, split, condition, slice_name, template)] = y_pred
                        outcome_rows.append(
                            {
                                "split": split,
                                "condition": condition,
                                "slice": slice_name,
                                "template": template,
                                "seed": seed,
                                "macro_f1": f1_score(y_true, y_pred, average="macro") * 100.0,
                            }
                        )

    cost_rows = aggregate_cost_rows(profile_rows)
    corruption_rows = build_corruption_manifest(bundle.records)
    q_proxy_rows = build_q_proxy_rows(bundle)
    q_policy_rows = build_q_policy_map()
    q_diag_rows = build_q_diagnostics(bundle, outcome_rows)

    inputs.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv_records(inputs.output_dir / "cost_table.csv", ("template", "p50_ms", "p95_ms", "peak_memory_mb"), cost_rows)
    write_csv_records(inputs.output_dir / "outcome_table.csv", ("split", "condition", "slice", "template", "seed", "macro_f1"), outcome_rows)
    write_csv_records(inputs.output_dir / "q_policy_map.csv", ("slice", "proposed_template", "proxy_rule"), q_policy_rows)
    write_csv_records(inputs.output_dir / "q_proxy_table.csv", q_proxy_fieldnames(), q_proxy_rows)
    write_csv_records(inputs.output_dir / "q_diagnostics.csv", ("check", "value", "threshold", "passed", "notes"), q_diag_rows)
    write_csv_records(inputs.output_dir / "corruption_manifest.csv", ("sample_id", "split", "label", "degraded_slice"), corruption_rows)

    summary = {
        "records": {split: len(rows) for split, rows in bundle.records.items()},
        "feature_sources": bundle.sources,
        "seeds": list(inputs.seeds),
        "video_source": inputs.video_source,
        "outputs": {
            "cost_table": str(inputs.output_dir / "cost_table.csv"),
            "outcome_table": str(inputs.output_dir / "outcome_table.csv"),
            "q_policy_map": str(inputs.output_dir / "q_policy_map.csv"),
            "q_proxy_table": str(inputs.output_dir / "q_proxy_table.csv"),
            "q_diagnostics": str(inputs.output_dir / "q_diagnostics.csv"),
            "corruption_manifest": str(inputs.output_dir / "corruption_manifest.csv"),
        },
    }
    write_json(inputs.output_dir / "producer_summary.json", summary)
    return summary


def load_annotations(annotations_dir: Path) -> dict[str, list[MeldRecord]]:
    records: dict[str, list[MeldRecord]] = {}
    for split, filename in ANNOTATION_FILES.items():
        path = annotations_dir / filename
        if not path.exists():
            raise ProtocolError(f"MELD annotation file not found: {path}")
        split_rows: list[MeldRecord] = []
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                emotion = row["Emotion"].strip().lower()
                if emotion not in LABEL_TO_ID:
                    raise ProtocolError(f"unknown MELD emotion label {emotion!r} in {path}")
                dialogue_id = int(row["Dialogue_ID"])
                utterance_id = int(row["Utterance_ID"])
                key = f"{dialogue_id}_{utterance_id}"
                split_rows.append(
                    MeldRecord(
                        split=split,
                        sample_id=f"{split}:{key}",
                        key=key,
                        utterance=row["Utterance"],
                        speaker=row["Speaker"],
                        emotion=emotion,
                        label=LABEL_TO_ID[emotion],
                        sentiment=row["Sentiment"].strip().lower(),
                        dialogue_id=dialogue_id,
                        utterance_id=utterance_id,
                        season=int(row["Season"]),
                        episode=int(row["Episode"]),
                        start_time=row["StartTime"],
                        end_time=row["EndTime"],
                    )
                )
        records[split] = split_rows
    return records


def build_feature_bundle(
    records: dict[str, list[MeldRecord]],
    *,
    features_dir: Path | None,
    raw_root: Path | None,
    video_source: str,
) -> FeatureBundle:
    features: dict[str, dict[str, np.ndarray]] = {}
    sources: dict[str, str] = {}

    for modality in ("text", "audio", "video"):
        if modality == "video" and video_source == "raw_stats":
            if raw_root is None:
                raise ProtocolError("--video-source raw_stats requires --raw-root")
            features[modality] = build_raw_video_stats(records, raw_root)
            sources[modality] = f"raw_stats:{raw_root}"
            continue

        loaded = load_modality_pickle(features_dir, modality) if features_dir else None
        if loaded is not None:
            features[modality], sources[modality] = loaded
            continue

        if modality == "text":
            features[modality] = build_text_hash_features(records)
            sources[modality] = "hashing_vectorizer_from_annotations"
        elif modality == "video" and video_source == "annotation_proxy":
            features[modality] = build_annotation_video_proxy(records)
            sources[modality] = "annotation_proxy_not_empirical_visual"
        else:
            raise ProtocolError(
                f"missing {modality} features. Provide official pickles or an approved fallback; "
                f"video_source={video_source!r}"
            )

    assert_feature_alignment(records, features)
    return FeatureBundle(records=records, features=features, sources=sources)


def load_modality_pickle(features_dir: Path | None, modality: str) -> tuple[dict[str, np.ndarray], str] | None:
    if features_dir is None or not features_dir.exists():
        return None
    candidates = FEATURE_PICKLE_CANDIDATES[modality]
    for name in candidates:
        matches = sorted(features_dir.rglob(name))
        if not matches:
            continue
        path = matches[0]
        with path.open("rb") as handle:
            payload = pickle.load(handle, encoding="latin1")
        return normalize_feature_payload(payload), str(path)
    return None


def normalize_feature_payload(payload: Any) -> dict[str, np.ndarray]:
    if isinstance(payload, (list, tuple)) and len(payload) >= 3:
        split_payloads = {
            "train": payload[0],
            "validation": payload[1],
            "test": payload[2],
        }
        output: dict[str, np.ndarray] = {}
        for split, split_values in split_payloads.items():
            if not isinstance(split_values, dict):
                continue
            for key, value in split_values.items():
                normalized = _flatten_feature(value)
                output[f"{split}:{key}"] = normalized
        return output
    if isinstance(payload, dict):
        output = {}
        for key, value in payload.items():
            if isinstance(value, dict):
                for nested_key, nested_value in value.items():
                    output[f"{key}:{nested_key}"] = _flatten_feature(nested_value)
            else:
                output[str(key)] = _flatten_feature(value)
        return output
    raise ProtocolError(f"unsupported feature pickle payload type: {type(payload)!r}")


def build_text_hash_features(records: dict[str, list[MeldRecord]], *, n_features: int = 512) -> dict[str, np.ndarray]:
    vectorizer = HashingVectorizer(n_features=n_features, alternate_sign=False, norm="l2")
    all_records = [record for split_records in records.values() for record in split_records]
    matrix = vectorizer.transform([record.utterance for record in all_records])
    return {
        record.sample_id: np.asarray(matrix[index].todense()).ravel().astype(np.float32)
        for index, record in enumerate(all_records)
    }


def build_raw_video_stats(records: dict[str, list[MeldRecord]], raw_root: Path) -> dict[str, np.ndarray]:
    output: dict[str, np.ndarray] = {}
    missing: list[str] = []
    for split, split_records in records.items():
        for record in split_records:
            video_path = find_raw_video(raw_root, split, record.raw_filename)
            if video_path is None:
                missing.append(f"{split}:{record.raw_filename}")
                continue
            size = video_path.stat().st_size
            duration = max(parse_timestamp_seconds(record.end_time) - parse_timestamp_seconds(record.start_time), 0.0)
            output[record.sample_id] = np.array(
                [
                    math.log1p(size),
                    duration,
                    record.season,
                    record.episode,
                    record.dialogue_id / 1000.0,
                    record.utterance_id / 50.0,
                    size / max(duration, 0.1),
                    len(record.utterance),
                ],
                dtype=np.float32,
            )
    if missing:
        preview = ", ".join(missing[:5])
        raise ProtocolError(f"missing raw video files for {len(missing)} MELD rows; examples: {preview}")
    return output


def build_annotation_video_proxy(records: dict[str, list[MeldRecord]]) -> dict[str, np.ndarray]:
    output: dict[str, np.ndarray] = {}
    for split_records in records.values():
        for record in split_records:
            duration = max(parse_timestamp_seconds(record.end_time) - parse_timestamp_seconds(record.start_time), 0.0)
            digest = hashlib.sha256(f"{record.season}:{record.episode}:{record.dialogue_id}".encode()).digest()
            hashed = np.frombuffer(digest[:16], dtype=np.uint8).astype(np.float32) / 255.0
            base = np.array(
                [
                    duration,
                    record.season / 10.0,
                    record.episode / 30.0,
                    record.dialogue_id / 1100.0,
                    record.utterance_id / 50.0,
                    len(record.utterance) / 250.0,
                ],
                dtype=np.float32,
            )
            output[record.sample_id] = np.concatenate([base, hashed])
    return output


def find_raw_video(raw_root: Path, split: str, filename: str) -> Path | None:
    for dirname in RAW_SPLIT_DIRS[split]:
        candidate = raw_root / dirname / filename
        if candidate.exists():
            return candidate
    matches = list(raw_root.rglob(filename))
    return matches[0] if matches else None


def assert_feature_alignment(records: dict[str, list[MeldRecord]], features: dict[str, dict[str, np.ndarray]]) -> None:
    for modality, modality_features in features.items():
        missing = [
            record.sample_id
            for split_records in records.values()
            for record in split_records
            if record.sample_id not in modality_features
        ]
        if missing:
            raise ProtocolError(
                f"{modality} feature table missing {len(missing)} records; examples: {missing[:5]}"
            )


def train_template_model(bundle: FeatureBundle, *, template: str, seed: int) -> Any:
    x_train, y_train = build_matrix(bundle, "train", template, slice_name=CLEAN_SLICE, seed=seed)
    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(
            max_iter=300,
            class_weight="balanced",
            random_state=seed,
            solver="lbfgs",
            multi_class="auto",
        ),
    )
    model.fit(x_train, y_train)
    return model


def predict_template(
    bundle: FeatureBundle,
    model: Any,
    *,
    template: str,
    split: str,
    slice_name: str,
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    x_eval, y_eval = build_matrix(bundle, split, template, slice_name=slice_name, seed=seed)
    return y_eval, model.predict(x_eval)


def build_matrix(
    bundle: FeatureBundle,
    split: str,
    template: str,
    *,
    slice_name: str,
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    rows = bundle.records[split]
    parts: list[np.ndarray] = []
    for modality in TEMPLATE_MODALITIES[template]:
        modality_features = []
        for record in rows:
            vector = bundle.features[modality][record.sample_id]
            vector = apply_degradation(vector, modality=modality, slice_name=slice_name, record=record, seed=seed)
            modality_features.append(vector)
        parts.append(np.vstack(modality_features))
    x = np.hstack(parts).astype(np.float32)
    y = np.array([record.label for record in rows], dtype=np.int64)
    return x, y


def apply_degradation(
    vector: np.ndarray,
    *,
    modality: str,
    slice_name: str,
    record: MeldRecord,
    seed: int,
) -> np.ndarray:
    if slice_name == CLEAN_SLICE:
        return vector
    degraded_modalities = {
        "degraded_text": {"T"},
        "degraded_audio": {"A"},
        "degraded_video": {"V"},
        "mixed_degraded": {"T", "A", "V"},
    }[slice_name]
    if modality not in degraded_modalities:
        return vector
    if slice_name == "mixed_degraded":
        scale = 0.35
    else:
        scale = 0.0
    if scale == 0.0:
        return np.zeros_like(vector)
    rng = np.random.default_rng(_stable_seed(record.sample_id, modality, seed))
    noise = rng.normal(0.0, 0.01, size=vector.shape).astype(np.float32)
    return (vector * scale + noise).astype(np.float32)


def profile_template(bundle: FeatureBundle, model: Any, *, template: str, repeats: int = 200) -> dict[str, float]:
    x_eval, _ = build_matrix(bundle, "validation", template, slice_name=CLEAN_SLICE, seed=0)
    sample = x_eval[:1]
    timings: list[float] = []
    for _ in range(10):
        model.predict_proba(sample)
    for _ in range(repeats):
        start = time.perf_counter()
        model.predict_proba(sample)
        timings.append((time.perf_counter() - start) * 1000.0)
    timings_sorted = sorted(timings)
    p95 = timings_sorted[min(int(0.95 * len(timings_sorted)), len(timings_sorted) - 1)]
    memory = sample.nbytes
    classifier = model.named_steps.get("logisticregression")
    scaler = model.named_steps.get("standardscaler")
    if classifier is not None:
        memory += getattr(classifier, "coef_", np.array([], dtype=np.float32)).nbytes
        memory += getattr(classifier, "intercept_", np.array([], dtype=np.float32)).nbytes
    if scaler is not None:
        memory += getattr(scaler, "mean_", np.array([], dtype=np.float32)).nbytes
        memory += getattr(scaler, "scale_", np.array([], dtype=np.float32)).nbytes
    return {
        "p50_ms": median(timings),
        "p95_ms": p95,
        "peak_memory_mb": memory / (1024.0 * 1024.0),
    }


def aggregate_cost_rows(profile_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for template in TEMPLATES:
        values = [row for row in profile_rows if row["template"] == template]
        rows.append(
            {
                "template": template,
                "p50_ms": median(row["p50_ms"] for row in values),
                "p95_ms": median(row["p95_ms"] for row in values),
                "peak_memory_mb": max(row["peak_memory_mb"] for row in values),
            }
        )
    return rows


def build_corruption_manifest(records: dict[str, list[MeldRecord]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for split in ("validation", "test"):
        by_label: dict[int, list[MeldRecord]] = {}
        for record in records[split]:
            by_label.setdefault(record.label, []).append(record)
        for label, label_records in by_label.items():
            for index, record in enumerate(sorted(label_records, key=lambda item: item.sample_id)):
                rows.append(
                    {
                        "sample_id": record.sample_id,
                        "split": split,
                        "label": EMOTION_LABELS[label],
                        "degraded_slice": DEGRADED_SLICES[index % len(DEGRADED_SLICES)],
                    }
                )
    return rows


def build_q_proxy_rows(bundle: FeatureBundle) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for split in ("validation", "test"):
        for record in bundle.records[split]:
            text_norm = float(np.linalg.norm(bundle.features["text"][record.sample_id]))
            audio_norm = float(np.linalg.norm(bundle.features["audio"][record.sample_id]))
            video_norm = float(np.linalg.norm(bundle.features["video"][record.sample_id]))
            rows.append(
                {
                    "sample_id": record.sample_id,
                    "split": split,
                    "missing_text": 0,
                    "missing_audio": 0,
                    "missing_video": 0,
                    "text_feature_norm": text_norm,
                    "audio_feature_norm": audio_norm,
                    "video_feature_norm": video_norm,
                    "utterance_length": len(record.utterance.split()),
                    "speaker_hash": _stable_hash_float(record.speaker),
                }
            )
    return rows


def q_proxy_fieldnames() -> tuple[str, ...]:
    return (
        "sample_id",
        "split",
        "missing_text",
        "missing_audio",
        "missing_video",
        "text_feature_norm",
        "audio_feature_norm",
        "video_feature_norm",
        "utterance_length",
        "speaker_hash",
    )


def build_q_policy_map() -> list[dict[str, str]]:
    return [
        {"slice": "clean", "proposed_template": "TAV", "proxy_rule": "all modalities reliable"},
        {"slice": "degraded_text", "proposed_template": "AV", "proxy_rule": "avoid low-reliability text"},
        {"slice": "degraded_audio", "proposed_template": "TV", "proxy_rule": "avoid low-reliability audio"},
        {"slice": "degraded_video", "proposed_template": "TA", "proxy_rule": "avoid low-reliability video"},
        {"slice": "mixed_degraded", "proposed_template": "T", "proxy_rule": "fallback to text anchor under mixed uncertainty"},
    ]


def build_q_diagnostics(bundle: FeatureBundle, outcome_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    q_f1 = q_only_task_classifier_score(bundle)
    shuffle_drop = q_shuffle_drop_proxy(outcome_rows)
    return [
        {
            "check": "q_only_task_classifier",
            "value": q_f1,
            "threshold": 40.0,
            "passed": q_f1 <= 40.0,
            "notes": "macro-F1 from q proxy features to task labels; high values indicate leakage risk",
        },
        {
            "check": "q_shuffle_control",
            "value": shuffle_drop,
            "threshold": 0.5,
            "passed": shuffle_drop >= 0.5,
            "notes": "macro-F1 drop from cyclic degraded-slice q shuffle proxy",
        },
    ]


def q_only_task_classifier_score(bundle: FeatureBundle) -> float:
    def q_matrix(split: str) -> tuple[np.ndarray, np.ndarray]:
        rows = []
        labels = []
        for record in bundle.records[split]:
            rows.append(
                [
                    0.0,
                    0.0,
                    0.0,
                    float(np.linalg.norm(bundle.features["text"][record.sample_id])),
                    float(np.linalg.norm(bundle.features["audio"][record.sample_id])),
                    float(np.linalg.norm(bundle.features["video"][record.sample_id])),
                    len(record.utterance.split()),
                    _stable_hash_float(record.speaker),
                ]
            )
            labels.append(record.label)
        return np.asarray(rows, dtype=np.float32), np.asarray(labels, dtype=np.int64)

    x_train, y_train = q_matrix("train")
    x_test, y_test = q_matrix("test")
    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=200, class_weight="balanced", random_state=0),
    )
    model.fit(x_train, y_train)
    pred = model.predict(x_test)
    return f1_score(y_test, pred, average="macro") * 100.0


def q_shuffle_drop_proxy(outcome_rows: list[dict[str, Any]]) -> float:
    by_slice_template: dict[tuple[str, str], list[float]] = {}
    for row in outcome_rows:
        if row["split"] != "validation" or row["condition"] != "degraded_tight":
            continue
        by_slice_template.setdefault((row["slice"], row["template"]), []).append(float(row["macro_f1"]))

    legal_tight = set(("T", "A", "V") + BIMODAL_TEMPLATES)
    best_by_slice: dict[str, str] = {}
    for slice_name in DEGRADED_SLICES:
        best_by_slice[slice_name] = max(
            legal_tight,
            key=lambda template: median(by_slice_template.get((slice_name, template), [0.0])),
        )

    slices = list(DEGRADED_SLICES)
    correct = []
    shuffled = []
    for index, slice_name in enumerate(slices):
        correct_template = best_by_slice[slice_name]
        shuffled_template = best_by_slice[slices[(index + 1) % len(slices)]]
        correct.append(median(by_slice_template[(slice_name, correct_template)]))
        shuffled.append(median(by_slice_template[(slice_name, shuffled_template)]))
    return float(median(correct) - median(shuffled))


def parse_timestamp_seconds(value: str) -> float:
    value = value.strip().replace(",", ".")
    parts = value.split(":")
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    if len(parts) == 2:
        minutes, seconds = parts
        return int(minutes) * 60 + float(seconds)
    return float(value)


def _limit_records(
    records: dict[str, list[MeldRecord]],
    max_train_samples: int | None,
    max_eval_samples: int | None,
) -> dict[str, list[MeldRecord]]:
    output = dict(records)
    if max_train_samples:
        output["train"] = _class_balanced_prefix(output["train"], max_train_samples)
    if max_eval_samples:
        output["validation"] = _class_balanced_prefix(output["validation"], max_eval_samples)
        output["test"] = _class_balanced_prefix(output["test"], max_eval_samples)
    return output


def _class_balanced_prefix(records: list[MeldRecord], limit: int) -> list[MeldRecord]:
    by_label: dict[int, list[MeldRecord]] = {}
    for record in records:
        by_label.setdefault(record.label, []).append(record)
    selected: list[MeldRecord] = []
    while len(selected) < limit:
        made_progress = False
        for label in sorted(by_label):
            if by_label[label]:
                selected.append(by_label[label].pop(0))
                made_progress = True
                if len(selected) >= limit:
                    break
        if not made_progress:
            break
    return sorted(selected, key=lambda item: item.sample_id)


def _flatten_feature(value: Any) -> np.ndarray:
    array = np.asarray(value, dtype=np.float32)
    if array.ndim == 0:
        array = array.reshape(1)
    return array.reshape(-1)


def _stable_seed(sample_id: str, modality: str, seed: int) -> int:
    digest = hashlib.sha256(f"{sample_id}:{modality}:{seed}".encode()).digest()
    return int.from_bytes(digest[:8], "little", signed=False)


def _stable_hash_float(value: str) -> float:
    digest = hashlib.sha256(value.encode()).digest()
    return int.from_bytes(digest[:4], "little") / float(2**32)

