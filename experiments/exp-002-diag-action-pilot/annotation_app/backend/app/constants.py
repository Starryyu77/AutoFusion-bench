"""Shared field options for the exp-002 annotation UI."""

QUALITY_STATUS = [
    "clean",
    "corrupted_usable",
    "corrupted_unusable",
    "missing",
    "not_applicable",
]

RELEVANCE_STATUS = [
    "necessary",
    "sufficient",
    "supportive",
    "irrelevant",
    "unclear",
]

FIELD_OPTIONS = {
    "review_status": [
        "needs_human_review",
        "in_progress",
        "reviewed",
        "needs_adjudication",
        "rejected",
    ],
    "source_decision": ["accept", "reject", "adjudicate"],
    "answerable_without_media": ["yes", "no", "unclear"],
    "blind_confidence": ["high", "medium", "low"],
    "source_modality": RELEVANCE_STATUS,
    "audio_video_joint_required": ["yes", "no", "unclear"],
    "modality_quality": QUALITY_STATUS,
    "modality_task_relevance": RELEVANCE_STATUS,
    "cross_modal_relation": [
        "consistent",
        "conflicting",
        "misaligned",
        "not_applicable",
        "unclear",
    ],
    "corruption_relevance": ["answer_relevant", "answer_irrelevant", "unclear"],
    "corruption_effect": [
        "no_effect",
        "route_change_only",
        "confidence_drop",
        "makes_unanswerable",
        "creates_conflict",
        "unclear",
    ],
    "post_corruption_answerability": [
        "answerable",
        "partially_answerable",
        "unanswerable",
        "unclear",
    ],
    "cross_modal_recoverability": [
        "recoverable",
        "partially_recoverable",
        "unrecoverable",
        "not_needed",
        "unclear",
    ],
    "main_answerability": ["answerable", "unanswerable", "exclude_from_main"],
    "oracle_answerability": ["answerable", "unanswerable", "partial"],
    "oracle_risk_level": ["normal", "cautious"],
    "annotation_confidence": ["high", "medium", "low"],
    "route_modality": ["audio", "video"],
}

DISAGREEMENT_FIELDS = [
    "source_modality_necessity",
    "modality_quality_status",
    "modality_task_relevance",
    "cross_modal_relation",
    "corruption_relevance",
    "corruption_effect",
    "post_corruption_answerability",
    "cross_modal_recoverability",
    "main_answerability",
    "recovery_source",
    "oracle_policy_action",
    "annotation_confidence",
]
