"""MELD-specific schema helpers for exp-001 producers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


EMOTION_LABELS = ("neutral", "surprise", "fear", "sadness", "joy", "disgust", "anger")
LABEL_TO_ID = {label: index for index, label in enumerate(EMOTION_LABELS)}

ANNOTATION_FILES = {
    "train": "train_sent_emo.csv",
    "validation": "dev_sent_emo.csv",
    "test": "test_sent_emo.csv",
}

ANNOTATION_URLS = {
    split: (
        "https://raw.githubusercontent.com/declare-lab/MELD/master/data/MELD/"
        f"{filename}"
    )
    for split, filename in ANNOTATION_FILES.items()
}

FEATURES_URL = "https://web.eecs.umich.edu/~mihalcea/downloads/MELD.Features.Models.tar.gz"
RAW_URL = "https://web.eecs.umich.edu/~mihalcea/downloads/MELD.Raw.tar.gz"

FEATURE_PICKLE_CANDIDATES = {
    "text": (
        "text_glove_average_emotion.pkl",
        "text_glove_CNN_emotion.pkl",
        "text_emotion.pkl",
    ),
    "audio": (
        "audio_embeddings_feature_selection_emotion.pkl",
        "audio_emotion.pkl",
    ),
    "video": (
        "video_embeddings_feature_selection_emotion.pkl",
        "visual_embeddings_feature_selection_emotion.pkl",
        "video_emotion.pkl",
        "visual_emotion.pkl",
        "meld_visual_features.pkl",
    ),
}

RAW_SPLIT_DIRS = {
    "train": ("train", "output_repeated_splits_train"),
    "validation": ("dev", "output_repeated_splits_dev"),
    "test": ("test", "output_repeated_splits_test"),
}


@dataclass(frozen=True)
class MeldRecord:
    split: str
    sample_id: str
    key: str
    utterance: str
    speaker: str
    emotion: str
    label: int
    sentiment: str
    dialogue_id: int
    utterance_id: int
    season: int
    episode: int
    start_time: str
    end_time: str

    @property
    def raw_filename(self) -> str:
        return f"dia{self.dialogue_id}_utt{self.utterance_id}.mp4"


def expected_annotation_path(root: Path, split: str) -> Path:
    return root / ANNOTATION_FILES[split]

