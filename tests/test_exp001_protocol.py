from pathlib import Path
import csv
import pickle
import tempfile
import unittest

from autofusion_bench.exp001.costs import build_budget_profile, load_cost_table
from autofusion_bench.exp001.meld_producer import (
    build_q_policy_map,
    build_feature_bundle,
    build_matrix,
    load_annotations,
    parse_timestamp_seconds,
)
from autofusion_bench.exp001.run_meld_table_producer import _parse_args
from autofusion_bench.exp001.runner import run_exp001


ROOT = Path(__file__).resolve().parents[1]
EXP_DIR = ROOT / "experiments" / "exp-001-decision-surface-pilot"
FIXTURES = EXP_DIR / "fixtures"


class Exp001ProtocolTests(unittest.TestCase):
    def test_budget_profile_keeps_tav_illegal_under_tight(self) -> None:
        costs = load_cost_table(FIXTURES / "cost_table.csv")
        profile = build_budget_profile(costs)
        self.assertGreaterEqual(profile.spread_ratio, 1.5)
        self.assertIn("AV", profile.legal_by_budget["tight"])
        self.assertNotIn("TAV", profile.legal_by_budget["tight"])

    def test_fixture_smoke_passes_protocol_and_signal_gates(self) -> None:
        summary = run_exp001(
            config_path=EXP_DIR / "config.yaml",
            cost_table_path=FIXTURES / "cost_table.csv",
            outcome_table_path=FIXTURES / "outcome_table.csv",
            q_policy_map_path=FIXTURES / "q_policy_map.csv",
            q_proxy_table_path=FIXTURES / "q_proxy_table.csv",
            q_diagnostics_path=FIXTURES / "q_diagnostics.csv",
            corruption_manifest_path=FIXTURES / "corruption_manifest.csv",
            output_dir=EXP_DIR / "outputs" / "unittest-smoke",
        )
        metrics = summary["metrics"]
        self.assertTrue(summary["status"]["protocol_passed"])
        self.assertTrue(summary["status"]["benchmark_signal_passed"])
        self.assertGreaterEqual(metrics["best_single_axis_oracle_regret_dt"], 3.0)
        self.assertGreaterEqual(metrics["joint_gap_closure"], 0.3)

    def test_meld_feature_bundle_loads_official_style_pickles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            annotations = root / "annotations"
            features = root / "features"
            annotations.mkdir()
            features.mkdir()
            for filename in ("train_sent_emo.csv", "dev_sent_emo.csv", "test_sent_emo.csv"):
                _write_annotation(annotations / filename)
            payload = [
                {"0_0": [1.0, 0.0], "0_1": [0.5, 0.5]},
                {"0_0": [0.0, 1.0], "0_1": [0.2, 0.8]},
                {"0_0": [0.3, 0.7], "0_1": [0.9, 0.1]},
            ]
            for filename in (
                "text_glove_average_emotion.pkl",
                "audio_embeddings_feature_selection_emotion.pkl",
                "visual_embeddings_feature_selection_emotion.pkl",
            ):
                with (features / filename).open("wb") as handle:
                    pickle.dump(payload, handle)

            records = load_annotations(annotations)
            bundle = build_feature_bundle(records, features_dir=features, raw_root=None, video_source="pickle")
            self.assertEqual(bundle.features["text"]["train:0_0"].shape, (2,))
            self.assertIn("visual_embeddings_feature_selection_emotion.pkl", bundle.sources["video"])
            matrix, labels = build_matrix(bundle, "train", "TAV", slice_name="clean", seed=0)
            self.assertEqual(matrix.shape, (2, 6))
            self.assertEqual(labels.tolist(), [0, 4])

    def test_meld_audio_concat_uses_dialogue_sequence_features(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            annotations = root / "annotations"
            features = root / "features"
            annotations.mkdir()
            features.mkdir()
            for filename in ("train_sent_emo.csv", "dev_sent_emo.csv", "test_sent_emo.csv"):
                _write_annotation(annotations / filename)
            base_payload = [
                {"0_0": [1.0, 0.0], "0_1": [0.5, 0.5]},
                {"0_0": [0.0, 1.0], "0_1": [0.2, 0.8]},
                {"0_0": [0.3, 0.7], "0_1": [0.9, 0.1]},
            ]
            sequence_payload = [
                {0: [[2.0, 0.0], [2.0, 1.0]]},
                {0: [[3.0, 0.0], [3.0, 1.0]]},
                {0: [[4.0, 0.0], [4.0, 1.0]]},
            ]
            for filename in (
                "text_glove_average_emotion.pkl",
                "visual_embeddings_feature_selection_emotion.pkl",
            ):
                with (features / filename).open("wb") as handle:
                    pickle.dump(base_payload, handle)
            with (features / "audio_embeddings_feature_selection_emotion.pkl").open("wb") as handle:
                pickle.dump(base_payload, handle)
            with (features / "audio_emotion.pkl").open("wb") as handle:
                pickle.dump(sequence_payload, handle)

            records = load_annotations(annotations)
            bundle = build_feature_bundle(
                records,
                features_dir=features,
                raw_root=None,
                video_source="pickle",
                audio_source="official_concat",
            )
            self.assertEqual(bundle.features["audio"]["train:0_0"].shape, (4,))
            self.assertEqual(bundle.features["audio"]["train:0_1"].tolist(), [0.5, 0.5, 2.0, 1.0])

    def test_parse_meld_timestamp_seconds(self) -> None:
        self.assertAlmostEqual(parse_timestamp_seconds("00:14:38,127"), 878.127)
        self.assertAlmostEqual(parse_timestamp_seconds("0:10:46,146"), 646.146)

    def test_meld_table_producer_accepts_semvis_clip_options(self) -> None:
        args = _parse_args(
            [
                "--video-source",
                "semvis_clip",
                "--semvis-model",
                "openai/clip-vit-base-patch32",
                "--semvis-frame-count",
                "16",
                "--semvis-batch-frames",
                "32",
                "--semvis-device",
                "cpu",
                "--degradation-profile",
                "text_stress",
            ]
        )
        self.assertEqual(args.video_source, "semvis_clip")
        self.assertEqual(args.semvis_model, "openai/clip-vit-base-patch32")
        self.assertEqual(args.semvis_frame_count, 16)
        self.assertEqual(args.semvis_batch_frames, 32)
        self.assertEqual(args.semvis_device, "cpu")
        self.assertEqual(args.degradation_profile, "text_stress")

    def test_text_stress_profile_degrades_text_across_degraded_slices(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            annotations = root / "annotations"
            features = root / "features"
            annotations.mkdir()
            features.mkdir()
            for filename in ("train_sent_emo.csv", "dev_sent_emo.csv", "test_sent_emo.csv"):
                _write_annotation(annotations / filename)
            payload = [
                {"0_0": [1.0, 0.0], "0_1": [0.5, 0.5]},
                {"0_0": [0.0, 1.0], "0_1": [0.2, 0.8]},
                {"0_0": [0.3, 0.7], "0_1": [0.9, 0.1]},
            ]
            for filename in (
                "text_glove_average_emotion.pkl",
                "audio_embeddings_feature_selection_emotion.pkl",
                "visual_embeddings_feature_selection_emotion.pkl",
            ):
                with (features / filename).open("wb") as handle:
                    pickle.dump(payload, handle)

            records = load_annotations(annotations)
            default_bundle = build_feature_bundle(records, features_dir=features, raw_root=None, video_source="pickle")
            stress_bundle = build_feature_bundle(
                records,
                features_dir=features,
                raw_root=None,
                video_source="pickle",
                degradation_profile="text_stress",
            )
            default_text, _ = build_matrix(default_bundle, "validation", "T", slice_name="degraded_audio", seed=0)
            stress_text, _ = build_matrix(stress_bundle, "validation", "T", slice_name="degraded_audio", seed=0)
            stress_video, _ = build_matrix(stress_bundle, "validation", "V", slice_name="degraded_audio", seed=0)

            self.assertGreater(float(default_text.sum()), 0.0)
            self.assertEqual(float(stress_text.sum()), 0.0)
            self.assertGreater(float(stress_video.sum()), 0.0)

    def test_text_stress_q_policy_map_avoids_text_when_other_modalities_degrade(self) -> None:
        mapping = {row["slice"]: row["proposed_template"] for row in build_q_policy_map("text_stress")}
        self.assertEqual(mapping["degraded_audio"], "V")
        self.assertEqual(mapping["degraded_video"], "A")


if __name__ == "__main__":
    unittest.main()


def _write_annotation(path: Path) -> None:
    fieldnames = [
        "Sr No.",
        "Utterance",
        "Speaker",
        "Emotion",
        "Sentiment",
        "Dialogue_ID",
        "Utterance_ID",
        "Season",
        "Episode",
        "StartTime",
        "EndTime",
    ]
    rows = [
        {
            "Sr No.": 1,
            "Utterance": "hello there",
            "Speaker": "Rachel",
            "Emotion": "neutral",
            "Sentiment": "neutral",
            "Dialogue_ID": 0,
            "Utterance_ID": 0,
            "Season": 1,
            "Episode": 1,
            "StartTime": "00:00:01,000",
            "EndTime": "00:00:02,000",
        },
        {
            "Sr No.": 2,
            "Utterance": "that is great",
            "Speaker": "Ross",
            "Emotion": "joy",
            "Sentiment": "positive",
            "Dialogue_ID": 0,
            "Utterance_ID": 1,
            "Season": 1,
            "Episode": 1,
            "StartTime": "00:00:03,000",
            "EndTime": "00:00:04,000",
        },
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
