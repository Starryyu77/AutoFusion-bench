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

MODALITY_FEATURE_KEYS = {
    "T": "text",
    "A": "audio",
    "V": "video",
}

CV2_VIDEO_FEATURE_DIM = 97
DEFAULT_SEMVIS_MODEL = "openai/clip-vit-base-patch32"


@dataclass(frozen=True)
class ProducerInputs:
    annotations_dir: Path
    features_dir: Path | None
    raw_root: Path | None
    output_dir: Path
    seeds: tuple[int, ...]
    video_source: str
    audio_source: str = "official_concat"
    feature_cache_dir: Path | None = None
    max_train_samples: int | None = None
    max_eval_samples: int | None = None
    semvis_model: str = DEFAULT_SEMVIS_MODEL
    semvis_frame_count: int = 8
    semvis_batch_frames: int = 64
    semvis_device: str = "auto"
    degradation_profile: str = "default"


@dataclass(frozen=True)
class FeatureBundle:
    records: dict[str, list[MeldRecord]]
    features: dict[str, dict[str, np.ndarray]]
    sources: dict[str, str]
    degradation_profile: str = "default"


def produce_meld_tables(inputs: ProducerInputs) -> dict[str, Any]:
    records = load_annotations(inputs.annotations_dir)
    records = _limit_records(records, inputs.max_train_samples, inputs.max_eval_samples)
    bundle = build_feature_bundle(
        records,
        features_dir=inputs.features_dir,
        raw_root=inputs.raw_root,
        video_source=inputs.video_source,
        audio_source=inputs.audio_source,
        feature_cache_dir=inputs.feature_cache_dir,
        semvis_model=inputs.semvis_model,
        semvis_frame_count=inputs.semvis_frame_count,
        semvis_batch_frames=inputs.semvis_batch_frames,
        semvis_device=inputs.semvis_device,
        degradation_profile=inputs.degradation_profile,
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
    q_policy_rows = build_q_policy_map(inputs.degradation_profile)
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
        "audio_source": inputs.audio_source,
        "degradation_profile": inputs.degradation_profile,
        "semvis_model": inputs.semvis_model if inputs.video_source == "semvis_clip" else None,
        "semvis_frame_count": inputs.semvis_frame_count if inputs.video_source == "semvis_clip" else None,
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
    audio_source: str = "official_concat",
    feature_cache_dir: Path | None = None,
    semvis_model: str = DEFAULT_SEMVIS_MODEL,
    semvis_frame_count: int = 8,
    semvis_batch_frames: int = 64,
    semvis_device: str = "auto",
    degradation_profile: str = "default",
) -> FeatureBundle:
    if degradation_profile not in {"default", "text_stress"}:
        raise ProtocolError(f"unknown degradation_profile={degradation_profile!r}")

    features: dict[str, dict[str, np.ndarray]] = {}
    sources: dict[str, str] = {}

    for modality in ("text", "audio", "video"):
        if modality == "video" and video_source == "raw_stats":
            if raw_root is None:
                raise ProtocolError("--video-source raw_stats requires --raw-root")
            features[modality] = build_raw_video_stats(records, raw_root)
            sources[modality] = f"raw_stats:{raw_root}"
            continue
        if modality == "video" and video_source == "cv2_stats":
            if raw_root is None:
                raise ProtocolError("--video-source cv2_stats requires --raw-root")
            features[modality] = build_cv2_video_stats(records, raw_root, feature_cache_dir)
            sources[modality] = f"cv2_stats:{raw_root}"
            continue
        if modality == "video" and video_source == "semvis_clip":
            if raw_root is None:
                raise ProtocolError("--video-source semvis_clip requires --raw-root")
            features[modality] = build_semantic_clip_video_features(
                records,
                raw_root,
                feature_cache_dir,
                model_name=semvis_model,
                frame_count=semvis_frame_count,
                batch_frames=semvis_batch_frames,
                device=semvis_device,
            )
            sources[modality] = f"semvis_clip:{semvis_model}:f{semvis_frame_count}:{raw_root}"
            continue
        if modality == "audio":
            loaded_audio = load_audio_features(features_dir, records, source=audio_source)
            if loaded_audio is not None:
                features[modality], sources[modality] = loaded_audio
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
    return FeatureBundle(
        records=records,
        features=features,
        sources=sources,
        degradation_profile=degradation_profile,
    )


def load_audio_features(
    features_dir: Path | None, records: dict[str, list[MeldRecord]], *, source: str
) -> tuple[dict[str, np.ndarray], str] | None:
    if features_dir is None or not features_dir.exists():
        return None
    base = load_named_feature_pickle(features_dir, "audio_embeddings_feature_selection_emotion.pkl")
    if base is None:
        return None
    base_features, base_source = base
    if source == "official_full":
        return base_features, base_source
    if source != "official_concat":
        raise ProtocolError(f"unknown audio_source={source!r}")

    sequence = load_dialogue_sequence_feature(
        features_dir, "audio_emotion.pkl", records
    )
    if sequence is None:
        return base_features, base_source
    sequence_features, sequence_source = sequence

    sample_ids = [record.sample_id for split_records in records.values() for record in split_records]
    missing = [
        sample_id
        for sample_id in sample_ids
        if sample_id not in base_features or sample_id not in sequence_features
    ]
    if missing:
        return base_features, base_source

    combined = {
        sample_id: np.concatenate([base_features[sample_id], sequence_features[sample_id]]).astype(np.float32)
        for sample_id in sample_ids
    }
    return combined, f"{base_source}+{sequence_source}"


def load_modality_pickle(features_dir: Path | None, modality: str) -> tuple[dict[str, np.ndarray], str] | None:
    if features_dir is None or not features_dir.exists():
        return None
    candidates = FEATURE_PICKLE_CANDIDATES[modality]
    for name in candidates:
        loaded = load_named_feature_pickle(features_dir, name)
        if loaded is not None:
            return loaded
    return None


def load_named_feature_pickle(features_dir: Path, name: str) -> tuple[dict[str, np.ndarray], str] | None:
    matches = sorted(features_dir.rglob(name))
    if not matches:
        return None
    path = matches[0]
    with path.open("rb") as handle:
        payload = pickle.load(handle, encoding="latin1")
    return normalize_feature_payload(payload), str(path)


def load_dialogue_sequence_feature(
    features_dir: Path,
    name: str,
    records: dict[str, list[MeldRecord]],
) -> tuple[dict[str, np.ndarray], str] | None:
    matches = sorted(features_dir.rglob(name))
    if not matches:
        return None
    path = matches[0]
    with path.open("rb") as handle:
        payload = pickle.load(handle, encoding="latin1")
    if not isinstance(payload, (list, tuple)) or len(payload) < 3:
        return None
    split_payloads = {
        "train": payload[0],
        "validation": payload[1],
        "test": payload[2],
    }
    output: dict[str, np.ndarray] = {}
    for split, split_records in records.items():
        split_payload = split_payloads[split]
        if not isinstance(split_payload, dict):
            return None
        for record in split_records:
            dialogue_key = record.dialogue_id
            if dialogue_key not in split_payload and str(dialogue_key) in split_payload:
                dialogue_key = str(dialogue_key)
            if dialogue_key not in split_payload:
                return None
            sequence = np.asarray(split_payload[dialogue_key], dtype=np.float32)
            if sequence.ndim < 2 or record.utterance_id >= sequence.shape[0]:
                return None
            output[record.sample_id] = sequence[record.utterance_id].reshape(-1).astype(np.float32)
    return output, str(path)


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
            output[record.sample_id] = raw_video_stat_vector(record, video_path)
    if missing:
        preview = ", ".join(missing[:5])
        raise ProtocolError(f"missing raw video files for {len(missing)} MELD rows; examples: {preview}")
    return output


def raw_video_stat_vector(record: MeldRecord, video_path: Path) -> np.ndarray:
    size = video_path.stat().st_size
    duration = max(parse_timestamp_seconds(record.end_time) - parse_timestamp_seconds(record.start_time), 0.0)
    return np.array(
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


def build_cv2_video_stats(
    records: dict[str, list[MeldRecord]],
    raw_root: Path,
    cache_dir: Path | None,
    *,
    frame_count: int = 8,
) -> dict[str, np.ndarray]:
    try:
        import cv2
    except Exception as exc:  # pragma: no cover - depends on server extra.
        raise ProtocolError(
            "--video-source cv2_stats requires opencv-python-headless. "
            "Install it in the project env or set PYTHONPATH to the project-local dependency path."
        ) from exc

    all_records = [record for split_records in records.values() for record in split_records]
    cache_path = None
    cache: dict[str, np.ndarray] = {}
    if cache_dir is not None:
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_path = cache_dir / f"meld_cv2_stats_v1_f{frame_count}.pkl"
        if cache_path.exists():
            with cache_path.open("rb") as handle:
                cache = pickle.load(handle)

    output: dict[str, np.ndarray] = {}
    computed = 0
    missing: list[str] = []
    for record in all_records:
        if record.sample_id in cache:
            output[record.sample_id] = cache[record.sample_id]
            continue
        video_path = find_raw_video(raw_root, record.split, record.raw_filename)
        if video_path is None:
            missing.append(f"{record.split}:{record.raw_filename}")
            continue
        try:
            vector = extract_cv2_video_feature(video_path, frame_count=frame_count, cv2=cv2)
        except ProtocolError:
            vector = _pad_feature(raw_video_stat_vector(record, video_path), CV2_VIDEO_FEATURE_DIM)
        cache[record.sample_id] = vector
        output[record.sample_id] = vector
        computed += 1
        if cache_path is not None and computed % 250 == 0:
            with cache_path.open("wb") as handle:
                pickle.dump(cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

    if missing:
        preview = ", ".join(missing[:5])
        raise ProtocolError(f"missing raw video files for {len(missing)} MELD rows; examples: {preview}")
    if cache_path is not None:
        with cache_path.open("wb") as handle:
            pickle.dump(cache, handle, protocol=pickle.HIGHEST_PROTOCOL)
    return output


def extract_cv2_video_feature(video_path: Path, *, frame_count: int, cv2: Any) -> np.ndarray:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ProtocolError(f"cv2 could not open video: {video_path}")
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
    width = float(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0.0)
    height = float(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0.0)
    if total_frames <= 0:
        sample_indices = [0]
    else:
        sample_indices = np.linspace(0, max(total_frames - 1, 0), num=frame_count, dtype=int).tolist()

    frame_features: list[np.ndarray] = []
    gray_frames: list[np.ndarray] = []
    for frame_index in sample_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ok, frame = cap.read()
        if not ok or frame is None:
            continue
        small = cv2.resize(frame, (64, 64), interpolation=cv2.INTER_AREA)
        rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[..., 0] /= 179.0
        hsv[..., 1:] /= 255.0
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
        gray_frames.append(gray)
        grad_x = np.abs(np.diff(gray, axis=1))
        grad_y = np.abs(np.diff(gray, axis=0))
        rgb_hist = np.concatenate(
            [np.histogram(rgb[..., channel], bins=8, range=(0.0, 1.0), density=True)[0] for channel in range(3)]
        ).astype(np.float32)
        rgb_hist = rgb_hist / max(float(rgb_hist.sum()), 1e-6)
        frame_features.append(
            np.concatenate(
                [
                    rgb.mean(axis=(0, 1)),
                    rgb.std(axis=(0, 1)),
                    hsv.mean(axis=(0, 1)),
                    hsv.std(axis=(0, 1)),
                    np.array(
                        [
                            gray.mean(),
                            gray.std(),
                            np.percentile(gray, 10),
                            np.percentile(gray, 50),
                            np.percentile(gray, 90),
                            grad_x.mean(),
                            grad_x.std(),
                            grad_y.mean(),
                            grad_y.std(),
                        ],
                        dtype=np.float32,
                    ),
                    rgb_hist,
                ]
            ).astype(np.float32)
        )
    cap.release()

    if not frame_features:
        raise ProtocolError(f"cv2 could not read frames from video: {video_path}")
    frame_matrix = np.vstack(frame_features)
    motion_values = []
    for left, right in zip(gray_frames, gray_frames[1:]):
        motion_values.append(float(np.mean(np.abs(right - left))))
    motion = np.array(
        [
            np.mean(motion_values) if motion_values else 0.0,
            np.std(motion_values) if motion_values else 0.0,
        ],
        dtype=np.float32,
    )
    metadata = np.array(
        [
            math.log1p(video_path.stat().st_size),
            total_frames / 1000.0,
            fps / 60.0,
            width / 1920.0,
            height / 1080.0,
        ],
        dtype=np.float32,
    )
    return np.concatenate(
        [
            frame_matrix.mean(axis=0),
            frame_matrix.std(axis=0),
            motion,
            metadata,
        ]
    ).astype(np.float32)


def build_semantic_clip_video_features(
    records: dict[str, list[MeldRecord]],
    raw_root: Path,
    cache_dir: Path | None,
    *,
    model_name: str = DEFAULT_SEMVIS_MODEL,
    frame_count: int = 8,
    batch_frames: int = 64,
    device: str = "auto",
) -> dict[str, np.ndarray]:
    try:
        import cv2
        import torch
        from PIL import Image
        from transformers import CLIPModel, CLIPProcessor
    except Exception as exc:  # pragma: no cover - depends on server extras.
        raise ProtocolError(
            "--video-source semvis_clip requires opencv-python-headless, torch, "
            "Pillow, and transformers with CLIP support."
        ) from exc

    if frame_count <= 0:
        raise ProtocolError("--semvis-frame-count must be positive")
    if batch_frames <= 0:
        raise ProtocolError("--semvis-batch-frames must be positive")

    resolved_device = _resolve_torch_device(torch, device)
    processor = CLIPProcessor.from_pretrained(model_name)
    model = CLIPModel.from_pretrained(model_name)
    model.eval()
    model.to(resolved_device)
    feature_dim = _clip_feature_dim(model)

    all_records = [record for split_records in records.values() for record in split_records]
    cache_path = None
    cache: dict[str, np.ndarray] = {}
    if cache_dir is not None:
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_path = cache_dir / f"meld_semvis_clip_v1_{_cache_key(model_name)}_f{frame_count}.pkl"
        if cache_path.exists():
            with cache_path.open("rb") as handle:
                cache = pickle.load(handle)

    output: dict[str, np.ndarray] = {}
    missing: list[str] = []
    pending_records: list[MeldRecord] = []
    pending_counts: list[int] = []
    pending_images: list[Any] = []
    computed = 0
    last_saved = 0

    def flush() -> None:
        nonlocal computed, last_saved
        if not pending_records:
            return
        if pending_images:
            frame_embeddings = _encode_clip_images(
                pending_images,
                processor=processor,
                model=model,
                torch=torch,
                device=resolved_device,
            )
        else:
            frame_embeddings = np.empty((0, feature_dim), dtype=np.float32)

        cursor = 0
        for record, count in zip(pending_records, pending_counts):
            if count == 0:
                vector = np.zeros(feature_dim, dtype=np.float32)
            else:
                vector = frame_embeddings[cursor : cursor + count].mean(axis=0).astype(np.float32)
                cursor += count
                norm = float(np.linalg.norm(vector))
                if norm > 0.0:
                    vector = (vector / norm).astype(np.float32)
            cache[record.sample_id] = vector
            output[record.sample_id] = vector

        computed += len(pending_records)
        pending_records.clear()
        pending_counts.clear()
        pending_images.clear()
        if cache_path is not None and computed - last_saved >= 100:
            with cache_path.open("wb") as handle:
                pickle.dump(cache, handle, protocol=pickle.HIGHEST_PROTOCOL)
            last_saved = computed

    for record in all_records:
        if record.sample_id in cache:
            output[record.sample_id] = cache[record.sample_id]
            continue
        video_path = find_raw_video(raw_root, record.split, record.raw_filename)
        if video_path is None:
            missing.append(f"{record.split}:{record.raw_filename}")
            continue
        try:
            frames = extract_semantic_video_frames(
                video_path,
                frame_count=frame_count,
                cv2=cv2,
                image_cls=Image,
            )
        except ProtocolError:
            frames = []
        pending_records.append(record)
        pending_counts.append(len(frames))
        pending_images.extend(frames)
        if len(pending_images) >= batch_frames:
            flush()

    flush()
    if missing:
        preview = ", ".join(missing[:5])
        raise ProtocolError(f"missing raw video files for {len(missing)} MELD rows; examples: {preview}")
    if cache_path is not None:
        with cache_path.open("wb") as handle:
            pickle.dump(cache, handle, protocol=pickle.HIGHEST_PROTOCOL)
    return output


def extract_semantic_video_frames(video_path: Path, *, frame_count: int, cv2: Any, image_cls: Any) -> list[Any]:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ProtocolError(f"cv2 could not open video: {video_path}")
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    if total_frames <= 0:
        sample_indices = [0]
    else:
        sample_indices = np.linspace(0, max(total_frames - 1, 0), num=frame_count, dtype=int).tolist()

    frames = []
    for frame_index in sample_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ok, frame = cap.read()
        if not ok or frame is None:
            continue
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frames.append(image_cls.fromarray(rgb))
    cap.release()
    if not frames:
        raise ProtocolError(f"cv2 could not read frames from video: {video_path}")
    return frames


def _encode_clip_images(
    images: list[Any],
    *,
    processor: Any,
    model: Any,
    torch: Any,
    device: str,
) -> np.ndarray:
    inputs = processor(images=images, return_tensors="pt")
    inputs = {key: value.to(device) for key, value in inputs.items()}
    with torch.no_grad():
        features = model.get_image_features(**inputs)
        features = features / features.norm(dim=-1, keepdim=True).clamp_min(1e-12)
    return features.detach().cpu().numpy().astype(np.float32)


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
        feature_key = MODALITY_FEATURE_KEYS[modality]
        modality_features = []
        for record in rows:
            vector = bundle.features[feature_key][record.sample_id]
            vector = apply_degradation(
                vector,
                modality=modality,
                slice_name=slice_name,
                record=record,
                seed=seed,
                profile=bundle.degradation_profile,
            )
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
    profile: str = "default",
) -> np.ndarray:
    if slice_name == CLEAN_SLICE:
        return vector
    base_degraded_modalities = {
        "degraded_text": {"T"},
        "degraded_audio": {"A"},
        "degraded_video": {"V"},
        "mixed_degraded": {"T", "A", "V"},
    }[slice_name]
    if profile == "default":
        degraded_modalities = base_degraded_modalities
    elif profile == "text_stress":
        degraded_modalities = set(base_degraded_modalities) | {"T"}
    else:
        raise ProtocolError(f"unknown degradation profile: {profile!r}")

    if modality not in degraded_modalities:
        return vector

    if profile == "text_stress" and modality == "T":
        scale = 0.0
    elif slice_name == "mixed_degraded":
        scale = 0.35
    else:
        scale = 0.0
    if scale == 0.0:
        return np.zeros_like(vector)
    rng = np.random.default_rng(_stable_seed(record.sample_id, modality, seed))
    noise = rng.normal(0.0, 0.01, size=vector.shape).astype(np.float32)
    return (vector * scale + noise).astype(np.float32)


def profile_template(bundle: FeatureBundle, model: Any, *, template: str, repeats: int = 120) -> dict[str, float]:
    x_eval, _ = build_matrix(bundle, "validation", template, slice_name=CLEAN_SLICE, seed=0)
    batch_size = min(1024, len(x_eval))
    sample = x_eval[:batch_size]
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


def build_q_policy_map(degradation_profile: str = "default") -> list[dict[str, str]]:
    if degradation_profile == "default":
        return [
            {"slice": "clean", "proposed_template": "TAV", "proxy_rule": "all modalities reliable"},
            {"slice": "degraded_text", "proposed_template": "AV", "proxy_rule": "avoid low-reliability text"},
            {"slice": "degraded_audio", "proposed_template": "TV", "proxy_rule": "avoid low-reliability audio"},
            {"slice": "degraded_video", "proposed_template": "TA", "proxy_rule": "avoid low-reliability video"},
            {"slice": "mixed_degraded", "proposed_template": "T", "proxy_rule": "fallback to text anchor under mixed uncertainty"},
        ]
    if degradation_profile == "text_stress":
        return [
            {"slice": "clean", "proposed_template": "TAV", "proxy_rule": "all modalities reliable"},
            {"slice": "degraded_text", "proposed_template": "AV", "proxy_rule": "avoid low-reliability text"},
            {"slice": "degraded_audio", "proposed_template": "V", "proxy_rule": "avoid low-reliability text and audio"},
            {"slice": "degraded_video", "proposed_template": "A", "proxy_rule": "avoid low-reliability text and video"},
            {"slice": "mixed_degraded", "proposed_template": "V", "proxy_rule": "fallback to semantic visual anchor under text-stress mixed uncertainty"},
        ]
    raise ProtocolError(f"unknown degradation_profile={degradation_profile!r}")


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


def _pad_feature(value: np.ndarray, target_dim: int) -> np.ndarray:
    value = value.astype(np.float32).reshape(-1)
    if value.shape[0] == target_dim:
        return value
    if value.shape[0] > target_dim:
        return value[:target_dim]
    output = np.zeros(target_dim, dtype=np.float32)
    output[: value.shape[0]] = value
    return output


def _resolve_torch_device(torch: Any, requested: str) -> str:
    if requested == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    return requested


def _clip_feature_dim(model: Any) -> int:
    config = getattr(model, "config", None)
    if config is not None:
        projection_dim = getattr(config, "projection_dim", None)
        if projection_dim:
            return int(projection_dim)
        vision_config = getattr(config, "vision_config", None)
        hidden_size = getattr(vision_config, "hidden_size", None) if vision_config is not None else None
        if hidden_size:
            return int(hidden_size)
    return 512


def _cache_key(value: str) -> str:
    return "".join(character if character.isalnum() else "-" for character in value).strip("-").lower()


def _stable_seed(sample_id: str, modality: str, seed: int) -> int:
    digest = hashlib.sha256(f"{sample_id}:{modality}:{seed}".encode()).digest()
    return int.from_bytes(digest[:8], "little", signed=False)


def _stable_hash_float(value: str) -> float:
    digest = hashlib.sha256(value.encode()).digest()
    return int.from_bytes(digest[:4], "little") / float(2**32)
